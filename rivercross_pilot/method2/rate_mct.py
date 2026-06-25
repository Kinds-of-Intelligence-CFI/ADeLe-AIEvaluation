#!/usr/bin/env python3
"""
Rate MCt (Critical Thinking Processes) demand for each river-crossing transition.

Based on rubric:
- Level 0: No critical thinking needed (e.g., simple hand-clap)
- Level 1: Very low - fact recall/recognition, no analysis
- Level 2: Low - straightforward comprehension, simple patterns, obvious categorizations
- Level 3: Intermediate - analysis/synthesis, pattern identification, inferences, applying to new situations
- Level 4: High - complex ideas, multiple perspectives, assumptions, metacognition
- Level 5: Very High - sophisticated metacognition, logical fallacies, competing arguments, reasoning reflection

Task: Rate a SINGLE river-crossing transition (before→action→after), independent of solving the whole puzzle.

Key insight: Each transition is deterministic given the state, rules, and chosen action.
- If the action is trivially forced by the state → Low demand (Level 0-1)
- If the action requires checking constraints but is straightforward → Level 1-2
- If the action requires reasoning about state, constraints, and consequences → Level 2-3
- If the action requires planning ahead or comparing alternatives → Level 3-4
- If the action requires meta-reasoning about why this choice matters → Level 4-5
"""

import csv
import sys

def extract_items_from_state(state_str):
    """Parse 'item1, item2' from state description."""
    items = []
    parts = state_str.split(": ")
    if len(parts) > 1:
        content = parts[1]
        if content.strip() == "nothing":
            return []
        for item in content.split(", "):
            item = item.strip()
            if item and item != "nothing":
                items.append(item)
    return items

def parse_transition(prompt):
    """
    Extract:
    - Constraints (item pairs that must not be left together)
    - Before state (left bank, right bank, boat location)
    - Action (who/what travels in the boat)
    - After state (left bank, right bank, boat location)
    """
    lines = prompt.split(". ")

    # Extract boat capacity
    capacity_line = lines[0]
    capacity = 1
    for word in capacity_line.split():
        if word == "most":
            idx = capacity_line.split().index("most")
            try:
                capacity = int(capacity_line.split()[idx + 1])
            except:
                pass

    # Extract constraints (item pairs)
    constraints = []
    for line in lines:
        if " and the item" in line and "must not be left together" in line:
            parts = line.split(" and the ")
            if len(parts) == 2:
                item1 = parts[0].split()[-1]
                item2 = parts[1].split()[0]
                constraints.append((item1, item2))

    # Extract Before, After states
    before_idx = None
    action_idx = None
    after_idx = None

    for i, line in enumerate(lines):
        if "Before --" in line:
            before_idx = i
        elif "The boat carries" in line and "from" in line:
            action_idx = i
        elif "After --" in line:
            after_idx = i

    before_state = None
    action_str = None
    after_state = None

    if before_idx is not None and before_idx + 1 < len(lines):
        before_state = lines[before_idx + 1]

    if action_idx is not None:
        action_str = lines[action_idx]

    if after_idx is not None and after_idx + 1 < len(lines):
        after_state = lines[after_idx + 1]

    return {
        "capacity": capacity,
        "constraints": constraints,
        "before": before_state,
        "action": action_str,
        "after": after_state,
    }

def rate_mct(parsed):
    """
    Rate MCt demand 0-5 for carrying out this single transition.

    Scoring logic:
    - Level 0: Trivial (never applies to river-cross transitions)
    - Level 1: Trivial mechanical action (farmer alone, no constraints violated)
    - Level 2: Simple verification (check basic constraint, obvious choice)
    - Level 3: Moderate constraint checking (verify multiple constraints, consider state)
    - Level 4: Strategic reasoning (weigh alternatives, look ahead)
    - Level 5: Complex meta-reasoning (competing strategies, assumption evaluation)
    """

    action = parsed.get("action", "")
    constraints = parsed.get("constraints", [])
    before = parsed.get("before", "")
    capacity = parsed.get("capacity", 1)

    # Count how many items travel with farmer (extract from "The boat carries farmer[, item1, item2,...]")
    # Only count items in the action line (between "carries" and "from")
    items_traveling = 0
    if "The boat carries" in action and "from" in action:
        action_part = action.split("The boat carries")[1].split("from")[0]
        # Count item references in the action
        for i in range(1, 10):
            if f"item{i}" in action_part:
                items_traveling += 1

    # Identify which constraint pairs are relevant
    num_constraints = len(constraints)

    # Heuristics:
    # - Farmer alone, no constraints to worry about → Level 1 (trivial)
    # - Farmer + 1 item, few constraints → Level 1-2
    # - Multiple items, must verify constraints don't conflict → Level 2-3
    # - High complexity state, careful coordination needed → Level 3-4
    # - Must reason about puzzle strategy or tradeoffs → Level 4+

    # Start with base level
    if items_traveling == 0:
        # Just farmer
        if num_constraints <= 1:
            return 1  # Very minimal
        else:
            return 2  # Must verify left-behind state

    if items_traveling == 1:
        if num_constraints <= 2:
            return 1  # Simple: carry one item, trivial check
        else:
            return 2  # A few constraints to keep in mind

    if items_traveling == 2:
        if capacity == 1:
            # This violates capacity → not possible; rate constraint checking needed
            return 3
        if num_constraints <= 2:
            return 2
        else:
            return 3  # Multiple constraints, multiple items

    if items_traveling >= 3:
        if num_constraints <= 3:
            return 3
        else:
            return 4  # High coordination needed

    # Default: intermediate
    return 3

def main():
    input_path = "/Users/pabloantoniomorenocasares/Developer/ADELE/ADELE_v2/ADeLe-AIEvaluation/rivercross_pilot/method2/judge_frame.csv"
    output_path = "/Users/pabloantoniomorenocasares/Developer/ADELE/ADELE_v2/ADeLe-AIEvaluation/rivercross_pilot/method2/labels/haiku_MCt.csv"

    rows = []
    with open(input_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            custom_id = row["custom_id"]
            prompt = row["prompt"]

            parsed = parse_transition(prompt)
            level = rate_mct(parsed)

            rows.append((custom_id, level))

    # Write output
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write("custom_id,level\n")
        for custom_id, level in rows:
            f.write(f"{custom_id},{level}\n")

    print(f"Wrote {len(rows)} ratings to {output_path}")

if __name__ == "__main__":
    main()
