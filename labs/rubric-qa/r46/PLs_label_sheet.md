# PLs (Simulating) — human anchor label sheet

Label against `src/adele/rubrics/data_v2/Paolo_Pablo/PLs.txt` (v2-r45).

## First, a problem with blindness you should know about

Part B's items have all been judged, and their measured values are written up in
`labs/rubric-qa/r45/RESULTS-r45.md`, which you have. So labelling Part B is **not blind** —
if you agree with the measured value, that agreement is weak evidence, because you may have
seen it. Only your *disagreements* there carry weight.

**Part A is fresh.** Ten items, never judged, no prediction of mine recorded anywhere. That
is where a real human anchor can still be established, and it is the part I would do first.
Do Part A before reading Part B, and before asking me what I expect.

## How to derive a label from the driver

The driver is: *how much interacting change must be tracked, at the precision the answer
requires.* Precision is a tolerance yardstick, not a second axis. Four questions, in order:

**Q1 — Is anything run forward at all?** If the situation is static, the outcome already
stated, the question is about the state as presented rather than how it unfolds, or the
situation is *named but not actually given* — score **0**.

**Q2 — Does one familiar process advance once, with the outcome following at once?** Any
rough projection landing on the same answer — score **1**.

**Q3 — Does anything interact in a way that bears on the answer?** If one process runs on
undisturbed, or several run on without affecting each other, score **2** — however long the
horizon, however intricate the inner churn, and however exact the arithmetic. A *chain*,
where each event causes the next but nothing feeds back, counts as non-interacting.

**Q4 — If processes do influence one another, how fine is the required answer?**
- Coarse: once the gross effect of the coupling is captured, loose tracking still lands on
  it — **3**.
- Fine enough that dropping any one coupling, or tracking it loosely, flips the result — **4**.
- The task demands saying which of two courses that begin close together and end far apart
  the situation actually takes, sustained the whole way — **5**.

**Guards.** Exact arithmetic over an undeflected course does not raise this. Specialised
knowledge of the governing regularities does not raise this. How hard the current state is
to perceive or find out does not raise this. Divergence in the situation does not by itself
place a task at 5 if a coarse answer would survive it. Choosing among one's *own* actions is
planning, not simulating. Inferring what someone believes or wants is mind-modelling; a
described tendency propagated forward is not.

---

# PART A — fresh items (do these first)

**F1.** A finished chess game's full move list is given. State which side won.
**Label:** ____  **Deciding phrase:** ______________________

**F2.** A cup of hot coffee is left on a desk in a cool room. State what happens to its
temperature.
**Label:** ____  **Deciding phrase:** ______________________

**F3.** A slow leak drips into a bucket at the stated rate; the bucket's capacity is given.
State whether it overflows before morning.
**Label:** ____  **Deciding phrase:** ______________________

**F4.** Given the stated principal, interest rate and fixed monthly payment, state the exact
month in which the loan is paid off.
**Label:** ____  **Deciding phrase:** ______________________

**F5.** A town's only bakery raises its prices. A second bakery opens across the square, and
each adjusts its opening hours in response to the queues at the other. State whether bread
is cheaper in the town a year later.
**Label:** ____  **Deciding phrase:** ______________________

**F6.** A described island holds goats and a single grass species. The goats eat the grass;
the grass regrows at the stated rate. State whether the goat population stabilises or
crashes.
**Label:** ____  **Deciding phrase:** ______________________

**F7.** Three described medications interact pairwise as stated, with dosing staggered as
described. State which of the four listed side effects appears first.
**Label:** ____  **Deciding phrase:** ______________________

**F8.** A described weir, two feeder streams and an abstraction schedule are given, each
affecting the others through the stated rules. State whether the downstream flow falls below
the stated ecological minimum in August.
**Label:** ____  **Deciding phrase:** ______________________

**F9.** From the described starting configuration of the slope, state which of the two
described valleys the avalanche reaches once the slab releases.
**Label:** ____  **Deciding phrase:** ______________________

**F10.** A described negotiation with a supplier. Work out the opening offer that gets you
the best price.
**Label:** ____  **Deciding phrase:** ______________________

---

# PART B — already-judged items (disagreements only)

Twelve carried from r40/r41 and six from r45's boundary round. Label only where you think
the text gets it wrong; a blank means "no objection", which is not the same as agreement.

**A3.** From described atmospheric conditions, which of two neighbouring valleys does the
storm strike three days out? **Label:** ____
**A4.** A ball thrown at 18 m/s at 35°; ignoring air resistance, compute exactly where it
lands. **Label:** ____
**A6.** From a described billiards break, which pocket does the ball nearest the cushion
reach? **Label:** ____
**A7.** From the same break, does any ball at all reach any pocket? **Label:** ____
**A8.** A predator–prey pair oscillates; does the rabbit population at the next trough fall
below the stated extinction threshold? **Label:** ____
**B1.** Work out a plan to get a frightened cat down from a tree. **Label:** ____
**B3.** Sally leaves her marble in the basket; Anne moves it. Where will Sally look?
**Label:** ____
**B5.** What happens when a lump of sodium is dropped into water? **Label:** ____
**B7.** Reconcile a year of a ledger across twelve statements, following the given
procedure. **Label:** ____
**B8.** Trace the described sorting algorithm on the given list; state the final order.
**Label:** ____
**P1-absent.** Predict how the population described in the attached demographic report
changes over the coming decade. (No report is attached.) **Label:** ____
**P1-present.** A town of 12,000: births 130/yr, deaths 95/yr, 200 leave annually, no inward
migration. Predict the population over the coming decade. **Label:** ____
**X1.** A road's outer lane closes; drivers reroute onto parallel streets, which congest and
send some back. Do overall travel times go up? **Label:** ____
**X2.** A line of dominoes, each close enough to topple the next; the first is pushed. Does
the last fall? **Label:** ____
**X3.** Two shops each reset price weekly by a rule responding to the other's price and to
their own queue. Are prices higher at month's end? **Label:** ____
**X4.** A bucket chain from well to fire, each person passing at the stated rate. Does water
reach the fire within ten minutes? **Label:** ____
**X5.** A hillside's rabbits feed the foxes and the foxes thin the rabbits. Is the rabbit
population larger or smaller a decade from now? **Label:** ____
**X6.** A relay of runners carries a message, each handing on at the stated pace. Does it
arrive before nightfall? **Label:** ____
