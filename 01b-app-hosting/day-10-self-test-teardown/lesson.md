# Day 10 - Self-Test and Teardown

No new syntax today. This is a checkpoint day.

## Self-Test
Without looking back at Days 00-09, try to answer:
- What's the difference between `param` and `var`?
- Why does a role assignment need `guid()` for its name?
- What does `existing` do, and when do you need it?
- What's the difference between how a single VM and a VMSS define `zones`?
- Why does `reserved: true` matter for a Linux App Service plan?

If any of those are shaky, that's the lesson file to reread before Week 3.

## Teardown Checklist
- [ ] All VMs from this block deallocated or deleted
- [ ] VMSS deleted if not needed going forward
- [ ] App Service / Container App scaled down or deleted
- [ ] Confirm the $50 budget alert from Day 03 is still active
- [ ] Commit all Bicep files and lab docs to the repo

## Why This Matters (Business Context)
A company gets a surprise bill because a proof-of-concept environment from three months ago never got deleted. Teardown discipline isn't optional at a real company - it's the difference between a lab and a liability.
