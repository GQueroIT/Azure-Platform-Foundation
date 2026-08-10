# Day 09 - Bicep Consolidation Pass

No new syntax today. This session is about pulling everything from Days
00-08 into one working set of Bicep files that deploys cleanly end to end.

## What To Actually Do
1. Open every .bicep file you've written so far across this phase and
   01-compute-governance.
2. Check for repeated values (resource group location, admin username,
   naming prefixes) that should be pulled up into shared `param` values
   instead of hardcoded in each file.
3. Try turning your most-repeated resource pattern (the VM, most likely)
   into a `module` that the others call, using what Day 00 taught about
   `module` blocks.
4. Redeploy everything with `az deployment group create` and confirm
   nothing broke.

## Why This Matters
This is the day the exam actually cares about most, in a sense - AZ-104
questions about Bicep test whether you understand modules, parameters, and
reusability, not just whether you can write one resource block. A pile of
9 unrelated .bicep files is very different from a small set of
well-parameterized ones that call each other.

## Why This Matters (Business Context)
A contractor hands off a project as nine unrelated scripts, no shared naming convention, hardcoded values specific to their test environment. The next engineer spends a week just figuring out how to redeploy it somewhere else. Modular, parameterized Bicep is what makes a handoff take an hour instead of a week.
