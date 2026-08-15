# Day 03 Lesson - Resource Locks and Budgets

## Core Concepts (Read This First)

### Locks Override RBAC - On Purpose
This is the detail that trips people up: a resource lock isn't a
permission, it's a hard stop that applies regardless of what RBAC role
someone holds. Even the Subscription Owner can't delete a
`CanNotDelete`-locked resource without first removing the lock. That's
the entire point - a lock protects against the exact scenario where
someone technically has full permission and still shouldn't act, like the
2am production-database scenario below. Locks inherit downward too: a
lock on a resource group applies to everything inside it, even resources
that don't have their own lock.

### Budgets Don't Stop Spending
A common assumption worth correcting early: an Azure budget is not a
spending cap. Nothing about a `Microsoft.Consumption/budgets` resource
stops a VM from running or blocks a deployment once you cross the
threshold - it only fires a notification. If you actually want spend to
trigger an automated response (like shutting something down), that
requires wiring the budget's alert to an Action Group and further
automation yourself; it doesn't happen by default. Treat the budget in
this lesson as a smoke alarm, not a circuit breaker - it tells you
something's on fire, it doesn't put the fire out.

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

## Why This Matters (Business Context)
A junior engineer runs a cleanup script against the wrong resource group and deletes a production database at 2am. A lock doesn't prevent honest mistakes from happening, it prevents them from being one click away. Budgets solve the more common failure: nobody notices a forgotten test environment running until the bill arrives, sometimes 10x over what anyone expected.
