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

## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworks/virtualnetworkpeerings>

## Why This Matters (Business Context)
Two teams each built their own VNet for their own project, and now a shared service needs to talk to both without routing traffic over the public internet. Peering keeps that traffic on Microsoft's backbone instead of exposing it externally; private DNS means internal services find each other by name instead of hardcoded IPs that break the moment something gets redeployed.
