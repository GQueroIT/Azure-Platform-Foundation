# Day 02 Lesson - Azure Policy (Terraform)

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
