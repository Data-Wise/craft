<!-- Planted regression check (F6): a legitimate small subset count for the
     smallest count type (agents, expected=2) must not read as a stale total.
     Before the floor fix, the 40%-of-expected threshold for agents was
     `2 * 40 / 100 == 0` -- the guard ADR-007 and the code comments describe
     did not exist for this type, so every mention of "N agent(s)", however
     small, was treated as a candidate stale total. -->

# Migration Notes

**TL;DR** — this patch only touches 1 agent config file; the other agent is untouched.
