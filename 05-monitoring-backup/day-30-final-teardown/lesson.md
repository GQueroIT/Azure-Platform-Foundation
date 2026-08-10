# Day 30 - Final Self-Test and Full Teardown

No new syntax today. This closes out the 6-week build.

## Self-Test
- Why does a diagnostic setting need an explicit `scope:` property?
- What do `evaluationFrequency` and `windowSize` control on an alert rule,
  and what format are they in?
- Why is a backup protected item's `name` such a strange format?
- Why isn't Azure Arc onboarding itself a Bicep resource?

## Full Teardown Checklist
- [ ] Every VM and VMSS from the entire build deallocated or deleted
- [ ] Bastion, VPN Gateway, and Load Balancer from Week 3 confirmed deleted
- [ ] Private endpoints from Week 4 confirmed deleted
- [ ] Recovery Services vault backup jobs stopped/cleaned up if not needed
- [ ] Budget alert from Day 03 still active
- [ ] Every phase's Bicep files deploy cleanly from a fresh resource group
- [ ] All lab docs and lessons committed to the repo

## Next
Weeks 7-8 of the Master Blueprint: Microsoft Learn practice assessment,
targeted review of weak domains, then book the exam.