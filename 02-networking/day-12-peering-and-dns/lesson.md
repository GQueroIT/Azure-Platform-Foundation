# Day 12 Lesson - VNet Peering and Private DNS

## Core Concepts (Read This First)

### What Private DNS Actually Solves
Without it, a VM in Azure has no way to resolve a custom internal
hostname (like `db.internal.contoso.com`) to another VM's private IP -
you'd be stuck hardcoding IP addresses everywhere, which breaks the
moment anything gets redeployed with a new IP. A private DNS zone gives
you that internal name resolution. To actually work, it has to be linked
to one or more VNets through a **virtual network link** - creating the
zone alone doesn't connect it to anything.

### Peering Is Not Transitive
A genuinely easy mistake to make, and a real exam topic: if VNet A is
peered with VNet B, and VNet B is peered with VNet C, that does **not**
mean A can reach C. Each peering relationship is a direct connection
between exactly two VNets - there's no automatic "pass it along" the way
routing sometimes works elsewhere. If A needs to reach C, A and C need
their own direct peering (or traffic needs to be routed through a
network appliance sitting in B on purpose).

## What You're Building Today
Peering two VNets together, and a private DNS zone.

## New Bicep Concepts
- Referencing two separate `existing` resources to create a relationship
  between them
- Peering is one-directional per resource - two VNets need two peering
  resources, one on each side

## Annotated Example
```bicep
param vnetAName string
param vnetBName string

resource vnetA 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: vnetAName
}

resource vnetB 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: vnetBName
}

resource peeringAtoB 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-11-01' = {
  name: '${vnetAName}-to-${vnetBName}'
  parent: vnetA
  properties: {
    remoteVirtualNetwork: {
      id: vnetB.id
    }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: false
    allowGatewayTransit: false
    useRemoteGateways: false
  }
}

resource peeringBtoA 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-11-01' = {
  name: '${vnetBName}-to-${vnetAName}'
  parent: vnetB
  properties: {
    remoteVirtualNetwork: {
      id: vnetA.id
    }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: false
    allowGatewayTransit: false
    useRemoteGateways: false
  }
}
```

## Why It's Written This Way
- This is the clearest example yet of why `existing` matters: both VNets
  were created on an earlier day, in a different Bicep file. This file
  doesn't recreate them, it just references them so it can build a
  relationship (the peering) between two things that already exist.
- Peering is genuinely two separate resources under the hood, one
  attached as a child of each VNet, each describing the connection from
  that VNet's point of view. Forgetting the second one is the single most
  common peering mistake - the connection will look "half-working."
- `allowGatewayTransit` and `useRemoteGateways` are opposite ends of the
  same relationship (one VNet offers its gateway, the other uses it) -
  they show up again if you build the VPN Gateway lab this week.

## Service Deep Dive

### What It Can't Do
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
propagation and sync problems" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworks/virtualnetworkpeerings>

## Why This Matters (Business Context)
Two teams each built their own VNet for their own project, and now a shared service needs to talk to both without routing traffic over the public internet. Peering keeps that traffic on Microsoft's backbone instead of exposing it externally; private DNS means internal services find each other by name instead of hardcoded IPs that break the moment something gets redeployed.
