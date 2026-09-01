"""Controlled testbeds with exact ground truth, used to calibrate demand rubrics.

Unlike a benchmark, a testbed knows the right answer: `rivercross` ships an exact
BFS solver, so a rubric's demand labels can be scored against true remaining work
rather than only against other judges.
"""
