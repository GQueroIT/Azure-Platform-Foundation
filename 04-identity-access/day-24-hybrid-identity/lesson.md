# Day 24 Lesson - Hybrid Identity

## Straight Talk First
Microsoft Entra Connect (the sync engine that connects an on-prem Active
Directory to Entra ID) is an installed agent running on a Windows server,
not an Azure resource and not something Bicep deploys. There is no
`Microsoft.Graph/entraConnect` or ARM equivalent - this is fundamentally
outside both Bicep and the Graph extension's scope, the same way installing
a piece of desktop software isn't something Terraform or Bicep would model
either.

## What This Day Actually Is
Concept and theory, since standing up a real hybrid identity lab needs an
on-prem AD domain controller, which is a heavier lift than this repo's
scope. Focus on:
- What Entra Connect actually syncs (users, groups, password hashes or
  pass-through auth) and on what schedule
- The difference between password hash sync, pass-through authentication,
  and federation (ADFS) - the three ways hybrid auth can work
- Why hybrid identity is still extremely common in real enterprise
  environments, even as cloud-only tenants grow

## If You Want Hands-On Later
This is a good candidate for a future lab once you have spare capacity for
a Windows Server VM: install Entra Connect against a test AD forest, and
watch objects sync into a test Entra tenant. Not this build's scope, but
worth flagging for later.

## Service Deep Dive

### What It Can't Do
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
Health - Diagnose duplicated attribute synchronization errors" docs.*


## Source
General Entra Connect architecture concepts - no Bicep-specific source
applies here since this isn't a Bicep-deployable resource.

## Why This Matters (Business Context)
A company has fifteen years of on-prem Active Directory - decades of accumulated group policy, file shares, and legacy apps that will never move to the cloud - but also wants Microsoft 365 and Azure. Hybrid identity is how that company gets one identity that works everywhere, instead of maintaining two separate, drifting sets of user accounts forever.
