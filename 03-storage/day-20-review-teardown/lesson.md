# Day 20 - Storage Week Review and Teardown

No new syntax today.

## Self-Test
- What does the `<Tier>_<Redundancy>` pattern in `sku.name` actually
  control, and which one is right for a lab budget?
- Why is the lifecycle management policy always named `'default'`?
- Why does a private endpoint live under `Microsoft.Network`, not
  `Microsoft.Storage`?

## Teardown Checklist
- [ ] Private endpoint from Day 19 deleted if not needed going forward
- [ ] Any test containers/shares with real cost impact cleaned up
- [ ] Bicep files for this phase deploy cleanly from a fresh resource group
- [ ] Lab docs and lessons committed