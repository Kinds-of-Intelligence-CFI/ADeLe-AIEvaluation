# PLe r38 — Pablo's pre-registered labels (fill in BEFORE any judge runs)

Rubric: Action control and execution (PLe). Score each TASK INSTANCE 0–5 for the
demand the task itself places on keeping execution on track. Label against the
**r38 candidate text** (PLe_r38_candidate.txt — L1 now carries the recoverability
condition). Tie-break lower when in doubt between adjacent levels.

## How to derive a label from the driver, in order

The driver of PLe is: *how much of the burden of keeping execution on track falls on
the agent rather than the environment* — set jointly by how sparse and how settling
the environment's feedback is, and by what recovery costs when an error surfaces.
Work through four questions, in this order:

**Q1 — What are the actions?** Individuate the finest units that could be separately
instructed, done wrong, and redone (a tool call, a message sent, an edit, a posted
entry). Words and tokens are not actions. A task completed by one atomic action is
Level 0 — even if finding out *what* to do was hard (that difficulty belongs to other
dimensions).

**Q2 — After which actions does the environment settle success?** "Settle" means:
something the environment returns establishes, *without further work*, whether the
action did what it was for — not an observation from which success must still be
worked out, and not an interlocutor's acknowledgement. The purpose referent is the
plan step's goal. This gives the feedback band: essentially every action → L1;
natural checkpoints every few actions → L2; stretches of tens of actions, or the
whole task, with nothing settling anything → L3.

**Q3 — What does recovery cost?** This can override the feedback band upward.
If an error, once noticed, is fixed where it occurred → the feedback band stands
(≤L3). If an undetected error silently corrupts the work built on it, so discovery
forces tracing and reworking dependents → L4. If a wrong consequential step cannot
be redone at all, and the task's own success turns on getting such steps right
first time → L5. Under the r38 L1 text this check is mandatory even when feedback
is per-action: a return that only confirms an unretractable step has *executed*
does not license L1.

**Q4 — Apply the guards.** (a) Severity-not-placement: an action being destructive
or high-stakes raises nothing by itself — what matters is whether the task's success
turns on unretractable steps being right first time. A destructive action that is the
*intended outcome*, performed under per-step feedback with recovery available, is
still low. (b) Deliberation is not execution: devising or revising the plan is
planning work; only *keeping the given plan on track* counts here. (c) Length, memory
load, information-finding, and other agents raise this demand only insofar as they
make deviations harder to detect or recover from. (d) Tie-break lower.

Label the task-side demand from the text alone. Do not anchor on the July record or
on any score you remember — the point of the pre-registration is an independent
human derivation.

## Items (write your label 0–5 after each)

### tau-0007

````
[τ-bench: airline] A customer-service agent must assist a user.
Reason for the call: You want to cancel your upcoming flights within reservation IDs XEHM4B and 59XX6W.
Known information: Your user id is 'daiki_muller_1116'.
What the user wants: If the agent says either of the two reservations is basic economy, ask to upgrade to economy first and then cancel the reservation.

You are very persistent and terse but clear.

In the middle of the conversation after the third agent message, you also want to check if you have any other upcoming flights and ask for what the total cost of those flights is.

````

**Your label (0–5):** 2   Deciding phrase: "can be checked at checkpoints and corrected" (Pablo, via chat, 2026-08-21)

### tau-0106

````
[τ-bench: retail] A customer-service agent must assist a user.
Reason for the call: You wonder when is your air purifier is arriving. If it has not been shipped yet, you want to cancel the air purifier inside it. If you cannot cancel just the air purifier, you want to modify it to the cheapest possible air purifier, and refund to the gift card. You do not remember your gift card id but it should be in your user account. If you cannot modify it or refund to the gift card, no action.
Known information: You are ivan_hernandez_6923 living in San Diego, 92133.
Unknown information: You don't have an email.
What the user wants: You are polite but brief and firm.

````

**Your label (0–5):** 2   Deciding phrase: "can be checked at checkpoints and corrected" (Pablo, via chat, 2026-08-21)

### tau-0146

````
[τ-bench: retail] A customer-service agent must assist a user.
Reason for the call: You want to change your LA order to your NYC address (you prefer not to reveal it but it is in your other order). You also want to exchange Bluetooth Speaker to be the cheapest green type.
Known information: You name is Yusuf Li and your zip code is 91148.
Unknown information: You do not remember your email address.
What the user wants: You are cautious, insecure, organized.

````

**Your label (0–5):** 2   Deciding phrase: "can be checked at checkpoints and corrected" (Pablo, via chat, 2026-08-21)

### tau-0089

````
[τ-bench: retail] A customer-service agent must assist a user.
Reason for the call: You just moved from Florida to Phoenix. Unfortunately your address is still the old one, and you want to update it. Your current address should be in your recent order (you can mention this to the agent), and you do not want to reveal it. Also, you want to know what is the price of the cheapest available t-shirt right now, and if you can order it through the agent.
Known information: You are fatima_taylor_3452, and you just moved from Florida (32169) to Phoenix (85033).
Unknown information: You do not remember your email address
What the user wants: You are a funny person with lots of jokes, and you want to make the agent laugh.

````

**Your label (0–5):** 2   Deciding phrase: "can be checked at checkpoints and corrected" (Pablo, via chat, 2026-08-21)

### tau-0094

````
[τ-bench: retail] A customer-service agent must assist a user.
Reason for the call: You want to change the Desk Lamp in order #W9300146 that you've placed for the cheapest Desk Lamp that's available. Any price difference should go to a gift card. You also want to know how much you get back in total.
Known information: You are Aarav Anderson, residing in Philadelphia 19031.
Unknown information: You do not remember your email address
What the user wants: You're a private person and are reluctant to share information unless it's absolutely necessary.

````

**Your label (0–5):** 2   Deciding phrase: "same family: tool returns and user confirmations settle the work at natural junctures of a short task" (proposed by Claude 2026-08-22, pending Pablo's endorsement)

### probe-kill

````
A server's monitoring dashboard shows a runaway process consuming all memory. Following the given runbook, identify the frozen process by its PID and terminate it with the kill command, then confirm the service restarts.

````

**Your label (0–5):** 1   Deciding phrase: "dashboard and restart confirmation settle each action on the spot; nothing left for the agent to establish" (proposed by Claude 2026-08-22, pending Pablo's endorsement)

### probe-filing

````
Submit a company's annual regulatory filing through the government portal, following the given checklist. Once submitted, the filing cannot be amended or withdrawn; errors carry formal penalties. All figures and documents are prepared and provided.

````

**Your label (0–5):** 2   Deciding phrase: "checking is easy and must merely happen before the click; unretractability alone places nothing" (Pablo, via chat, 2026-08-22)

### swe-0090

````
models.E015 is raised when ordering uses lookups that are not transforms.
Description
	
./manage.py check
SystemCheckError: System check identified some issues:
ERRORS:
app.Stock: (models.E015) 'ordering' refers to the nonexistent field, related field, or lookup 'supply__product__parent__isnull'.
However this ordering works fine:
>>> list(Stock.objects.order_by('supply__product__parent__isnull').values_list('pk', flat=True)[:5])
[1292, 1293, 1300, 1295, 1294]
>>> list(Stock.objects.order_by('-supply__product__parent__isnull').values_list('pk', flat=True)[:5])
[108, 109, 110, 23, 107]
I believe it was fine until #29408 was implemented.
Stock.supply is a foreign key to Supply, Supply.product is a foreign key to Product, Product.parent is a ForeignKey('self', models.CASCADE, null=True)


````

**Your label (0–5):** 2   Deciding phrase: "the issue supplies the pass criteria (check command + working queries): checks provided, the agent has only to reach them" (proposed by Claude 2026-08-22, pending Pablo's endorsement)

### swe-0461

````
Exception when multiplying BlockMatrix containing ZeroMatrix blocks
When a block matrix with zero blocks is defined

```
>>> from sympy import *
>>> a = MatrixSymbol("a", 2, 2)
>>> z = ZeroMatrix(2, 2)
>>> b = BlockMatrix([[a, z], [z, z]])
```

then block-multiplying it once seems to work fine:

```
>>> block_collapse(b * b)
Matrix([
[a**2, 0],
[0, 0]])
>>> b._blockmul(b)
Matrix([
[a**2, 0],
[0, 0]])
```

but block-multiplying twice throws an exception:

```
>>> block_collapse(b * b * b)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 297, in block_collapse
    result = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 44, in chain_rl
    expr = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 33, in conditioned_rl
    return rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 95, in switch_rl
    return rl(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 361, in bc_matmul
    matrices[i] = A._blockmul(B)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
>>> b._blockmul(b)._blockmul(b)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
```

This seems to be caused by the fact that the zeros in `b._blockmul(b)` are not `ZeroMatrix` but `Zero`:

```
>>> type(b._blockmul(b).blocks[0, 1])
<class 'sympy.core.numbers.Zero'>
```

However, I don't understand SymPy internals well enough to find out why this happens. I use Python 3.7.4 and sympy 1.4 (installed with pip).


````

**Your label (0–5):** 2   Deciding phrase: "given repro settles success at the end of a short task; what must pass is stated, not devised" (proposed by Claude 2026-08-22, pending Pablo's endorsement)

### usaco-0002

````
Elsie is trying to describe her favorite USACO contest to Bessie, but Bessie is
having trouble understanding why Elsie likes it so much. Elsie says "And It's
mooin' time! Who wants a mooin'? Please, I just want to do USACO".
Bessie still doesn't understand, so she transcribes Elsie's description in a
string of length $N$ ($3 \leq N \leq 10^5$)  containing lowercase alphabetic
characters $s_1s_2 \ldots s_N$.  Elsie considers a string $t$ containing three
characters a moo if $t_2 = t_3$ and $t_2 \neq t_1$.
A triplet $(i, j, k)$ is valid if $i < j < k$ and string $s_i s_j s_k$ forms a
moo. For the triplet, FJ performs the following to calculate its value:
FJ bends string $s$ 90-degrees at index $j$
The value of the
triplet is twice the area of $\Delta ijk$.
In other words, the value of the triplet is $(j-i)(k-j)$.
Bessie asks you $Q$ ($1 \leq Q \leq 3 \cdot 10^4$) queries. In each query, she
gives you two integers $l$ and $r$ ($1 \leq l \leq r \leq N$, $r-l+1 \ge 3$) and
ask you for the maximum value among valid triplets $(i, j, k)$ such that
$l \leq i$ and $k \leq r$. If no valid triplet exists, output $-1$.
Note that the large size of integers involved in this problem may require the
use of 64-bit integer data types (e.g., a "long long" in C/C++).
INPUT FORMAT (input arrives from the terminal / stdin):
The first line contains two integers $N$ and $Q$.
The following line contains $s_1 s_2, \ldots s_N$.
The following $Q$ lines contain two integers $l$ and $r$, denoting each query.
OUTPUT FORMAT (print output to the terminal / stdout):
Output the answer for each query on a new line.
SAMPLE INPUT:
12 5
abcabbacabac
1 12
2 7
4 8
2 5
3 10
SAMPLE OUTPUT:
28
6
1
-1
12
For the first query, ($i,j,k$) must satisfy $1 \le i < j < k \le 12$. It can be
shown that the maximum area of $\Delta ijk$ for some valid ($i,j,k$) is achieved
when $i=1$, $j=8$, and $k=12$. Note that $s_1 s_8 s_{12}$ is the string "acc"
which is  a moo according to the definitions above. $\Delta ijk$ will have legs
of lengths $7$ and $4$ so two times the area of it will be $28$.
For the third query, ($i,j,k$) must satisfy $4 \le i < j < k \le 8$. It can be
shown that the maximum area of $\Delta ijk$ for some valid ($i,j,k$) is achieved
when $i=4$, $j=5$, and $k=6$.
For the fourth query, there exists no ($i,j,k$) satisfying
$2 \le i < j < k \le 5$ in which $s_i s_j s_k$ is a moo so the output to that
query is $-1$.

````

**Your label (0–5):** 3   Deciding phrase: "sample cases do not settle correctness or efficiency at these bounds; the agent must decide what tests to run and what the results would have to show" (proposed by Claude 2026-08-22, pending Pablo's endorsement)

### ab-0024

````
Based on the last decade (2014-2023), what is the likelihood that it will snow on New Year’s Eve in Chicago? (Provide the answer in percentage.)

````

**Your label (0–5):** 2   Deciding phrase: "each year's datum is settled by the retrieved record; per-year checkpoints on a short task" (proposed by Claude 2026-08-22, pending Pablo's endorsement)


### probe-cave (NEW designed probe — must score 5 under the r38 text)

````
Pilot a submersible glider through a silt-blacked underwater cave passage by executing the pre-computed dive plan: a fixed sequence of compass headings, thruster settings, and timed legs. Nothing is visible in the water, no positioning reference penetrates the rock, and where the glider actually is becomes known only when it emerges at the far entrance — or fails to. A small uncorrected drift on any leg carries through the whole traverse.
````

**Your label (0–5):** 5   Deciding phrase: "checking is needed (drift carries through) yet nothing can reveal a deviation before the outcome is settled" (proposed by Claude 2026-08-22, pending Pablo's endorsement)
