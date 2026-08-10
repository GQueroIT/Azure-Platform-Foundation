# Cost Log

Real spend, logged after each session. Not an estimate - what the
subscription actually shows. Check Cost Management + Billing in the
portal, or `az consumption usage list`, and record what you find.

This becomes a real artifact you can point to: "built and tore down the
full AZ-104 hands-on build for $X total" is a concrete, specific claim
that means something in an interview. A vague "I did some Azure labs"
doesn't.

## Log

| Date | Day | What Ran | Deallocated/Deleted? | Cost This Session | Running Total |
|------|-----|----------|----------------------|--------------------|----------------|
|      |     |          |                       |                    |                |

## Notes
- Log every session, even a $0.00 one - the pattern matters as much as
  the number.
- If a number looks wrong (way higher than expected), that's worth
  investigating immediately, not just recording. See TROUBLESHOOTING.md.
- Week 3 (Networking, Days 11-15) is the week most likely to spike this
  log - Bastion and VPN Gateway bill hourly with no "pause" option.
