"""Kaggle Game Arena: what the model sees, one instance per game x role.

Sources (all public, no login, no API key, no terms accepted):
  Kaggle datasets kaggle/<game>-gameplay (CC BY 4.0), one JSON per episode, read with HTTP
      range requests on the zip that https://www.kaggle.com/api/v1/datasets/download/... points to
      (a signed storage.googleapis.com URL). Only the zip directory and the chosen episodes are read.
  github.com/Kaggle/kaggle-environments   (Apache-2.0) KENV_COMMIT: the live harness
  github.com/google-deepmind/game_arena   (Apache-2.0) GA_COMMIT: the original chess/poker harness

robots.txt: www.kaggle.com, api.kaggle.com and storage.googleapis.com all answer 404 for
/robots.txt (checked 2026-10-03; the Wayback Machine has only 404 snapshots of www.kaggle.com's
since 2024). Under RFC 9309 a 4xx robots.txt means no restriction. ``get`` re-checks robots.txt
before every uncached request and refuses a disallowed URL, so a new robots.txt is honoured.

The prompt of an instance is a prompt the harness actually sent: it is read from the episode
log (``call_details[].prompt`` in current logs, ``generate_returns[].request_for_logging``
in older ones, ``kwargs.raw_prompt`` for Werewolf). Each logged prompt already holds the
harness instructions, the rules and the current observation. Rule: take the most recent
episode (highest EpisodeId) whose log has prompts, and the role's SECOND decision in it
(first attempt), so the board or history is not empty. The template is located in the
pinned harness source, and a probe string checks that source and logged prompt agree.

Writes:
  data/instances/instances_gamearena.parquet  benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_gamearena.csv           one row per instance (game facts, provenance)
  data/downloads/gamearena/listings/<dataset>.csv   zip directory per dataset
  data/downloads/gamearena/episodes/<dataset>/<id>.json.gz   cached episodes
  data/downloads/gamearena/repos/              pinned harness clones

Run: python experiments/benchmarks/gamearena-data/fetch_tasks.py
"""

import gzip
import hashlib
import io
import json
import re
import struct
import subprocess
import time
import urllib.parse
import urllib.robotparser
import zipfile
import zlib
from pathlib import Path

import pandas as pd
import requests

BENCHMARK = "gamearena"
ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "downloads" / "gamearena"
OUT = ROOT / "data" / "instances"
UA = "adele-data/0.1"
KAGGLE = "https://www.kaggle.com"
API = "https://api.kaggle.com"
KENV_URL, KENV_COMMIT = "https://github.com/Kaggle/kaggle-environments.git", "eb8b5ef905cb066babf8bfcd776540d0e9dd8fa6"
GA_URL, GA_COMMIT = "https://github.com/google-deepmind/game_arena.git", "6ddcc7dac06321472f2f22fabdeceab97eebeb73"
OS_GAMES = "kaggle_environments/envs/open_spiel_env/games/"

# key: dataset slug, leaderboard slug, players, roles, structure, hidden info, free text,
# harness source (repo, path) and a probe string that must occur in source and prompt.
GAMES = {
    "chess-text": dict(ds="chess-text-gameplay", lb="chess-text", players=2, roles=["player"],
                       kind="2p zero-sum", hidden="no", text="no",
                       src=("kenv", "kaggle_environments/core_harness.py"),
                       probe="Play your strongest move. The move MUST be legal."),
    "chess-text-openings": dict(ds="chess-text-openings-gameplay", lb="chess-text-openings", players=2,
                                roles=["player"], kind="2p zero-sum", hidden="no", text="no",
                                src=("ga", "game_arena/harness/prompt_templates.py"),
                                probe="Play your strongest move. The move MUST be legal."),
    "checkers": dict(ds="checkers-gameplay", lb="checkers", players=2, roles=["player"], kind="2p zero-sum",
                     hidden="no", text="no", src=("kenv", OS_GAMES + "checkers/harness.py"),
                     probe="Let's play Checkers (American draughts)."),
    "clobber": dict(ds="clobber-gameplay", lb="clobber", players=2, roles=["player"], kind="2p zero-sum",
                    hidden="no", text="no", src=("kenv", OS_GAMES + "clobber/harness.py"),
                    probe="Let's play Clobber."),
    "dark-hex": dict(ds="dark-hex-gameplay", lb="dark-hex", players=2, roles=["player"], kind="2p zero-sum",
                     hidden="yes (opponent stones)", text="no", src=("kenv", OS_GAMES + "dark_hex/harness.py"),
                     probe="Let's play Dark Hex (imperfect-information Hex)."),
    "five-in-a-row": dict(ds="five-in-a-row-gameplay", lb="five-in-a-row", players=2, roles=["player"],
                          kind="2p zero-sum", hidden="no", text="no",
                          src=("kenv", OS_GAMES + "connect_four/harness.py"), probe="You are a world-class Connect X AI."),
    "four-in-a-row": dict(ds="four-in-a-row-gameplay", lb="four-in-a-row", players=2, roles=["player"],
                          kind="2p zero-sum", hidden="no", text="no",
                          src=("kenv", OS_GAMES + "connect_four/harness.py"), probe="You are a world-class Connect X AI."),
    "dots-and-boxes": dict(ds="game-arena-dots-and-boxes-gameplay", lb="dots-and-boxes", players=2,
                           roles=["player"], kind="2p zero-sum", hidden="no", text="no",
                           src=("kenv", OS_GAMES + "dots_and_boxes/harness.py"), probe="Let's play Dots and Boxes."),
    "go": dict(ds="go-gameplay", lb="go", players=2, roles=["player"], kind="2p zero-sum", hidden="no", text="no",
               src=("kenv", OS_GAMES + "go/harness.py"), probe="Let's play Go."),
    "lines-of-action": dict(ds="lines-of-action-gameplay", lb="lines-of-action", players=2, roles=["player"],
                            kind="2p zero-sum", hidden="no", text="no",
                            src=("kenv", OS_GAMES + "lines_of_action/harness.py"), probe="Let's play Lines of Action."),
    "nine-mens-morris": dict(ds="nine-mens-morris-gameplay", lb="nine-mens-morris", players=2, roles=["player"],
                             kind="2p zero-sum", hidden="no", text="no",
                             src=("kenv", OS_GAMES + "nine_mens_morris/harness.py"),
                             probe="Let's play Nine Men's Morris"),
    "reversi": dict(ds="reversi-gameplay", lb="reversi", players=2, roles=["player"], kind="2p zero-sum",
                    hidden="no", text="no", src=("kenv", OS_GAMES + "othello/harness.py"), probe="Let's play Reversi."),
    "ultimate-tic-tac-toe": dict(ds="ultimate-tic-tac-toe-gameplay", lb="ultimate-tic-tac-toe", players=2,
                                 roles=["player"], kind="2p zero-sum", hidden="no", text="no",
                                 src=("kenv", OS_GAMES + "ultimate_tic_tac_toe/harness.py"),
                                 probe="Ultimate Tic-Tac-Toe."),
    "poker-heads-up": dict(ds="poker-heads-up-gameplay", lb="poker-heads-up", players=2, roles=["player"],
                           kind="2p zero-sum, chance, 100 hands", hidden="yes (hole cards)", text="no",
                           src=("kenv", OS_GAMES + "repeated_poker/harness.py"),
                           probe="Primary Objective: Maximize Expected Value (EV)."),
    "bargaining": dict(ds="bargaining-gameplay", lb="bargaining", players=2, roles=["player"],
                       kind="2p general-sum negotiation (win = higher own payoff)", hidden="yes (valuations)",
                       text="no (structured offers)", src=("kenv", OS_GAMES + "bargaining/harness.py"),
                       probe="Let's play Bargaining"),
    "coin-game": dict(ds="coin-game-gameplay", lb="coin-game", players=4, roles=["player"],
                      kind="2v2; each team = 2 copies of one model on its own private board",
                      hidden="yes (other board)", text="no",
                      src=("kenv", OS_GAMES + "coin_game_arena/harness.py"),
                      probe="Let's play Coin Game Arena (2v2 team coin game)."),
    "word-art": dict(ds="word-art-gameplay", lb="word-art", players=4, roles=["artist", "guesser"],
                     kind="2v2; each team = 2 copies of one model; parallel rounds, team scores independent",
                     hidden="yes (secret word)", text="yes (ASCII art, guesses)",
                     src=("kenv", "kaggle_environments/envs/word_art/harness.py"), probe="in Word Art (a 2v2 game)."),
    "word-association": dict(ds="word-association-gameplay", lb="word-association", players=4,
                             roles=["cluemaster", "guesser"],
                             kind="2v2; each team = 2 copies of one model; shared board (Codenames-like)",
                             hidden="yes (word colours, guesser only)", text="yes (clues)",
                             src=("kenv", "kaggle_environments/envs/word_association/harness.py"),
                             probe="in Word Association."),
    "werewolf": dict(ds="werewolf-gameplay", lb="werewolf", players=8,
                     roles=["werewolf", "seer", "doctor", "villager"],
                     kind="8 players, 2 teams (2 wolves vs 6 village), mixed models per game",
                     hidden="yes (roles)", text="yes (day discussion)",
                     src=("kenv", "kaggle_environments/envs/werewolf/werewolf.py"),
                     probe="You are a master strategist playing the game of Werewolf."),
}
ROLE_PREFIX = {("word-art", "artist"): "You are the ARTIST", ("word-art", "guesser"): "You are the GUESSER",
               ("word-association", "cluemaster"): "Cluemaster in Word Association",
               ("word-association", "guesser"): "Guesser in Word Association"}

# ------------------------------------------------------------------ polite HTTP

_robots: dict = {}
_last: dict = {}


def allowed(url: str) -> bool:
    """robots.txt check for url's host (cached per host)."""
    p = urllib.parse.urlsplit(url)
    host = f"{p.scheme}://{p.netloc}"
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser(host + "/robots.txt")
        r = requests.get(host + "/robots.txt", headers={"User-Agent": UA}, timeout=60)
        if r.status_code in (401, 403):
            rp.disallow_all = True
        elif r.status_code >= 400:
            rp.allow_all = True  # RFC 9309: unavailable robots.txt = no restriction
        else:
            rp.parse(r.text.splitlines())
        _robots[host] = (rp, r.status_code)
    return _robots[host][0].can_fetch(UA, url)


def robots_status() -> dict:
    return {h: s for h, (_, s) in _robots.items()}


def get(url: str, *, method="GET", pause=1.0, **kw) -> requests.Response:
    """One request after the robots.txt check; at most one request per `pause` s per host."""
    assert allowed(url), f"robots.txt disallows {url}"
    host = urllib.parse.urlsplit(url).netloc
    wait = _last.get(host, 0) + pause - time.time()
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.time()
    headers = {"User-Agent": UA, **kw.pop("headers", {})}
    r = requests.request(method, url, headers=headers, timeout=180, **kw)
    r.raise_for_status()
    return r


# ------------------------------------------------------------------ dataset zips

def dataset_meta() -> pd.DataFrame:
    """Public dataset list (anonymous /api/v1/datasets/list), cached."""
    f = CACHE / "api" / "datasets_kaggle.json"
    if not f.exists():
        rows, seen = [], set()
        for q in ("gameplay", "werewolf", "poker"):
            for page in range(1, 4):
                r = get(f"{KAGGLE}/api/v1/datasets/list?search={q}&page={page}", pause=2).json()
                rows += [x for x in r if x["ref"].startswith("kaggle/") and x["ref"] not in seen]
                seen |= {x["ref"] for x in r}
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(rows))
    keep = ["ref", "title", "currentVersionNumber", "lastUpdated", "licenseName", "totalBytes"]
    return pd.DataFrame(json.loads(f.read_text()))[keep]


def leaderboard(slug: str) -> dict:
    """Public leaderboard kaggle/<slug> (anonymous benchmarks API, as `kaggle b leaderboard` calls it), cached."""
    f = CACHE / "leaderboards" / f"{slug}.json"
    if not f.exists():
        r = get(f"{API}/v1/benchmarks.BenchmarksApiService/GetBenchmarkLeaderboard", method="POST",
                json={"ownerSlug": "kaggle", "benchmarkSlug": slug}, pause=2)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(r.text)
    return json.loads(f.read_text())


class RemoteZip:
    """A dataset's archive.zip read by HTTP range requests (signed URL from the Kaggle API)."""

    def __init__(self, dataset: str):
        self.dataset = dataset
        self._url = None

    @property
    def url(self) -> str:
        if self._url is None:  # signed URLs live 3 days; ask once per run
            r = get(f"{KAGGLE}/api/v1/datasets/download/kaggle/{self.dataset}", allow_redirects=False, pause=2)
            self._url = r.headers["location"]
        return self._url

    def _range(self, a: int, b: int) -> bytes:
        return get(self.url, headers={"Range": f"bytes={a}-{b}"}, pause=0.05).content

    def listing(self) -> pd.DataFrame:
        f = CACHE / "listings" / f"{self.dataset}.csv"
        if f.exists():
            return pd.read_csv(f)
        size = int(get(self.url, headers={"Range": "bytes=0-0"}).headers["Content-Range"].split("/")[1])
        tail = 1 << 20
        while True:  # read the end of the zip until the whole central directory is in hand
            blob = self._range(max(0, size - tail), size - 1)
            try:
                z = zipfile.ZipFile(_Tail(blob, size))
                break
            except zipfile.BadZipFile:
                assert tail < size, "central directory not found"
                tail *= 8
        df = pd.DataFrame([dict(name=i.filename, episode_id=int(i.filename.split(".")[0]), file_size=i.file_size,
                                compress_size=i.compress_size, header_offset=i.header_offset,
                                method=i.compress_type) for i in z.infolist()])
        f.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(f, index=False)
        return df

    def episode(self, row) -> dict | None:
        """Episode JSON (cached gzipped). None for an empty member."""
        f = CACHE / "episodes" / self.dataset / f"{row.episode_id}.json.gz"
        if not f.exists():
            a = int(row.header_offset)
            blob = self._range(a, a + 30 + 1024 + int(row.compress_size))  # 1 KB slack for name + extra
            assert blob[:4] == b"PK\x03\x04", "bad local header"
            n, e = struct.unpack("<HH", blob[26:30])
            data = blob[30 + n + e: 30 + n + e + int(row.compress_size)]
            raw = zlib.decompressobj(-15).decompress(data) if row.method == 8 else data
            assert len(raw) == int(row.file_size), "size mismatch"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(gzip.compress(raw))
        raw = gzip.decompress(f.read_bytes())
        return json.loads(raw) if raw else None


class _Tail(io.RawIOBase):
    """Seekable view of the last bytes of a remote file (enough for zipfile's directory scan)."""

    def __init__(self, blob: bytes, size: int):
        self.blob, self.size, self.start, self.pos = blob, size, size - len(blob), 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def readinto(self, b):
        if self.pos < self.start:
            raise zipfile.BadZipFile("need more tail")
        chunk = self.blob[self.pos - self.start: self.pos - self.start + len(b)]
        b[:len(chunk)] = chunk
        self.pos += len(chunk)
        return len(chunk)


# ------------------------------------------------------------------ episode parsing

def _gr_prompt(s: str) -> str:
    """Prompt text inside an old-format generate_returns entry."""
    try:
        msgs = json.loads(s)["request_for_logging"]["messages"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return ""
    parts = []
    for m in msgs:
        c = m.get("content")
        texts = [c] if isinstance(c, str) else [x.get("text", "") for x in c or [] if isinstance(x, dict)]
        parts.append(("" if m.get("role") == "user" else f"[{m.get('role')}]\n") + "\n".join(texts))
    return "\n\n".join(parts)


def decisions(ep: dict) -> list[dict]:
    """Every model decision in an episode: seat, step, attempt prompts, action, self-reported status."""
    out = []
    for i, st in enumerate(ep.get("steps") or []):
        for seat, a in enumerate(st):
            act = a.get("action")
            if not isinstance(act, dict):
                continue
            if "call_details" in act:
                prompts = [c.get("prompt") or "" for c in act["call_details"]]
            elif "generate_returns" in act:
                prompts = [_gr_prompt(g) for g in act["generate_returns"]]
            elif "action_type" in act:  # werewolf
                kw = act.get("kwargs") or {}
                prompts = [kw.get("raw_prompt") or ""]
            else:
                continue
            if not prompts:  # setup steps (model not called)
                continue
            out.append(dict(seat=seat, step=i, prompts=prompts, n_calls=len(prompts), action=act,
                            status=str(act.get("status", "")), observation=a.get("observation") or {}))
    return out


def werewolf_players(ep: dict) -> list[dict]:
    """Seat-ordered players (id, model, role) from GAME_END; seat order = TeamNames = rewards order."""
    return [dict(id=p["id"], model=p["agent"]["display_name"], role=p["agent"]["role"].lower())
            for p in ep["info"]["GAME_END"]["all_players"]]


def decision_role(game: str, ep: dict, d: dict) -> str | None:
    if game == "werewolf":
        actor = (d["action"].get("kwargs") or {}).get("actor_id")
        return {p["id"]: p["role"] for p in werewolf_players(ep)}.get(actor)
    if game in ("word-art", "word-association"):
        p = d["prompts"][0] if d["prompts"] else ""
        for (g, role), pre in ROLE_PREFIX.items():
            if g == game and pre in p[:200]:
                return role
        return None
    return "player"


# ------------------------------------------------------------------ harness repos

def repo(name: str) -> Path:
    url, commit = {"kenv": (KENV_URL, KENV_COMMIT), "ga": (GA_URL, GA_COMMIT)}[name]
    d = CACHE / "repos" / {"kenv": "kaggle-environments", "ga": "game_arena"}[name]
    if not d.exists():
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", url, str(d)], check=True)
    if subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() != commit:
        subprocess.run(["git", "-C", str(d), "checkout", "-q", commit], check=True)
    return d


def source_text(src: tuple) -> str:
    name, path = src
    return subprocess.run(["git", "-C", str(repo(name)), "show", f"HEAD:{path}"], capture_output=True,
                          text=True, check=True).stdout


# ------------------------------------------------------------------ main

def representative(game: str, cfg: dict, z: RemoteZip, listing: pd.DataFrame, max_tries=25):
    """Most recent non-empty episode with a logged prompt for every role; role -> its 2nd decision."""
    for row in listing[listing.file_size > 0].sort_values("episode_id", ascending=False).head(max_tries).itertuples():
        ep = z.episode(row)
        if not ep:
            continue
        picks = {}
        for role in cfg["roles"]:
            ds = [d for d in decisions(ep) if d["prompts"] and d["prompts"][0] and decision_role(game, ep, d) == role
                  and (role != "player" or d["seat"] == 0)]
            if len(ds) >= 2:
                picks[role] = ds[1]
        if len(picks) == len(cfg["roles"]):
            return row, ep, picks
    raise RuntimeError(f"{game}: no recent episode with prompts for all roles")


def model_of(game: str, ep: dict, seat: int) -> str:
    if game == "werewolf":
        return werewolf_players(ep)[seat]["model"]
    return ep["info"]["TeamNames"][seat]


def main():
    dsm = dataset_meta().set_index("ref")
    rows, metas = [], []
    for game, cfg in GAMES.items():
        z = RemoteZip(cfg["ds"])
        lst = z.listing()
        row, ep, picks = representative(game, cfg, z, lst)
        src = source_text(cfg["src"])
        n_lb = len(leaderboard(cfg["lb"])["rows"])
        dm = dsm.loc[f"kaggle/{cfg['ds']}"]
        for role, d in picks.items():
            prompt = d["prompts"][0]
            probe = cfg["probe"]
            iid = f"{game}@{role}"
            rows.append(dict(benchmark=BENCHMARK, instance_id=iid, prompt=prompt,
                             prompt_sha12=hashlib.sha256(prompt.encode()).hexdigest()[:12]))
            metas.append(dict(
                instance_id=iid, game=game, role=role, players=cfg["players"], structure=cfg["kind"],
                hidden_info=cfg["hidden"], free_text=cfg["text"], dataset=f"kaggle/{cfg['ds']}",
                dataset_version=int(dm.currentVersionNumber), dataset_updated=str(dm.lastUpdated)[:10],
                dataset_licence=dm.licenseName, n_episodes_in_dataset=int((lst.file_size > 0).sum()),
                n_empty_members=int((lst.file_size == 0).sum()), episode_id_min=int(lst.episode_id.min()),
                episode_id_max=int(lst.episode_id.max()), leaderboard=f"kaggle/{cfg['lb']}", n_models_leaderboard=n_lb,
                source_episode=int(row.episode_id), source_module_version=ep.get("module_version"),
                source_seat=d["seat"], source_step=d["step"], source_model=model_of(game, ep, d["seat"]),
                harness_repo=cfg["src"][0], harness_file=cfg["src"][1],
                harness_commit=KENV_COMMIT if cfg["src"][0] == "kenv" else GA_COMMIT,
                probe=probe, probe_in_source=(probe in src) if probe else None,
                probe_in_prompt=(probe in prompt) if probe else None, prompt_chars=len(prompt),
                episode_config=json.dumps({k: v for k, v in ep.get("configuration", {}).items()
                                           if k not in ("agents",)}, sort_keys=True)[:2000]))
        print(f"{game:22s} episodes={metas[-1]['n_episodes_in_dataset']:6d} source={row.episode_id} "
              f"v{ep.get('module_version')} roles={list(picks)} chars={[len(d['prompts'][0]) for d in picks.values()]}",
              flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(OUT / "instances_gamearena.parquet", index=False)
    pd.DataFrame(metas).to_csv(OUT / "meta_gamearena.csv", index=False)
    print("robots.txt status per host:", robots_status())


if __name__ == "__main__":
    main()
