# Day 03 Lesson - Resource Locks and Budgets

## What You're Building Today
A resource lock and a subscription budget alert, in Bicep. This is also
your cost-control safety net for the rest of the build.

## New Bicep Concepts
- `Microsoft.Authorization/locks` - a resource type with almost no
  properties, just a lock level
- `notifications` as an object with dynamic keys (not an array)

## Annotated Example
```bicep
resource doNotDeleteLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: 'do-not-delete-rg'
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects the resource group while the AZ-104 build is active'
  }
}

param contactEmails array
param budgetAmount int = 50

resource monthlyBudget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'az104-monthly-budget'
  properties: {
    category: 'Cost'
    amount: budgetAmount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: '2026-08-01T00:00:00Z'
    }
    notifications: {
      Actual_GreaterThan_80_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: contactEmails
      }
    }
  }
}
```

## Why It's Written This Way
- `level: 'CanNotDelete'` still allows editing, just blocks deletion.
  `'ReadOnly'` is the stricter option and would break almost everything
  you're doing this build, since it also blocks writes.
- The budget's `notifications` block is an object, not an array, and each
  key (`Actual_GreaterThan_80_Percent` here) is just a label you choose -
  Azure doesn't care what you name it, but the convention of naming it
  after what it does makes the file self-documenting.
- `threshold: 80` is a percentage of `amount`, not a dollar figure. At
  `amount: 50` and `threshold: 80`, this fires once actual spend crosses
  $40.

## Source
<https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/quick-create-budget-bicep>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.consumption/budgets>