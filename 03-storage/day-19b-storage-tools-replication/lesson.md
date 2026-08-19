# Day 19b Lesson - Storage Explorer, AzCopy, Object Replication, and Blob Versioning

## Core Concepts (Read This First)

### Storage Explorer and AzCopy Solve Different Problems
**Storage Explorer** is a GUI (desktop app or the in-portal version) for
browsing, uploading, and managing blobs, files, queues, and tables
interactively - the visual tool for "let me look at what's actually in
this account." **AzCopy** is a command-line tool built specifically for
moving large amounts of data fast, with resumable, parallelized transfers
- the tool for "migrate a few hundred GB from on-prem into this
account," not something you'd reach for to check one file's metadata.
Both are named explicitly in the exam objective as the tools for this
job - neither is optional to at least recognize by name and use case.

### Object Replication Needs Two Other Features Turned On First
Object replication (copying blobs from one account to another,
asynchronously, as they change) isn't a standalone switch - it requires
**blob versioning** enabled on both the source and destination accounts,
and **change feed** enabled specifically on the source. Skip either
prerequisite and the replication policy can't be created at all, not
just created and silently non-functional.

## What You're Building Today
Blob versioning and change feed enabled on a source account, and an
object replication policy copying a container's blobs to a second
account.

## New Bicep Concepts
- `isVersioningEnabled` and `changeFeed.enabled` as properties on the
  storage account's blob service, not the account itself
- `Microsoft.Storage/storageAccounts/objectReplicationPolicies` -
  deployed on the *destination* account, referencing the source by ID

## Annotated Example
```bicep
resource sourceBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: sourceStorageAccount
  properties: {
    isVersioningEnabled: true
    changeFeed: { enabled: true }
  }
}

resource destBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: destStorageAccount
  properties: {
    isVersioningEnabled: true
  }
}

resource replicationPolicy 'Microsoft.Storage/storageAccounts/objectReplicationPolicies@2023-01-01' = {
  name: destStorageAccount.name
  parent: destStorageAccount
  properties: {
    sourceAccount: sourceStorageAccount.name
    destinationAccount: destStorageAccount.name
    rules: [
      {
        sourceContainer: 'source-container'
        destinationContainer: 'dest-container'
      }
    ]
  }
  dependsOn: [ sourceBlobService, destBlobService ]
}
```

## Why It's Written This Way
- Both `blobServices` resources have to deploy and take effect before the
  replication policy - `dependsOn` makes that explicit, since the
  policy's creation genuinely fails if versioning isn't already active on
  both sides.
- The replication policy resource is named after the *destination*
  account and deployed as its child, even though it describes a
  relationship spanning two accounts - a real, slightly unintuitive
  Azure API design choice worth remembering rather than re-deriving each
  time.
- Change feed is enabled only on the source in this example, matching
  the actual requirement - the destination doesn't need it, only
  versioning.

## Service Deep Dive

### What It Can't Do
Object replication only works between General Purpose v2 or Premium
block blob accounts - both source and destination have to match one of
those types, and it only replicates block blobs, not append or page
blobs. It isn't supported on accounts with a hierarchical namespace
enabled (Data Lake Storage Gen2) at all. And once an account has an
active replication policy, blob versioning can't be disabled on it
without first deleting the replication policy - the dependency runs both
directions.

AzCopy and Storage Explorer aren't backup tools by design - copying data
with AzCopy doesn't preserve point-in-time recovery the way a real backup
policy would, and neither tool replaces the Backup/lifecycle features
from earlier storage days.

### Nuances Worth Knowing
- Object replication is one-way per policy - replicating in both
  directions between two accounts needs two separate policies, one per
  direction, and mixing that up carelessly can create replication loops.
- Deletions replicate too, not just new/changed blobs - a blob deleted at
  the source disappears at the destination as well, which matters if the
  destination was meant to be an independent, delete-resistant copy;
  pairing replication with soft delete at the destination is the real
  safety net there, not the replication policy alone.
- Replication is asynchronous and has a measurable, documented SLA
  (99% of objects replicated within 15 minutes for same-continent
  source/destination pairs under Priority Replication) rather than being
  instantaneous - a design assuming near-real-time consistency between
  the two accounts will be wrong by design, not by bug.
- Configuring an object replication policy requires at least Contributor
  scoped to the storage account (or higher) - a real, specific
  permission requirement beyond generic storage access.

### Troubleshooting You'll Actually Hit
- **Error:** creating an object replication policy fails outright ->
  **Cause:** blob versioning isn't enabled on both accounts, or change
  feed isn't enabled on the source - the three prerequisites (versioning
  x2, change feed x1) genuinely block policy creation, not just
  functionality -> **Fix:** enable versioning on both accounts and
  change feed on the source first, then create the policy.
- **Error:** trying to disable blob versioning on an account fails or is
  rejected -> **Cause:** an active object replication policy still
  depends on it -> **Fix:** delete the replication policy first, then
  disable versioning if that's genuinely still the goal.
- **Symptom:** a blob deleted at the source also disappeared from what
  was assumed to be an independent destination copy -> **Cause:**
  replication propagates deletes by design, it isn't a one-way backup ->
  **Fix:** enable soft delete (or immutability) at the destination
  account specifically if the goal is protection against accidental
  deletion, since replication alone won't provide that.

*Checked against: Microsoft Learn's "Object replication overview" and
"Configure object replication" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/storage/blobs/object-replication-overview>
<https://learn.microsoft.com/en-us/azure/storage/blobs/object-replication-configure>
<https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10>

## Why This Matters (Business Context)
A company needs a read-optimized copy of its blob data in a second region so users there don't pay cross-region latency on every request - object replication keeps that copy current automatically instead of someone running a manual sync job. AzCopy is the tool that actually moves the terabytes of existing data there in the first place, since dragging files through a browser upload doesn't scale past a folder or two.
