# Azure-Platform-Foundation

## Scope
Hands-on Azure build covering the full AZ-104 exam blueprint: Identities and
Governance, Compute, Storage, Networking, and Monitoring. Built and documented
phase by phase against an 8-week plan. Every lab is built in the Azure portal
first, then translated into Bicep, verified, and documented before moving to
the next objective.

## What This Covers

- **01-compute-governance** - management groups, subscriptions, RBAC, Azure
  Policy, resource locks, budgets, VMs across availability zones, VM Scale Sets
- **01b-app-hosting** - App Service, Azure Container Apps
- **02-networking** - VNets, subnets, NSGs, VNet peering, private DNS, Load
  Balancer, Application Gateway, Bastion, VPN Gateway, Network Watcher
- **03-storage** - storage accounts, redundancy tiers, blob lifecycle
  management, Azure Files, SAS tokens, private endpoints
- **04-identity-access** - Entra ID users/groups, RBAC vs Entra roles,
  Conditional Access, SSPR, hybrid identity
- **05-monitoring-backup** - Azure Monitor, Log Analytics, alerts, Azure
  Backup, Update Management, Azure Arc

## How Each Phase Folder Is Organized

Each phase folder contains one subfolder per study day
(`day-01-rbac-and-management-groups/`, etc). Inside each day's folder:

- **lesson.md** - the Bicep lesson for that day, written before you build.
  No prior coding background assumed.
- **lab.md** - your portal steps, verification, and write-up for that day
- **solution.bicep** - your actual Bicep code for that day's build

## Daily Loop

1. Read the lesson (`lesson.md`) for that day
2. Build it in the Azure Portal first
3. Translate it to Bicep (`solution.bicep`)
4. Validate before deploying - `az bicep build`, then
   `az deployment group validate`, then `az deployment group what-if`.
   See `assets/validation-guide.md` if you're not sure what these do or
   why they matter - short answer: they catch mistakes for free, before
   you pay for anything.
5. Deploy, and confirm it matches what `what-if` predicted
6. Verify it actually works the way the lesson said it should
7. Fill in `lab.md` - steps taken, verification, any issues you hit
8. Read the lesson's "Why This Matters" section and make sure you could
   explain it out loud, not just recite it
9. Commit and push - don't let work sit uncommitted past one session
10. Confirm nothing billable is left running before you close the laptop

## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from, and `assets/validation-guide.md` for
how to check your Bicep before deploying it. Every lesson also ends with a
"Why This Matters" section tying that day's work to a real business
reason - it's worth reading even after you've built the lab.

Also at the repo root: `GLOSSARY.md` for any term you hit that isn't
explained inline, `COST-LOG.md` to track real spend session by session,
`TROUBLESHOOTING.md` to log real errors and what fixed them, and
`PROGRESS.md` for the day-by-day checklist and the definition of done
for the whole build.