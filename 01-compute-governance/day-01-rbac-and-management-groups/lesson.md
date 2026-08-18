# Day 01 Lesson - RBAC and Management Groups

## Core Concepts (Read This First)

### What a Management Group Actually Is
A management group is a container that sits above subscriptions, purely
for governance - it has nothing to do with billing (that's what a
subscription is for). Its whole job is letting you assign RBAC roles and
Azure Policy once, at the top, and have that assignment flow down
automatically to every subscription, resource group, and resource
underneath it. Without management groups, a company with 50 subscriptions
would need to apply the same policy 50 separate times, with 50 separate
chances to get it wrong or forget one.

### The Hierarchy
Every Azure tenant has exactly one **Tenant Root Group** at the very top -
Azure creates it automatically, you can't delete it or move it, and its
ID is the same as your tenant ID. Every subscription in the tenant lands
under the Tenant Root Group by default when it's created. Below the root,
you can build up to **six levels** of your own custom management groups
(that limit doesn't count the root itself or the subscription level).
Each management group or subscription can only have one direct parent,
but a management group can have as many children as you want.

A typical shape looks like: Tenant Root Group -> "Contoso" -> "Production"
/ "Non-Production" -> individual subscriptions underneath each. Real
organizations rarely use all six levels - going deeper makes it harder to
reason about what's inheriting from where.

### Inheritance
Anything assigned at a management group - a policy, an RBAC role -
applies to everything below it in the tree, automatically, with no extra
step. Assign "deny VM creation outside East US" at the "Production"
management group, and every subscription, resource group, and resource
under Production inherits that rule the moment it's created, whether or
not anyone remembers to reapply it. This is the entire reason management
groups exist.

### Why This Needs a Different Scope Than Everything Else
Every deployment you've been thinking about so far targets a resource
group (`az deployment group create`). Management groups don't live inside
a resource group or a subscription the way most resources do - they sit
at the very top. Creating one requires deploying at `tenant` scope, using
`scope: tenant()` on the resource itself. Day 00's "Scope and
targetScope" section covers this in full if you haven't read it yet.

```bicep
targetScope = 'tenant'

param mgName string
param mgDisplayName string
param parentMgId string   // e.g. your tenant ID, to parent under the Tenant Root Group

resource managementGroup 'Microsoft.Management/managementGroups@2024-02-01-preview' = {
  scope: tenant()
  name: mgName
  properties: {
    displayName: mgDisplayName
    details: {
      parent: {
        id: '/providers/Microsoft.Management/managementGroups/${parentMgId}'
      }
    }
  }
}
```

Deploying this needs `az deployment tenant create`, not the
`az deployment group` commands you've used so far - and it needs
Owner-level permission at the tenant scope, a real permission boundary,
not just a syntax difference. If your account doesn't have that,
building the hierarchy through the Portal for the lab and only
referencing it (with `existing`) in Bicep is the realistic path - which
is exactly what this day's lab objective has you do.

### How This Connects Back to RBAC
A custom role's `assignableScopes` (below) isn't limited to subscriptions
- it can point at a management group ID too, meaning "this role can be
handed out anywhere under this branch of the org," not just one
subscription. Management groups and RBAC are two separate systems, but
they're designed to be used together at scale.

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

## Service Deep Dive

### What It Can't Do
RBAC is purely additive - there's no "deny" the way an NSG rule can deny
traffic. If a principal has Contributor from one assignment and a
tightly-scoped custom role from another, they get the *union* of both;
the custom role's `notActions` only carves exceptions out of that same
role's own `actions`, it can't strip a permission granted by a completely
separate assignment. The one real exception is a **deny assignment**, a
separate ARM construct that explicitly blocks specific actions regardless
of role - but you don't hand-write these day to day; they mostly show up
generated by Azure Blueprints or managed applications.

Role assignment changes also aren't instant. Azure's control plane can
take several minutes to propagate a new or removed assignment everywhere
it needs to - if you grant yourself a role and immediately get a 403
testing it, that's often propagation delay, not a broken assignment.

Management groups can't represent every org shape either: each management
group or subscription has exactly one direct parent, so there's no way to
model a subscription that logically belongs under two different branches
at once.

### Nuances Worth Knowing
- **Hard, unraisable limits exist and real organizations hit them.** 4,000
  role assignments per subscription (counting subscription-, resource-
  group-, and resource-scoped assignments together, not management-group
  ones), 500 per management group, and 5,000 custom role definitions per
  tenant. None of these can be increased by a support ticket - the
  documented fix is always "assign to groups instead of individual
  principals" and "consolidate duplicate custom roles."
- **`principalType` isn't decorative.** Feeding a role assignment the
  wrong `principalType` (labeling a group as `'User'`, for instance) is a
  common way for an assignment to silently not behave as expected,
  especially right after creating a brand-new group or service principal,
  since Azure's directory lookup can lag a few seconds behind the object
  actually existing.
- **A `CanNotDelete` lock on a resource group doesn't override RBAC, it
  sits on top of it** - even a Subscription Owner can't delete a locked
  resource until the lock itself is removed. Day 03 covers this in full.

### Troubleshooting You'll Actually Hit
- **Error:** `RoleAssignmentLimitExceeded` (`No more role assignments can
  be created`) -> **Cause:** hit the 4,000-per-subscription (or
  500-per-management-group) cap -> **Fix:** find principals with
  duplicate individual assignments and consolidate them into a
  group-based assignment instead - Azure Resource Graph has a documented
  query pattern for finding these.
- **Symptom:** a role assignment against a brand-new Entra group or
  freshly created managed identity fails with a "principal not found"
  style error even though the object clearly exists in the portal ->
  **Cause:** Entra directory replication lag - the object exists but
  hasn't fully propagated to the identity lookup RBAC uses ->
  **Fix:** retry after a short wait, or (in scripts) add a brief
  delay/retry loop between creating the principal and assigning the role.
- **Symptom:** a permission you just granted still returns a 403 ->
  **Cause:** RBAC propagation delay, typically resolves within a few
  minutes -> **Fix:** wait and retest before assuming the assignment
  itself is wrong; check the assignment's scope and `principalId` only if
  it's still failing after several minutes.

*Checked against: Microsoft Learn's "Troubleshoot Azure RBAC limits" and
"Azure custom roles" docs for the exact limit numbers.*


## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-rbac>
<https://learn.microsoft.com/en-us/azure/role-based-access-control/quickstart-role-assignments-bicep>

## Why This Matters (Business Context)
A new hire in finance needs read-only access to cost data, not the ability to delete production VMs. Without RBAC scoped correctly, companies either lock everything down so tight nobody can do their job, or leave everything open so one mistake (or one compromised account) can take down the whole environment. Management groups exist because a 200-subscription company can't apply policy one subscription at a time - they say 'everything under Finance follows this rule' once, and it inherits down automatically.
