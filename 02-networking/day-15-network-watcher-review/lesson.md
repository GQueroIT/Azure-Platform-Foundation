# Day 15 - Network Watcher and Week Review

## What You're Building Today
Network Watcher is enabled per-region automatically in most subscriptions,
so today is lighter on new resource syntax and heavier on review.

## New Bicep Concepts
- `Microsoft.Network/networkWatchers` - usually referenced as `existing`
  rather than created, since Azure auto-provisions one per region

## Annotated Example
```bicep
resource networkWatcher 'Microsoft.Network/networkWatchers@2023-11-01' existing = {
  name: 'NetworkWatcher_eastus'
  scope: resourceGroup('NetworkWatcherRG')
}
```

## Why It's Written This Way
- Network Watcher lives in a special, auto-created resource group called
  `NetworkWatcherRG` in most subscriptions - the `scope:` on the existing
  reference points there specifically, since it's not in your own resource
  group.
- You'll mostly interact with Network Watcher's diagnostic tools (IP flow
  verify, NSG diagnostics, connection troubleshoot) through the Azure CLI
  or portal rather than deploying more Bicep against it - it's a platform
  service you configure, not something you build much of.

## Review Pass
Go back through Days 11-14 and confirm:
- [ ] Every NSG rule has a `priority` you can explain the reasoning for
- [ ] Both peering resources exist (one on each VNet)
- [ ] Bastion and VPN Gateway from Day 14 are DELETED, not just tested
- [ ] Your Bicep files for this phase deploy cleanly from scratch if you
      delete the resource group and redeploy

## Why This Matters (Business Context)
A firewall rule change breaks connectivity between two services and nobody can tell if it's DNS, routing, or the NSG without hours of guessing. Network Watcher's diagnostic tools turn 'we think it's the network' into an actual answer in minutes.

## Service Deep Dive

### What It Can't Do
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
docs.*

