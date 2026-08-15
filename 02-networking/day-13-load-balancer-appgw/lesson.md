# Day 13 Lesson - Load Balancer and Application Gateway

## Core Concepts (Read This First)

### Load Balancer vs Application Gateway - The Actual Difference
This day's title mentions both, but the example only builds a Load
Balancer - worth understanding both before moving on, since mixing them
up is one of the most common AZ-104 exam traps. **Load Balancer**
operates at Layer 4 (TCP/UDP) - it only sees IP addresses and ports, has
no idea what HTTP even is, and routes based purely on that.
**Application Gateway** operates at Layer 7 (HTTP) - it can read the
actual request and route based on URL path or hostname (e.g. `/api/*` to
one backend pool, everything else to another), terminate SSL for you, and
optionally run a Web Application Firewall (WAF) in front of your app.
Rule of thumb: pure TCP-level traffic distribution, use Load Balancer;
anything that needs to understand HTTP content to route correctly, use
Application Gateway.

### Public vs Internal Load Balancer
This lesson's example uses a public IP on the frontend, making it
internet-facing. Swap that for a private IP instead (an **Internal Load
Balancer**, sometimes called ILB) and the same resource type distributes
traffic that should never leave the VNet - e.g. balancing traffic between
app-tier VMs that only a web tier inside the same network should ever
reach.

Cost note: Standard Load Balancer bills hourly. Deploy, test, delete same
day - see the root README cost strategy.

## What You're Building Today
A Standard Load Balancer in front of two backend addresses.

## New Bicep Concepts
- A resource with several distinct sub-collections that all reference each
  other by name inside the same resource (frontend, backend pool, rules)

## Annotated Example
```bicep
resource pip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-lb'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource lb 'Microsoft.Network/loadBalancers@2023-11-01' = {
  name: 'lb-web'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: {
    frontendIPConfigurations: [
      {
        name: 'frontend1'
        properties: {
          publicIPAddress: { id: pip.id }
        }
      }
    ]
    backendAddressPools: [
      { name: 'backendPool1' }
    ]
    probes: [
      {
        name: 'httpProbe'
        properties: {
          protocol: 'Tcp'
          port: 80
          intervalInSeconds: 15
          numberOfProbes: 2
        }
      }
    ]
    loadBalancingRules: [
      {
        name: 'httpRule'
        properties: {
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/loadBalancers/frontendIPConfigurations', 'lb-web', 'frontend1')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/loadBalancers/backendAddressPools', 'lb-web', 'backendPool1')
          }
          probe: {
            id: resourceId('Microsoft.Network/loadBalancers/probes', 'lb-web', 'httpProbe')
          }
          protocol: 'Tcp'
          frontendPort: 80
          backendPort: 80
        }
      }
    ]
  }
}
```

## Why It's Written This Way
- Notice `loadBalancingRules` references the frontend, backend pool, and
  probe by ID using `resourceId(...)`, not by pointing at a Bicep symbolic
  name. That's because those three things are sub-resources declared
  *inside the same resource block*, not separate top-level resources -
  `resourceId()` is how you build a reference to something nested that
  deep.
- A load balancer without a probe just guesses backends are healthy. The
  probe is what actually pulls unhealthy instances out of rotation.
- This whole resource bills by the hour the moment it exists - the SKU is
  `'Standard'` specifically because Basic SKU is being retired and is not
  recommended for anything you build going forward.

## Source
Structure based on `Microsoft.Network/loadBalancers` general resource
patterns - see <https://learn.microsoft.com/en-us/azure/templates/microsoft.network/loadbalancers>
for the full property reference.

## Why This Matters (Business Context)
A company's app runs fine on one server until that server needs a restart for a patch, and the site goes down during the restart. A load balancer means traffic just shifts to the healthy instances during a rolling update, and customers never notice.
