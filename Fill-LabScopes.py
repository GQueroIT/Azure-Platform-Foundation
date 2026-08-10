#!/usr/bin/env python3
"""
Fills in the "## 1. Objective" section of every day's lab.md with the real
scope for that lab. This is static content - what each lab is supposed to
build and which AZ-104 domain it maps to - so it's filled in now rather
than left blank. Everything else in lab.md (steps, verification, issues,
takeaways) stays blank on purpose - that part has to come from you
actually doing the work, not from this script.

Run this after Restructure-AzurePlatformFoundation.py, from inside the repo.
Safe to re-run - only touches the placeholder line, skips days already filled in.
"""

from pathlib import Path

base_path = Path(__file__).resolve().parent

PLACEHOLDER = "What this lab builds and which AZ-104 skill it maps to."

SCOPES = {
    "day-01-rbac-and-management-groups":
        "Deploy a management group hierarchy and a custom RBAC role via Bicep. "
        "Maps to the Identities and Governance domain.",
    "day-02-azure-policy":
        "Assign a built-in Azure Policy (tag enforcement, region restriction) via "
        "Bicep. Maps to Identities and Governance.",
    "day-03-locks-and-budgets":
        "Deploy a resource lock and a subscription budget alert via Bicep, "
        "establishing the cost guardrails for the rest of the build. Maps to "
        "Identities and Governance.",
    "day-04-vm-availability-zones":
        "Deploy a B1s Linux VM pinned to an availability zone via Bicep. Maps to "
        "the Compute domain.",
    "day-05-vm-scale-sets":
        "Deploy a small VM Scale Set spread across availability zones via Bicep. "
        "Maps to Compute.",
    "day-06-disks-and-extensions":
        "Attach a managed data disk and run a VM extension on the Day 04 VM via "
        "Bicep. Maps to Compute.",
    "day-07-app-service":
        "Deploy a Free-tier App Service web app via Bicep. Maps to Compute.",
    "day-08-container-apps":
        "Deploy a container to Azure Container Apps on the consumption plan via "
        "Bicep. Maps to Compute.",
    "day-09-bicep-consolidation":
        "Consolidate Days 00-08 into a shared, parameterized set of Bicep files "
        "and confirm a clean redeploy. No new exam objective - a code-quality "
        "checkpoint.",
    "day-10-self-test-teardown":
        "Self-test on Days 00-09 and fully tear down every billable resource "
        "from Weeks 1-2 before starting Networking.",
    "day-11-vnet-subnets-nsg":
        "Deploy a VNet with subnets and an NSG with custom rules via Bicep. "
        "Maps to the Networking domain.",
    "day-12-peering-and-dns":
        "Peer two VNets and deploy a private DNS zone via Bicep. Maps to "
        "Networking.",
    "day-13-load-balancer-appgw":
        "Deploy a Standard Load Balancer in front of two backend addresses via "
        "Bicep. Maps to Networking.",
    "day-14-bastion-vpn-gateway":
        "Deploy Azure Bastion and a basic VPN Gateway via Bicep - the most "
        "expensive lab in the build, delete both the same day. Maps to "
        "Networking.",
    "day-15-network-watcher-review":
        "Reference Network Watcher and review Week 3 (Days 11-14) before "
        "moving to Storage.",
    "day-16-storage-accounts-redundancy":
        "Deploy a storage account and test redundancy tier configurations via "
        "Bicep. Maps to the Storage domain.",
    "day-17-blob-lifecycle":
        "Deploy a blob lifecycle management policy via Bicep. Maps to Storage.",
    "day-18-azure-files":
        "Deploy an Azure Files share via Bicep. Maps to Storage.",
    "day-19-sas-private-endpoints":
        "Deploy a private endpoint for the storage account via Bicep, and "
        "generate a SAS token via Azure CLI. Maps to Storage.",
    "day-20-review-teardown":
        "Self-test on Days 16-19 and tear down any billable storage-adjacent "
        "resources (private endpoints) before moving to Identity.",
    "day-21-entra-users-groups":
        "Deploy an Entra ID security group via the Microsoft Graph Bicep "
        "extension. Maps to the Identities and Governance domain.",
    "day-22-rbac-vs-entra-roles":
        "Compare Azure RBAC role assignments against Entra directory role "
        "assignments, both in Bicep via the Graph extension. Maps to "
        "Identities and Governance.",
    "day-23-conditional-access-sspr":
        "Document how Conditional Access and SSPR are actually configured "
        "(Graph PowerShell/portal, not Bicep) and cross-reference "
        "identity-security-entra. Maps to Identities and Governance.",
    "day-24-hybrid-identity":
        "Document hybrid identity concepts - Entra Connect, password hash sync "
        "vs pass-through auth vs federation. Theory day, no deployable "
        "resource. Maps to Identities and Governance.",
    "day-25-self-test":
        "Self-test on Days 21-24 before moving to Monitoring & Backup.",
    "day-26-log-analytics-diagnostics":
        "Deploy a Log Analytics workspace and a diagnostic setting via Bicep. "
        "Maps to the Monitor domain.",
    "day-27-alerts-action-groups":
        "Deploy an action group and a metric alert rule via Bicep. Maps to "
        "Monitor.",
    "day-28-azure-backup":
        "Deploy a Recovery Services vault and backup policy, and back up the "
        "Day 04 VM via Bicep. Maps to Monitor (backup).",
    "day-29-update-management-arc":
        "Onboard the RHEL box itself as an Azure Arc-enabled server via "
        "azcmagent, then reference it in Bicep. Maps to Monitor.",
    "day-30-final-teardown":
        "Final self-test across the whole build and full teardown of every "
        "remaining billable resource.",
}

import re

filled = 0
skipped = 0
missing = 0
titles_fixed = 0

for lab_file in sorted(base_path.glob("*/day-*/lab.md")):
    day_slug = lab_file.parent.name
    scope = SCOPES.get(day_slug)

    if scope is None:
        print(f"No scope defined for {day_slug} - skipping")
        missing += 1
        continue

    text = lab_file.read_text(encoding="utf-8")
    changed = False

    # Fix titles that lost their day number, e.g. "# Day Azure Policy"
    # should read "# Day 02 - Azure Policy". The number lives in the
    # folder slug itself (day-02-azure-policy).
    num_match = re.match(r"day-(\d+)-", day_slug)
    if num_match:
        day_num = num_match.group(1)
        bad_header_match = re.match(r"# Day (?!\d)(.+)", text)
        if bad_header_match:
            fixed_header = f"# Day {day_num} - {bad_header_match.group(1)}"
            text = fixed_header + text[bad_header_match.end():]
            changed = True
            titles_fixed += 1

    if PLACEHOLDER not in text:
        if changed:
            lab_file.write_text(text, encoding="utf-8")
        print(f"{day_slug}: placeholder not found, already filled in? skipping")
        skipped += 1
        continue

    text = text.replace(PLACEHOLDER, scope)
    lab_file.write_text(text, encoding="utf-8")
    filled += 1

print()
print(f"Done - {filled} lab.md files filled in, {skipped} skipped (already edited), "
      f"{missing} missing a scope, {titles_fixed} titles fixed.")