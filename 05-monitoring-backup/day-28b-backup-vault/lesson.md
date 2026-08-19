# Day 28b Lesson - Backup Vault (Distinct From Recovery Services Vault)

## Core Concepts (Read This First)

### Two Different Vault Resource Types, on Purpose
Day 28 built a **Recovery Services vault**
(`Microsoft.RecoveryServices/vaults`) - the original, broad vault
covering Azure VMs, Azure Files, SQL on VM, SAP HANA, and (as part of the
same underlying service) Azure Site Recovery. **Backup vault**
(`Microsoft.DataProtection/backupVaults`) is a newer, separate resource
type introduced for workloads Azure Backup added more recently - Azure
managed disks, Blob Storage, and Azure Database for PostgreSQL. Neither
replaces the other; a real environment commonly uses both side by side,
picking the vault type based on which workload is being protected.

### Operational vs Vaulted Backup
Backup vault workloads split into two backup styles with genuinely
different mechanics. **Operational backup** (what disk and blob backup
through Backup vault actually are) works via snapshots and change
tracking - fast, and billed only for the incremental storage delta, but
data isn't transferred into long-term vault storage the way Recovery
Services vault backups are. **Vaulted backup** (a newer option, also
available for some Backup-vault workloads) does move data into
durable vault storage for longer retention, closer in spirit to how
Recovery Services vault has always worked.

## What You're Building Today
A Backup vault with a blob storage backup policy protecting a storage
account.

## New Bicep Concepts
- `Microsoft.DataProtection/backupVaults` - a completely separate
  resource namespace from `Microsoft.RecoveryServices`
- Managed identity required on the vault for it to actually perform
  backup/restore operations against the protected resource

## Annotated Example
```bicep
resource backupVault 'Microsoft.DataProtection/backupVaults@2023-05-01' = {
  name: 'bv-lab'
  location: resourceGroup().location
  identity: { type: 'SystemAssigned' }
  properties: {
    storageSettings: [
      {
        datastoreType: 'VaultStore'
        type: 'LocallyRedundant'
      }
    ]
  }
}

resource backupPolicy 'Microsoft.DataProtection/backupVaults/backupPolicies@2023-05-01' = {
  name: 'blob-backup-policy'
  parent: backupVault
  properties: {
    objectType: 'BackupPolicy'
    datasourceTypes: [ 'Microsoft.Storage/storageAccounts/blobServices' ]
  }
}
```

## Why It's Written This Way
- `identity: { type: 'SystemAssigned' }` is required, not optional - the
  vault performs backup/restore by acting *as* that managed identity
  against the storage account, which needs its own explicit RBAC role
  assignment on the storage account (a separate deployment step, not
  shown here) before backups actually work.
- `datastoreType: 'VaultStore'` picks the durable, long-term-retention
  storage style rather than the pure snapshot-only operational path -
  worth deliberately choosing based on the actual retention requirement,
  not defaulting blindly.
- This resource lives under `Microsoft.DataProtection`, a completely
  different provider namespace than Day 28's `Microsoft.RecoveryServices`
  - a real signal that these are architecturally separate services under
  the hood, not variations of the same one.

## Service Deep Dive

### What It Can't Do
Backup vault doesn't do full, application-consistent VM backups the way
Recovery Services vault does - disk backup through Backup vault is
crash-consistent snapshots of OS and data disks, not the same guarantee
as a proper VM-level backup. It also doesn't support Azure Site Recovery
at all - ASR lives exclusively under Recovery Services vault; there's no
Backup-vault equivalent. Disk backup specifically caps at 200 total
snapshots per disk and 180 snapshots per backup policy - a real,
retention-limiting ceiling: hourly backups (24/day) cap out around 7
days of retention purely from the snapshot count limit, not a
configuration choice.

### Nuances Worth Knowing
- Restoring from a disk backup through Backup vault can only create a
  *new* disk - there's no "replace the existing disk in place" restore
  option the way some other backup tools offer.
- On-demand backups and restores through Backup vault are meaningfully
  faster than the equivalent Recovery Services vault operations for VM
  backups, precisely because operational backup works at the snapshot
  layer rather than transferring data into vault storage first.
- The vault's managed identity needing its own RBAC role assignment on
  the protected resource is a real, separate step that's easy to
  forget - a vault and policy can both deploy successfully and backups
  still fail if that role assignment was never added, and the resulting
  error can take up to 30 minutes to reflect after the role assignment
  is finally corrected.
- Blob backup is itself a form of operational backup that doesn't "store"
  data inside the vault in the traditional sense, even though the vault
  resource is still required to manage and orchestrate the backup/restore
  operations.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Backup vault and policy both deploy successfully, but
  backup jobs fail immediately -> **Cause:** the vault's managed identity
  was never granted the RBAC role it needs on the target resource
  (storage account or disk) -> **Fix:** assign the required role (varies
  by datasource type, documented per workload) to the vault's system-
  assigned identity, scoped to the resource being protected, and allow
  up to 30 minutes for the role assignment to actually take effect.
- **Symptom:** disk backup retention can't be extended as far as
  expected for a frequent backup schedule -> **Cause:** the 200-snapshot-
  per-disk / 180-per-policy ceiling limits how much history hourly or
  even daily backups can actually hold -> **Fix:** reduce backup
  frequency if longer retention matters more than granularity, since the
  snapshot count cap doesn't flex based on how the schedule is
  configured.
- **Symptom:** someone expects to configure Site Recovery from inside a
  Backup vault and can't find the option -> **Cause:** Site Recovery is
  exclusively a Recovery Services vault capability -> **Fix:** use the
  Recovery Services vault from Day 28 for anything involving Site
  Recovery; Backup vault has no equivalent.

*Checked against: Microsoft Learn's "Configure and manage backup for
Azure Blobs" doc and community documentation comparing Recovery Services
vault and Backup vault.*

## Source
<https://learn.microsoft.com/en-us/azure/backup/blob-backup-configure-manage>
<https://learn.microsoft.com/en-us/azure/backup/backup-managed-disks>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.dataprotection/backupvaults>

## Why This Matters (Business Context)
A team accidentally deletes a batch of blobs from a storage account backing a customer-facing app, and without operational backup through a Backup vault, that data is gone the moment soft delete's retention window passes. Knowing there are two different vault types - and which one actually protects which workload - is the difference between assuming something is backed up and it actually being backed up.
