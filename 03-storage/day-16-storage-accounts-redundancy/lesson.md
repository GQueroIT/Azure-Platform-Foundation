# Day 16 Lesson - Storage Accounts and Redundancy

## Core Concepts (Read This First)

### What a Storage Account Actually Is
One storage account is a namespace that can hold up to four distinct
kinds of storage: **Blob** (object storage - files, images, backups,
addressed by name, not organized like a traditional filesystem), **Files**
(SMB/NFS network shares - behaves like a real network drive), **Queue**
(simple message queuing between application components), and **Table**
(NoSQL key-value storage). Redundancy and most account-wide settings
apply to the whole account regardless of which of these you're using;
individual blobs can still override some settings (like access tier) on
their own.

### Access Tier and Redundancy Are Two Separate Dials
Easy to conflate, genuinely different things. **Redundancy** (LRS / ZRS /
GRS) is about durability - how many copies exist and where. **Access
tier** (Hot / Cool / Cold / Archive) is about the tradeoff between
storage cost and retrieval cost - Hot costs more to store but nothing
extra to read; Archive costs almost nothing to store but is expensive
and slow to read back (see Day 17's note on rehydration time). You choose
a redundancy level and an access tier independently - a GRS account can
still have individual blobs sitting in the Cool or Archive tier.

## What You're Building Today
A storage account, testing different redundancy configurations.

## New Bicep Concepts
- `sku.name` encodes BOTH performance tier and redundancy in one string
  (e.g. `Standard_LRS`, `Standard_GRS`)
- `kind` vs `sku` - two properties that both affect what the account can do

## Annotated Example
```bicep
param storageSku string = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: 'stg${uniqueString(resourceGroup().id)}'
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: {
    name: storageSku
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}
```

## Why It's Written This Way
- `sku.name` values follow a pattern: `<Tier>_<Redundancy>`. `Standard_LRS`
  is locally redundant (cheapest, 3 copies in one datacenter),
  `Standard_ZRS` spreads across availability zones in one region,
  `Standard_GRS` replicates to a second region entirely (most expensive,
  most durable). For a lab-scale build, `LRS` is the right default -
  `GRS` roughly doubles the storage cost for redundancy you don't need at
  this scale.
- `kind: 'StorageV2'` is the modern, recommended kind for basically every
  new storage account - the older `Storage` and `BlobStorage` kinds exist
  mostly for legacy compatibility.
- `allowBlobPublicAccess: false` is a security default worth setting
  explicitly rather than relying on whatever the platform default happens
  to be - it blocks anonymous public read access at the account level.

## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts>

## Why This Matters (Business Context)
A regional outage takes out a datacenter, and a company running LRS-only storage loses access to its data until that datacenter recovers. GRS costs more for a reason - it's the difference between a bad afternoon and a real disaster, and part of the job is knowing which workloads are worth paying for that on.
