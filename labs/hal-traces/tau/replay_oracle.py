"""DB-replay oracle for TAU-bench airline traces.

Replays the tool calls recorded in a HAL trace through tau-bench's deterministic
airline environment (pip install git+https://github.com/sierra-research/tau-bench)
and scores the database state at any checkpoint against the task's gold state.

V(k) in [0,1]: fraction of required entity changes correctly in place, penalised
by spurious writes (entities changed away from gold that gold left untouched).
V=1 for zero-write tasks iff the agent wrote nothing wrong.

Validation on the two runs used in the pilot: final-state match agrees with
HAL's reported success on 97/100 tasks; the 3 mismatches are runs where the DB
was correct but tau-bench's required-communication (outputs) check failed.

Inputs:  toolcalls_<tag>.json  ({task_id: {turns: [[{name, kwargs}...]...], success}})
Output:  oracle_tau_V.csv      (custom_id, V) for the pilot's 36 checkpoints.
"""
import json, math
import pandas as pd
from tau_bench.envs.airline.env import MockAirlineDomainEnv
from tau_bench.types import Action

TASKS = ('36', '37', '30', '28', '46', '45')
CPS = ((0.25, 'cp25'), (0.5, 'cp50'), (0.75, 'cp75'))


def entities(data):
    out = {}
    for rid, r in data['reservations'].items(): out[('res', rid)] = json.dumps(r, sort_keys=True)
    for uid, u in data['users'].items(): out[('user', uid)] = json.dumps(u, sort_keys=True)
    for fn, f in data['flights'].items(): out[('flt', fn)] = json.dumps(f, sort_keys=True)
    return out


def state_after(env, turns, upto):
    env.data = env.data_load_func()
    for calls in turns[:upto]:
        for c in calls:
            if not c['name'] or c['kwargs'] is None or c['name'] in env.terminate_tools:
                continue
            try:
                env.step(Action(name=c['name'], kwargs=c['kwargs']))
            except Exception:
                pass
    return entities(env.data)


def gold_state(env):
    env.data = env.data_load_func()
    for a in env.task.actions:
        if a.name not in env.terminate_tools:
            env.step(a)
    return entities(env.data)


def V(cur, gold, init):
    keys = set(cur) | set(gold) | set(init)
    need = {e for e in keys if gold.get(e) != init.get(e)}
    spurious = {e for e in keys if cur.get(e) != gold.get(e) and gold.get(e) == init.get(e)}
    done = {e for e in need if cur.get(e) == gold.get(e)}
    denom = len(need) + len(spurious)
    return 1.0 if denom == 0 else len(done) / denom


if __name__ == '__main__':
    rows = []
    for tag in ('opus41tc', 'gemflash'):
        tc = json.load(open(f'toolcalls_{tag}.json'))
        for tid in TASKS:
            env = MockAirlineDomainEnv(user_strategy='human', task_index=int(tid))
            init = entities(env.data_load_func())
            gold = gold_state(env)
            turns = tc[tid]['turns']
            n = len(turns)
            for frac, cp in CPS:
                k = max(2, math.ceil(frac * n))
                rows.append({'custom_id': f'{tag}:task{tid}#{cp}',
                             'V': V(state_after(env, turns, k), gold, init)})
    pd.DataFrame(rows).to_csv('oracle_tau_V.csv', index=False)
    print(len(rows), 'checkpoint V values written')
