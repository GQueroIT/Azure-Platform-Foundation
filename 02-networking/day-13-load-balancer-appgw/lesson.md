# Day 13 Lesson - Load Balancer and Application Gateway

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