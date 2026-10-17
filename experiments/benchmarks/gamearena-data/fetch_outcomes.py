"""Kaggle Game Arena outcomes per (game, role, model) from a stratified episode sample.

Needs fetch_tasks.py in this folder (helpers, game table). Same sources and robots.txt rule.

Sampling: per dataset, non-empty episodes sorted by EpisodeId (a proxy for time) are cut into
10 equal strata and N[game] / 10 episodes are drawn at random from each (seed SEED). The draw
does not see models (the zip directory has only episode ids), so per-model counts are roughly
2N/M (M models). Werewolf and team games have more seats per episode.

Outcomes (see NOTES.md for what each means and which one we recommend):
  win / draw / loss, win_rate      relative: mean 0.5 by construction in symmetric 2-player games
  forfeit_rate                     absolute: share of this model's games lost by an illegal or
                                   unparsable move after all retries (env INVALID path)
  error_rate                       share of games where this seat ended ERROR / TIMEOUT
  retry_rate                       absolute: share of decisions needing more than one model call
  abs_score (+ abs_score_name)     game-specific absolute score, where one exists
  game-specific extras             bargaining deal / Pareto / welfare, word-art DQ / solve,
                                   word-association precision / trap, werewolf votes
  lb_score, p_beat_anchor          public leaderboard score; for Elo-type boards the implied
                                   P(beat ANCHOR) = 1 / (1 + 10^(-(s - s_anchor) / 400))

Writes:
  data/downloads/gamearena/derived/seats.parquet        one row per episode x seat (gitignored)
  data/downloads/gamearena/derived/status_texts.json   harness status strings seen, per game
  experiments/benchmarks/gamearena-data/outcomes.csv    one row per game x role x model
  experiments/benchmarks/gamearena-data/leaderboards.csv
  experiments/benchmarks/gamearena-data/sample_counts.csv
  experiments/benchmarks/gamearena-data/crosscheck.csv  sample win rate vs leaderboard, per game

Run: python experiments/benchmarks/gamearena-data/fetch_outcomes.py
"""

import itertools
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_tasks import (CACHE, GAMES, RemoteZip, decision_role, decisions, leaderboard, repo,  # noqa: E402
                         robots_status, werewolf_players)

HERE = Path(__file__).resolve().parent
DERIVED = CACHE / "derived"
SEED = 20261003
N_DEFAULT = 500
N = {"bargaining": 800, "dark-hex": 800, "go": 300, "chess-text-openings": 300, "word-art": 300,
     "werewolf": 200, "poker-heads-up": 120}
BUDGET_BYTES = 2.5e9
ANCHOR = "GPT-5 mini"
ELO_BOARDS = {g for g in GAMES if g not in ("poker-heads-up", "werewolf")}
FORFEIT_RE = re.compile(r"forfeit|invalid action", re.I)


# ------------------------------------------------------------------ models, versions

def model_names() -> dict:
    """lower-case slug or name -> leaderboard display name."""
    m = {}
    for g in list(GAMES) + ["game-arena"]:
        for r in leaderboard(GAMES[g]["lb"] if g in GAMES else g)["rows"]:
            m[r["modelVersionSlug"].lower()] = r["modelVersionName"]
            m[r["modelVersionName"].lower()] = r["modelVersionName"]
    return m


def version_dates() -> dict:
    """kaggle-environments version -> first commit date with that version in pyproject.toml."""
    d = repo("kenv")
    log = subprocess.run(["git", "-C", str(d), "log", "--reverse", "--format=%H %cs", "--", "pyproject.toml"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    out = {}
    for line in filter(None, log):
        h, date = line.split()
        txt = subprocess.run(["git", "-C", str(d), "show", f"{h}:pyproject.toml"], capture_output=True, text=True).stdout
        m = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.M)
        if m and m.group(1) not in out:
            out[m.group(1)] = date
    return out


def leaderboard_table() -> pd.DataFrame:
    rows = []
    for g in list(GAMES) + ["game-arena"]:
        slug = GAMES[g]["lb"] if g in GAMES else g
        for r in leaderboard(slug)["rows"]:
            rec = dict(game=g, model=r["modelVersionName"], model_slug=r["modelVersionSlug"])
            for t in r["taskResults"]:
                nr = t["result"].get("numericResult", {})
                name = t["benchmarkTaskName"]
                key = {"Score": "lb_score", "Mean BB/100": "lb_score", "Equilibrium Rating": "lb_score",
                       "Avg. Tokens/Turn": "tokens_per_turn", "Avg. Cost/Turn": "cents_per_turn",
                       "Matches Played": "matches_played", "Games Covered": "games_covered"}.get(name, name)
                rec[key] = nr.get("value", 0.0)  # proto3 JSON omits zeros: the anchor model has score 0
                ci = nr.get("unevenConfidenceInterval") or {}
                if key == "lb_score":
                    rec["lb_metric"] = name
                    rec["lb_ci_plus"] = ci.get("plus", nr.get("confidenceInterval"))
                    rec["lb_ci_minus"] = ci.get("minus", nr.get("confidenceInterval"))
            rows.append(rec)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ sampling

def sample(listing: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    df = listing[listing.file_size > 0].sort_values("episode_id").reset_index(drop=True)
    if n >= len(df):
        return df
    rng = random.Random(seed)
    strata = np.array_split(np.arange(len(df)), 10)
    per = [n // 10 + (1 if i < n % 10 else 0) for i in range(10)]
    idx = sorted(itertools.chain.from_iterable(rng.sample(list(s), k) for s, k in zip(strata, per)))
    return df.iloc[idx]


# ------------------------------------------------------------------ per-game parsing

def _obs_json(a: dict) -> dict:
    s = (a.get("observation") or {}).get("observationString")
    try:
        return json.loads(s) if s else {}
    except json.JSONDecodeError:
        return {}


def bargaining_extra(ep: dict) -> dict:
    last = ep["steps"][-1]
    o0, o1 = _obs_json(last[0]), _obs_json(last[1])
    items = list(o0.get("pool", {}))
    pool = [o0["pool"][k] for k in items]
    v = [[o0["my_values"][k] for k in items], [o1["my_values"][k] for k in items]]
    allocs = list(itertools.product(*[range(q + 1) for q in pool]))  # items that seat 0 receives
    pay = [(sum(a * b for a, b in zip(x, v[0])), sum((q - a) * b for q, a, b in zip(pool, x, v[1]))) for x in allocs]
    best = max(p0 + p1 for p0, p1 in pay)
    r = [float(x) for x in ep["rewards"]]
    deal = bool(o0.get("agreement_reached"))
    pareto = deal and not any(p0 >= r[0] and p1 >= r[1] and (p0 > r[0] or p1 > r[1]) for p0, p1 in pay)
    return dict(deal=deal, welfare=sum(r), welfare_max=best, pareto=pareto)


def werewolf_rows(ep: dict) -> list[dict]:
    ge = ep["info"]["GAME_END"]
    players = werewolf_players(ep)
    role = {p["id"]: p["role"] for p in players}
    elim = {e["player_id"]: (e["eliminated_during_day"], e["eliminated_during_phase"]) for e in ge["elimination_info"]}

    def alive_at_day_vote(pid, day):
        d, ph = elim.get(pid, (-1, None))
        if ph is None:
            return True
        return not ((ph == "Night" and d <= day - 1) or (ph == "Day" and d < day))

    votes = defaultdict(list)  # actor -> [(target, chance)]
    received = Counter()
    n_village_votes = Counter()  # per day
    errors = Counter()
    for d in decisions(ep):
        kw = d["action"].get("kwargs") or {}
        actor = kw.get("actor_id")
        if kw.get("error"):
            errors[actor] += 1
        if d["action"].get("action_type") == "VoteAction" and kw.get("phase") == "Day" and kw.get("target_id"):
            day = int(kw.get("day", 0))
            alive = [p for p in role if alive_at_day_vote(p, day)]
            wolves = sum(role[p] == "werewolf" for p in alive if p != actor)
            votes[actor].append((role.get(kw["target_id"]) == "werewolf", wolves / max(1, len(alive) - 1)))
            if role.get(actor) != "werewolf":
                received[kw["target_id"]] += 1
                n_village_votes[actor] += 1
    total_village_votes = sum(n_village_votes.values())
    out = []
    for seat, p in enumerate(players):
        vs = votes.get(p["id"], [])
        rec = dict(seat=seat, team="werewolves" if p["role"] == "werewolf" else "villagers", role=p["role"],
                   model_raw=p["model"], reward=float(ep["rewards"][seat] or 0), survived=p["id"] not in elim or
                   elim[p["id"]][1] is None, n_errors=errors[p["id"]])
        if p["role"] != "werewolf":
            rec.update(n_votes=len(vs), vote_hits=sum(h for h, _ in vs), vote_chance=sum(c for _, c in vs))
        else:
            rec.update(votes_received=received[p["id"]], village_votes=total_village_votes)
        out.append(rec)
    return out


def seat_rows(game: str, ep: dict) -> list[dict]:
    """One row per seat (team games: per seat too; team outcomes repeated on both seats)."""
    eid, ver = ep["info"].get("EpisodeId"), ep.get("module_version")
    decs = decisions(ep)
    by_seat = defaultdict(list)
    for d in decs:
        by_seat[d["seat"]].append(d)
    statuses = ep.get("statuses") or []
    if game == "werewolf":
        rows = werewolf_rows(ep)
    else:
        names = ep["info"]["TeamNames"]
        rew = [None if x is None else float(x) for x in ep["rewards"]]
        team_of = (lambda s: s // 2) if len(names) == 4 else (lambda s: s)
        rows = [dict(seat=s, team=team_of(s), role="player", model_raw=names[s], reward=rew[s]) for s in range(len(names))]
        last = ep["steps"][-1]
        for r in rows:
            info = last[r["seat"]].get("info") or {}
            ds = by_seat.get(r["seat"], [])
            r["forfeit"] = bool(("actionSubmitted" in info and info.get("actionApplied") is None
                                 and info.get("actionSubmitted") is not None)
                                or (ds and FORFEIT_RE.search(ds[-1]["status"]) and ds[-1]["action"].get("submission") == -1))
        if game == "bargaining":
            ex = bargaining_extra(ep)
            for r in rows:
                r.update(ex)
        if game == "coin-game":
            o = _obs_json(last[0])
            tt = o.get("team_totals") or [None, None]
            for r in rows:
                r["team_score"] = tt[r["team"]]
        if game == "word-art":
            hist = (last[0].get("observation") or {}).get("history") or []
            for r in rows:
                c = ["blue", "yellow"][r["team"]]
                pts = [h.get(f"{c}_points") or 0 for h in hist]
                dq = [bool(h.get(f"{c}_art_disqualified")) for h in hist]
                r.update(team_score=sum(pts), rounds=len(hist), art_dq=sum(dq),
                         solved=sum(p > 0 for p in pts), solved_clean=sum(p > 0 for p, q in zip(pts, dq) if not q),
                         rounds_clean=sum(not q for q in dq))
        if game == "word-association":
            o = last[0].get("observation") or {}
            turns = o.get("current_game_turns") or []
            for r in rows:
                c = ["blue", "yellow"][r["team"]]
                res = [x for t in turns if t.get("team") == c for x in t.get("results", [])]
                r.update(guesses=len(res), own_hits=sum(x == c for x in res), trap=int("trap" in res),
                         clue_turns=sum(t.get("team") == c for t in turns),
                         invalid_clues=sum(t.get("team") == c and "invalid" in json.dumps(t).lower() for t in turns))
        if game == "poker-heads-up":
            hands = ep["configuration"].get("setNumHands") or 100
            for r in rows:
                r["bb_per_100"] = None if r["reward"] is None else r["reward"] / 2 / hands * 100
    for r in rows:
        ds = by_seat.get(r["seat"], [])
        st = statuses[r["seat"]] if r["seat"] < len(statuses) else None
        r.update(game=game, episode_id=eid, module_version=ver, final_status=st,
                 error=st in ("ERROR", "TIMEOUT"), n_decisions=len(ds), n_calls=sum(d["n_calls"] for d in ds),
                 n_retry_decisions=sum(d["n_calls"] > 1 for d in ds),
                 n_fallback=sum(d["status"] not in ("", "OK") for d in ds))
        if game in ("word-art", "word-association"):
            roles = Counter(decision_role(game, ep, d) for d in ds)
            r["roles_played"] = ",".join(sorted(k for k in roles if k))
    # opponents and result
    for r in rows:
        opp = [o for o in rows if o["team"] != r["team"]]
        r["opponents_raw"] = "|".join(sorted({o["model_raw"] for o in opp}))
        if game == "werewolf":
            r["result"] = "win" if r["reward"] > 0 else "loss"
        elif r["reward"] is None or any(o["reward"] is None for o in opp):
            r["result"] = None
        else:
            mine, theirs = r["reward"], max(o["reward"] for o in opp)
            r["result"] = "win" if mine > theirs else "loss" if mine < theirs else "draw"
    return rows


# ------------------------------------------------------------------ aggregation

def aggregate(seats: pd.DataFrame, lb: pd.DataFrame) -> pd.DataFrame:
    out = []
    lbs = lb.set_index(["game", "model"])
    for (game, role, model), g in seats.groupby(["game", "instance_role", "model"]):
        # team games: count each team once per episode
        gg = g.drop_duplicates(["episode_id", "team"]) if GAMES[game]["players"] == 4 else g
        res = gg.result.value_counts()
        n_res = int(res.sum())
        rec = dict(game=game, role=role, instance_id=f"{game}@{role}", model=model, n_episodes=gg.episode_id.nunique(),
                   n_seat_games=len(gg), win=int(res.get("win", 0)), draw=int(res.get("draw", 0)),
                   loss=int(res.get("loss", 0)),
                   win_rate=(res.get("win", 0) + 0.5 * res.get("draw", 0)) / n_res if n_res else np.nan,
                   error_rate=g.error.mean(), n_decisions=int(g.n_decisions.sum()),
                   retry_rate=g.n_retry_decisions.sum() / g.n_decisions.sum() if g.n_decisions.sum() else np.nan,
                   fallback_rate=g.n_fallback.sum() / g.n_decisions.sum() if g.n_decisions.sum() else np.nan)
        if "forfeit" in g and game != "werewolf":
            rec["forfeit_rate"] = g.forfeit.astype(float).mean()
        if game == "coin-game":
            rec.update(abs_score_name="team_total/64", abs_score=gg.team_score.mean() / 64, team_score_mean=gg.team_score.mean())
        elif game == "word-art":
            rec.update(abs_score_name="team_points/20", abs_score=gg.team_score.sum() / (2 * gg.rounds.sum()),
                       art_dq_rate=gg.art_dq.sum() / gg.rounds.sum(),
                       solve_rate_clean_art=gg.solved_clean.sum() / max(1, gg.rounds_clean.sum()))
        elif game == "word-association":
            rec.update(abs_score_name="own_word_share_of_guesses", abs_score=gg.own_hits.sum() / max(1, gg.guesses.sum()),
                       trap_rate=gg.trap.mean(), invalid_clue_rate=gg.invalid_clues.sum() / max(1, gg.clue_turns.sum()))
        elif game == "bargaining":
            rec.update(abs_score_name="own_payoff/10", abs_score=g.reward.mean() / 10, deal_rate=g.deal.mean(),
                       pareto_rate=g.pareto.mean(), welfare_eff=(g.welfare / g.welfare_max).mean())
        elif game == "poker-heads-up":
            rec.update(abs_score_name="bb_per_100 (zero-sum)", abs_score=g.bb_per_100.mean())
        elif game == "werewolf":
            if role == "werewolf":
                rec.update(abs_score_name="survival", abs_score=g.survived.mean(),
                           votes_received_share=g.votes_received.sum() / max(1, g.village_votes.sum()))
            else:
                hits, chance, nv = g.vote_hits.sum(), g.vote_chance.sum(), g.n_votes.sum()
                rec.update(abs_score_name="day_vote_on_wolf", abs_score=hits / nv if nv else np.nan,
                           vote_chance=chance / nv if nv else np.nan, n_votes=int(nv))
            rec["agent_error_rate"] = g.n_errors.sum() / max(1, g.n_decisions.sum())
        if (game, model) in lbs.index:
            row = lbs.loc[(game, model)]
            rec.update(lb_metric=row.lb_metric, lb_score=row.lb_score, lb_ci_plus=row.lb_ci_plus,
                       lb_ci_minus=row.lb_ci_minus)
            if game in ELO_BOARDS and (game, ANCHOR) in lbs.index:
                rec["p_beat_anchor"] = 1 / (1 + 10 ** (-(row.lb_score - lbs.loc[(game, ANCHOR)].lb_score) / 400))
        # strength of schedule: mean leaderboard score of sampled opponents
        opp = [o for s in gg.opponents for o in s.split("|") if o]
        sc = [lbs.loc[(game, o)].lb_score for o in opp if (game, o) in lbs.index]
        rec["opp_lb_score_mean"] = float(np.mean(sc)) if sc else np.nan
        out.append(rec)
    return pd.DataFrame(out)


def main():
    names = model_names()
    def norm(s):
        # exact slug/name, else drop a "-<n>" suffix (seen on opponents in some 1.30.1 chess games)
        k = str(s).strip()
        return names.get(k.lower()) or names.get(re.sub(r"-\d+$", "", k).lower()) or k
    vdates = version_dates()
    lb = leaderboard_table()
    lb.to_csv(HERE / "leaderboards.csv", index=False)

    plans, total = {}, 0
    for game, cfg in GAMES.items():
        z = RemoteZip(cfg["ds"])
        s = sample(z.listing(), N.get(game, N_DEFAULT), SEED)
        plans[game] = (z, s)
        total += s.compress_size.sum()
    print(f"planned compressed bytes: {total / 1e9:.2f} GB", flush=True)
    assert total < BUDGET_BYTES, "over download budget"

    seats, counts, status_texts = [], [], {}
    for game, (z, s) in plans.items():
        st = Counter()
        n_ok = 0
        versions = Counter()
        for i, row in enumerate(s.itertuples()):
            ep = z.episode(row)
            if not ep:
                continue
            try:
                rows = seat_rows(game, ep)
            except Exception as e:  # keep going; count parse failures
                print(f"  {game} {row.episode_id}: parse error {e!r}", flush=True)
                continue
            n_ok += 1
            versions[ep.get("module_version")] += 1
            st.update(d["status"][:80] for d in decisions(ep))
            seats += rows
            if (i + 1) % 100 == 0:
                print(f"  {game}: {i + 1}/{len(s)}", flush=True)
        vs = sorted(versions, key=lambda v: tuple(int(x) for x in re.findall(r"\d+", str(v))))
        counts.append(dict(game=game, dataset=GAMES[game]["ds"], n_in_dataset=int((z.listing().file_size > 0).sum()),
                           n_sampled=len(s), n_parsed=n_ok, bytes_compressed=int(s.compress_size.sum()),
                           module_version_min=vs[0] if vs else None, module_version_max=vs[-1] if vs else None,
                           harness_date_min=vdates.get(vs[0]) if vs else None,
                           harness_date_max=vdates.get(vs[-1]) if vs else None,
                           module_versions=json.dumps(dict(versions))))
        status_texts[game] = dict(st.most_common(40))
        print(f"{game:22s} parsed {n_ok}/{len(s)} versions {vs[:1]}..{vs[-1:]}", flush=True)

    df = pd.DataFrame(seats)
    for c in ("deal", "pareto", "forfeit", "survived", "error", "trap"):
        if c in df:
            df[c] = df[c].astype(float)
    df["team"] = df.team.astype(str)
    df["model"] = df.model_raw.map(norm)
    df["opponents"] = df.opponents_raw.map(lambda s: "|".join(sorted({norm(x) for x in s.split("|") if x})))
    df["instance_role"] = df.role
    # word games: the team (one model) plays both roles; the team outcome is attached to both instances
    multi = df.game.isin(["word-art", "word-association"])
    df = pd.concat([df[~multi]] + [df[multi].assign(instance_role=r) for r in ("artist", "guesser", "cluemaster")])
    df = df[~((df.game == "word-art") & (df.instance_role == "cluemaster"))
            & ~((df.game == "word-association") & (df.instance_role == "artist"))]
    DERIVED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DERIVED / "seats.parquet", index=False)
    (DERIVED / "status_texts.json").write_text(json.dumps(status_texts, indent=1))

    sc = pd.DataFrame(counts)
    seen = df.groupby("game").model.nunique().rename("n_models_in_sample")
    unmapped = df[~df.model.str.lower().isin(names)].groupby("game").model_raw.unique()
    sc = sc.merge(seen, on="game", how="left")
    sc["unmapped_model_names"] = sc.game.map(lambda g: "|".join(map(str, unmapped.get(g, []))))
    sc.to_csv(HERE / "sample_counts.csv", index=False)

    out = aggregate(df, lb)
    out.to_csv(HERE / "outcomes.csv", index=False, float_format="%.4g")

    # cross-check: sample win rate vs leaderboard score (Spearman over models with >= 10 results)
    cc = []
    for (game, role), g in out.groupby(["game", "role"]):
        h = g[(g.win + g.draw + g.loss) >= 10].dropna(subset=["lb_score"])
        cc.append(dict(game=game, role=role, n_models=len(h), spearman_winrate_vs_lb=h.win_rate.corr(h.lb_score, method="spearman")
                       if len(h) > 2 else np.nan))
    pd.DataFrame(cc).to_csv(HERE / "crosscheck.csv", index=False, float_format="%.3f")
    print(pd.DataFrame(cc).to_string())
    print("robots.txt status per host:", robots_status())


if __name__ == "__main__":
    main()
