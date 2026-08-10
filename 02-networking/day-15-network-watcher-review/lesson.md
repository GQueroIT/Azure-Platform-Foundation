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
