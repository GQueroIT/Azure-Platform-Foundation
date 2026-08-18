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