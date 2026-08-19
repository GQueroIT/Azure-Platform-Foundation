# Cost Log

Real spend, logged after each session. Not an estimate - what the
subscription actually shows. Check Cost Management + Billing in the
portal, or `az consumption usage list`, and record what you find.

This becomes a real artifact you can point to: "built and tore down the
full AZ-104 hands-on build for $X total" is a concrete, specific claim
that means something in an interview. A vague "I did some Azure labs"
doesn't.

## Log

| Date       | Day | What Ran                                  | Deallocated/Deleted? | Cost This Session | Running Total |
|------------|-----|-------------------------------------------|----------------------|-------------------|---------------|
| 08/12/2026 | 01  | Storage account                           | Deallocated          | $0.00             | $0.00         |
| 08/15/2026 | 02  | n/a                                       | n/a                  | $0.00             | $0.00         |
| 08/18/2026 | 03  | Resource locks and budget                 | n/a                  | $0.00             | $0.00         |
| 08/18/2026 | 03b | Tags, Azure Advisor, and Cost Management  | n/a                  | $0.00             | $0.00         |

## Notes
- Log every session, even a $0.00 one - the pattern matters as much as
  the number.
- If a number looks wrong (way higher than expected), that's worth
  investigating immediately, not just recording. See TROUBLESHOOTING.md.
- Week 3 (Networking, Days 11-15) is the week most likely to spike this
  log - Bastion and VPN Gateway bill hourly with no "pause" option.

## Notes

- Log every session, even a $0.00 one - the pattern matters as much as the number.
- If a number looks wrong (way higher than expected), investigate it immediately instead of just recording it. See `TROUBLESHOOTING.md`.
- Week 3 (Networking, Days 11-15) is the week most likely to increase this log - Bastion and VPN Gateway bill hourly with no pause option.


## Session Logs

### Day 01 - 08/12/2026

- Worked with a storage account during the lab.
- Checked Azure costs after completing the work.
- No meaningful charges were recorded for the session.
- Removed the lab resource after I was finished with it.

**Session Cost:** $0.00  
**Running Total:** $0.00


### Day 02 - 08/15/2026

- Completed Day 02 governance work.
- The lab did not require any resources that created noticeable charges.
- Checked costs after completing the session.

**Session Cost:** $0.00  
**Running Total:** $0.00


### Day 03 - 08/18/2026

**Locks and Budgets**

- Created and tested Azure resource locks.
- Worked with `CanNotDelete` and `ReadOnly` locks to see how they affect resource management.
- Confirmed that `CanNotDelete` protects a resource from deletion while still allowing changes.
- Used a budget to track expected Azure spending and set thresholds for cost monitoring.
- Learned that a budget does not shut resources down when the limit is reached. It is used for tracking and alerts.

**Tags, Advisor, and Cost Management**

- Added tags to resources to practice organizing and identifying Azure resources.
- Used tags such as environment, owner, and purpose to understand how they can help manage larger environments.
- Reviewed Azure Advisor to see the recommendations Azure provides for improving an environment.
- Used Cost Management to review spending and see where Azure costs are coming from.
- Connected the different governance tools together: tags organize resources, locks protect them, budgets monitor spending, and Advisor provides recommendations.

**Session Cost:** $0.00  
**Running Total:** $0.00