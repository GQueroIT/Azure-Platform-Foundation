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

## Service Deep Dive

### What It Can't Do
A `ReadOnly` lock is far more aggressive than its name suggests - it
doesn't just block deletes and property changes, it blocks *any*
control-plane POST request, which includes operations that look
read-only on the surface. The best-known case: a `ReadOnly` lock on a
storage account blocks the "list keys" operation entirely, because
listing keys is technically a POST. It also blocks creating new blob
containers through the control plane, and blocks new RBAC role
assignments scoped to that storage account. A `ReadOnly` lock on an App
Service blocks the Kudu console and deployments outright, and on a VM it
blocks even a restart, since restart is a POST action. None of this is a
bug - it's locks doing exactly what they're documented to do, and it's
why the almost-universal guidance is to default to `CanNotDelete` and
reach for `ReadOnly` only when you specifically mean to freeze
configuration too.

Neither lock type protects *data* inside a resource. A `CanNotDelete`
lock on a storage account stops someone from deleting the account
itself, but does nothing to stop someone from deleting the blobs or
files inside it - that's a data-plane operation, a different permission
boundary entirely.

Budgets, as this lesson's Core Concepts section already says, don't cap
spend - and there's a second gap worth knowing: actual cost data feeding
a budget can lag real spend by several hours, so a budget alert is a
same-day warning, not a same-minute one.

### Nuances Worth Knowing
- **Locks inherit downward and the most restrictive one wins.** A
  `ReadOnly` lock at the resource group level overrides a resource that
  has no lock of its own, or even one with a less restrictive
  `CanNotDelete` lock directly on it.
- **A `CanNotDelete` lock at the resource-group level can quietly break
  autoscale-in behavior** for anything that scales by deleting instances
  (like an Azure ML compute cluster), because scaling in requires
  deleting the instances being removed - a real, documented interaction,
  not an edge case.
- **Removing a lock is instant and low-risk.** A lock is a lightweight
  resource with essentially one meaningful property (`level`), so taking
  one off to make an emergency change and reapplying it afterward is a
  normal, safe operation, not something to be nervous about.

### Troubleshooting You'll Actually Hit
- **Symptom:** can't retrieve a storage account's access keys even as the
  account owner -> **Cause:** a `ReadOnly` lock is applied somewhere in
  the resource's scope chain (on the account itself or an ancestor
  resource group) -> **Fix:** locate and remove the lock
  (`az lock list --resource-group <rg>`), retrieve the keys, then decide
  whether `ReadOnly` was really the intended lock level - `CanNotDelete`
  is usually what people actually meant.
- **Symptom:** a VM won't restart, or an App Service deployment silently
  fails with a permissions-flavored error, despite the account clearly
  having Owner/Contributor -> **Cause:** RBAC isn't the blocker - a lock
  is, since locks apply on top of RBAC regardless of role -> **Fix:**
  check for locks specifically (`az lock list`), not just role
  assignments, whenever a should-have-permission action fails.
- **Symptom:** a budget alert email never arrives even though spend is
  well past the threshold -> **Cause:** cost data has a real reporting
  lag (up to several hours) before it's reflected against the budget ->
  **Fix:** treat budget alerts as a same-day signal, not real-time, and
  don't rely on them for anything that needs a faster reaction than that.

*Checked against: Microsoft Learn's "Lock your Azure resources" doc and
its storage-account-specific lock article.*


## Source
<https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/quick-create-budget-bicep>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.consumption/budgets>

## Why This Matters (Business Context)
A junior engineer runs a cleanup script against the wrong resource group and deletes a production database at 2am. A lock doesn't prevent honest mistakes from happening, it prevents them from being one click away. Budgets solve the more common failure: nobody notices a forgotten test environment running until the bill arrives, sometimes 10x over what anyone expected.
