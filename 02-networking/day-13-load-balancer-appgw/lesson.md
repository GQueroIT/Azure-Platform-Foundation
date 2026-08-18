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

## Service Deep Dive

### What It Can't Do
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
Application Gateway" docs.*


## Source
Structure based on `Microsoft.Network/loadBalancers` general resource
patterns - see <https://learn.microsoft.com/en-us/azure/templates/microsoft.network/loadbalancers>
for the full property reference.

## Why This Matters (Business Context)
A company's app runs fine on one server until that server needs a restart for a patch, and the site goes down during the restart. A load balancer means traffic just shifts to the healthy instances during a rolling update, and customers never notice.
