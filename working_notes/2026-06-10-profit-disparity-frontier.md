# Within the band, profit and disparity are mostly NEGATIVELY coupled — except where laundered

**2026-06-10. Tony's pitch: "build the ensemble this way → increase profitability while holding
discrimination at the floor." Tests whether profit ⊥ disparity within the band. Script:
`scripts/profit_disparity_frontier_probe.py`. Output: `runs/profit_disparity_frontier.json`.**

## Frozen prediction LOST in the bank's favor

I predicted P1 (profit POSITIVELY coupled to disparity → pitch dies) at prior 0.45. The data came
back mostly **P3 (negatively coupled → pitch stronger than asked).** I lost, and the loss is good news
for the pitch.

## Result (profit EV: grant+repaid=+r, grant+default=−1, deny=0; r=0.25; disparity = grant-gap by G)

```
  channel  band  corr(profit,|disp|)  members dominating random  floor−random profit
  D1        56      -0.20                    13                     +23   (floor is FREE)
  D2         4      -0.92                     2                     +44   (floor is FREE)
  D3        18      -0.70                    12                     -52   (floor COSTS)
  D4         3      +1.00                     0                      -7   (floor COSTS)
```

- **3 of 4 channels: profit NEGATIVELY coupled with disparity.** The more profitable band members are
  the LESS discriminatory ones. 12–13 members DOMINATE the random pick on BOTH axes (≥ profit AND ≤
  |disparity|). "Pick the profitable one" ≈ "pick the fair one." The dice-roll
  ([[project_pick_one_hides_choice]]) is strictly wasteful — the ensemble can do strictly better on
  profit AND fairness simultaneously. **Tony's pitch is real, and stronger than asked, on D1/D2/D3.**

- **D4 is the honest warning (the fairwash channel):** corr flips to +1.0 — profit IS bought with
  disparity, perfectly, ZERO dominating members. **Where disparity is LAUNDERED into admitted proxies,
  profit and disparity become the same axis and the pitch collapses.** And that sign-flip is itself the
  ALARM: corr(profit,|disp|) > 0 within the band is a detector for "the profitable signal here is the
  laundered one." (This is the canary the redundancy-k probe FAILED to find
  [[2026-06-10-redundancy-canary-REFUTED]] — it lives in the profit-coupling sign, not in k.)

## Honest scope

- Synthetic substrate; r=0.25 fixed (profit magnitudes are illustrative, signs/correlations are the
  claim). Profit ranks are all negative here because the DGP default rate is high — the SIGN of the
  coupling and the DOMINATION count are the load-bearing results, not absolute profit.
- "floor costs money" on D3/D4 means the min-disparity member is not the max-profit member there — the
  selectable corner (max profit NEAR the floor) is the honest operating point, and on D1/D2 it equals
  the floor (free), on D3 it recovers most of the gap (−52 → the corner is better than the raw floor).

## The pitch, stated honestly to a bank

"The Rashomon band gives you a menu of equally-accurate models. On normal risk structure, the
profitable members are also the fairer ones — you can pick a model that beats a random choice on BOTH
profit and disparity (12–13 such models here). The one exception is when disparity has been laundered
into your features: there profit and disparity fuse, and the band tells you so (the profit–disparity
correlation flips positive). So the ensemble is both a profit tool and a laundering detector."

## Live successor (Tony's type-(2) feedback loop — the deeper reframe)

Tony: the "maybe" band is where the bank could write correctly-priced higher-rate loans IF it can
identify TYPE-(2) structure (individual properties, invisible per-case, visible in AGGREGATE, on
LAWFUL grounds) vs TYPE-(1) (unforeseeable macro noise). The shuffle-set is then a RESEARCH QUEUE: the
borrowers where the current model class has run out of lawful signal and resorts to arbitrary carving.
**Test the loop:** in the shuffle-set, is there extractable aggregate structure predicting default on
G-ORTHOGONAL (lawful) grounds? If yes → the marginal band is a profit-AND-fairness opportunity (mine
type-2, fold into next model, band shrinks toward correctly-priced loans, disparity drops because
arbitrariness is replaced by justified pricing). If the shuffle-set is type-(1) noise → the loop is
empty and the honest answer is "these are genuinely unpredictable; stop discriminating in the guess."
This also explains D4: there the profitable members mine type-2-SHAPED but UNLAWFUL signal (the proxy)
→ profit couples to disparity. [next probe]

## Meta

Priored predictions 0-for-8, but this miss is the most useful kind: I bet against the bank's pitch and
the bench said the pitch holds (mostly), with a precise exception that became a NEW detector. The
instrument keeps getting reborn: failed protected-detector → due-process score → (failed redundancy
canary) → profit-coupling laundering detector + type-2 research queue.
