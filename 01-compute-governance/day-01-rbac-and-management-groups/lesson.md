# Day 01 Lesson - RBAC and Management Groups

## What You're Building Today
A management group hierarchy and a custom RBAC role, in Bicep.

## New Bicep Concepts
- `scope` property - tells Bicep WHERE a resource applies, separate from
  where it's deployed from
- `guid()` function - generates a deterministic unique ID, required for
  role assignment names
- `existing` keyword - referencing a built-in role instead of recreating it

## Annotated Example
Assigning a built-in role to a principal (a user, group, or service
identity) on a resource group:
```bicep
param principalId string
param principalType string = 'ServicePrincipal'

resource contributorRoleDefinition 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: subscription()
  name: 'b24988ac-6180-42a0-ab88-20f7382dd24c'   // built-in Contributor role ID
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, principalId, contributorRoleDefinition.id)
  properties: {
    roleDefinitionId: contributorRoleDefinition.id
    principalId: principalId
    principalType: principalType
  }
}
```

## Why It's Written This Way
- The `existing` block doesn't create anything - built-in roles like
  Contributor already exist in every Azure tenant. You're just getting a
  reference to it so you can use its `.id` below.
- `scope: subscription()` on that existing reference matters: built-in role
  definitions live at the subscription level, not the resource group level,
  so Bicep needs to be told to look there.
- The `guid()` function is required because `Microsoft.Authorization/roleAssignments`
  needs a GUID as its name, and it has to be the same GUID every time you
  redeploy the same assignment (otherwise Azure would try to create a
  duplicate). Feeding `guid()` the same three inputs every time
  (`resourceGroup().id`, `principalId`, `contributorRoleDefinition.id`)
  guarantees that.
- `principalType` matters more than it looks - if you get it wrong (e.g.
  labeling a group as `'User'`), the assignment can silently fail to work
  as expected.

## For a Custom Role Instead of a Built-In One
```bicep
resource customRole 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' = {
  name: guid('custom-vm-operator-role')
  properties: {
    roleName: 'Custom VM Operator'
    description: 'Can start and restart VMs, cannot delete them'
    assignableScopes: [
      subscription().id
    ]
    permissions: [
      {
        actions: [
          'Microsoft.Compute/virtualMachines/start/action'
          'Microsoft.Compute/virtualMachines/restart/action'
          'Microsoft.Compute/virtualMachines/read'
        ]
        notActions: []
      }
    ]
  }
}
```
`actions` is an allow-list of specific operations (not full role names like
"Contributor") - these come from Azure's resource provider operation list,
which you can browse per-service in the Azure docs.

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-rbac>
<https://learn.microsoft.com/en-us/azure/role-based-access-control/quickstart-role-assignments-bicep>

## Why This Matters (Business Context)
A new hire in finance needs read-only access to cost data, not the ability to delete production VMs. Without RBAC scoped correctly, companies either lock everything down so tight nobody can do their job, or leave everything open so one mistake (or one compromised account) can take down the whole environment. Management groups exist because a 200-subscription company can't apply policy one subscription at a time - they say 'everything under Finance follows this rule' once, and it inherits down automatically.
