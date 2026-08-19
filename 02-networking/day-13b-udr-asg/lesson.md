# Day 13b Lesson - User-Defined Routes and Application Security Groups

## Core Concepts (Read This First)

### NSGs Decide "Allowed," Routes Decide "Where"
Easy to conflate, genuinely separate questions. An NSG answers "is this
traffic allowed through at all." A route table answers "once it's
allowed, which direction does it actually travel." A design that forces
traffic through a firewall appliance for inspection depends entirely on
routing, not NSG rules - the NSG could allow the traffic perfectly and it
still won't reach the firewall unless a route says to send it there
first.

### ASGs Replace IP Addresses With Roles
An Application Security Group doesn't do anything by itself - it's a
label. You add VM NICs to it, then reference the ASG (instead of a raw
IP address or range) as the source or destination in an NSG rule. The
payoff: "allow AsgWeb to reach AsgDb on 1433" reads as an actual policy
statement and keeps working automatically as VMs are added or removed
from the group, instead of a rule needing to be hand-edited every time
the IP addresses behind it change.

## What You're Building Today
A route table sending subnet traffic through a virtual appliance's NIC,
and NSG rules that reference application security groups instead of IP
ranges.

## New Bicep Concepts
- `Microsoft.Network/routeTables` and its child `routes` collection
- `Microsoft.Network/applicationSecurityGroups` - referenced by ID inside
  an NSG rule's source/destination, not associated with a subnet like an
  NSG is

## Annotated Example
```bicep
resource routeTable 'Microsoft.Network/routeTables@2023-11-01' = {
  name: 'rt-spoke'
  location: resourceGroup().location
  properties: {
    routes: [
      {
        name: 'force-through-firewall'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'VirtualAppliance'
          nextHopIpAddress: '10.0.0.4'   // private IP of the NVA's NIC
        }
      }
    ]
  }
}

resource asgWeb 'Microsoft.Network/applicationSecurityGroups@2023-11-01' = {
  name: 'asg-web'
  location: resourceGroup().location
}

resource asgDb 'Microsoft.Network/applicationSecurityGroups@2023-11-01' = {
  name: 'asg-db'
  location: resourceGroup().location
}

resource nsgRule 'Microsoft.Network/networkSecurityGroups/securityRules@2023-11-01' = {
  name: '${nsg.name}/allow-web-to-db'
  properties: {
    priority: 200
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourceApplicationSecurityGroups: [ { id: asgWeb.id } ]
    destinationApplicationSecurityGroups: [ { id: asgDb.id } ]
    sourcePortRange: '*'
    destinationPortRange: '1433'
  }
}
```

## Why It's Written This Way
- `nextHopType: 'VirtualAppliance'` plus an explicit `nextHopIpAddress`
  is what actually redirects traffic - `nextHopType` alone without the IP
  isn't enough for this hop type.
- The NIC on the virtual appliance receiving forwarded traffic needs
  "Enable IP forwarding" turned on - a setting on the NIC resource, not
  on the route table - or the appliance drops traffic that isn't
  addressed directly to itself.
- ASGs are referenced by `id`, not embedded inline, because they're
  independent resources a NIC gets added to separately (via the NIC's IP
  configuration) - the NSG rule and the ASG membership are two different
  places in the config, on purpose.

## Service Deep Dive

### What It Can't Do
A subnet can only have one route table associated at a time - no
stacking two route tables the way NSGs can layer at subnet and NIC
level. All network interfaces in a given ASG have to live in the same
virtual network as the first NIC added to it - you can't mix NICs from
different VNets into one ASG. And if an NSG rule references ASGs as both
source and destination, both ASGs' NICs have to be in that same single
VNet too - a rule can't bridge ASGs across VNets even indirectly.

### Nuances Worth Knowing
- A route with `nextHopType: 'None'` deliberately drops matching
  traffic - Azure's own default system routes use this for reserved
  address ranges outside the VNet, and it's also how you'd build an
  explicit blackhole route on purpose.
- Network Watcher's Next Hop tool exists specifically to answer "what
  will actually happen to this traffic" - given a source VM and a
  destination IP, it reports the real next hop type in effect, which is
  the fastest way to confirm whether a UDR is actually being applied the
  way you think it is.
- A single NSG rule can reference up to 10 ASGs in its source or
  destination - useful to know before assuming a rule needs to be split
  across multiple rules for a design with several role groups.
- 0.0.0.0/0 forced through a virtual appliance is powerful but has real
  documented edge cases with services like Azure Route Server and
  certain Private Link/IPv6 traffic - a catch-all route isn't always as
  total as it looks.

### Troubleshooting You'll Actually Hit
- **Symptom:** two VMs in different subnets of the same VNet can't reach
  each other, and NSG rules all look correct -> **Cause:** likely a
  routing issue, not a security-rule issue - a UDR overriding the
  default VNet-local route -> **Fix:** run Network Watcher's Next Hop
  tool between the two VMs; if the next hop type is `VirtualAppliance` or
  `None` instead of `VnetLocal`, a route table is redirecting or dropping
  the traffic before the NSG is even the relevant layer to check.
- **Symptom:** traffic forced through a virtual appliance never arrives,
  even though the route table and NSG both look correct -> **Cause:**
  the appliance's NIC doesn't have IP forwarding enabled, so it silently
  discards traffic not addressed to itself -> **Fix:** enable IP
  forwarding on that specific NIC - a setting easy to miss since it's
  not part of the route table configuration at all.
- **Error:** an NSG rule referencing two ASGs fails to save or apply
  incorrectly -> **Cause:** the ASGs' member NICs aren't all in the same
  VNet, which the rule requires when ASGs sit on both sides -> **Fix:**
  confirm every NIC in both referenced ASGs actually lives in the one
  VNet before building the rule.

*Checked against: Microsoft Learn's "Azure virtual network traffic
routing," "Application security groups overview," and "Network security
groups and application security groups" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview>
<https://learn.microsoft.com/en-us/azure/virtual-network/application-security-groups>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/routetables>

## Why This Matters (Business Context)
A security team wants all outbound traffic inspected by a firewall before it leaves the network, and NSGs alone can't force that path - only routing can. ASGs are the difference between an NSG rule that says '10.0.1.4, 10.0.1.7, 10.0.1.12 through 10.0.1.19 can reach the database' (which breaks the moment a new web server gets a different IP) and one that says 'the web tier can reach the database,' which just keeps working.
