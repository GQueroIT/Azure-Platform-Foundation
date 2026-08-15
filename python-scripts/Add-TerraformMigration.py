#!/usr/bin/env python3
"""
Add-TerraformMigration.py

Scaffolds the 06-terraform-migration/ track onto Azure-Platform-Foundation,
mirroring the existing Bicep day-by-day structure so the two tracks stay
easy to navigate side by side.

USAGE
    Run this from the ROOT of your azure-platform-foundation repo:

        python Add-TerraformMigration.py

    Safe to re-run: it never overwrites a file that already exists, so it
    won't clobber any work you've already done. Root files (.gitignore,
    README.md, PROGRESS.md) are only appended to, and only if the new
    section isn't already there.

WHAT IT CREATES
    06-terraform-migration/
        README.md
        day-00-terraform-fundamentals/lesson.md          (read only, no lab)
        day-01-rbac-and-management-groups/{lesson.md,lab.md,main.tf}
        day-02-azure-policy/{lesson.md,lab.md,main.tf}
        day-03-locks-and-budgets/{lesson.md,lab.md,main.tf}

    Plus appends to root .gitignore, README.md, and PROGRESS.md.

SEQUENCING RULE (worth remembering, not just enforcing in code)
    Don't start a Terraform day here until the matching Bicep day in
    01-compute-governance is fully checked off in PROGRESS.md. One new
    variable at a time -- either the Azure concept or the tool syntax,
    never both together.
"""

from pathlib import Path

REPO_ROOT = Path.cwd()
TF_ROOT = REPO_ROOT / "06-terraform-migration"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        print(f"  skip (already exists): {path.relative_to(REPO_ROOT)}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  created: {path.relative_to(REPO_ROOT)}")
    return True


def append_if_missing(path: Path, marker: str, content: str) -> None:
    """Append content to an existing root file, only if the marker isn't already there."""
    if not path.exists():
        print(f"  WARNING: {path.name} not found at repo root -- skipping, add it manually")
        return
    existing = path.read_text(encoding="utf-8")
    if marker in existing:
        print(f"  skip (already present): {path.name}")
        return
    with path.open("a", encoding="utf-8") as f:
        f.write(content)
    print(f"  updated: {path.name}")


# ---------------------------------------------------------------------------
# Day 00 -- Terraform Fundamentals (read only, no lab, like Bicep's Day 00)
# ---------------------------------------------------------------------------

DAY00_LESSON = '''# Day 00 Lesson - Terraform Fundamentals

Read this before Day 01. Every later lesson in this track assumes you know
what's here. You already know Bicep, so this lesson leans on that constantly
- same ideas, different tool.

## What Terraform Actually Is
Like Bicep, Terraform is declarative: you write what you want to exist, not
the steps to create it. The difference is Bicep only ever talks to Azure and
compiles down to ARM JSON behind the scenes. Terraform talks to *any* cloud
through a plugin system called providers, and it keeps its own record of
what it created in a separate file called state. That one difference -
Terraform tracking its own state instead of relying on Azure Resource
Manager as the source of truth - is the biggest conceptual shift from
Bicep, and it's where most real Terraform pain (and most interview
questions about Terraform) comes from.

## Install and Authenticate
Install Terraform from HashiCorp directly, and use the Azure CLI you
already installed for the Bicep track.

For local learning, the simplest auth path is the one you already use for
Bicep:
```bash
az login
```
Terraform's azurerm provider can read your Azure CLI session directly - no
extra setup needed for solo learning.

HashiCorp's own get-started tutorial instead sets up a Service Principal
with explicit environment variables (ARM_CLIENT_ID, ARM_CLIENT_SECRET,
ARM_SUBSCRIPTION_ID, ARM_TENANT_ID). You don't need that yet - az login is
enough for everything in this track. You WILL need the Service Principal
method later, once this gets wired into GitHub Actions, because a CI
pipeline can't open a browser to log you in interactively.

## The Building Blocks
Every Terraform configuration is built from some combination of these:
```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-day00-example"
  location = "eastus"
}

variable "environment" {
  type    = string
  default = "dev"
}

output "resource_group_id" {
  value = azurerm_resource_group.rg.id
}
```
- **terraform block** - settings for Terraform itself, including which
  providers to download. Bicep has no equivalent - it doesn't need to
  "download" Azure support, because Bicep only ever targets Azure.
- **provider block** - configures a specific provider (azurerm here).
  Roughly equivalent to nothing in Bicep - Bicep is implicitly always
  talking to Azure.
- **resource block** - an actual thing getting created:
  `resource "<type>" "<your-name-for-it>" { ... }`. This is the direct
  equivalent of Bicep's resource keyword, just written the other way
  around (type first, then your name, instead of your name first).
- **variable block** - the Terraform equivalent of Bicep's param.
- **output block** - the same idea as Bicep's output, values handed back
  after apply.

## Reading a Resource Block
```hcl
resource "azurerm_storage_account" "storage" {
  name                     = "stday00001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```
- `azurerm_storage_account` - the resource type. Every azurerm resource
  type maps to something in the Azure Resource Manager API, same as a
  Bicep resource type string - it's just named differently and doesn't
  carry an explicit API version in the block itself (the provider version
  in the terraform block controls that under the hood).
- `"storage"` - your symbolic name for this resource inside this
  configuration, same role as Bicep's symbolic resource name.
- Everything inside `{ }` - the resource's arguments. What's required
  varies by resource type, same as Bicep.
- Notice `azurerm_resource_group.rg.name` - referencing another resource's
  attribute directly. This is how Terraform tracks dependencies between
  resources automatically, without you writing dependsOn the way you
  sometimes have to in Bicep.

## The Workflow
This is your new daily loop, and it maps directly onto the Bicep loop you
already know:

| Step             | Bicep                            | Terraform            |
|------------------|-----------------------------------|-----------------------|
| Download tooling | not needed                        | `terraform init`      |
| Check syntax     | `az bicep build`                  | `terraform validate`  |
| Preview changes  | `az deployment group what-if`     | `terraform plan`      |
| Deploy           | `az deployment group create`      | `terraform apply`     |
| Tear down        | manual delete / `az group delete` | `terraform destroy`   |

`terraform init` downloads the provider plugins your terraform block asked
for and sets up the local working directory. Run it once per new
configuration, and again any time you add a new provider or module.

`terraform plan` is the one to slow down and actually read every time, not
just skim. It shows exactly what will be created, changed, or destroyed
before anything happens - same spirit as what-if, but Terraform *requires*
you to see and approve a plan before apply runs, where Bicep's what-if is
something you have to remember to run yourself.

## State
When you run `terraform apply`, Terraform writes what it created into a
file called `terraform.tfstate` in your working directory. This file is
how Terraform knows what it's responsible for - if you delete something in
the Azure Portal by hand, Terraform's state doesn't know that happened,
and the next plan will show a mismatch (this is called "drift," and it's a
real thing you'll hit).

Two things to get right immediately, because they matter for the rest of
your career with this tool, not just this lesson:
- **Never commit terraform.tfstate to git.** It can contain resource
  properties and sometimes secrets in plaintext. This setup script already
  added it to your .gitignore.
- **State is local by default**, meaning it only exists on your machine.
  Real teams store it remotely (in an Azure Storage Account, typically) so
  more than one person - or a CI pipeline - can safely run Terraform
  against the same infrastructure. You'll set this up later in this
  track's remote-state day; for now, local state is fine.

## Why This Matters (Business Context)
Bicep only works if a team is 100% Azure. The moment a company runs
multi-cloud, or even just wants one tool that manages Azure resources
*and* a GitHub team's repo settings *and* a monitoring dashboard, Bicep
can't do that - Terraform can, through the same provider system you just
saw. That's the entire reason Terraform shows up in Platform/IaaS job
postings as often as Bicep does: it's the one IaC skill that isn't locked
to a single vendor, so it's the one hiring managers can be confident
transfers to whatever the company runs next.

## Source
<https://developer.hashicorp.com/terraform/tutorials/azure-get-started>
<https://developer.hashicorp.com/terraform/tutorials/azure-get-started/azure-build>
<https://developer.hashicorp.com/terraform/language>
'''


# ---------------------------------------------------------------------------
# Day 01 -- RBAC and Management Groups
# ---------------------------------------------------------------------------

DAY01_LESSON = '''# Day 01 Lesson - RBAC and Management Groups (Terraform)

Read this after Day 00. This is the Terraform version of the same
objective you already completed in Bicep - you already understand *what*
a management group hierarchy and RBAC assignment are, so this lesson is
purely about the HCL syntax.

## Lab Objective
Reproduce, in Terraform, whatever you built in
`01-compute-governance/day-01-rbac-and-management-groups/solution.bicep`:
a role assignment scoped to a resource.

## A Real Constraint Worth Knowing About
Creating management groups requires access at the tenant root, which most
personal or free Azure subscriptions don't have. If your Bicep version of
this lab was also done at resource-group scope for the same reason,
you're in good company - real engineers hit this same limitation on
personal sandbox subscriptions constantly, which is exactly why
interviewers ask about RBAC scoped at the resource or resource-group level
far more than they ask about management-group hierarchies. Build what you
have access to; it's the more commonly-tested skill anyway.

## Role Assignment in Terraform
```hcl
data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "example" {
  name     = "rg-day01-terraform"
  location = "eastus"
}

resource "azurerm_role_assignment" "reader" {
  scope                = azurerm_resource_group.example.id
  role_definition_name = "Reader"
  principal_id          = data.azurerm_client_config.current.object_id
}
```
- **`data "azurerm_client_config"`** - a data source, not a resource. Data
  sources read existing information instead of creating something new.
  This one reads details about whoever is currently authenticated (you,
  via az login) so you can reference your own object ID without hardcoding
  it. Bicep has no exact equivalent keyword, but you already saw the same
  *idea* in the `existing` keyword from Bicep's Day 00 lesson - reading
  something that's already there instead of creating it.
- **`role_definition_name`** - a built-in Azure role like "Reader",
  "Contributor", or "Owner". For a custom role (less common, more
  advanced), create an azurerm_role_definition resource first and
  reference its ID here instead.
- **`scope`** - what the role applies to. Here it's a resource group, but
  it can be a subscription, a management group, or a single resource,
  exactly like in the portal or in Bicep.

## Custom Role Definition (if you want to go further)
```hcl
resource "azurerm_role_definition" "custom" {
  name        = "Custom VM Operator"
  scope       = azurerm_resource_group.example.id
  description = "Can start and restart VMs, nothing else."

  permissions {
    actions = [
      "Microsoft.Compute/virtualMachines/start/action",
      "Microsoft.Compute/virtualMachines/restart/action",
    ]
    not_actions = []
  }

  assignable_scopes = [
    azurerm_resource_group.example.id,
  ]
}
```
This is the direct equivalent of whatever custom roleDefinitions resource
you wrote in Bicep for this same day.

## Why This Matters (Business Context)
Overly broad RBAC is the single most common real finding in a cloud
security review - someone gets Contributor on a whole subscription because
it was faster than scoping a custom role properly, and eighteen months
later nobody remembers why, or notices, until a pen test flags it. Being
able to write the tightly-scoped version in Terraform, not just click
through it once in the portal, is what turns "I understand least
privilege" from an interview answer into something you can actually prove
with a repo link.

## Source
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment>
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition>
'''

DAY01_LAB = '''# Day 01 - RBAC and Management Groups (Terraform)

## 1. Objective

### Reference (Bicep version)
Link back to `../../01-compute-governance/day-01-rbac-and-management-groups/lab.md`
- what did that version actually build?

### Terraform Objective
Write Terraform that reproduces the same role assignment using
azurerm_role_assignment (and azurerm_role_definition if you built a
custom role in the Bicep version).

## 2. Steps Taken
What you ran, in order (init, validate, plan, apply).

## 3. Configuration
The final main.tf you wrote. Paste it here or link to the file in this
folder.

## 4. Verification
How you confirmed it actually deployed correctly (terraform show, portal
check, az cli query, etc).

## 5. Issues & Fixes
Anything that broke, the error message, and what fixed it. This section
is worth more than it looks - it's what you'll actually remember, and
it's the strongest part of any video you make about this.

## 6. Key Takeaways
2-3 sentences: what did this teach you about Terraform specifically, not
just about the Azure concept you already knew from Bicep?

## Cost Note
What ran, for how long, and confirmation `terraform destroy` was run
before closing the session.
'''

DAY01_MAIN_TF = "# day-01-rbac-and-management-groups - your Terraform code goes here\n"


# ---------------------------------------------------------------------------
# Day 02 -- Azure Policy
# ---------------------------------------------------------------------------

DAY02_LESSON = '''# Day 02 Lesson - Azure Policy (Terraform)

Read this after Day 01. Same objective as your Bicep Day 02 lab - enforce
something with Azure Policy - now in Terraform.

## Lab Objective
Reproduce your Bicep Day 02 policy assignment in Terraform: a policy that
requires a specific tag on new resources, assigned at resource-group
scope.

## Policy Definition and Assignment
Azure Policy in Terraform is two resources working together, same as it
is in Bicep: a definition (the rule) and an assignment (where the rule
applies).
```hcl
resource "azurerm_resource_group" "example" {
  name     = "rg-day02-terraform"
  location = "eastus"
}

resource "azurerm_policy_definition" "require_tag" {
  name         = "require-costcenter-tag"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Require a CostCenter tag"

  policy_rule = jsonencode({
    if = {
      field  = "tags['CostCenter']"
      exists = "false"
    }
    then = {
      effect = "deny"
    }
  })
}

resource "azurerm_resource_group_policy_assignment" "require_tag" {
  name                 = "require-costcenter-tag-assignment"
  resource_group_id    = azurerm_resource_group.example.id
  policy_definition_id = azurerm_policy_definition.require_tag.id
}
```
- **`policy_rule`** - this is genuinely just JSON, wrapped in Terraform's
  jsonencode() function. Azure Policy rules are JSON everywhere, including
  in Bicep and the Portal - Terraform doesn't change that, it just needs
  jsonencode() to embed a JSON object inside an HCL file cleanly.
- **`azurerm_resource_group_policy_assignment`** - notice the resource
  type names the scope directly (resource_group_policy_assignment vs.
  subscription_policy_assignment vs. management_group_policy_assignment).
  Bicep instead uses one generic Microsoft.Authorization/policyAssignments
  type and controls scope through where in the file you deploy it. Small
  syntax difference, same underlying Azure concept.

## Why This Matters (Business Context)
This is the exact policy pattern behind the "tags enforced at deploy time,
not after" idea from your landing-zone project - a policy set to deny
stops an untagged resource from being created at all, instead of relying
on someone remembering to tag it manually. Enforced at write-time like
this, cost attribution actually holds up instead of degrading the moment
someone's in a hurry.

## Source
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition>
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group_policy_assignment>
'''

DAY02_LAB = '''# Day 02 - Azure Policy (Terraform)

## 1. Objective

### Reference (Bicep version)
Link back to `../../01-compute-governance/day-02-azure-policy/lab.md` -
what did that version enforce?

### Terraform Objective
Write Terraform that reproduces the same policy using
azurerm_policy_definition and azurerm_resource_group_policy_assignment.

## 2. Steps Taken
What you ran, in order (init, validate, plan, apply).

## 3. Configuration
The final main.tf you wrote. Paste it here or link to the file in this
folder.

## 4. Verification
Prove the policy actually blocks what it's supposed to - try creating an
untagged resource on purpose and show it gets denied. This is your best
screenshot/video moment for this day.

## 5. Issues & Fixes
Anything that broke, the error message, and what fixed it.

## 6. Key Takeaways
2-3 sentences: what did this teach you about Terraform specifically?

## Cost Note
What ran, for how long, and confirmation `terraform destroy` was run
before closing the session.
'''

DAY02_MAIN_TF = "# day-02-azure-policy - your Terraform code goes here\n"


# ---------------------------------------------------------------------------
# Day 03 -- Locks and Budgets
# ---------------------------------------------------------------------------

DAY03_LESSON = '''# Day 03 Lesson - Locks and Budgets (Terraform)

Read this after Day 02. Same objective as your Bicep Day 03 lab, now in
Terraform: a resource lock and a budget with an alert.

## Lab Objective
Reproduce your Bicep Day 03 lab: prevent accidental deletion with a lock,
and set a budget with a notification threshold.

## Resource Lock
```hcl
resource "azurerm_management_lock" "no_delete" {
  name       = "prevent-delete"
  scope      = azurerm_resource_group.example.id
  lock_level = "CanNotDelete"
  notes      = "Locked to prevent accidental deletion during learning."
}
```
lock_level takes one of two values: CanNotDelete (can still edit, can't
delete) or ReadOnly (can't edit or delete anything). Same two options
Bicep gives you, same underlying Azure resource lock feature.

## Budget with an Alert
```hcl
resource "azurerm_consumption_budget_resource_group" "monthly" {
  name              = "day03-monthly-budget"
  resource_group_id = azurerm_resource_group.example.id

  amount     = 20
  time_grain = "Monthly"

  time_period {
    start_date = "2026-08-01T00:00:00Z"
  }

  notification {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThan"
    contact_emails = ["you@example.com"]
  }
}
```
- **amount / time_grain** - the budget ceiling and how often it resets,
  same fields you set in the portal or in Bicep.
- **notification** - fires when spend crosses threshold percent of
  amount. You can define multiple notification blocks for multiple
  thresholds (50%, 80%, 100%, for example) - real FinOps setups almost
  always use more than one.

## Before You Close the Laptop
Run terraform destroy on this lab like every other day in this track.
Unlike your Bicep labs, forgetting this one doesn't just risk leftover
cost - it also leaves state pointing at real resources that a later plan
will trip over if you come back to this folder weeks later and forget
what's live.

## Why This Matters (Business Context)
This pair - a lock plus a budget alert - is the minimum viable governance
setup that shows up in nearly every Platform/IaaS job posting's list of
responsibilities: stop someone from deleting something critical by
accident, and get told before a bill becomes a surprise instead of after.
Neither one is complicated to build. The fact that most environments
still don't have both is exactly why it's worth having on a resume.

## Source
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_lock>
<https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/consumption_budget_resource_group>
'''

DAY03_LAB = '''# Day 03 - Locks and Budgets (Terraform)

## 1. Objective

### Reference (Bicep version)
Link back to `../../01-compute-governance/day-03-locks-and-budgets/lab.md`.

### Terraform Objective
Write Terraform that reproduces the same lock and budget using
azurerm_management_lock and azurerm_consumption_budget_resource_group.

## 2. Steps Taken
What you ran, in order (init, validate, plan, apply).

## 3. Configuration
The final main.tf you wrote. Paste it here or link to the file in this
folder.

## 4. Verification
Try to delete the locked resource on purpose and confirm Azure blocks it.
Confirm the budget shows up correctly in Cost Management in the portal.

## 5. Issues & Fixes
Anything that broke, the error message, and what fixed it.

## 6. Key Takeaways
2-3 sentences: what did this teach you about Terraform specifically?

## Cost Note
What ran, for how long, and confirmation `terraform destroy` was run
before closing the session -- this is the last day of the module, so also
confirm nothing at all is left running in this resource group.
'''

DAY03_MAIN_TF = "# day-03-locks-and-budgets - your Terraform code goes here\n"


# ---------------------------------------------------------------------------
# Folder index README
# ---------------------------------------------------------------------------

TF_FOLDER_README = '''# Terraform Migration Track

Terraform rebuild of the objectives already completed in Bicep under
01-compute-governance. This track exists to prove tool-agnostic
understanding, not to re-learn Azure concepts you already know.

**Rule:** don't start a day here until the matching Bicep day is fully
checked off in the root PROGRESS.md. One new variable at a time.

- day-00-terraform-fundamentals - read first, no lab
- day-01-rbac-and-management-groups
- day-02-azure-policy
- day-03-locks-and-budgets

Each day's lesson.md leans directly on the Bicep version of the same
objective and calls out what's actually different about Terraform, rather
than re-explaining the Azure concept from scratch.
'''


# ---------------------------------------------------------------------------
# Root file additions
# ---------------------------------------------------------------------------

GITIGNORE_ADDITIONS = '''
# --- Terraform (added by Add-TerraformMigration.py) ---
**/.terraform/
*.tfstate
*.tfstate.backup
*.tfvars
!*.tfvars.example
crash.log
override.tf
override.tf.json
'''

README_ADDITION = '''

## Terraform Migration Track (06-terraform-migration)

A second pass through the compute-governance objectives, rebuilt in
Terraform instead of Bicep. Same Azure concepts, different tool -- the
point is proving the underlying understanding transfers, not re-learning
RBAC or Azure Policy from zero.

**Sequencing rule:** don't start a Terraform day until the matching Bicep
day above is fully checked off. See `06-terraform-migration/README.md`
for the day-by-day breakdown and the reasoning behind the rule.
'''

PROGRESS_ADDITION = '''

## Terraform Migration Track
Start each day here only after the matching Bicep day above is checked
off. Not part of the AZ-104 definition of done -- this is the
differentiator track, not the exam-prep track.

- [ ] Day 00 - Terraform Fundamentals (read only, no lab)
- [ ] Day 01 - RBAC and Management Groups in Terraform
- [ ] Day 02 - Azure Policy in Terraform
- [ ] Day 03 - Locks and Budgets in Terraform
- [ ] At least one lesson written up as a "Bicep vs Terraform" post/video
'''


def main() -> None:
    print(f"Adding Terraform migration track to: {REPO_ROOT}\n")

    print("Day 00 (fundamentals, read only):")
    write_if_missing(TF_ROOT / "day-00-terraform-fundamentals" / "lesson.md", DAY00_LESSON)

    print("\nDay 01 (RBAC and management groups):")
    write_if_missing(TF_ROOT / "day-01-rbac-and-management-groups" / "lesson.md", DAY01_LESSON)
    write_if_missing(TF_ROOT / "day-01-rbac-and-management-groups" / "lab.md", DAY01_LAB)
    write_if_missing(TF_ROOT / "day-01-rbac-and-management-groups" / "main.tf", DAY01_MAIN_TF)

    print("\nDay 02 (Azure Policy):")
    write_if_missing(TF_ROOT / "day-02-azure-policy" / "lesson.md", DAY02_LESSON)
    write_if_missing(TF_ROOT / "day-02-azure-policy" / "lab.md", DAY02_LAB)
    write_if_missing(TF_ROOT / "day-02-azure-policy" / "main.tf", DAY02_MAIN_TF)

    print("\nDay 03 (locks and budgets):")
    write_if_missing(TF_ROOT / "day-03-locks-and-budgets" / "lesson.md", DAY03_LESSON)
    write_if_missing(TF_ROOT / "day-03-locks-and-budgets" / "lab.md", DAY03_LAB)
    write_if_missing(TF_ROOT / "day-03-locks-and-budgets" / "main.tf", DAY03_MAIN_TF)

    print("\nFolder index:")
    write_if_missing(TF_ROOT / "README.md", TF_FOLDER_README)

    print("\nRoot files:")
    append_if_missing(REPO_ROOT / ".gitignore", "Add-TerraformMigration.py", GITIGNORE_ADDITIONS)
    append_if_missing(REPO_ROOT / "README.md", "## Terraform Migration Track", README_ADDITION)
    append_if_missing(REPO_ROOT / "PROGRESS.md", "## Terraform Migration Track", PROGRESS_ADDITION)

    print("\nDone.")
    print("Start with: 06-terraform-migration/day-00-terraform-fundamentals/lesson.md")
    print("Remember the rule: don't open Day 01 here until Bicep Day 01-03 are checked off.")


if __name__ == "__main__":
    main()