# Adjudication packet (with full rules) — judge which reasoning is right

A/B/C are the same three models across all cases; mapping hidden until you finish. For each case, read the RULES + current state + objective facts, then mark which annotation reasons most accurately.

Reminder: you are scoring the demand to COMPLETE the puzzle (get everything to the right bank) FROM the current state.

## Case 1 — dimension QLl
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 1 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item2↔item3.
CURRENT STATE: Left bank = item1; Right bank = farmer, item2, item3; boat on the right.
OBJECTIVE: optimal crossings to finish = **4**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item2; take farmer,item1; take farmer; take farmer,item2
Model annotations (for QLl):
- **A**: level 3 — "Capacity 1 forces strict ordering; 2 chained constraints must be combined across multi-step sequence to avoid forbidden pairs"
- **B**: level 4 — 2 chaining conflict pairs; capacity-1 forces multi-step; negation constraints interact
- **C**: level 1 — Item alone on left is safe; farmer returns with item.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 2 — dimension QLl
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 2 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item1↔item3, item1↔item4, item1↔item5.
CURRENT STATE: Left bank = item2, item3; Right bank = farmer, item1, item4, item5; boat on the right.
OBJECTIVE: optimal crossings to finish = **4**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item1; take farmer,item1,item2; take farmer,item1; take farmer,item1,item3
Model annotations (for QLl):
- **A**: level 3 — "Capacity 2, two items left, item1 conflicts with four; combine binding pairs over sequence"
- **B**: level 5 — 4 star hub conflicts all; capacity-1; hub on right creates conflicts on every departure
- **C**: level 2 — Four constraints (star); item1 hub; multi-step with limited boat capacity.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 3 — dimension QLl
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 2 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item1↔item3, item1↔item4, item1↔item5, item1↔item6.
CURRENT STATE: Left bank = farmer, item1, item2, item3, item4; Right bank = item5, item6; boat on the left.
OBJECTIVE: optimal crossings to finish = **5**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item1,item2; take farmer,item1; take farmer,item1,item3; take farmer,item1; take farmer,item1,item4
Model annotations (for QLl):
- **A**: level 4 — "Capacity 2, three items start bank, hub item1 conflicts with five; many binding constraints chained"
- **B**: level 5 — 5 star hub conflicts all; capacity-1; complex multi-trip with hub always creating conflict
- **C**: level 2 — Five constraints (star); item1 hub; multi-step ferry with limited capacity.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 4 — dimension MCt
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 3 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item1↔item3.
CURRENT STATE: Left bank = farmer, item1; Right bank = item2, item3; boat on the left.
OBJECTIVE: optimal crossings to finish = **1**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item1
Model annotations (for MCt):
- **A**: level 3 — "Plan from start with hub conflicts, capacity 3; moderate inference tracking shared constraint"
- **B**: level 2 — Take central item directly; no complex inference needed
- **C**: level 1 — Central item safe if moved alone; trivial once recognized.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 5 — dimension MCt
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 4 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item1↔item3.
CURRENT STATE: Left bank = farmer, item1; Right bank = item2, item3; boat on the left.
OBJECTIVE: optimal crossings to finish = **1**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item1
Model annotations (for MCt):
- **A**: level 3 — "Capacity 4; hub conflicts still require planning and constraint-monitoring, moderate critical thinking"
- **B**: level 2 — Trivially solved in one crossing; constraint satisfied automatically with farmer present
- **C**: level 1 — Central item safe if moved alone; large capacity makes solution obvious.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 6 — dimension MCt
RULES: A farmer must be in the boat every crossing; the boat carries the farmer + at most 4 item(s). Forbidden to leave together on a bank WITHOUT the farmer: item1↔item2, item1↔item3, item1↔item4.
CURRENT STATE: Left bank = farmer, item1; Right bank = item2, item3, item4; boat on the left.
OBJECTIVE: optimal crossings to finish = **1**; a wrong-but-legal 'backward' move is possible here = **YES (needs lookahead)**.
OPTIMAL CONTINUATION: take farmer,item1
Model annotations (for MCt):
- **A**: level 3 — "Capacity 4 from start; hub-conflict structure planned with moderate constraint-tracking"
- **B**: level 2 — One trip suffices; farmer's presence prevents constraint violation during crossing
- **C**: level 1 — All items fit in boat at once; no inference required.
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___
