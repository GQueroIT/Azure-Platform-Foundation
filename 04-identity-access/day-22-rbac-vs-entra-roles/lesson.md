# Day 22 Lesson - RBAC vs Entra Roles

## Straight Talk First
This is a concept day more than a syntax day, because the two role systems
live in genuinely different places:
- **Azure RBAC** (`Microsoft.Authorization/roleAssignments`, from Day 01)
  controls who can do what to AZURE RESOURCES - VMs, storage accounts,
  resource groups.
- **Entra roles** (Global Administrator, User Administrator, etc) control
  who can do what inside ENTRA ID ITSELF - creating users, resetting
  passwords, managing tenant settings. These are a completely separate
  permission system.

A person can be a Global Administrator in Entra ID and have zero Azure
RBAC access to any subscription. The two systems do not overlap by
default - this trips up almost everyone the first time they hit it.

## New Bicep Concepts
Assigning an Entra directory role uses the Graph extension from Day 21,
combined with the `roleManagement` Graph resource:
```bicep
extension microsoftGraphV1

param principalUpn string

resource principal 'Microsoft.Graph/users@v1.0' existing = {
  userPrincipalName: principalUpn
}

resource userAdminRole 'Microsoft.Graph/directoryRoles@v1.0' existing = {
  roleTemplateId: 'fe930be7-5e62-47db-91af-98c3a49a38b1'   // User Administrator
}

resource roleAssignment 'Microsoft.Graph/directoryRoleAssignments@v1.0' = {
  principalId: principal.id
  roleDefinitionId: userAdminRole.id
}
```

## Why It's Written This Way
- Notice the resource types here are all `Microsoft.Graph/...`, not
  `Microsoft.Authorization/...` - confirming these live entirely inside
  Entra ID's permission model, separate from anything you built on Day 01.
- `roleTemplateId` is a fixed GUID Microsoft assigns to each built-in
  Entra role - unlike Azure RBAC's role definitions, these aren't
  something you'd typically create custom versions of as a beginner.

## What To Actually Compare Hands-On
Go back to your Day 01 `roleAssignments` Bicep and put it side by side
with this lesson's `directoryRoleAssignments`. Same shape at a glance,
completely different systems underneath.

## Source
<https://learn.microsoft.com/en-us/graph/templates/overview-bicep-templates-for-graph>

## Why This Matters (Business Context)
A well-meaning admin grants someone Global Administrator in Entra ID to fix an Azure resource permission problem, not realizing the two systems are unrelated. That's a massively over-scoped grant for a problem RBAC alone would have solved. Knowing the actual boundary between the two systems is what prevents that kind of accidental over-permissioning.
