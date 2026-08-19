# Day 29 Lesson - Update Management and Azure Arc

## Straight Talk First
Azure Arc onboarding is NOT a Bicep resource deployment in the normal
sense. You onboard a machine by running the Azure Connected Machine agent
installer (`azcmagent`) directly on that machine, which registers it with
Azure. AFTER it's onboarded, the machine shows up as a
`Microsoft.HybridCompute/machines` resource that you CAN reference or tag
in Bicep - but the actual onboarding step is a script you run on the box,
not a `resource` block you deploy.

## Today's Real Lab
You have a spare machine for this: the RHEL box already running your CCNA
Gauntlet. Onboard it as an Arc-enabled server instead of treating this as
theory-only.

```bash
# Run this ON the RHEL machine itself, not from Bicep/CLI against Azure
sudo dnf install -y azcmagent
sudo azcmagent connect \
  --resource-group <your-rg> \
  --tenant-id <your-tenant-id> \
  --location eastus \
  --subscription-id <your-subscription-id>
```

## New Bicep Concepts (post-onboarding)
Once onboarded, you can reference the Arc machine like any existing
resource:
```bicep
resource arcMachine 'Microsoft.HybridCompute/machines@2023-10-03' existing = {
  name: 'your-rhel-hostname'
}

output arcMachineId string = arcMachine.id
output arcMachineStatus string = arcMachine.properties.status
```

## Why It's Written This Way
- The `existing` keyword shows up one more time here, for the same reason
  it has all build: you're referencing something that was created OUTSIDE
  this Bicep file (in this case, by a CLI agent install, not by Bicep at
  all) so you can read its properties or attach other resources to it,
  like Update Management configuration or a Log Analytics connection.
- Update Management itself, once a machine is Arc-connected, is typically
  configured through Azure Update Manager settings (patch schedules,
  maintenance configurations) which ARE Bicep-deployable
  (`Microsoft.Maintenance/maintenanceConfigurations`) - worth exploring
  once the machine is actually onboarded.

## Service Deep Dive

### What It Can't Do
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
  (`%ProgramData%\AzureConnectedMachineAgent\Log\` on Windows,
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
troubleshooting guidance.*


## Source
General Azure Arc onboarding process (azcmagent) - no single Bicep
reference applies to the onboarding step itself, since it isn't a Bicep
operation.

## Why This Matters (Business Context)
A company has a mix of cloud VMs and physical servers still sitting in a closet somewhere, and the on-prem boxes never get the same patching, monitoring, or policy the cloud VMs get, because they're invisible to the same tools. Arc is how a company brings those boxes into the same management plane instead of treating them as a permanent blind spot.
