# Bicep Syntax Cheat Sheet

Quick lookup for syntax patterns used across this repo. This is a
reference, not a tutorial - see Day 00's lesson.md for the explanations
behind each of these.

## File Structure

```bicep
targetScope = 'resourceGroup'          // optional, this is the default

param environmentName string = 'dev'   // input
var fullName = 'proj-${environmentName}'  // computed
resource myThing 'Type@version' = { }  // actual Azure resource
module sub './file.bicep' = { }        // call another Bicep file
output myOutput string = myThing.id    // value returned after deploy
```

## Scope

```bicep
targetScope = 'subscription'   // resourceGroup (default) | subscription | managementGroup | tenant

resource thing 'Type@version' = {
  scope: subscription()        // overrides targetScope for THIS resource only
}
```

| Scope | Deploy command | Can create |
|---|---|---|
| resourceGroup | `az deployment group create` | resources inside the RG |
| subscription | `az deployment sub create` | resource groups, subscription-level resources |
| managementGroup | `az deployment mg create` | policy/RBAC at MG level, child MGs |
| tenant | `az deployment tenant create` | management groups |

## Existing Resources

```bicep
resource myVnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: 'vnet-lab'
}
// Reference only - creates nothing. Use myVnet.id, myVnet.properties.x below.
```

## Dependencies

```bicep
// Implicit (preferred) - referencing a property creates the order automatically
resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  properties: {
    networkProfile: {
      networkInterfaces: [ { id: nic.id } ]   // <- this line creates the dependency
    }
  }
}

// Explicit (rare) - only when there's no property link to reference
resource second 'Type@version' = {
  dependsOn: [ first ]
}
```

## Decorators

```bicep
@secure()
param adminPassword string

@description('what this param is for')
param environmentName string

@allowed([ 'dev', 'staging', 'prod' ])
param environmentType string

@minLength(3)
@maxLength(24)
param storageAccountName string

@minValue(1)
@maxValue(10)
param instanceCount int
```

## Loops

```bicep
resource subnets 'Microsoft.Network/virtualNetworks/subnets@2023-11-01' = [for name in subnetNames: {
  name: name
  parent: vnet
}]

// with index
resource things 'Type@version' = [for (item, i) in items: {
  name: 'thing-${i}'
}]
```

## Conditions

```bicep
resource bastion 'Microsoft.Network/bastionHosts@2023-11-01' = if (deployBastion) {
  name: 'bastion-lab'
}
```

## Parent / Child Resources

```bicep
// Modern style
resource policy 'Microsoft.RecoveryServices/vaults/backupPolicies@2023-04-01' = {
  name: 'daily-policy'
  parent: vault
}

// Older style, same result
resource policy 'Microsoft.RecoveryServices/vaults/backupPolicies@2023-04-01' = {
  name: '${vault.name}/daily-policy'
}
```

## Common Functions

| Function | Returns |
|---|---|
| `resourceGroup()` | current resource group's `.location`, `.name`, `.id` |
| `subscription()` | current subscription's properties |
| `tenant()` | current tenant's properties |
| `managementGroup()` | current management group's properties (MG-scoped files only) |
| `uniqueString(...)` | deterministic hash - for globally-unique names |
| `guid(...)` | deterministic GUID - for role assignment names |
| `resourceId(...)` | full resource ID string, for cross-resource-group references |

## RBAC Role Assignment (built-in role)

```bicep
param principalId string
param principalType string = 'ServicePrincipal'

resource role 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: subscription()
  name: 'b24988ac-6180-42a0-ab88-20f7382dd24c'   // Contributor
}

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, principalId, role.id)
  properties: {
    roleDefinitionId: role.id
    principalId: principalId
    principalType: principalType
  }
}
```

## Management Group (tenant scope)

```bicep
targetScope = 'tenant'

resource mg 'Microsoft.Management/managementGroups@2024-02-01-preview' = {
  scope: tenant()
  name: 'mg-name'
  properties: {
    displayName: 'Display Name'
    details: {
      parent: {
        id: '/providers/Microsoft.Management/managementGroups/${parentMgId}'
      }
    }
  }
}
```

## Validation, Every Day

```bash
az bicep build --file solution.bicep
az deployment group validate --resource-group <rg> --template-file solution.bicep
az deployment group what-if --resource-group <rg> --template-file solution.bicep
```
