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

## Service Deep Dive

### What It Can't Do
Not every redundancy conversion is a one-step toggle, despite the portal
presenting them all as a dropdown. Direct GZRS -> LRS, GRS -> ZRS, and
ZRS -> GRS conversions aren't supported at all - each requires a staged,
two-step conversion through an intermediate SKU, with a mandatory
72-hour wait enforced between the two steps to let background
replication catch up. A storage account with boot diagnostics enabled
for a VM can't convert to ZRS or GZRS at all until boot diagnostics is
disabled first - and once disabled to allow the conversion, it can't be
re-enabled afterward without further changes. An account holding blobs
in the Archive tier can't move to a zone-redundant option either -
Archive isn't supported there, so those blobs have to be rehydrated to
Hot or Cool first, which is itself slow and can be genuinely costly.

### Nuances Worth Knowing
- Redundancy conversions don't cause downtime or data loss for most
  account types - access continues normally during the switch. The one
  documented exception: accounts with a hierarchical namespace enabled
  (Data Lake Storage Gen2) can see a brief pause, under 30 seconds,
  while the account switches over.
- Enabling geo-redundancy (moving to GRS/GZRS) triggers a one-time
  egress charge to replicate existing data to the secondary region - a
  real, billed event, not a free background sync.
- Failing a GRS account over to its secondary region during a real
  outage doesn't preserve geo-redundancy afterward - the account becomes
  LRS in the new primary region, and it specifically can't convert
  straight back to ZRS or GZRS from that state; getting zone-redundancy
  back requires a manual migration, not just flipping the setting again.
- Storage account names are globally unique across all of Azure, not
  just your subscription - lowercase letters and numbers only, 3-24
  characters. That's exactly why this lesson's Bicep uses
  `uniqueString(resourceGroup().id)` rather than a fixed name - a fixed
  name has a real chance of colliding with someone else's account
  somewhere in the world.

### Troubleshooting You'll Actually Hit
- **Error:** converting an account's redundancy fails outright with an
  unsupported-conversion error -> **Cause:** the specific direction
  attempted (GZRS->LRS, GRS->ZRS, or ZRS->GRS) isn't a supported direct
  conversion -> **Fix:** check Microsoft's redundancy conversion matrix
  for the actual supported path - almost always a two-step conversion
  with a mandatory 72-hour wait between steps.
- **Error:** `StorageAccountTypeNotSupported` when starting a VM, or a
  redundancy conversion silently fails -> **Cause:** boot diagnostics is
  enabled on a VM using this storage account, which blocks
  zone-redundant conversions entirely -> **Fix:** disable boot
  diagnostics on the account first if the conversion needs to go through.
- **Error:** deployment fails with a storage account name conflict even
  though it looks unique -> **Cause:** storage account names are
  globally unique across every Azure customer, not just your own
  subscription -> **Fix:** use `uniqueString()` or another
  guaranteed-unique naming pattern instead of a fixed, guessable name.

*Checked against: Microsoft Learn's "Change how a storage account is
replicated" and "Storage redundancy change FAQs" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts>

## Why This Matters (Business Context)
A regional outage takes out a datacenter, and a company running LRS-only storage loses access to its data until that datacenter recovers. GRS costs more for a reason - it's the difference between a bad afternoon and a real disaster, and part of the job is knowing which workloads are worth paying for that on.
