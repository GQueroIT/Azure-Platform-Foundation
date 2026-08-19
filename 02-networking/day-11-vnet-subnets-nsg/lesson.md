# Day 11 Lesson - VNet, Subnets, and NSGs

## Core Concepts (Read This First)

### What a Subnet Actually Is
A VNet owns a block of IP addresses (this lesson's example uses
`10.0.0.0/16` - 65,536 addresses). A subnet carves out a smaller,
non-overlapping slice of that block (`10.0.1.0/24` - 256 addresses) for a
specific group of resources. Resources in different subnets within the
same VNet can still talk to each other by default (unless an NSG says
otherwise) - subnets are about organization and applying different rules
to different groups of resources, not automatic isolation.

### NSGs Are Stateful
This is the detail that trips people up on the exam: if an NSG rule
allows inbound traffic on a port, the *response* to that traffic is
automatically allowed back out - you do not need a matching outbound rule
for a reply. Stateful means the NSG tracks the connection, not just each
packet in isolation. You only need explicit outbound rules for traffic
your resource *initiates* outward, not for replying to something that
came in.

### NSGs Can Apply at Two Levels
An NSG can be associated with a subnet, a network interface (NIC), or
both at once. When both apply to the same VM's traffic, Azure evaluates
both sets of rules - traffic has to pass both to get through. This is a
common source of "why is this blocked, I definitely allowed it" - the
rule you're looking at might be right, and the other NSG might be the one
blocking it.

## What You're Building Today
A virtual network with subnets, and a network security group with custom
rules attached to one of them.

## New Bicep Concepts
- Defining subnets inline on the VNet resource (the recommended way)
- `securityRules` as an array of rule objects, each with a `priority`

## Annotated Example
```bicep
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-lab'
  location: resourceGroup().location
  properties: {
    addressSpace: {
      addressPrefixes: [ '10.0.0.0/16' ]
    }
    subnets: [
      {
        name: 'subnet-app'
        properties: {
          addressPrefix: '10.0.1.0/24'
        }
      }
    ]
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-app'
  location: resourceGroup().location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPSInbound'
        properties: {
          priority: 300
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}
```

## Why It's Written This Way
- Subnets are defined INSIDE the `properties.subnets` array on the VNet
  resource, not as a separate top-level resource. Microsoft's own docs
  specifically warn against defining subnets as a separate child resource
  type - doing so can cause the subnet to briefly disappear during
  redeployments, which can knock resources offline. Keep subnets nested.
- `priority` on an NSG rule matters a lot - lower numbers are evaluated
  first, and the first matching rule wins. Built-in rules always sit above
  65000, so your custom rules (in the low hundreds/thousands) always take
  precedence if written correctly.
- NSG rules aren't attached to a subnet automatically just by being in the
  same resource group - you associate an NSG with a subnet by setting the
  subnet's `networkSecurityGroup` property to point at the NSG's `.id`
  (not shown above for brevity, but you'll need it to actually apply
  these rules).

## Service Deep Dive

### What It Can't Do
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
and Azure networking documentation on subnet address reservation.*


## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-virtual-networks>
<https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.NSG.AnyInboundSource/>

## Why This Matters (Business Context)
A company puts its database on the same open subnet as its public-facing web server. One vulnerability in the web app and the database is directly reachable. Subnets and NSGs are what stop a compromised front-end from automatically meaning a compromised back-end.
