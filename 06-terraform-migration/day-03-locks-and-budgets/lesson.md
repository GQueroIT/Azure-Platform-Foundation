# Day 03 Lesson - Locks and Budgets (Terraform)

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
