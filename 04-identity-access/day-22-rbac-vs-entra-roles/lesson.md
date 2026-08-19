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

## Service Deep Dive

### What It Can't Do
Being Global Administrator in Entra ID grants nothing at all in Azure by
default - not Reader, not Contributor, nothing. The two systems are
deliberately, completely separate authorization models: Entra role
assignments don't grant Azure resource access, and Azure RBAC
assignments don't grant Entra ID access. A brand-new Global Admin
signing into the Azure portal for the first time can see zero
subscriptions, not because anything is broken, but because that's simply
how the systems are designed to work.

Entra roles also can't scope the same granular way Azure RBAC can. Azure
RBAC scopes to a management group, subscription, resource group, or
individual resource; most Entra roles are tenant-wide by default
(Administrative Units narrow some Entra roles to a subset of users or
groups, but it's a fundamentally coarser scoping model than Azure RBAC's).

### Nuances Worth Knowing
- There's exactly one documented bridge between the two systems: a
  Global Administrator can flip "Access management for Azure resources"
  to Yes under Microsoft Entra ID > Properties, which grants User Access
  Administrator in Azure RBAC at the tenant root scope (`/`) - not
  permanently, and not automatically. It's a one-time elevation a Global
  Admin has to explicitly trigger, and Microsoft's own guidance is to
  remove that elevated role assignment once the task is done rather than
  leaving it in place.
- That elevation setting is per-user, not global - triggering it
  elevates the specific signed-in Global Administrator's own access; it
  doesn't elevate every Global Administrator in the tenant at once.
- The resulting User Access Administrator role at root scope is enough
  to *assign* access to any subscription or management group, but it
  isn't the same as being Owner or Contributor everywhere - it's
  specifically an access-management role.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Global Administrator signs into the Azure portal and
  sees no subscriptions, or can't see/manage one someone else created ->
  **Cause:** exactly the expected behavior when the two authorization
  systems have never been bridged - Global Admin status alone was never
  going to grant Azure access -> **Fix:** use the "Access management for
  Azure resources" toggle in Entra ID Properties to self-elevate to User
  Access Administrator at root scope, make the needed change, then
  remove the elevated assignment again afterward.
- **Symptom:** switching directories/tenants in the portal seems to fix
  a similar-looking access problem for someone else -> **Cause:** a
  different, more common cause of "I can't see my subscription" is
  simply being signed into the wrong Entra tenant, which looks identical
  to a genuine RBAC gap at first glance -> **Fix:** confirm the correct
  directory is selected before assuming it's an RBAC/Entra-role mismatch
  at all.
- **Symptom:** an automation app or service account needs visibility
  across every subscription in the tenant -> **Cause:** this is one of
  the intended real use cases for elevated access, not a workaround ->
  **Fix:** use the same elevation mechanism to grant that principal User
  Access Administrator at root scope, deliberately and temporarily.

*Checked against: Microsoft Learn's "Elevate access to manage all Azure
subscriptions and management groups" doc.*


## Source
<https://learn.microsoft.com/en-us/graph/templates/overview-bicep-templates-for-graph>

## Why This Matters (Business Context)
A well-meaning admin grants someone Global Administrator in Entra ID to fix an Azure resource permission problem, not realizing the two systems are unrelated. That's a massively over-scoped grant for a problem RBAC alone would have solved. Knowing the actual boundary between the two systems is what prevents that kind of accidental over-permissioning.
