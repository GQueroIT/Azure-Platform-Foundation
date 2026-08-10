#!/usr/bin/env python3
"""
Splits the "## 1. Objective" section in every lab.md into two distinct
objectives: what you're building in the Azure Portal that day (the actual
AZ-104 skill), and what you're separately writing in Bicep to reproduce
it. These are genuinely two different deliverables under the portal-first-
then-Bicep workflow, and one merged sentence was hiding that.

Run this after Fill-LabScopes.py, from inside the repo. Safe to re-run -
it finds the "## 1. Objective" through "## 2. Steps Taken" block by its
headers, not by matching specific old text, so it works whether that
section is still the placeholder, the single-objective version, or has
already been split.
"""

from pathlib import Path
import re

base_path = Path(__file__).resolve().parent

LAB_OBJECTIVES = {
    "day-01-rbac-and-management-groups":
        "Set up a management group hierarchy and assign a custom RBAC role "
        "through the Azure Portal. Maps to the Identities and Governance domain.",
    "day-02-azure-policy":
        "Assign a built-in Azure Policy (tag enforcement, region restriction) "
        "through the Portal. Maps to Identities and Governance.",
    "day-03-locks-and-budgets":
        "Create a resource lock and a subscription budget alert through the "
        "Portal, establishing the cost guardrails for the rest of the build. "
        "Maps to Identities and Governance.",
    "day-04-vm-availability-zones":
        "Deploy a B1s Linux VM pinned to an availability zone through the "
        "Portal. Maps to the Compute domain.",
    "day-05-vm-scale-sets":
        "Deploy a small VM Scale Set spread across availability zones through "
        "the Portal. Maps to Compute.",
    "day-06-disks-and-extensions":
        "Attach a managed data disk and run a VM extension on the Day 04 VM "
        "through the Portal. Maps to Compute.",
    "day-07-app-service":
        "Deploy a Free-tier App Service web app through the Portal. Maps to "
        "Compute.",
    "day-08-container-apps":
        "Deploy a container to Azure Container Apps on the consumption plan "
        "through the Portal. Maps to Compute.",
    "day-09-bicep-consolidation":
        "No new portal work today - this is a code-quality pass over Days 00-08.",
    "day-10-self-test-teardown":
        "No new portal work - confirm every resource from Weeks 1-2 is "
        "actually deallocated or deleted.",
    "day-11-vnet-subnets-nsg":
        "Deploy a VNet with subnets and an NSG with custom rules through the "
        "Portal. Maps to the Networking domain.",
    "day-12-peering-and-dns":
        "Peer two VNets and deploy a private DNS zone through the Portal. "
        "Maps to Networking.",
    "day-13-load-balancer-appgw":
        "Deploy a Standard Load Balancer in front of two backend addresses "
        "through the Portal. Maps to Networking.",
    "day-14-bastion-vpn-gateway":
        "Deploy Azure Bastion and a basic VPN Gateway through the Portal - "
        "the most expensive lab in the build, delete both the same day. Maps "
        "to Networking.",
    "day-15-network-watcher-review":
        "Explore Network Watcher's diagnostic tools through the Portal. "
        "Review Week 3 (Days 11-14) before moving to Storage.",
    "day-16-storage-accounts-redundancy":
        "Deploy a storage account and test redundancy tier configurations "
        "through the Portal. Maps to the Storage domain.",
    "day-17-blob-lifecycle":
        "Configure a blob lifecycle management policy through the Portal. "
        "Maps to Storage.",
    "day-18-azure-files":
        "Deploy an Azure Files share through the Portal. Maps to Storage.",
    "day-19-sas-private-endpoints":
        "Generate a SAS token via Azure CLI and deploy a private endpoint for "
        "the storage account through the Portal. Maps to Storage.",
    "day-20-review-teardown":
        "No new portal work - confirm private endpoints and other billable "
        "storage resources are torn down.",
    "day-21-entra-users-groups":
        "Create an Entra ID security group through the Portal or Graph "
        "PowerShell. Maps to the Identities and Governance domain.",
    "day-22-rbac-vs-entra-roles":
        "Assign a test account an Entra directory role through the Portal, "
        "alongside an Azure RBAC role. Maps to Identities and Governance.",
    "day-23-conditional-access-sspr":
        "Configure Conditional Access and SSPR through the Portal - these "
        "aren't Bicep-deployable. Maps to Identities and Governance.",
    "day-24-hybrid-identity":
        "No hands-on portal work planned for this build - theory day on "
        "hybrid identity.",
    "day-25-self-test":
        "No new portal work - self-test on Days 21-24.",
    "day-26-log-analytics-diagnostics":
        "Deploy a Log Analytics workspace and enable a diagnostic setting "
        "through the Portal. Maps to the Monitor domain.",
    "day-27-alerts-action-groups":
        "Create an action group and a metric alert rule through the Portal. "
        "Maps to Monitor.",
    "day-28-azure-backup":
        "Create a Recovery Services vault and backup policy, and back up the "
        "Day 04 VM, through the Portal. Maps to Monitor (backup).",
    "day-29-update-management-arc":
        "Onboard the RHEL box as an Azure Arc-enabled server using azcmagent, "
        "run from the machine itself, not the Portal. Maps to Monitor.",
    "day-30-final-teardown":
        "Full teardown of every remaining billable resource across the whole "
        "6-week build.",
}

BICEP_OBJECTIVES = {
    "day-01-rbac-and-management-groups":
        "Write Bicep that defines the same management group hierarchy and a "
        "custom RBAC role using roleDefinitions and roleAssignments.",
    "day-02-azure-policy":
        "Write Bicep that assigns the same policy definitions via "
        "policyAssignments, parameterized instead of hardcoded.",
    "day-03-locks-and-budgets":
        "Write Bicep that deploys the same lock and budget via "
        "Microsoft.Authorization/locks and Microsoft.Consumption/budgets.",
    "day-04-vm-availability-zones":
        "Write Bicep that deploys the same VM, NIC, and zone placement from "
        "scratch.",
    "day-05-vm-scale-sets":
        "Write Bicep that deploys the same VMSS, with sku.capacity and zones "
        "set correctly.",
    "day-06-disks-and-extensions":
        "Write Bicep that attaches the same data disk and deploys the same "
        "extension as a child resource.",
    "day-07-app-service":
        "Write Bicep for the App Service Plan and the Site resource together.",
    "day-08-container-apps":
        "Write Bicep for the managed environment and the container app, "
        "including ingress and scale-to-zero.",
    "day-09-bicep-consolidation":
        "Refactor Days 00-08's Bicep into a shared, parameterized set of "
        "files/modules and confirm a clean redeploy from scratch.",
    "day-10-self-test-teardown":
        "No new code - self-test yourself on Days 00-09's concepts without "
        "looking back at the lessons.",
    "day-11-vnet-subnets-nsg":
        "Write Bicep for the same VNet, subnets, and NSG, with securityRules "
        "matching what you built.",
    "day-12-peering-and-dns":
        "Write Bicep that references both existing VNets and deploys peering "
        "resources on each side.",
    "day-13-load-balancer-appgw":
        "Write Bicep for the load balancer, frontend, backend pool, probe, "
        "and rule - delete the resource the same day.",
    "day-14-bastion-vpn-gateway":
        "Write Bicep for both gateway resources, including the required "
        "AzureBastionSubnet/GatewaySubnet naming.",
    "day-15-network-watcher-review":
        "Write a Bicep reference to the existing Network Watcher resource in "
        "NetworkWatcherRG.",
    "day-16-storage-accounts-redundancy":
        "Write Bicep for the storage account, parameterizing the SKU so you "
        "can redeploy at different redundancy tiers.",
    "day-17-blob-lifecycle":
        "Write Bicep for the same lifecycle policy as a managementPolicies "
        "child resource.",
    "day-18-azure-files":
        "Write Bicep for the fileServices and shares child resources.",
    "day-19-sas-private-endpoints":
        "Write Bicep for the private endpoint only - SAS tokens aren't a "
        "deployable resource.",
    "day-20-review-teardown":
        "No new code - self-test yourself on Days 16-19's concepts.",
    "day-21-entra-users-groups":
        "Write Bicep using the Microsoft Graph extension to deploy the same "
        "group and reference an existing user as owner.",
    "day-22-rbac-vs-entra-roles":
        "Write Bicep for both a Microsoft.Authorization roleAssignment and a "
        "Microsoft.Graph directoryRoleAssignment, side by side.",
    "day-23-conditional-access-sspr":
        "No Bicep today - document why, and cross-reference "
        "identity-security-entra instead.",
    "day-24-hybrid-identity":
        "No Bicep today - Entra Connect isn't a deployable Azure/Graph "
        "resource.",
    "day-25-self-test":
        "No new code - self-test yourself on Days 21-24's concepts.",
    "day-26-log-analytics-diagnostics":
        "Write Bicep for the workspace and a diagnostic setting scoped to an "
        "existing resource.",
    "day-27-alerts-action-groups":
        "Write Bicep for both resources, with the alert referencing the "
        "action group by ID.",
    "day-28-azure-backup":
        "Write Bicep for the vault, policy, and protected item - including "
        "that awkward protected-item name format.",
    "day-29-update-management-arc":
        "Write a Bicep reference to the now-onboarded Arc machine as an "
        "existing resource.",
    "day-30-final-teardown":
        "No new code - final self-test across everything built.",
}

SECTION_PATTERN = re.compile(
    r"## 1\. Objective\n.*?\n\n(?=## 2\. Steps Taken)",
    re.DOTALL,
)

split_count = 0
missing = 0

for lab_file in sorted(base_path.glob("*/day-*/lab.md")):
    day_slug = lab_file.parent.name
    lab_obj = LAB_OBJECTIVES.get(day_slug)
    bicep_obj = BICEP_OBJECTIVES.get(day_slug)

    if lab_obj is None or bicep_obj is None:
        print(f"No objectives defined for {day_slug} - skipping")
        missing += 1
        continue

    text = lab_file.read_text(encoding="utf-8")

    if not SECTION_PATTERN.search(text):
        print(f"{day_slug}: couldn't find the Objective section, skipping")
        missing += 1
        continue

    new_section = (
        "## 1. Objective\n\n"
        f"### Lab Objective (Portal)\n{lab_obj}\n\n"
        f"### Bicep Objective\n{bicep_obj}\n\n"
    )
    text = SECTION_PATTERN.sub(new_section, text, count=1)
    lab_file.write_text(text, encoding="utf-8")
    split_count += 1

# Update the reusable template too, so any future day you add follows suit
template_file = base_path / "assets" / "lab-template.md"
if template_file.exists():
    text = template_file.read_text(encoding="utf-8")
    old = "## 1. Objective\nWhat this lab builds and which AZ-104 skill it maps to.\n\n"
    new = (
        "## 1. Objective\n\n"
        "### Lab Objective (Portal)\nWhat this lab builds and which AZ-104 "
        "skill it maps to.\n\n"
        "### Bicep Objective\nWhat you're separately writing in Bicep to "
        "reproduce it.\n\n"
    )
    if old in text:
        text = text.replace(old, new)
        template_file.write_text(text, encoding="utf-8")
        print("assets/lab-template.md updated to match")

print()
print(f"Done - {split_count} lab.md files split into Lab + Bicep objectives, {missing} skipped.")