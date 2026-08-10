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

## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.recoveryservices/vaults/backuppolicies>
<https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep>

## Why This Matters (Business Context)
A ransomware attack encrypts a company's production database, and their only backup is a manual export someone meant to automate eighteen months ago. Azure Backup with a real retention policy is what makes 'restore from last night' an actual option instead of a hope.
