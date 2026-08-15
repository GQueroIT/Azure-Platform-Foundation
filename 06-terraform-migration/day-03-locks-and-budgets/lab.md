# Day 03 - Locks and Budgets (Terraform)

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
