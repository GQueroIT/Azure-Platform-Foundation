# Day 01 Lesson - RBAC and Management Groups (Terraform)

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
