#!/usr/bin/env python3
"""
Adds a "## Service Deep Dive" section to each lesson.md - what the service
actually can't do, nuances that aren't obvious from the Bicep syntax alone,
and troubleshooting patterns (symptom -> cause -> fix) you're likely to hit
building it. This is the layer the original lessons were missing: they teach
the Bicep, this teaches the service underneath the Bicep.

Every fact in DEEP_DIVES below was checked against Microsoft Learn or
Microsoft's own GitHub docs repos before being written, not pulled from
memory alone - see the inline source note at the end of each day's entry
for what to go re-read if you want the primary source.

WHERE THIS SCRIPT LIVES: one folder below the repo root (python-scripts/),
matching every other script in this toolchain. If you move it, fix
base_path below - it needs to point at the folder that directly contains
01-compute-governance, 02-networking, etc.

Content gets added to DEEP_DIVES in phases as each day is researched - the
script itself doesn't change, just the dictionary. Running it only touches
days that have an entry below; every other lesson.md is left alone and
reported as "no deep dive content yet." Safe to re-run any time a new day
is added - it skips anything that already has the section.

Progress: Days 00-06 (01-compute-governance) and Day 13
(load-balancer-appgw, 02-networking) done. Remaining days get added the
same way.

Consolidation/self-test/teardown days (09, 10, 20, 25, 30) are intentionally
never given an entry here - there's no new service on those days, just a
review pass, so there's nothing to deep-dive.
"""

from pathlib import Path

# One level up from this script's own folder (python-scripts/) to the repo root.
base_path = Path(__file__).resolve().parent.parent

HEADER = "## Service Deep Dive"

DEEP_DIVES = {

    "day-00-bicep-fundamentals": '''### What It Can't Do
Bicep only talks to Azure Resource Manager. It has no concept of on-prem
infrastructure, other clouds, or anything outside the ARM control plane -
if a resource type doesn't have an ARM provider, Bicep can't touch it,
full stop. It also has no real nested loops: `[for item in collection: {...}]`
works one level deep on a resource, module, variable, or output, but you
cannot put a second `[for]` directly inside that block's properties. The
common workaround is pushing the inner loop into its own module and
looping over the module call instead, or using the built-in `map()`
function to flatten the transformation before you loop.

Bicep also doesn't track state the way some other IaC tools do. There's no
local state file - Azure Resource Manager itself is the source of truth
for what exists. That sounds convenient (nothing to lose or corrupt
locally), but it also means Bicep has no built-in way to show you "here's
what's drifted since I last deployed this" outside of `what-if`, and no
local record you can inspect offline.

### Nuances Worth Knowing
- **Deployment mode matters more than it looks.** `az deployment group create`
  defaults to **Incremental** mode - it only adds or updates what's in the
  template and leaves everything else in the resource group alone. There's
  also a **Complete** mode that deletes anything in the resource group
  *not* declared in the template. Nobody in this repo needs Complete mode,
  but it's worth knowing it exists so you never accidentally reach for it.
- **`@secure()` on outputs is a relatively recent addition** (Bicep v0.35+).
  Before that, any output value - even one built from a `@secure()`
  parameter - was written to deployment history in plain text and visible
  to anyone who could read the deployment. If you're ever on an older
  Bicep CLI version, never output anything secret; wire secrets through
  directly instead.
- **Two separate 800-limits exist and they're easy to confuse.** One is a
  hard cap of 800 stored deployment *records* per resource group - once
  hit, no new deployment can run until you clear old history (deleting
  history doesn't touch the actual deployed resources). The other is a cap
  of 800 total *resources* per single deployment template - and
  validation counts every iteration of a loop toward that total, including
  branches that would evaluate to `false` under an `if`. On a repo like
  this one, where you tear down and redeploy the same resource group
  nightly, the deployment-history cap is the one you'll actually hit first.
- The deployment job itself has a 1MB size limit after compression -
  rarely an issue at this scale, but worth knowing if a template balloons
  with large inline parameter arrays.

### Troubleshooting You'll Actually Hit
- **Error:** `The provided value for the template parameter 'adminPassword'
  is not valid. Expected a value of type 'String, Uri', but received a
  value of type 'Object'` -> **Cause:** a `@secure()` property nested
  inside a custom object type, passed through a tool (like a PowerShell
  cmdlet) that doesn't handle nested secure values correctly ->
  **Fix:** keep secure values as top-level string/object parameters
  instead of nesting them inside a custom `type`.
- **Error:** `The current deployment count is '800'. Please delete some
  deployments before creating a new one` -> **Cause:** deployment history
  for the resource group hit its cap from repeated redeploys ->
  **Fix:** `az deployment group list -g <rg> --query "[].name" -o tsv` to
  see what's stored, then delete the oldest ones with
  `az deployment group delete` - this has zero effect on the resources
  that are actually running.
- **Symptom:** validation fails with something like `The template
  resource '...' at line X is not valid` when you try to write a loop
  inside a loop -> **Cause:** genuine nested `[for]` loops aren't
  supported -> **Fix:** extract the inner loop into its own module, and
  call that module from inside the outer loop.

*Checked against: Microsoft Learn's Bicep deployment modes and template
limits docs, and the Azure/bicep GitHub issue tracker for the nested-loop
and secure-output behavior.*''',

    "day-01-rbac-and-management-groups": '''### What It Can't Do
RBAC is purely additive - there's no "deny" the way an NSG rule can deny
traffic. If a principal has Contributor from one assignment and a
tightly-scoped custom role from another, they get the *union* of both;
the custom role's `notActions` only carves exceptions out of that same
role's own `actions`, it can't strip a permission granted by a completely
separate assignment. The one real exception is a **deny assignment**, a
separate ARM construct that explicitly blocks specific actions regardless
of role - but you don't hand-write these day to day; they mostly show up
generated by Azure Blueprints or managed applications.

Role assignment changes also aren't instant. Azure's control plane can
take several minutes to propagate a new or removed assignment everywhere
it needs to - if you grant yourself a role and immediately get a 403
testing it, that's often propagation delay, not a broken assignment.

Management groups can't represent every org shape either: each management
group or subscription has exactly one direct parent, so there's no way to
model a subscription that logically belongs under two different branches
at once.

### Nuances Worth Knowing
- **Hard, unraisable limits exist and real organizations hit them.** 4,000
  role assignments per subscription (counting subscription-, resource-
  group-, and resource-scoped assignments together, not management-group
  ones), 500 per management group, and 5,000 custom role definitions per
  tenant. None of these can be increased by a support ticket - the
  documented fix is always "assign to groups instead of individual
  principals" and "consolidate duplicate custom roles."
- **`principalType` isn't decorative.** Feeding a role assignment the
  wrong `principalType` (labeling a group as `'User'`, for instance) is a
  common way for an assignment to silently not behave as expected,
  especially right after creating a brand-new group or service principal,
  since Azure's directory lookup can lag a few seconds behind the object
  actually existing.
- **A `CanNotDelete` lock on a resource group doesn't override RBAC, it
  sits on top of it** - even a Subscription Owner can't delete a locked
  resource until the lock itself is removed. Day 03 covers this in full.

### Troubleshooting You'll Actually Hit
- **Error:** `RoleAssignmentLimitExceeded` (`No more role assignments can
  be created`) -> **Cause:** hit the 4,000-per-subscription (or
  500-per-management-group) cap -> **Fix:** find principals with
  duplicate individual assignments and consolidate them into a
  group-based assignment instead - Azure Resource Graph has a documented
  query pattern for finding these.
- **Symptom:** a role assignment against a brand-new Entra group or
  freshly created managed identity fails with a "principal not found"
  style error even though the object clearly exists in the portal ->
  **Cause:** Entra directory replication lag - the object exists but
  hasn't fully propagated to the identity lookup RBAC uses ->
  **Fix:** retry after a short wait, or (in scripts) add a brief
  delay/retry loop between creating the principal and assigning the role.
- **Symptom:** a permission you just granted still returns a 403 ->
  **Cause:** RBAC propagation delay, typically resolves within a few
  minutes -> **Fix:** wait and retest before assuming the assignment
  itself is wrong; check the assignment's scope and `principalId` only if
  it's still failing after several minutes.

*Checked against: Microsoft Learn's "Troubleshoot Azure RBAC limits" and
"Azure custom roles" docs for the exact limit numbers.*''',

    "day-02-azure-policy": '''### What It Can't Do
Policy can't retroactively fix anything by itself. A `Deny` effect blocks
non-compliant resources at creation time, but existing resources that were
compliant when created and later drift (or existed before the policy was
assigned) just sit there marked non-compliant - Policy doesn't reach out
and fix them. `DeployIfNotExists` and `Modify` effects *can* fix existing
resources, but only through an explicitly triggered **remediation task**;
nothing runs automatically against your existing environment just because
you assigned a policy.

Those same `DeployIfNotExists` and `Modify` effects also can't function
without a managed identity attached to the policy assignment - that
identity is what actually performs the remediation deployment, separate
from whatever evaluates the policy's compliance logic in the first place.
Forget to give the assignment an identity (or the identity the right RBAC
role), and remediation tasks fail even though the policy itself looks
correctly assigned.

Policy also isn't real-time for existing resources: Azure re-evaluates
compliance across everything already deployed roughly every 24 hours,
plus whenever you edit the assignment. Don't expect the compliance
dashboard to reflect a change the moment it happens.

### Nuances Worth Knowing
- **`DeployIfNotExists` has a configurable evaluation delay, defaulting to
  10 minutes.** Immediately after a resource is created, Policy waits
  that long before checking whether the required companion resource
  exists and deploying it if not. Checking compliance one minute after
  creating a resource and seeing "non-compliant, nothing happened yet" is
  expected, not broken.
- **Remediation only ever touches existing resources, once.** If a
  remediation task fixes a resource and someone later reverts the change
  back to non-compliant, the policy will flag it non-compliant again on
  the next evaluation cycle, but it will not automatically re-remediate -
  you have to run another remediation task.
- **`Deny` and `Audit` are what you'll use almost constantly**; `Append`,
  `Modify`, and `DeployIfNotExists` are the ones that quietly change or
  add something without you doing anything, which is exactly why they
  need their own identity and permissions.

### Troubleshooting You'll Actually Hit
- **Symptom:** a `DeployIfNotExists` policy assignment shows resources as
  non-compliant, but nothing ever gets deployed for them ->
  **Cause:** the assignment has no managed identity, or the identity
  exists but lacks the RBAC role the policy definition requires ->
  **Fix:** `az policy assignment show --name <name> --query identity` to
  confirm an identity exists, then check that identity has been granted
  the role the policy definition specifies it needs.
- **Symptom:** existing resources from before the policy was assigned
  stay non-compliant indefinitely -> **Cause:** `DeployIfNotExists`/
  `Modify` never auto-remediate pre-existing resources -> **Fix:**
  manually trigger a remediation task against the policy assignment; it's
  a separate step from assigning the policy itself.
- **Symptom:** compliance dashboard doesn't reflect a change made minutes
  ago -> **Cause:** compliance re-evaluation on existing resources runs
  on roughly a 24-hour cycle, not continuously -> **Fix:** trust
  `az deployment group what-if` and deployment-time enforcement for
  anything time-sensitive; treat the dashboard as eventually-consistent,
  not live.

*Checked against: Microsoft Learn's "deployIfNotExists effect" and
"Remediate non-compliant resources" docs.*''',

    "day-03-locks-and-budgets": '''### What It Can't Do
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
its storage-account-specific lock article.*''',

    "day-04-vm-availability-zones": '''### What It Can't Do
You can't move a running VM between availability zones - zone placement
is set at creation and is immutable; changing it means deleting and
recreating the VM (and anything stateful on it) from scratch. Not every
VM size is available in every zone of a given region either - a size can
be available in zones 1 and 2 of a region but not zone 3, so a
"spread across all zones" design has to be checked against actual
size-availability for that region, not assumed.

Zone numbers are also logical to your own subscription, not physical -
"zone 1" in your subscription is not guaranteed to map to the same
physical datacenter as "zone 1" in a different subscription, even in the
same region. Don't assume cross-subscription zone alignment means
anything.

Availability Zones themselves depend on the region actually having
multiple physically independent datacenters - plenty of Azure regions
don't support zones at all, and a Bicep deployment that assumes zone
support in an unsupported region fails outright rather than silently
falling back to non-zonal placement.

### Nuances Worth Knowing
- **VM resize can force a restart, or worse, a full deallocation,
  depending on availability.** Resizing a running VM to a size available
  on its current hardware cluster just restarts it; resizing to a size
  that isn't available there requires deallocating first, since Azure has
  to move the VM to different hardware. Either way, resizing a running VM
  should be treated as disruptive, not free.
- **Disk-tier boundaries interact with zone and VM-size choices** -
  Premium SSD requires certain VM series (the ones with an "s" in the
  size name, like `Standard_B2s` vs `Standard_B2`) to actually get
  premium performance; picking a non-"s" size with a Premium disk
  attached doesn't error, it just silently caps you at the lower-tier
  disk's throughput characteristics.
- **The `zones` array takes strings, not integers** - `zones: [ '1' ]`,
  not `zones: [ 1 ]`. This is a genuinely common first mistake, and
  Bicep won't always catch it clearly at compile time depending on how
  it's used.

### Troubleshooting You'll Actually Hit
- **Error:** deployment fails with something like `SkuNotAvailable` or a
  zone-related allocation failure for a VM size you know exists in that
  region -> **Cause:** that specific size isn't available in the
  specific zone you pinned -> **Fix:** check size availability per zone
  with `az vm list-skus --location <region> --zone --output table`
  before committing to a zone in the template, not after.
- **Symptom:** resizing a running VM hangs or fails, and the VM ends up
  stuck between states -> **Cause:** the target size isn't available on
  the current hardware cluster and requires deallocation first, which
  wasn't done -> **Fix:** deallocate the VM explicitly
  (`az vm deallocate`), then resize, then start it back up.
- **Symptom:** a VM attached to a Premium SSD performs like it's on
  Standard storage -> **Cause:** the VM size doesn't support Premium
  storage (missing the "s" in the size family) -> **Fix:** confirm the
  size supports premium storage before attaching a premium disk; check
  `az vm list-skus` for the `PremiumIO` capability on that size.

*Checked against: Microsoft Learn's "Resize a virtual machine" doc and
Azure VM SKU/zone availability guidance.*''',

    "day-05-vm-scale-sets": '''### What It Can't Do
Orchestration mode is a one-way door - once a scale set is created as
Uniform or Flexible, it cannot be converted in place; changing your mind
means recreating the scale set entirely. Uniform mode, despite being the
older and still-default-if-unset mode, genuinely can't do several things
Flexible can: individual instances aren't compatible with standard VM
APIs, Azure Resource Manager tagging, RBAC scoped to the instance, Azure
Backup, or Azure Site Recovery - they're only reachable through the
scale-set-specific API surface. Flexible mode fixes all of that by making
each instance a real, standalone VM resource under the hood, which is
exactly why Microsoft now recommends Flexible for basically everything
new.

A scale set with `capacity: 3` also doesn't scale itself - a bare VMSS
resource with no attached `Microsoft.Insights/autoscaleSettings` resource
just runs a fixed number of instances forever, identical to a fixed count
of individual VMs, until someone manually changes the number.
Autoscaling is a genuinely separate resource you have to deploy on top.

### Nuances Worth Knowing
- **VM instances that Flexible mode creates implicitly (through
  autoscaling, not manually added) don't get default outbound internet
  access** the way a manually created VM would - a documented, deliberate
  security default, not a bug, but a real source of "why can't this
  instance reach the internet" confusion the first time you hit it.
- **Both orchestration modes cap at 1,000 instances per scale set** - not
  a limit you'll come close to in this lab, but worth knowing it exists.
- **A setting called "force strictly even balance across zones" can cause
  scale-in and scale-out operations to fail outright** if Azure can't
  maintain perfectly even distribution across zones at that exact
  moment - it's off by default, but if you ever turn it on expecting
  stricter guarantees, know that it trades that guarantee for occasional
  scaling failures instead of a best-effort rebalance.

### Troubleshooting You'll Actually Hit
- **Symptom:** an instance inside a Flexible-mode scale set can't reach
  the internet or pull an update, even though the VNet/NSG look fine ->
  **Cause:** instances created implicitly through autoscaling don't get
  default outbound access the way manually-created instances do ->
  **Fix:** attach a NAT Gateway, a public IP, or an explicit outbound
  rule on a Standard Load Balancer to the subnet or scale set - don't
  assume default outbound applies here the way it does for a normal VM.
- **Symptom:** trying to switch an existing scale set's
  `orchestrationMode` in Bicep fails or gets rejected -> **Cause:**
  orchestration mode can't be changed after creation -> **Fix:** deploy a
  new scale set with the correct mode and migrate instances/traffic over;
  there's no in-place conversion.
- **Symptom:** an instance stops working and never gets automatically
  replaced -> **Cause:** automatic instance repair isn't on by default -
  it requires both a health probe/extension reporting instance health
  *and* an explicit repair policy configured on the scale set ->
  **Fix:** confirm both pieces are actually configured; having one
  without the other means nothing happens when an instance goes
  unhealthy.

*Checked against: Microsoft Learn's "Orchestration modes for Virtual
Machine Scale Sets" and the Flexible VMSS migration/networking docs.*''',

    "day-06-disks-and-extensions": '''### What It Can't Do
You can't shrink a managed disk - resize only ever goes up, and there's
no supported way back down except creating a new, smaller disk and
copying the data over yourself. OS disks can't be resized online at all;
only certain data disks support the "expand without downtime" feature,
and even that has real limits - it's not supported on Ultra Disks or
Premium SSD v2, not supported on shared disks, and crossing the 4 TiB
boundary always requires deallocating the VM first regardless of disk
type, because disks above and below that size use different underlying
storage back-ends and moving between them needs the disk detached.

A VM extension can also fail in a way that blocks the entire deployment
from reporting success, even if every other resource in the template
deployed fine - if the Custom Script Extension's script fails or times
out, the extension resource itself reports a failed provisioning state,
and that failure propagates up to the whole deployment.

### Nuances Worth Knowing
- **Resizing a disk changes the Azure-side size almost immediately, but
  the operating system inside the VM has no idea** - the OS still sees
  the old partition size until you go in and extend the
  partition/filesystem yourself. Two separate steps, easy to do the first
  and forget the second.
- **Extension version pinning matters.** `autoUpgradeMinorVersion: true`
  (used in this lesson's example) means Azure can silently apply newer
  minor versions of the extension over time - generally fine for
  something like the Custom Script Extension, but worth knowing if you
  ever need a script's exact behavior to stay frozen.
- **A detached data disk keeps its data indefinitely** - since it's an
  independent top-level resource, deleting the VM it was attached to does
  not delete the disk unless you explicitly delete the disk too (or the
  VM was created with the disk set to auto-delete on VM deletion, which
  is not the default).

### Troubleshooting You'll Actually Hit
- **Error:** the whole deployment reports as failed, but every resource
  in the portal looks like it deployed -> **Cause:** a VM extension's
  `provisioningState` came back `Failed` (usually the Custom Script
  Extension's script itself erroring or timing out), and that one failure
  fails the overall deployment -> **Fix:** check the extension's status
  directly (`az vm extension show` or the portal's "Extensions" blade on
  the VM) for its actual error output, not just the top-level deployment
  error.
- **Symptom:** a disk resize succeeds in Azure but the VM still reports
  the old, smaller size internally -> **Cause:** resizing the Azure disk
  object doesn't touch the OS partition table -> **Fix:** extend the
  partition and filesystem from inside the OS after the Azure-side resize
  completes (Disk Management on Windows, `growpart`/`resize2fs` or
  equivalent on Linux).
- **Symptom:** resizing a data disk unexpectedly requires the VM to be
  deallocated when you expected it to be online -> **Cause:** the disk is
  crossing the 4 TiB boundary, or is an Ultra Disk/Premium SSD v2/shared
  disk type that doesn't support online resize at all -> **Fix:** confirm
  which category the disk falls into before assuming online resize will
  work; plan for a deallocate/resize/reallocate window if it doesn't.

*Checked against: Microsoft Learn's "Troubleshoot Azure disk resize
failures" and "Expand virtual hard disks" docs.*''',

    "day-13-load-balancer-appgw": '''### What It Can't Do
Load Balancer has no Layer 7 awareness at all - no path-based routing, no
cookie-based session affinity (only source-IP-based), no ability to
terminate SSL or read a single byte of HTTP. It also can't do outbound
connectivity for free: a Standard Load Balancer with no outbound rule
configured, and no NAT Gateway attached to the subnet, means VMs behind
it with no public IP of their own simply have no path to the internet -
that's not a side effect, it's how Standard SKU works by design.

Application Gateway can't span regions - it's a regional resource, not a
global one, so it can't fail over to a healthy region on its own; that's
Front Door or Traffic Manager sitting in front of multiple gateways. It
also requires a dedicated subnet that nothing else can share, and v1 SKU
(still seen in older deployments and tutorials) has no autoscaling and no
zone redundancy at all - only v2 supports either.

Basic SKU Load Balancer is being retired outright, so it's not a real
option to build against going forward regardless of what older
documentation shows.

### Nuances Worth Knowing
- Outbound SNAT ports are finite and allocated per backend instance, not
  shared evenly across the whole pool by default - a Standard Load
  Balancer's automatic outbound port allocation is deliberately
  conservative and scales down as the backend pool grows, which is
  exactly why Microsoft's own guidance is to configure outbound rules
  with manual port allocation instead of relying on the default,
  especially for anything opening a lot of short-lived outbound
  connections.
- Application Gateway's backend health isn't binary. "Unknown" means the
  gateway's control plane couldn't even reach the instances or resolve
  the backend's FQDN (a network/DNS problem); "Unhealthy" means it
  reached the backend and didn't like what came back (an app/probe
  problem). Treating those as the same failure wastes real
  troubleshooting time.
- A backend can pass a manual curl test from your own machine and still
  show Unhealthy in Application Gateway - a documented real-world case
  traced this to the gateway enforcing TLS 1.2 while the backend required
  TLS 1.3, producing a 502 with nothing else pointing at TLS as the
  cause.
- The default health probe hits `/` with no other configuration - if that
  route redirects to a login page or requires auth, the probe fails and
  the backend is marked unhealthy even though the app itself is
  completely fine.

### Troubleshooting You'll Actually Hit
- **Symptom:** outbound connections start failing intermittently under
  load, with no clear error anywhere in the Azure portal ->
  **Cause:** SNAT port exhaustion on one or more backend instances ->
  **Fix:** configure outbound rules with manual port allocation instead
  of the default, and reduce short-lived one-request-per-connection
  patterns in the app itself (connection reuse/pooling) - or move the
  outbound path to a NAT Gateway entirely.
- **Error:** clients see "502 Bad Gateway" from Application Gateway ->
  **Cause:** almost always backend health showing Unhealthy or Unknown ->
  **Fix:** check the Backend Health blade first, not the frontend error;
  if it's Unknown, check NSGs/route tables between the gateway's subnet
  and the backend, and DNS resolution of the backend FQDN; if it's
  Unhealthy, check the probe's timeout, path, and expected status code
  against what the backend actually returns.
- **Symptom:** backend health shows Unhealthy despite the app responding
  fine to a direct browser or curl test -> **Cause:** frequently a TLS
  version mismatch between the gateway's minimum TLS policy and the
  backend's enforced minimum -> **Fix:** align the two, or check that the
  probe path isn't hitting a redirect/login page instead of a real health
  endpoint.

*Checked against: Microsoft Learn's "Source Network Address Translation
for outbound connections," "Troubleshoot Azure Load Balancer outbound
connectivity issues," and "Troubleshoot backend health issues in Azure
Application Gateway" docs.*''',

    "day-07-app-service": '''### What It Can't Do
F1/D1 aren't just "no custom domain" tiers - they carry hard daily quotas
that stop the app outright. Free tier gets 60 CPU minutes per day (reset
at midnight UTC), plus a rolling 5-minute CPU quota, plus bandwidth,
memory, and filesystem caps. Cross any of them and the app returns a 403
"Quota Exceeded" page for the rest of that window - a full stop, not a
slowdown. Background processes (WebJobs, health-check pings, even
platform diagnostics) burn this quota even when nobody is visiting the
site, which is exactly why a lab app with near-zero real traffic can
still hit it.

Free tier also has no Always On - idle apps unload after roughly 20
minutes, so the next request pays a cold start. Always On itself doesn't
exist below Basic tier. And SNAT limits apply here too, unrelated to CPU
quota: each App Service worker gets 128 preallocated SNAT ports for
outbound connections to the same address+port combination, and that
limit bites even on paid tiers under real load.

### Nuances Worth Knowing
- A deployment slot swap doesn't move everything, and which settings move
  is easy to get backward. Settings marked "Deployment slot setting"
  (sticky) stay with the slot and don't swap; unmarked settings swap with
  the code. Forgetting to mark a staging-only connection string as sticky
  is a real, common way for the wrong database to end up live in
  production after a swap.
- Not every setting respects stickiness even when marked - a documented
  case found `healthCheckPath` swapping despite being expected to stay
  put, so "sticky" isn't airtight for every property. "Swap with Preview"
  shows exactly what will move before it happens, rather than trusting
  the marking blindly.
- Custom domains, TLS/SSL bindings, scale settings, and Always On itself
  are always slot-specific and never swap, regardless of any setting -
  no marking required or possible.

### Troubleshooting You'll Actually Hit
- **Error:** "Quota Exceeded," app returns 403 and won't load even though
  traffic looks light -> **Cause:** F1/D1's daily or 5-minute CPU quota
  was hit, often from background processes rather than real visits ->
  **Fix:** check the App Service Plan > Quotas blade for which quota
  tripped and its reset countdown; for a lab, wait it out - for anything
  real, move off Free/Shared tier.
- **Symptom:** after a slot swap, production is suddenly pointed at the
  wrong database or config -> **Cause:** a setting that should have been
  marked sticky wasn't, so it swapped along with the code -> **Fix:**
  use "Swap with Preview" before swapping for real, and mark
  environment-specific settings (connection strings, per-slot secrets)
  as sticky consistently in both slots.
- **Symptom:** intermittent failed or slow outbound calls to the same
  external API or database under load -> **Cause:** SNAT port
  exhaustion, same root cause as Day 13's Load Balancer -> **Fix:**
  reuse/dispose HttpClient and connection objects instead of opening new
  ones per call, or route the destination through a service/private
  endpoint, which sidesteps the SNAT limit entirely.

*Checked against: Microsoft Learn's "Azure App Service quotas and
metrics," "Troubleshoot intermittent outbound connection errors," and
"Set up staging environments" docs.*''',

    "day-08-container-apps": '''### What It Can't Do
Container Apps doesn't support vertical scaling - there's no "give this
replica more CPU under load," only horizontal scale-out to more
replicas. Replica counts are also a target, not a guarantee - Container
Apps aims for what the scale rule computes, not a contractual exact
number at every instant. Dapr actors specifically can't scale to zero
even if the rest of the app's scale rule would otherwise allow it,
because actor state depends on the replica staying alive.

The Consumption plan's `minReplicas: 0` means the first request after
idle always pays a real cold start - pulling the image, provisioning,
and starting the app. And the default resource allocation when nothing
is specified (0.25 vCPU / 0.5 Gi) is genuinely too small for most
real workloads; it doesn't fail loudly, it just throttles, which looks
exactly like an app bug with no obvious log entry pointing at resource
limits.

### Nuances Worth Knowing
- Editing a scale rule doesn't update the running revision in place - it
  creates an entirely new revision. In multiple-revisions mode, the old
  one keeps running under its old rules until traffic allocation is
  managed manually.
- CPU throttling from an undersized allocation produces no error at all -
  the process just runs slower. That absence of any obvious signal is
  exactly what makes it look like a code problem instead of a sizing one.
- Java apps in particular are known for slow startup, which can trip the
  default readiness probe (the probe times out before the app is
  actually ready) and get a replica stuck restarting in a loop, even
  though it would have started fine given a few more seconds.

### Troubleshooting You'll Actually Hit
- **Symptom:** log stream shows "This revision is scaled to zero" and
  nothing appears to be running -> **Cause:** exactly what it says -
  `minReplicas` is 0 and nothing has triggered scale-out yet ->
  **Fix:** send a request to trigger scale-out, or temporarily deploy a
  revision with `minReplicas: 1` while actively debugging so logs
  actually populate.
- **Symptom:** a revision cycles between Running and Degraded, with
  cryptic exit codes or nothing useful in the logs -> **Cause:** almost
  always one of three things: the process crashes on startup (bad
  config/missing secret), the readiness/liveness probe fails because the
  app takes too long to start, or the app is listening on the wrong port
  -> **Fix:** check system logs first (not just application logs) for
  the actual exit reason, then increase the probe's initial delay if
  slow startup is the real cause.
- **Symptom:** the app feels slow under load with no clear cause in the
  code -> **Cause:** CPU throttling from the default 0.25 vCPU/0.5 Gi
  allocation being too small -> **Fix:** measure actual CPU/memory usage
  first, then explicitly set `resources` on the container to match
  rather than guessing.

*Checked against: Microsoft Learn's "Scaling in Azure Container Apps,"
"Troubleshooting in Azure Container Apps," and "Troubleshoot start
failures in Azure Container Apps" docs.*''',

    "day-11-vnet-subnets-nsg": '''### What It Can't Do
Azure reserves five IP addresses in every subnet, not one - the network
address, three Azure reserves for its own use (default gateway and DNS
mapping), and the broadcast address at the top. A /24 subnet's 256
addresses isn't actually 256 usable ones, it's 251. This catches people
sizing subnets right at the edge of what they think they need.

NSGs also can't do stateful application-layer inspection - they filter
on the classic five-tuple (source/destination IP, source/destination
port, protocol), not on what's actually inside the packet. "Block
malicious HTTP payloads" is Azure Firewall or a WAF's job, not an NSG's.

A subnet or NIC can only have one NSG at a time - no stacking two
directly on the same subnet - though a subnet's NSG and a NIC's NSG
absolutely can both be in play for the same VM simultaneously, which is
where "traffic has to pass both" comes from.

### Nuances Worth Knowing
- The default rules (AllowVNetInBound, AllowAzureLoadBalancerInBound,
  DenyAllInBound, and their outbound equivalents) can never be deleted
  or edited, only overridden with a higher-priority (lower number)
  custom rule. In the portal they show grayed out, which sometimes gets
  mistaken for "disabled" - they're still fully active, just read-only.
- Rule evaluation order differs by traffic direction: inbound traffic
  hits the subnet-level NSG first, then the NIC-level NSG; outbound hits
  the NIC-level NSG first, then subnet-level. Getting this backward is a
  common source of "I fixed the rule but it's still blocked" when the
  block is actually happening at the other level.
- NSG flow logs (the older diagnostic tool) are being retired in favor
  of Virtual Network flow logs - if a tutorial or older reference
  mentions the former, that's the path going away, not the one to build
  against now.

### Troubleshooting You'll Actually Hit
- **Symptom:** a deployment fails validation with something like "the
  specified address prefix is fully utilized" for a subnet that "should"
  have room -> **Cause:** forgetting Azure reserves 5 addresses per
  subnet -> **Fix:** size subnets with that reservation in mind - a /28
  for a handful of VMs, not a raw headcount match.
- **Symptom:** traffic is blocked and a specific rule that should allow
  it looks completely correct -> **Cause:** the block is coming from the
  *other* NSG in the chain (subnet-level vs NIC-level) -> **Fix:** check
  both NSGs attached to the resource's traffic path, and remember the
  evaluation order differs for inbound vs outbound.
- **Error:** `InUseNetworkSecurityGroupCannotBeDeleted` /
  `InUseSubnetCannotBeDeleted` when tearing down a resource group ->
  **Cause:** the NSG or subnet still has something attached to it (a
  NIC, a peering, a private endpoint) -> **Fix:** the error message
  lists exactly what's still attached - detach or delete that first.

*Checked against: Microsoft Learn's "Network security groups overview"
and Azure networking documentation on subnet address reservation.*''',

    "day-12-peering-and-dns": '''### What It Can't Do
Peering can't route through a gateway automatically. If VNet A has a VPN
Gateway or ExpressRoute connection that VNet B needs to use, that
requires explicitly enabling gateway transit on A's side
(`allowGatewayTransit`) and remote gateways on B's side
(`useRemoteGateways`) - leave either off and the peering update itself
fails, not just silently declines to route.

A private DNS zone by itself resolves nothing across a peering, even
with correct records - Azure's default DNS resolver (168.63.129.16)
only resolves names for VMs in the same VNet or a directly linked
private DNS zone; being peered doesn't automatically extend that.

Address spaces can't overlap between peered VNets - if both happen to
use the same range (common when two teams each grab 10.0.0.0/16
independently), peering can't be established until one is readdressed.

### Nuances Worth Knowing
- Peering requires links from both sides. If only one side is created,
  the peering state shows "Initiated," not "Connected" - traffic doesn't
  flow in that state, and it's easy to miss since the portal doesn't
  loudly flag it as broken.
- A peering stuck "Disconnected" can't just be edited back to health -
  the fix is deleting the peering from both sides and recreating both
  links from scratch.
- Route propagation after creating or changing a peering isn't instant -
  it can take a few minutes, so "resources can't reach each other yet"
  right after standing up a peering is often just propagation delay.
- A VM peered and DNS-linked correctly for the same-VNet case can still
  fail cross-VNet name resolution intermittently - a documented
  real-world pattern that often traces back to client-side DNS caching
  or which specific DNS server the VM's NIC is actually using, not the
  peering or zone configuration itself.

### Troubleshooting You'll Actually Hit
- **Symptom:** two VNets are peered but resources can't reach each other
  at all -> **Cause:** peering status shows "Initiated" instead of
  "Connected" - only one side created its half -> **Fix:** create the
  missing peering resource on the other VNet.
- **Symptom:** a VM can ping another VM's private IP across the peering
  but not by hostname -> **Cause:** DNS resolution isn't automatic
  across a peering -> **Fix:** link a Private DNS Zone to both VNets (or
  configure custom DNS servers both point to), and confirm actual
  records exist for the names being resolved.
- **Error:** enabling `useRemoteGateways` fails or is rejected ->
  **Cause:** the corresponding `allowGatewayTransit` wasn't set on the
  VNet that actually owns the gateway -> **Fix:** set gateway transit on
  the gateway-owning VNet's peering first, then remote gateways on the
  other side.

*Checked against: Microsoft Learn's "Troubleshoot virtual network
peering issues" and "Troubleshoot virtual network peering route
propagation and sync problems" docs.*''',

    "day-14-bastion-vpn-gateway": '''### What It Can't Do
Basic SKU Bastion (this lesson's build) can't do file upload/download
through the portal at all - that's only available through a native
RDP/SSH client, and only from Standard SKU up. Basic also can't use
custom ports, IP-based connections, or host scaling - it's fixed at two
instances with no way to add more.

The GatewaySubnet has hard, non-negotiable requirements: named exactly
`GatewaySubnet`, sized at least /27, and no NSG, route table, or other
resource attached to it - genuinely can't, not just shouldn't. Azure
refuses or fails the deployment if any of these are violated.
AzureBastionSubnet has its own separate, equally strict requirement:
exactly that name, minimum /26 (not /27 - that changed in November 2021,
so older /27 deployments only still work because they predate the
change), and no other resources or route tables in it either.

Basic SKU VPN Gateway is treated as legacy - current guidance is
VpnGw1 and above, and mixing SKUs (a Basic gateway with a Standard-SKU
public IP) is a real, documented cause of deployment failure, not a
style preference.

### Nuances Worth Knowing
- A brand-new VPN Gateway deployment isn't fast - creating the gateway
  resource itself commonly takes 30-45 minutes even when everything is
  configured correctly, easy to mistake for a stuck deployment given how
  quickly most other resources in this repo deploy.
- Site-to-Site connections are policy-based or route-based, and
  mismatched Security Association settings or "one tunnel per subnet
  pair" expectations between Azure and an on-prem device are a
  documented cause of *intermittent* (not permanent) disconnects - it
  looks unstable rather than broken, which sends people looking in the
  wrong place first.
- A user-defined route accidentally placed on the GatewaySubnet is a
  documented, sneaky cause of "the tunnel shows Connected but traffic
  still doesn't flow correctly for some destinations" - it's allowed to
  exist there in ways that don't block deployment but do quietly break
  specific traffic paths.

### Troubleshooting You'll Actually Hit
- **Error:** Bastion deployment fails validation -> **Cause:** almost
  always the subnet name isn't exactly `AzureBastionSubnet`, or it's
  smaller than /26 -> **Fix:** rename/resize the subnet to match exactly
  - no flexibility here, unlike most subnet naming elsewhere in this
  repo.
- **Error:** VPN Gateway deployment fails or times out -> **Cause:**
  most commonly the GatewaySubnet is undersized (below /27), misnamed,
  or has an NSG/route table attached; a Basic-SKU gateway paired with a
  non-Basic public IP is another frequent cause -> **Fix:** confirm
  GatewaySubnet is named exactly that, sized /27+, has nothing else
  attached, and that gateway/IP SKUs match.
- **Symptom:** a Site-to-Site connection shows Connected but specific
  traffic still doesn't reach its destination -> **Cause:** frequently a
  UDR on the GatewaySubnet quietly overriding the expected path ->
  **Fix:** check for and remove any route table on the GatewaySubnet
  before assuming the VPN configuration itself is wrong.

*Checked against: Microsoft Learn's "Azure Bastion FAQ," "About Azure
Bastion configuration settings," and "Troubleshoot an Azure S2S VPN
connection" docs.*''',

    "day-15-network-watcher-review": '''### What It Can't Do
Network Watcher's tools mostly diagnose the control plane and
packet-level behavior - they don't reach inside application content. IP
Flow Verify tells you whether a specific packet would be allowed or
denied by NSG rules at a VM, but not whether the application behind that
port is actually working; a green "Allowed" result and a broken app
aren't mutually exclusive.

NSG flow logs specifically can't be newly created anymore (creation
stopped mid-2025), and the feature retires entirely on September 30,
2027, at which point Azure deletes the flow log resources themselves
(already-written log data in storage stays, following its own retention
policy). Anything built against NSG flow logs going forward is building
on a feature already past its practical shelf life - Virtual Network
flow logs are the current path.

Connection Troubleshoot and VPN Troubleshoot are one-time checks, not
continuous monitoring - they answer "is this working right now," not
"alert me if this breaks later." Continuous monitoring is Connection
Monitor's job, a separate capability.

### Nuances Worth Knowing
- Network Watcher is usually auto-enabled per region the first time a
  VNet is created there, and it lives in a special auto-created resource
  group (`NetworkWatcherRG`) separate from your own - exactly why this
  lesson's `existing` reference uses
  `scope: resourceGroup('NetworkWatcherRG')` instead of the resource
  group everything else in this repo deploys into.
- IP Flow Verify and NSG Diagnostics sound similar but check different
  scopes: IP Flow Verify answers the question at a single VM; NSG
  Diagnostics can answer it across a VM, a VM Scale Set, or an
  Application Gateway, and shows every NSG rule from every NSG in the
  traffic's path, not just the first one it hits.
- Packet capture requires an actual agent running on the target VM -
  it's not a pure control-plane operation like most of Network Watcher's
  other tools, so a VM without connectivity for the agent to phone home
  can't be packet-captured even though every other diagnostic still
  works against it.

### Troubleshooting You'll Actually Hit
- **Symptom:** two connected resources can't reach each other and
  neither NSG inspection nor peering status shows anything obviously
  wrong -> **Cause:** exactly the ambiguous case Connection Troubleshoot
  exists for -> **Fix:** run Connection Troubleshoot between the two
  specific endpoints; it tests actual connectivity rather than just
  checking configuration, and reports the specific hop or rule where it
  fails.
- **Symptom:** a Site-to-Site VPN connection is unhealthy and it's
  unclear why -> **Cause:** commonly a mismatched shared key between the
  two gateways, something config inspection alone doesn't always surface
  clearly -> **Fix:** run VPN Troubleshoot against the gateway; it's
  built specifically to catch this class of mismatch.
- **Symptom:** an older tutorial walks through setting up NSG flow logs
  -> **Cause:** the tutorial predates the retirement announcement ->
  **Fix:** build against Virtual Network flow logs instead - new NSG
  flow log creation has already stopped.

*Checked against: Microsoft Learn's "Network Watcher overview," "NSG
flow logs overview," and "Network Watcher Frequently Asked Questions"
docs.*''',

    "day-16-storage-accounts-redundancy": '''### What It Can't Do
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
replicated" and "Storage redundancy change FAQs" docs.*''',

    "day-17-blob-lifecycle": '''### What It Can't Do
A lifecycle management policy can't rehydrate a blob back to an online
tier - it only ever moves things toward colder/cheaper tiers or deletes
them; getting a blob out of Archive requires a separate, manual
rehydration operation. It also can't run retroactively against its own
creation - it applies going forward from its first evaluation, so blobs
that already qualify at the moment the policy is created don't get swept
up instantly; they wait for the first evaluation cycle like everything
else.

The delete action specifically won't touch a blob in an immutable
container, or a blob currently in a soft-deleted state - the policy
engine respects both protections rather than overriding them. And a
policy can't be partially updated - the whole JSON policy is one
document, so a small edit means resubmitting the entire policy, not
patching one rule in place.

### Nuances Worth Knowing
- Nothing here runs on demand or continuously - Azure evaluates
  lifecycle policies roughly once per day, and after creating or editing
  a policy, the first evaluation can take up to 24 hours to even start.
  "I set the rule five minutes ago and nothing moved" isn't broken, it's
  just before the first scheduled run.
- The clock a rule uses depends on what it's evaluating: current blob
  versions use last-modified time (or last-access time, if access
  tracking is explicitly enabled - it's off by default), previous
  versions use their own creation time, and snapshots use the time the
  snapshot itself was taken.
- Moving a blob out of Cool into Archive before it's spent Cool's
  minimum retention window (30 days) triggers an early-deletion charge -
  a real, billed penalty for a rule that tiers too aggressively.
- If a blob gets manually rehydrated back to Hot/Cool while a lifecycle
  policy targeting it is still active, the same policy can tier it right
  back to Archive on its next run - rehydrating doesn't exempt a blob
  from the rule that archived it unless the rule or blob itself changes.

### Troubleshooting You'll Actually Hit
- **Symptom:** a rule was created or edited, and blobs that clearly meet
  its conditions haven't moved or deleted after a day or more ->
  **Cause:** either still within the up-to-24-hour window before the
  first evaluation, or the modification/access timestamp hasn't actually
  crossed the threshold yet -> **Fix:** confirm the actual timestamp on
  the blob itself, and wait out the full evaluation window before
  assuming the rule is broken.
- **Symptom:** blobs that should be deleted remain in place indefinitely
  -> **Cause:** commonly the blob is in an immutable container, or in a
  soft-deleted state, both of which the delete action deliberately won't
  touch -> **Fix:** check the container's immutability policy and the
  blob's soft-delete status before assuming the rule is misconfigured.
- **Symptom:** a rule using `daysAfterLastAccessTimeGreaterThan` never
  triggers -> **Cause:** access time tracking wasn't explicitly enabled
  on the account, so `LastAccessTime` isn't being recorded at all ->
  **Fix:** enable last-access-time tracking first; a last-access rule
  with tracking off will silently never fire.

*Checked against: Microsoft Learn's "Azure Blob Storage lifecycle
management overview" and "lifecycle management policy structure"
docs.*''',

    "day-18-azure-files": '''### What It Can't Do
Azure Files' SMB protocol communicates over TCP port 445, and a large
number of ISPs and corporate networks block that port outbound entirely,
for historical reasons tied to old SMB 1.0 vulnerabilities - this isn't
an Azure-side limitation, but it's a very real, very common blocker for
on-prem or home-network clients trying to mount a share directly over
the internet. There's no way to change which port SMB uses; the
workarounds all avoid a direct SMB connection over the internet in the
first place (private endpoint, VPN/ExpressRoute, or Azure File Sync as a
local cache reachable over port 443).

NFS shares specifically require the Premium tier and can't use the
storage account's public endpoint at all - NFS Azure Files only works
over a private endpoint or service endpoint inside a VNet, the opposite
of SMB's default (publicly reachable unless explicitly restricted). A
file share's quota is a ceiling, not a reservation on Standard tier -
`shareQuota: 5` caps the share at 5 GB, but billing follows actual usage,
not the quota; Premium tier is the opposite, provisioning and billing
for the full quota upfront regardless of actual usage.

### Nuances Worth Knowing
- The standard diagnosis path for "can't mount, works from an Azure VM
  but not from home" is almost always port 445, not credentials or share
  config - the practical first test is a direct TCP connection check
  (`Test-NetConnection -Port 445` or `nc -zv ... 445`) before touching
  anything else.
- Entra ID Kerberos authentication for SMB is a two-layer permission
  model, not one - it needs both a share-level RBAC role assignment (in
  Azure) and correct NTFS folder-level ACLs (set from within Windows).
  Missing either layer blocks access even when the other is perfectly
  configured, and the resulting error doesn't clearly say which layer is
  the problem.
- Standard file shares don't provision performance the way Premium
  does - Premium performance scales directly with the quota set (bigger
  provisioned quota = more IOPS/throughput), so undersizing quota on
  Premium isn't just a capacity risk, it's a performance ceiling too.

### Troubleshooting You'll Actually Hit
- **Error:** "System error 53" or "System error 67" when mounting from
  an on-prem machine -> **Cause:** port 445 is blocked somewhere between
  the client and Azure - an ISP or corporate firewall, not an Azure-side
  failure -> **Fix:** confirm with a direct port test first; if 445 is
  genuinely blocked and can't be opened, route through a private
  endpoint + VPN/ExpressRoute, or use Azure File Sync as a local
  port-443 workaround instead of forcing a direct SMB mount.
- **Symptom:** a user has the correct share-level RBAC role but still
  can't access specific folders -> **Cause:** Entra Kerberos auth needs
  matching NTFS ACLs set from Windows in addition to the RBAC role ->
  **Fix:** verify both the Azure-side role assignment and the
  Windows-side NTFS permissions on the specific folder, not just one or
  the other.
- **Symptom:** connecting works fine from an Azure VM in the same region
  but fails from anywhere else -> **Cause:** consistent with a port-445
  block specific to the client's network -> **Fix:** same as above -
  this pattern (works from Azure, fails externally) is close to a
  diagnostic signature for the port-445 case specifically.

*Checked against: Microsoft Learn's "Troubleshoot Azure Files SMB
connectivity and access issues" doc and Azure Files networking training
material.*''',

    "day-19-sas-private-endpoints": '''### What It Can't Do
Creating a private endpoint doesn't automatically disable the storage
account's public endpoint - those are two separate settings. Deploying a
private endpoint and leaving public network access enabled leaves the
resource reachable both ways at once, which defeats the isolation goal
if the intent was "private only." A private endpoint also doesn't make
DNS resolve correctly by itself - creating it creates a private IP, but
nothing automatically points client DNS lookups at it; that requires a
Private DNS Zone actually linked to the VNet the client sits in.

A SAS token can't be selectively revoked once issued unless it was built
around a stored access policy - a SAS generated directly against account
keys is valid until it expires, full stop; the only way to kill it early
is rotating the account keys themselves, which invalidates every other
SAS issued from those same keys at the same time, not just the one meant
to be revoked.

### Nuances Worth Knowing
- The single most common private endpoint failure isn't actually a
  private-endpoint problem, it's DNS - and it typically shows up as a
  403 "This TCP connection does not allow access" error from the
  resource's firewall, because the client resolved the *public* hostname,
  connected over the public endpoint, and got rejected by the exact
  firewall rule the private endpoint was supposed to make irrelevant.
- If a VNet uses custom DNS servers instead of Azure-provided DNS,
  linking the Private DNS Zone to the VNet isn't enough by itself - the
  custom DNS server also has to forward `privatelink.*` queries
  specifically to Azure's DNS resolver (168.63.129.16), or it never even
  asks Azure DNS about the private zone.
- A private endpoint connection can sit in a Pending state even after
  setup looks complete - this happens for cross-subscription or
  cross-tenant connections, where the resource owner has to manually
  approve the connection before any traffic flows.
- User Delegation SAS tokens are capped at a maximum lifetime of 7 days
  when re-authentication isn't required within that window - unlike
  Account or Service SAS, which can be issued with much longer
  expirations.

### Troubleshooting You'll Actually Hit
- **Error:** "403 - This TCP connection does not allow access to {host}"
  on a resource with a private endpoint configured -> **Cause:** almost
  always DNS resolving the public hostname to the public IP instead of
  the private endpoint's IP, so the firewall rejects the connection as
  if the private endpoint didn't exist -> **Fix:** `nslookup` the
  hostname from a VM inside the VNet - if it returns a public IP, check
  the Private DNS Zone is linked to that specific VNet, and if custom
  DNS is in play, confirm it forwards `privatelink.*` queries to Azure
  DNS.
- **Symptom:** a private endpoint was created and everything else looks
  correct, but traffic doesn't flow -> **Cause:** the connection is
  sitting Pending, which happens by design for cross-subscription/
  cross-tenant private endpoints until the resource owner approves it ->
  **Fix:** check the connection's status on the target resource itself
  and approve it if Pending.
- **Symptom:** DNS resolves to the private IP on one attempt and the
  public IP on the next, intermittently -> **Cause:** commonly multiple
  DNS paths in play at once (a custom forwarder alongside Azure-provided
  DNS, or stale caching from before the zone was linked) -> **Fix:**
  flush the client's DNS cache, and confirm there's exactly one
  consistent resolution path rather than a mix of custom and
  Azure-provided DNS.

*Checked against: Microsoft Learn's "Troubleshoot private endpoint DNS
resolution failure" and "Troubleshoot 403 access denied errors ...
through an approved private endpoint" docs.*''',

    "day-21-entra-users-groups": '''### What It Can't Do
The Graph extension's supported resource list is genuinely narrow, and
even within Groups real gaps exist. A single Groups resource can't
declare more than 20 members or owners - go over that and deployment
fails outright with a 400 error, with nothing in the syntax warning
about the wall in advance. Role-assignable groups (`isAssignableToRole:
true`) look fully supported in the schema, but deploying one fails
regardless of permissions - it's declared but not actually deployable
through this extension yet; the documented workaround is a
`DeploymentScript` resource calling Microsoft Graph directly instead.

`what-if` doesn't work against Graph resources at all - none of the
preview-before-deploy safety net this repo has relied on since Day 00
applies here. Neither do deployment stacks or verbose deployment output.
And deployed Graph resources genuinely don't show up on the Azure
portal's deployment details page - only true ARM resources do, so
confirming a Graph deployment succeeded means checking Entra ID
directly, not the deployment history checked for everything else in
this repo.

### Nuances Worth Knowing
- If a Graph resource created through Bicep gets deleted some other way
  (portal, PowerShell, Graph API directly), redeploying the same Bicep
  file doesn't recreate it cleanly - it throws a conflict error about
  the unique name still technically existing in a deleted state. The fix
  is one of three specific paths: permanently purge the deleted item,
  restore it, or change the unique name in the Bicep file and redeploy
  under a new identity.
- App-only deployment (the kind used in most CI/CD pipelines) can't
  declare a group with a `membershipRule` (dynamic membership) - that
  combination fails with an explicit "AppOnly OBO tokens not supported"
  error, because dynamic membership evaluation doesn't support the
  automation flow app-only deployments use.
- Application passwords (`passwordCredentials`) aren't supported on
  `applications` or `servicePrincipals` resources - only `keyCredentials`
  (certificates) are. A genuinely required password/secret is another
  `DeploymentScript`-calls-Graph workaround, not a native Bicep property.

### Troubleshooting You'll Actually Hit
- **Error:** a Groups resource deployment fails with a 400 error and no
  obviously wrong syntax -> **Cause:** likely more than 20 members
  and/or owners declared on that single group -> **Fix:** split
  membership assignment across multiple deployments/operations rather
  than declaring everyone in one Groups resource block.
- **Error:** redeploying a previously-working file fails with a
  conflict about a group name that "already exists" even though it's
  gone from the portal -> **Cause:** the group was deleted outside of
  Bicep and Entra still holds it in a soft-deleted state under that
  unique name -> **Fix:** purge or restore the deleted item through
  Graph, or change the Bicep file's unique name and redeploy fresh.
- **Symptom:** a deployment managing Graph resources "succeeds" per the
  CLI, but nothing shows up in the Azure portal's deployment history ->
  **Cause:** expected, not a failure - the portal's deployment details
  page doesn't display Microsoft Graph resources at all -> **Fix:**
  verify success directly in Entra ID or via Graph API/PowerShell.

*Checked against: Microsoft Learn's "Known issues: Microsoft Graph Bicep
Templates" and "Microsoft Graph Bicep Feature Limitations and
Restrictions" docs.*''',

    "day-22-rbac-vs-entra-roles": '''### What It Can't Do
Being Global Administrator in Entra ID grants nothing at all in Azure by
default - not Reader, not Contributor, nothing. The two systems are
deliberately, completely separate authorization models: Entra role
assignments don't grant Azure resource access, and Azure RBAC
assignments don't grant Entra ID access. A brand-new Global Admin
signing into the Azure portal for the first time can see zero
subscriptions, not because anything is broken, but because that's simply
how the systems are designed to work.

Entra roles also can't scope the same granular way Azure RBAC can. Azure
RBAC scopes to a management group, subscription, resource group, or
individual resource; most Entra roles are tenant-wide by default
(Administrative Units narrow some Entra roles to a subset of users or
groups, but it's a fundamentally coarser scoping model than Azure RBAC's).

### Nuances Worth Knowing
- There's exactly one documented bridge between the two systems: a
  Global Administrator can flip "Access management for Azure resources"
  to Yes under Microsoft Entra ID > Properties, which grants User Access
  Administrator in Azure RBAC at the tenant root scope (`/`) - not
  permanently, and not automatically. It's a one-time elevation a Global
  Admin has to explicitly trigger, and Microsoft's own guidance is to
  remove that elevated role assignment once the task is done rather than
  leaving it in place.
- That elevation setting is per-user, not global - triggering it
  elevates the specific signed-in Global Administrator's own access; it
  doesn't elevate every Global Administrator in the tenant at once.
- The resulting User Access Administrator role at root scope is enough
  to *assign* access to any subscription or management group, but it
  isn't the same as being Owner or Contributor everywhere - it's
  specifically an access-management role.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Global Administrator signs into the Azure portal and
  sees no subscriptions, or can't see/manage one someone else created ->
  **Cause:** exactly the expected behavior when the two authorization
  systems have never been bridged - Global Admin status alone was never
  going to grant Azure access -> **Fix:** use the "Access management for
  Azure resources" toggle in Entra ID Properties to self-elevate to User
  Access Administrator at root scope, make the needed change, then
  remove the elevated assignment again afterward.
- **Symptom:** switching directories/tenants in the portal seems to fix
  a similar-looking access problem for someone else -> **Cause:** a
  different, more common cause of "I can't see my subscription" is
  simply being signed into the wrong Entra tenant, which looks identical
  to a genuine RBAC gap at first glance -> **Fix:** confirm the correct
  directory is selected before assuming it's an RBAC/Entra-role mismatch
  at all.
- **Symptom:** an automation app or service account needs visibility
  across every subscription in the tenant -> **Cause:** this is one of
  the intended real use cases for elevated access, not a workaround ->
  **Fix:** use the same elevation mechanism to grant that principal User
  Access Administrator at root scope, deliberately and temporarily.

*Checked against: Microsoft Learn's "Elevate access to manage all Azure
subscriptions and management groups" doc.*''',

    "day-23-conditional-access-sspr": '''### What It Can't Do
Conditional Access can't retroactively kill an already-issued sign-in
token - policies are evaluated at sign-in time, so a session established
before a new or tightened policy takes effect keeps running under the
old rules until the token naturally expires or the user is forced to
reauthenticate. It also can't protect against legacy authentication a
third-party app still uses under the hood - if an app authenticates
using a protocol Conditional Access doesn't evaluate, CA simply never
gets a chance to apply. And Conditional Access for workload identities
(service principals, managed identities) is a related-but-distinct
capability from user-focused CA - a policy scoped to "All users" doesn't
automatically cover a service principal's sign-ins unless workload
identity CA is specifically configured for it.

### Nuances Worth Knowing
- Report-only mode is genuinely load-bearing, not a formality: it
  evaluates every sign-in against the policy and logs exactly what
  *would* have happened, without blocking or requiring anything. The
  universally repeated guidance across real incident write-ups is that
  every new policy starts in Report-only and gets checked against
  sign-in logs before ever switching to On, no exceptions.
- The single most common cause of a full tenant lockout isn't an
  attacker - it's an admin publishing a policy scoped to "All users"
  (instead of a pilot group) directly to On, with no break-glass account
  excluded. When every admin loses access at once, there's no way to fix
  it from inside the tenant - it becomes an out-of-band recovery
  problem.
- Break-glass accounts (at least two, cloud-only, excluded from every CA
  policy) exist specifically as the last resort for that failure mode.
  Best practice explicitly recommends two, not one - a single account is
  itself a single point of failure if its password expires or its
  credential is lost.
- A Conditional Access policy that blocks legacy authentication or
  requires a compliant device can end up blocking the very sign-in flow
  a user needs to reach the SSPR password reset page, if the reset
  portal itself isn't explicitly accounted for in policy scope.

### Troubleshooting You'll Actually Hit
- **Symptom:** every administrator is suddenly unable to sign in
  shortly after a Conditional Access change -> **Cause:** almost always
  a policy scoped too broadly, pushed straight to On without a
  break-glass exclusion, matching the classic full-tenant-lockout
  pattern -> **Fix:** if a working break-glass account exists, sign in
  with it and disable/fix the offending policy immediately; if none
  works, this becomes a Microsoft Support recovery case, not something
  fixable from inside the tenant.
- **Symptom:** a new policy switched to On and specific users report
  being blocked unexpectedly -> **Cause:** the policy wasn't validated
  in Report-only first, so edge cases weren't caught before enforcement
  -> **Fix:** revert to Report-only, review sign-in logs filtered to
  that policy name for every would-be-blocked result, and resolve or
  explicitly exclude each case before re-enabling.
- **Symptom:** a user can't complete SSPR after a Conditional Access
  rollout despite correct credentials -> **Cause:** the policy is
  blocking the authentication step needed to reach the reset flow itself
  -> **Fix:** confirm the SSPR path is accounted for in the policy's
  scope or exclusions, not just the main sign-in flow.

*Checked against: Microsoft Q&A and Microsoft Learn guidance on
Conditional Access lockout recovery and Report-only rollout practices.*''',

    "day-24-hybrid-identity": '''### What It Can't Do
Entra Connect can't fix a duplicate-attribute conflict on its own - if
two AD objects end up with the same UserPrincipalName or proxyAddress,
export to Entra ID fails with an `AttributeValueMustBeUnique`-style
error, and the sync engine doesn't guess which one is "right." The fix
always happens on the source side, in on-premises Active Directory - not
inside Entra Connect itself. It also can't sync changes faster than its
own cycle - the default delta sync interval is 30 minutes, so a change
made in on-prem AD doesn't appear in Entra ID instantly; it waits for
the next scheduled cycle, or a manually triggered one.

Pass-through authentication specifically can't work if none of the
lightweight authentication agents are online - unlike password hash sync
(which keeps a hash copy in the cloud and keeps validating sign-ins even
if every on-prem agent goes down), PTA validates every sign-in against
on-prem AD in real time through those agents. No agent reachable means
no sign-in validation, tenant-wide, for every hybrid user relying on it.

### Nuances Worth Knowing
- The single most common category of sync failure by far is a
  duplicate-attribute conflict, not a connectivity or credentials
  problem - two users ending up with the same UserPrincipalName or proxy
  address is the case worth checking first when an object silently stops
  syncing.
- Actually running down a duplicate-attribute error is procedural:
  identify the conflicting objects and the specific duplicated attribute
  (via the Synchronization Service Manager connector space or the Entra
  Connect Health sync error report), decide which object keeps the
  value, remove it from the other object in on-prem AD, then let the
  next sync cycle pick up the fix.
- Since 2016, Entra ID has "duplicate attribute resiliency" enabled by
  default - this quarantines the specific duplicated value rather than
  blocking the entire object from syncing, a meaningfully softer failure
  mode, but it still doesn't resolve the underlying duplicate; it just
  stops one bad attribute from taking down an otherwise-fine object.
- A stale "Last Synchronization" timestamp in Entra Connect Health
  (older than the expected 30-minute cycle) is itself a symptom worth
  treating seriously - it usually means the sync service has stopped
  running entirely, not just that one object is having trouble.

### Troubleshooting You'll Actually Hit
- **Error:** an object export fails with `AttributeValueMustBeUnique`
  (commonly on UserPrincipalName or proxyAddresses) -> **Cause:** two
  on-prem AD objects have the same value for an attribute Entra ID
  requires to be unique -> **Fix:** identify both conflicting objects
  via Entra Connect Health's sync error report or the Synchronization
  Service Manager, correct the wrong one directly in on-prem AD, and let
  the next sync cycle clear the error.
- **Symptom:** a change made in on-prem AD hasn't shown up in Entra ID
  after a few minutes -> **Cause:** normal behavior, not a failure - the
  default delta sync cycle runs every 30 minutes -> **Fix:** wait for
  the next scheduled cycle, or manually trigger a delta sync if the
  change is time-sensitive.
- **Symptom:** hybrid users relying on pass-through authentication
  suddenly can't sign in at all, tenant-wide -> **Cause:** all PTA
  agents are offline or unreachable, leaving no path to validate
  sign-ins against on-prem AD -> **Fix:** check agent health/connectivity
  first; this is exactly the class of outage password hash sync, kept as
  a backup alongside PTA, is specifically recommended to guard against.

*Checked against: Microsoft Learn's "Microsoft Entra Connect:
Troubleshoot errors during synchronization" and "Microsoft Entra Connect
Health - Diagnose duplicated attribute synchronization errors" docs.*''',

    "day-26-log-analytics-diagnostics": '''### What It Can't Do
Diagnostic settings can't filter within a category - it's the whole log
category or none of it; finer filtering happens after ingestion via a
transformation, not at the diagnostic setting itself. A single
diagnostic setting also can't send to more than one destination of the
same type - one workspace, one storage account, one Event Hub max per
setting; fanning out to two workspaces means creating two separate
diagnostic settings.

Every resource is capped at five diagnostic settings total, regardless
of destinations or categories - hit that cap and the fix is removing an
unused setting, not requesting an increase. For regional destinations
(Storage accounts and Event Hubs specifically), the destination has to
be in the same region as the resource being monitored - a diagnostic
setting can't route logs cross-region to a storage account sitting
somewhere else.

### Nuances Worth Knowing
- Nothing here is instant. Data can take up to 90 minutes to start
  flowing after a diagnostic setting is first configured, even though it
  usually arrives within a few minutes in practice - an empty query five
  minutes after setup is expected, not broken.
- A Log Analytics workspace has a default ingestion rate limit around
  6 GB/minute (uncompressed) - a real, hittable ceiling under a genuine
  spike, separate from the daily cap setting.
- If a resource goes quiet and starts exporting nothing but zero-value
  metrics, Azure incrementally backs off how often it checks it, up to a
  two-hour maximum interval after seven days of inactivity - a
  legitimately idle resource can look like a broken diagnostic setting
  purely because of this backoff behavior, snapping back to normal
  latency the moment real data starts flowing again.
- Sending overlapping log categories from two diagnostic settings on the
  same resource into the same workspace produces duplicate records, not
  merged ones - each setting should own a distinct set of categories, or
  point somewhere else entirely.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Log Analytics query comes back empty right after
  setting up a diagnostic setting -> **Cause:** normal ingestion
  latency, up to 90 minutes -> **Fix:** wait before assuming
  misconfiguration; re-check after enough time has passed.
- **Symptom:** data collection stops mid-day with no obvious cause ->
  **Cause:** either the workspace's daily cap was reached, or the
  ~6 GB/min ingestion rate limit was hit -> **Fix:** run
  `Operation | where OperationCategory == 'Data Collection Status'`
  for the daily cap, or check for an "Ingestion" operation citing a rate
  threshold crossed, then raise the cap or wait for the reset.
- **Symptom:** metrics selected in the diagnostic setting don't show up
  as expected when queried -> **Cause:** metrics routed through a
  diagnostic setting land in the `AzureDiagnostics` table, not a
  dedicated metrics table, and not every metric is exportable this way
  -> **Fix:** query `AzureDiagnostics` specifically, and pull anything
  missing directly via the Metrics REST API instead of assuming the
  diagnostic setting is broken.

*Checked against: Microsoft Learn's "Diagnostic settings in Azure
Monitor" and "Troubleshoot why data is no longer being collected in
Azure Monitor" docs.*''',

    "day-27-alerts-action-groups": '''### What It Can't Do
Notification actions aren't treated equally under the hood - SMS, voice,
and email are all rate limited per phone number/address, but webhooks,
Functions, and Logic App actions aren't rate limited at all. SMS and
voice are capped at one notification every 5 minutes per number; email
is capped at 100 messages per hour per address. Cross a threshold and
Azure doesn't queue the extras for later - they're dropped, with only a
separate notification saying rate limiting kicked in. This is an actual
AZ-104 exam topic: an alert firing every minute for an hour produces
roughly 60 emails but only about 12 SMS messages, purely from these two
different caps.

Metric alerts are also stateful by default - once an alert fires on a
specific metric time series, it won't fire again for that series until
the condition clears (three consecutive evaluations without it being
met) and re-triggers. Deliberate noise reduction, not a bug, but it
means "the alert only notified me once even though the CPU stayed high
for an hour" is expected behavior.

### Nuances Worth Knowing
- If genuinely continuous notifications are needed, that requires
  explicitly making the alert rule stateless (`autoMitigate: false` in
  Bicep/ARM, or unchecking "Automatically resolve alerts" in the
  portal) - the default stateful behavior otherwise suppresses repeat
  notifications on purpose.
- Dynamic thresholds need real history before they mean anything -
  Microsoft's own guidance is a minimum of 3 days and 30 metric samples
  before a dynamic threshold becomes active. A dynamic-threshold alert
  on a resource created minutes ago has nothing to learn from yet.
- Action groups aren't capped per subscription (effectively unlimited),
  but an alert rule's combined properties (query, dimensions,
  description, referenced action groups) can't exceed 64 KB - a large
  KQL query with many dimensions can hit this ceiling and fail at
  creation with a vague "there was a problem with the server" error that
  doesn't obviously point at size as the cause.
- A fired alert visible in the portal but with no SMS/voice/push
  actually delivered is very often an alert processing rule silently
  suppressing that action (e.g. a maintenance-window suppression rule) -
  worth checking before assuming the action group itself is broken.

### Troubleshooting You'll Actually Hit
- **Symptom:** an alert is clearly firing repeatedly in the portal, but
  notifications stopped arriving partway through -> **Cause:** the
  per-recipient rate limit was hit and the excess notifications were
  simply dropped -> **Fix:** confirm this by checking for the rate-limit
  notice sent to that address/number, then reduce alert noise at the
  source or route high-volume notifications through a non-rate-limited
  action type like a webhook instead.
- **Symptom:** a condition stays true for a long stretch but only one
  notification ever arrived -> **Cause:** the metric alert is stateful
  by default and deliberately doesn't re-notify on the same ongoing
  issue -> **Fix:** if repeat notifications are actually wanted,
  explicitly set the rule to stateless (`autoMitigate: false`).
- **Symptom:** creating an alert rule fails with a vague server error ->
  **Cause:** the combined size of the rule's query, dimensions,
  description, and action group references exceeded 64 KB -> **Fix:**
  simplify the query or split an overly broad multi-dimension rule into
  smaller, more targeted rules.

*Checked against: Microsoft Learn's "Create and manage action groups in
Azure Monitor," "Troubleshooting Azure Monitor alerts and
notifications," and "Troubleshoot Azure Monitor metric alerts" docs.*''',

    "day-28-azure-backup": '''### What It Can't Do
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
and "FAQ - soft delete in Azure Backup" docs.*''',

    "day-29-update-management-arc": '''### What It Can't Do
Arc onboarding requires genuine outbound HTTPS (port 443) connectivity
to a specific set of Microsoft endpoints - not general internet access,
specific URLs (agent service, guest configuration, resource management,
and more). A machine with broad internet access but a corporate/ISP
firewall blocking a subset of those specific hostnames still fails
onboarding, and the failure often looks like a generic network error
unless you specifically check for which endpoint is unreachable. Arc
also can't provide identical feature parity with a genuinely native
Azure VM - `Microsoft.HybridCompute/machines` gives Azure Policy, RBAC,
tagging, and (once onboarded) Update Manager against the machine, but
it's a different resource type sitting on top of real hardware, not a VM
ARM fully manages the underlying compute for.

### Nuances Worth Knowing
- `azcmagent check` exists specifically to answer "can this machine
  actually reach what it needs to reach" before or during onboarding -
  it tests connectivity against every required endpoint individually and
  reports exactly which succeeded or failed, and also reports whether
  traffic is routing directly, through a private link, or through a
  proxy. Running this first, rather than attempting `connect` and
  parsing a generic failure, is the faster path to the actual root
  cause.
- `azcmagent` failures return a specific exit/error code (like
  `AZCM0026` for a network error) that maps to a documented cause -
  looking up the specific code is more useful than treating any failure
  as the same generic "it didn't work."
- A machine that connects successfully once can still later show as
  "Disconnected" in the portal - this specifically means it lost its
  ongoing connection after initially succeeding, and the fix path
  (re-running `connect`, sometimes after force-disconnecting locally and
  deleting the stale Azure-side resource) differs from a first-time
  onboarding failure.
- Verbose agent logs live locally on the machine itself
  (`%ProgramData%\\AzureConnectedMachineAgent\\Log\\` on Windows,
  `/var/opt/azcmagent/log/` on Linux, directly relevant to the RHEL box)
  - checking these directly is often faster than working only from what
  the CLI prints to the terminal.

### Troubleshooting You'll Actually Hit
- **Error:** `azcmagent connect` fails with exit code `AZCM0026`
  (Network Error) listing specific unreachable endpoints -> **Cause:**
  outbound HTTPS to one or more required Arc endpoints is blocked by a
  firewall, proxy, or DNS issue - agent installation succeeded, but the
  machine can't register with Azure's control plane -> **Fix:** run
  `azcmagent check --location <your-region>` for the exact list of
  reachable vs. unreachable endpoints, then fix whatever's actually
  blocking those specific URLs rather than opening broad outbound
  access.
- **Symptom:** a previously-connected Arc machine shows as
  "Disconnected" in the portal -> **Cause:** the agent lost its ongoing
  connection after a successful initial registration - could be the same
  connectivity causes as onboarding, or a stopped/crashed agent service
  -> **Fix:** check the agent's live status and service health on the
  machine itself first, and if reconnecting cleanly isn't possible,
  force a local disconnect and delete the stale Azure-side resource
  before re-registering fresh.
- **Symptom:** connectivity looks fine over a general internet test, but
  Arc onboarding still fails -> **Cause:** Arc doesn't need generic
  internet access, it needs specific documented endpoints reachable - a
  firewall can pass general traffic while still blocking the handful of
  hostnames Arc actually needs -> **Fix:** don't trust a general
  ping/browse test; use `azcmagent check` against the actual required
  endpoint list instead.

*Checked against: Microsoft Learn's "Troubleshoot Azure Connected
Machine agent connection issues" doc and Azure Arc connectivity
troubleshooting guidance.*''',
}

# 06-terraform-migration re-uses day-01/02/03 folder names for its own
# Terraform re-dos of the same labs. It's parked (Terraform is its own
# project after AZ-104 per the project instructions), and even once it's
# active, Terraform-specific nuances need their own write-up rather than
# reusing the Bicep-flavored content below - so it's excluded here on
# purpose, not an oversight.
EXCLUDED_PHASE_FOLDERS = {"06-terraform-migration"}

added = 0
already = 0
missing = 0

for lesson_file in sorted(base_path.glob("*/day-*/lesson.md")):
    phase_folder = lesson_file.parent.parent.name
    if phase_folder in EXCLUDED_PHASE_FOLDERS:
        continue

    day_slug = lesson_file.parent.name
    deep_dive = DEEP_DIVES.get(day_slug)

    if deep_dive is None:
        print(f"No deep dive content yet for {day_slug} - skipping")
        missing += 1
        continue

    text = lesson_file.read_text(encoding="utf-8")

    if HEADER in text:
        already += 1
        continue

    section = f"{HEADER}\n\n{deep_dive}\n\n"

    if "\n## Source" in text:
        # Insert right before the Source section, so the deep dive reads
        # after the code/example and right before the citations.
        text = text.replace("\n## Source", f"\n{section}\n## Source", 1)
    else:
        # No Source section found (shouldn't happen for a day with an
        # entry above) - append at the end as a fallback.
        text = text.rstrip() + f"\n\n{section}"

    lesson_file.write_text(text, encoding="utf-8")
    added += 1
    print(f"Added Service Deep Dive to {day_slug}")

print()
print(f"Done - {added} lessons got a Service Deep Dive section, "
      f"{already} already had one, {missing} have no deep dive content "
      f"defined yet (later phases).")