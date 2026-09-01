# PLp (Planning) — adjudication packet

A/B/C are the same three models throughout (mapping hidden). For each case read the RULES + state + objective facts, then mark which annotation reasons most accurately for PLANNING demand to finish from here.

PLp difficulty drivers (from its rubric): temporal horizon, number of subtasks, sequencing, anticipating challenges. (No other agents / open-endedness here.)

## Case 1
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 2 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item1↔item3, item1↔item4.
STATE: Left = farmer, item1, item2, item3; Right = item4; boat on the left.
OBJECTIVE: optimal crossings to finish (planning horizon) = **3**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer,item1,item2; take farmer,item1; take farmer,item1,item3
PLp annotations:
- **A**: level 3 — "Capacity 2 on left with farmer+item1,item2,item3; cannot leave hub item1 conflicts; multi-trip ferrying, ordering, traps; ~4-5 crossings"
- **B**: level 1 — 2 crossings; hub item last; non-hub items safely batched first
- **C**: level 2 — 3 constraints; 4 ite
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 2
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 2 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item1↔item3, item1↔item4, item1↔item5, item1↔item6.
STATE: Left = farmer, item1, item2, item3, item4; Right = item5, item6; boat on the left.
OBJECTIVE: optimal crossings to finish (planning horizon) = **5**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer,item1,item2; take farmer,item1; take farmer,item1,item3; take farmer,item1; take farmer,item1,item4
PLp annotations:
- **A**: level 4 — "Capacity 2 on left with farmer+item1,item2,item3,item4; hub item1 conflicts with all; many constrained trips, ordering, traps"
- **B**: level 2 — 5 crossings; 4 items left; hub must travel last; multi-trip non-hub shuttling
- **C**: level 2 — star: 6 items; boat
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 3
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 2 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item1↔item4, item2↔item3, item3↔item4.
STATE: Left = item1, item3; Right = farmer, item2, item4; boat on the right.
OBJECTIVE: optimal crossings to finish (planning horizon) = **2**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer; take farmer,item1,item3
PLp annotations:
- **A**: level 3 — "Capacity 2, item1,item3 left (mutually safe in cycle); ferry both, watch arrival conflicts; ~3 crossings, ordering"
- **B**: level 1 — 2 crossings; non-adjacent items retrievable as safe pair; clean two-step
- **C**: level 2 — 4 constraints; 4 ite
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 4
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 3 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item1↔item6, item2↔item3, item3↔item4, item4↔item5, item5↔item6.
STATE: Left = item1, item3, item5; Right = farmer, item2, item4, item6; boat on the right.
OBJECTIVE: optimal crossings to finish (planning horizon) = **2**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer; take farmer,item1,item3,item5
PLp annotations:
- **A**: level 3 — "Capacity 3, three items item1,item3,item5 left in 6-cycle; load all safely, cross; ~2 crossings, constraint-checking"
- **B**: level 1 — 2 crossings; alternating-parity split means no conflicts in either half
- **C**: level 2 — 6 constraints; 6 ite
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 5
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 1 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item2↔item3.
STATE: Left = item1; Right = farmer, item2, item3; boat on the right.
OBJECTIVE: optimal crossings to finish (planning horizon) = **4**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer,item2; take farmer,item1; take farmer; take farmer,item2
PLp annotations:
- **A**: level 2 — "Boat capacity 1; one item left but farmer/boat on right, needs ferry-back then return; short horizon ~3-4 crossings, sequencing required"
- **B**: level 2 — ~4 crossings; 1 remaining item; capacity-1 forces anticipating 2-3 conflict trap
- **C**: level 1 — "~1 crossing, 2 const"
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___

## Case 6
RULES: A farmer must be in the boat every crossing; boat carries the farmer + at most 2 item(s). Forbidden together on a bank WITHOUT the farmer: item1↔item2, item2↔item3, item3↔item4.
STATE: Left = item1, item3; Right = farmer, item2, item4; boat on the right.
OBJECTIVE: optimal crossings to finish (planning horizon) = **2**; a backward/undo move is needed (re-planning) = **YES**.
OPTIMAL CONTINUATION: take farmer; take farmer,item1,item3
PLp annotations:
- **A**: level 2 — "Capacity 2, two items (item1,item3) left non-adjacent; farmer ferries both over, possibly one trip; ~2-3 crossings, ordering"
- **B**: level 1 — 2 crossings; 2 items to fetch; non-conflicting pair retrievable together
- **C**: level 2 — 3 constraints; 4 ite
VERDICT: most accurate = ___ ; your level = ___ ; torn? ___
