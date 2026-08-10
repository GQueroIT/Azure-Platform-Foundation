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

## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from.