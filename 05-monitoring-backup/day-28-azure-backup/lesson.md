# Day 28 Lesson - Azure Backup

## What You're Building Today
A Recovery Services vault, a backup policy, and backing up the VM from
Week 1-2.

## New Bicep Concepts
- Three-level resource nesting: vault, then policy, then protected item
- A protected item's name is a slash-separated path encoding fabric and
  container, not a simple name

## Annotated Example
```bicep
resource vault 'Microsoft.RecoveryServices/vaults@2023-04-01' = {
  name: 'rsv-lab'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: {}
}

resource backupPolicy 'Microsoft.RecoveryServices/vaults/backupPolicies@2023-04-01' = {
  name: 'daily-vm-policy'
  parent: vault
  properties: {
    backupManagementType: 'AzureIaasVM'
    schedulePolicy: {
      schedulePolicyType: 'SimpleSchedulePolicy'
      scheduleRunFrequency: 'Daily'
      scheduleRunTimes: [ '2026-08-10T23:00:00Z' ]
    }
    retentionPolicy: {
      retentionPolicyType: 'LongTermRetentionPolicy'
      dailySchedule: {
        retentionTimes: [ '2026-08-10T23:00:00Z' ]
        retentionDuration: {
          count: 7
          durationType: 'Days'
        }
      }
    }
  }
}

resource protectedVm 'Microsoft.RecoveryServices/vaults/backupFabrics/protectionContainers/protectedItems@2023-04-01' = {
  name: '${vault.name}/Azure/iaasvmcontainer;iaasvmcontainerv2;${resourceGroup().name};vm-web-01/vm;iaasvmcontainerv2;${resourceGroup().name};vm-web-01'
  properties: {
    protectedItemType: 'Microsoft.Compute/virtualMachines'
    policyId: backupPolicy.id
    sourceResourceId: vm.id
  }
}
```

## Why It's Written This Way
- The vault and policy follow the same `parent:` pattern you've seen all
  build - straightforward. The protected item is the odd one out: its
  `name` has to encode the backup fabric (`Azure`), the protection
  container (a generated string tied to the VM), and the protected item
  itself, all in one slash-and-semicolon-separated string. This is a
  known rough edge in the Recovery Services API - you're not missing
  something simpler, this genuinely is the required format.
- `scheduleRunTimes` takes a full timestamp even though only the TIME
  portion (23:00:00Z) actually matters for a daily recurring schedule -
  the date part is effectively ignored by the platform after the first
  run.
- `retentionDuration.count: 7` with `durationType: 'Days'` keeps 7 daily
  recovery points before the oldest ages out - reasonable for a lab,
  production policies often keep weekly/monthly/yearly points layered on
  top of this.

## Service Deep Dive

### What It Can't Do
A Recovery Services vault can't be deleted while it still contains
protected items, registered containers, or - critically - anything in a
soft-deleted state, and it can't skip that soft-delete waiting period
even on demand. Soft-deleted backup items are retained for 14 days
before Azure permanently removes them, and in regions where "secure by
default" is enforced, that soft-delete behavior can't even be disabled
through the portal to speed things up. For a repo built around tearing
down resource groups on a regular cadence, this is a direct conflict:
deleting the resource group containing this vault fails if the vault has
anything in a soft-deleted state, and there's no force-delete override -
waiting out the 14 days is the only guaranteed path if soft delete can't
be disabled first.

The vault also can't be removed by deleting its resource group in one
clean sweep the way most other resources in this repo can - the resource
group deletion fails with the same underlying vault error, so the vault
needs cleaning up (backup items stopped/deleted, soft delete disabled if
the region allows it) before the resource group deletion will succeed.

### Nuances Worth Knowing
- Stopping backup on a protected item is a choice between two
  meaningfully different options: "stop protection and retain data"
  (keeps existing recovery points, no new backups run) versus "stop
  protection and delete data" (existing recovery points go into the
  soft-deleted state, starting the 14-day clock). Picking the wrong one
  for a lab teardown is exactly what leaves items sitting in soft-delete
  purgatory blocking vault deletion later.
- If soft delete genuinely can't be disabled (secure-by-default
  regions), the only way to finish deleting a vault sooner than 14 days
  is: undelete the soft-deleted items first, then delete them again
  immediately - which, counterintuitively, is what actually triggers a
  real permanent delete rather than waiting for the timer.
- A vault itself can be soft-deleted too, not just the items inside it -
  deleting a vault (once its contents are clean) can land it in its own
  soft-deleted, recoverable state first, viewable and restorable from a
  separate "Manage Deleted Vaults" view before its own permanent purge.

### Troubleshooting You'll Actually Hit
- **Error:** deleting the resource group fails, and drilling in shows
  "Vault cannot be deleted as there are existing resources within the
  vault" -> **Cause:** the vault still has registered backup items,
  containers, or soft-deleted data -> **Fix:** stop protection (choosing
  delete data, not retain, for a clean teardown) on every backup item
  first, then delete the vault separately before retrying the resource
  group delete.
- **Error:** vault deletion fails with "there are backup items in soft
  deleted state" even after all visible items are gone -> **Cause:**
  items already deleted are sitting in the mandatory 14-day soft-delete
  retention window -> **Fix:** if the region allows disabling soft
  delete, do that, then undelete and immediately re-delete the
  soft-deleted items to force a real permanent delete; if soft delete
  can't be disabled for that vault/region, there's genuinely no faster
  path than waiting.
- **Symptom:** soft delete won't disable, citing the vault being set to
  "Always On" -> **Cause:** secure-by-default enforcement in that
  region/vault configuration locks soft delete on permanently ->
  **Fix:** accept the 14-day wait for that vault; worth knowing before
  building a habit of nightly resource group deletion around it.

*Checked against: Microsoft Learn's "Delete a Microsoft Azure Recovery
Services Vault," "Configure and manage soft delete for Azure Backup,"
and "FAQ - soft delete in Azure Backup" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.recoveryservices/vaults/backuppolicies>
<https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep>

## Why This Matters (Business Context)
A ransomware attack encrypts a company's production database, and their only backup is a manual export someone meant to automate eighteen months ago. Azure Backup with a real retention policy is what makes 'restore from last night' an actual option instead of a hope.
