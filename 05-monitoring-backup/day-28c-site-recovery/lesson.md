# Day 28c Lesson - Azure Site Recovery and Failover

## Straight Talk First
Site Recovery's actual replication configuration - enabling protection on
a specific VM, mapping its network/storage to the target region - spans
several interdependent Recovery Services vault sub-resources
(replication fabrics, protection containers, replication policies,
protected items) that are genuinely awkward to hand-write in Bicep and
are overwhelmingly configured through the Portal, PowerShell, or the
Site Recovery-specific CLI extension in real practice. This lesson builds
the vault itself in Bicep (the same pattern as Day 28's Recovery Services
vault) and documents the rest as a Portal/PowerShell workflow, the same
honest approach Day 23 took with Conditional Access.

## Core Concepts (Read This First)

### Replication, Failover, and Reprotection Are Three Different Steps
Enabling replication doesn't fail anything over by itself - it just
starts continuously copying the VM's disk changes to the target region,
building up recovery points over time. **Failover** is the separate,
deliberate action of actually bringing up a VM in the target region from
those recovery points. **Reprotection** is the step after a failover
that starts replicating the now-running target-region VM back toward the
original region, so a future failback is possible - without
reprotection, failover is one-way with no easy path home.

### Recovery Point Choice Matters at Failover Time
Failover isn't "just use whatever's most recent" by default - Site
Recovery offers several recovery point options (Latest, Latest processed,
Latest multi-VM processed, and app-consistent variants for VMs in a
replication group), and they trade off recency against consistency
guarantees. "Latest" gives the lowest possible data loss but pulls
directly from whatever's been sent, which stops being an option the
moment the source region itself goes down mid-transfer - at that point
"Latest processed" (the newest recovery point Site Recovery had already
fully processed before the outage) is what's actually available.

## What You're Building Today
The Recovery Services vault Site Recovery will use (same resource type as
Day 28's backup vault, now serving a second purpose), plus a documented,
Portal-driven walkthrough of enabling Azure-to-Azure replication and
running a test failover.

## New Bicep Concepts
- Nothing new at the resource-type level - Site Recovery reuses Day 28's
  `Microsoft.RecoveryServices/vaults`, since the same vault type serves
  both Backup and Site Recovery
- Recognizing when a task is intentionally left as a documented manual
  workflow rather than forced into Bicep for its own sake

## Annotated Example
```bicep
resource vault 'Microsoft.RecoveryServices/vaults@2023-04-01' = {
  name: 'rsv-dr-lab'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: {}
}
```

The actual Azure-to-Azure replication setup, done through the Portal:
1. In the vault, go to Site Recovery > Enable Replication.
2. Select the source VM and the target region.
3. Choose (or accept default) target resource group, VNet, and storage.
4. Set a replication policy (recovery point retention window, app-
   consistent snapshot frequency).
5. Once initial replication finishes, run **Test Failover** into an
   isolated test network - this is the safe, non-disruptive way to
   validate the setup without touching production traffic.

## Why It's Written This Way
- The vault itself is trivial Bicep - identical in shape to Day 28's,
  since it's literally the same resource type. Everything that makes
  Site Recovery specifically complicated (fabric mapping, replication
  policies tied to specific regions and networks) sits one layer above
  what's realistic to template generically for a lab this size.
- Test Failover exists specifically so failover can be validated without
  affecting the real, currently-running production VM - it spins up an
  isolated copy for testing, then tears it down, leaving actual
  production replication untouched throughout.

## Service Deep Dive

### What It Can't Do
Site Recovery has hard, documented churn limits per disk based on disk
size - a disk generating more data-change traffic than its size supports
triggers a specific "Data change rate beyond supported limits" event, and
the practical fix is a bigger disk (which comes with a higher churn
allowance), not a setting to raise the limit directly. It also can't
create an application-consistent recovery point for a Storage Spaces
Direct configuration - a documented, named gap with no direct fix, only
a workaround using custom pre/post scripts for Linux app-consistency
where applicable.

### Nuances Worth Knowing
- A recovery plan (grouping multiple VMs for coordinated failover)
  requires every VM in it to have at least one recovery point before a
  planned failover can run - a VM with zero recovery points blocks the
  whole plan, not just itself.
- Recovery points created before a Tier/SKU change on the source
  eventually become invalid for failover - triggering a failover against
  one of those specifically fails with a `BookmarkNotFound` error, and
  because pruning old recovery points is a background job, a stale,
  now-unusable recovery point can still visibly appear in the portal for
  a while after the change that invalidated it.
- Failing over shuts down the source VM (when reachable) specifically to
  minimize data loss - Site Recovery waits for pending writes to flush to
  disk before the failover proceeds, which is exactly why "Latest" (the
  lowest possible RPO option) depends on the source being reachable long
  enough for that shutdown to happen cleanly.
- After a failover, reprotection is a separate, explicit action - nothing
  automatically starts replicating the new production VM back toward the
  original region on its own.

### Troubleshooting You'll Actually Hit
- **Error:** an event fires reporting the data change rate on a disk
  exceeds Site Recovery's supported limits -> **Cause:** the disk's churn
  (rate of data change) is higher than its current size supports -
  smaller disks have proportionally lower churn allowances -> **Fix:**
  check Replicated items > VM > Events for the specific disk and its
  actual churn number, then increase that disk's size to raise its
  supported churn ceiling.
- **Error:** a failover attempt fails with `BookmarkNotFound` -> **Cause:**
  the selected recovery point predates a Tier/SKU change on the source
  and is no longer valid, even though it may still be visibly listed ->
  **Fix:** select a recovery point created after the Tier/SKU change, or
  wait for the automatic pruning job to clear the stale one from the
  list.
- **Symptom:** a planned failover for a recovery plan won't run at all
  -> **Cause:** at least one VM in the plan has zero recovery points ->
  **Fix:** confirm every VM in the recovery plan has at least one valid
  recovery point before attempting the planned (not disaster/unplanned)
  failover path, which specifically requires it.

*Checked against: Microsoft Learn's "Troubleshoot replication of Azure
VMs with Azure Site Recovery" and "About failover and failback in Azure
Site Recovery" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/site-recovery/azure-to-azure-troubleshoot-replication>
<https://learn.microsoft.com/en-us/azure/site-recovery/site-recovery-failover>
<https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep>

## Why This Matters (Business Context)
A regional Azure outage takes down the datacenter hosting a company's production VMs, and without Site Recovery already configured and tested, "fail over to another region" is a multi-day scramble instead of a rehearsed, minutes-long process. Test Failover exists precisely so that rehearsal happens on a random Tuesday afternoon, not for the first time during the actual outage.
