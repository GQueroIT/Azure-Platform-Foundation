#!/usr/bin/env python3
"""
Azure-Platform-Foundation - Core Concepts and Reference Hub

WHAT THIS FIXES:
Days 00-20 of this repo were written with a lesson template that jumps
straight to Bicep syntax (What You're Building Today -> New Bicep Concepts
-> Annotated Example) with no section actually teaching the underlying
Azure concept first. Days 21-30 use a richer template with a "Straight
Talk First" section that explains the concept before the syntax. This
script closes that gap for Days 00-06 (the current active phase) by:

1. Expanding Day 00's lesson.md with the Bicep fundamentals every later
   lesson silently assumes (scope/targetScope, existing, dependencies,
   decorators, loops/conditions, built-in functions, deployment commands
   by scope).
2. Adding two new always-available reference files inside the Day 00
   folder: glossary.md (every term used across all 6 phases) and
   bicep-cheatsheet.md (condensed syntax lookup, for use during any day's
   work, not just Day 00).
3. Inserting a "## Core Concepts (Read This First)" section into Days
   01-06's lesson.md, right after the title, teaching the Azure concept
   (management groups, policy effects, lock/RBAC interaction, availability
   zones vs sets, VMSS orchestration modes, disk tiers) before the
   existing syntax walkthrough.

Days 07-20 have the same gap (excluding the checkpoint/self-test days
09, 10, 15, 20, which already work fine as-is) and ARE fixed by this
script - see the printed summary at the end for what's covered.

Safe to re-run: every insertion is guarded by a marker check, so running
this twice does not duplicate content. Does not touch lab.md or
solution.bicep files. Does not overwrite existing content in lesson.md -
only inserts new sections.

Run from anywhere; resolves the repo root from this script's own location
(python-scripts/, one level below repo root).
"""

import sys
from pathlib import Path

# --- Resolve repo root (this script lives in python-scripts/, one level below root) ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if not (REPO_ROOT / "README.md").exists():
    print(f"ERROR: expected repo root at {REPO_ROOT} but no README.md found there.")
    print("This script must live in python-scripts/, one level below the repo root.")
    sys.exit(1)

PHASE_1 = REPO_ROOT / "01-compute-governance"

# CORE_CONCEPTS spans four phase folders - resolved by searching each one
# for the day slug, rather than hardcoding which phase each day belongs to.
PHASE_DIRS = [
    REPO_ROOT / "01-compute-governance",
    REPO_ROOT / "01b-app-hosting",
    REPO_ROOT / "02-networking",
    REPO_ROOT / "03-storage",
]


def find_day_dir(day_slug: str):
    """Search all known phase folders for a day-NN-slug directory."""
    for phase_dir in PHASE_DIRS:
        candidate = phase_dir / day_slug
        if candidate.exists():
            return candidate
    return None

# =====================================================================
# DAY 00 - LESSON.MD ADDITIONS
# =====================================================================

DAY00_MARKER = "## Scope and `targetScope`"

DAY00_LESSON_ADDITION = """

## Scope and `targetScope`

Every Bicep file has to land somewhere in Azure. By default, that's a
resource group - which is why every `az deployment group create` command
in this repo works without you specifying anything extra.

You can change that with `targetScope` at the very top of a file:

```bicep
targetScope = 'subscription'
```

Four values exist: `resourceGroup` (the default, so you rarely write it),
`subscription`, `managementGroup`, and `tenant`. Each one goes with its own
CLI command family - `az deployment group`, `az deployment sub`,
`az deployment mg`, `az deployment tenant`. A file targeting `subscription`
scope can create resource groups themselves (which a resource-group-scoped
file can't, since it's already inside one).

Separately from `targetScope`, individual resources have their own `scope`
property. This lets one resource in the file point somewhere other than
wherever the file itself is targeting - you'll see this in Day 01,
referencing the built-in Contributor role with `scope: subscription()`
even while the rest of the file deploys to a resource group. `targetScope`
sets the file's default; `scope` on a specific resource overrides it for
that one resource.

## The `existing` Keyword

Not everything a Bicep file touches needs to be created by that file.
`existing` marks a resource as "already there - just give me a reference
to it":

```bicep
resource myVnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: 'vnet-lab'
}
```

Nothing about this line creates or changes the VNet. It just lets the rest
of the file use `myVnet.id` or `myVnet.properties.something` to build a
relationship - attach an NSG, create a peering, assign a role. You'll use
`existing` constantly once resources start depending on things built in
earlier deployments, since a given Bicep file usually only owns one slice
of the overall build.

## Dependencies: Implicit vs Explicit

Bicep needs to know what order to create things in - you can't attach a
NIC to a VM before the NIC exists. Most of the time you never write that
ordering by hand. Referencing another resource's property (like `nic.id`
inside a VM's `networkProfile`) automatically tells Bicep "this depends on
that," and Bicep sorts out the deployment order for you. This is an
**implicit dependency**.

Sometimes two resources depend on each other with no property link between
them - nothing to reference. For that, there's an explicit `dependsOn`:

```bicep
resource second 'Microsoft.Something/thing@2024-01-01' = {
  name: 'second'
  dependsOn: [
    first
  ]
}
```

You'll rarely need this in this repo, because almost every dependency here
is implicit. If you ever find yourself reaching for `dependsOn`, it's
worth double-checking there isn't a property reference that would create
the dependency for free.

## Decorators

A decorator is a line starting with `@` placed directly above a `param`,
tightening what's allowed:

```bicep
@secure()
param adminPassword string

@description('Environment name, used in resource naming')
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

- `@secure()` - Azure won't log the value or show it in deployment history
  or the portal. Always use it for passwords, keys, connection strings.
- `@description()` - shows up as help text if this template is ever
  deployed through the portal's generated UI. Doesn't affect deployment
  behavior.
- `@allowed()` - deployment fails immediately if the value isn't one of
  the listed options, instead of failing later against Azure's own
  validation.
- `@minLength()` / `@maxLength()`, `@minValue()` / `@maxValue()` - catch
  bad input before it ever reaches Azure.

## Loops and Conditions

Deploying more than one of something without copy-pasting the resource
block:

```bicep
param subnetNames array = [ 'subnet-app', 'subnet-data' ]

resource subnets 'Microsoft.Network/virtualNetworks/subnets@2023-11-01' = [for name in subnetNames: {
  name: name
  parent: vnet
  properties: {
    addressPrefix: '10.0.1.0/24'
  }
}]
```

`[for item in collection: { ... }]` runs the resource block once per item.
There's also an index version - `[for (item, i) in collection: { ... }]` -
for when you need the position, e.g. to build unique addresses per item.

Deploying a resource only under certain conditions uses `if`:

```bicep
param deployBastion bool = false

resource bastion 'Microsoft.Network/bastionHosts@2023-11-01' = if (deployBastion) {
  name: 'bastion-lab'
}
```

If `deployBastion` is `false`, this resource is skipped entirely - not
deployed with empty values, just not deployed at all.

## Common Built-in Functions

A handful of these show up in nearly every lesson from here on:

- `resourceGroup()` - the current resource group's properties (`.location`,
  `.name`, `.id`)
- `subscription()` - same idea, one level up
- `tenant()` - same idea, one level up again
- `managementGroup()` - the current management group's properties, only
  valid in a management-group-scoped file
- `uniqueString(...)` - a deterministic hash from whatever you feed it,
  used to generate names that have to be globally unique (storage
  accounts, Key Vaults) without you hand-picking a name that might already
  be taken
- `guid(...)` - a deterministic GUID from whatever you feed it, used
  anywhere Azure requires a GUID-shaped name (role assignments, most
  notably)
- `resourceId(...)` - builds the full resource ID string for a resource,
  sometimes needed when you can't reference a symbolic name directly (e.g.
  pointing at a resource in a different resource group)

## Deployment Commands, By Scope

Matching `targetScope` to the CLI command that actually runs it:

| targetScope | Validate | What-if | Deploy |
|---|---|---|---|
| `resourceGroup` (default) | `az deployment group validate` | `az deployment group what-if` | `az deployment group create` |
| `subscription` | `az deployment sub validate` | `az deployment sub what-if` | `az deployment sub create` |
| `managementGroup` | `az deployment mg validate` | `az deployment mg what-if` | `az deployment mg create` |
| `tenant` | `az deployment tenant validate` | `az deployment tenant what-if` | `az deployment tenant create` |

Every day so far in this repo has used the `group` versions without you
needing to think about it. Day 01 is the first day that needs a different
one - you can't create a management group from inside a
resource-group-scoped file, because a management group doesn't live inside
a resource group at all.
"""

# =====================================================================
# DAY 00 - GLOSSARY.MD (new file)
# =====================================================================

DAY00_GLOSSARY = """# Glossary - Azure-Platform-Foundation

Every term used across all 6 phases of this repo, in one place. If a
lesson uses a word you haven't seen defined yet, check here before
searching outside the repo. Organized alphabetically.

## A

**Action Group** - a reusable set of notification/response targets
(email, SMS, webhook, Azure Function, etc) that alerts and budgets point
at, instead of each one defining its own contact list from scratch.

**Actions / notActions** - the two arrays inside a custom RBAC role
definition. `actions` is an allow-list of specific operations (not full
role names). `notActions` carves exceptions out of what `actions` already
granted - it's subtractive, not a separate restriction.

**Alert (metric alert)** - a rule that watches a metric (CPU, response
time, queue length) against a threshold and fires when it's crossed,
usually pointed at an Action Group to decide what happens next.

**Assignable Scopes** - the list on a custom role definition controlling
where that role is allowed to be assigned (a specific resource group, a
subscription, a management group) - not who can receive it, not what
regions it works in.

**Availability Set** - a logical grouping of VMs within a single Azure
datacenter, spread across separate update/fault domains so one hardware
failure or planned maintenance event doesn't take out every VM at once.
Protects against failures inside one datacenter. Compare Availability
Zone.

**Availability Zone** - a physically separate datacenter within an Azure
region, with independent power, cooling, and networking. Spreading VMs
across zones protects against an entire datacenter going down, not just a
single rack. Not every region supports zones.

**Azure Arc** - a service that extends Azure management (policy,
monitoring, tagging) to machines that aren't actually running in Azure -
on-prem servers, other clouds - by installing an agent that registers
them as an Azure resource.

**Azure Bastion** - a managed service that provides RDP/SSH access to VMs
through the Azure portal, without exposing a public RDP/SSH port on the
VM itself. Bills hourly with no pause button.

**Azure Files** - a fully managed file share service, accessible over
SMB/NFS, functioning like a network drive rather than object storage
(compare Blob storage).

**Azure Monitor** - the umbrella platform for collecting metrics, logs,
and alerts across Azure resources. Log Analytics workspaces, alerts, and
diagnostic settings all feed into or are managed under Azure Monitor.

**Azure Policy** - Azure's compliance system: independent of RBAC,
answers "does this comply with the rules?" rather than "is this person
allowed?" See Policy Definition, Policy Assignment, Initiative, Policy
Effect.

## B

**Blob lifecycle management** - a policy on a storage account that
automatically moves blobs between access tiers (Hot/Cool/Archive) or
deletes them based on age, without manual cleanup.

**Budget** - a cost-tracking resource that fires a notification when
spend crosses a threshold. Does NOT stop spending or block deployments by
default - it's an alert, not a cap.

## C

**Conditional Access** - an Entra ID feature that enforces access rules
(require MFA, block legacy auth, require a compliant device) based on
signals like user, location, or device - separate from RBAC, which
governs what you can do once you're in.

**Container App / Container Apps Environment** - a managed service for
running containers without managing the underlying infrastructure,
including the ability to scale to zero (and stop billing) when there's no
traffic. The Environment is the shared boundary multiple Container Apps
can run inside.

**Custom Role** - an RBAC role you define yourself (as opposed to a
built-in role like Contributor), built from `actions`, `notActions`, and
`assignableScopes`.

## D

**Data disk** - an independent, attachable storage resource
(`Microsoft.Compute/disks`) separate from a VM's OS disk. Exists whether
or not it's currently attached, and can be detached and reattached
elsewhere without losing data.

**Decorator** - a line starting with `@` placed above a Bicep `param`
that constrains or annotates it (`@secure()`, `@description()`,
`@allowed()`, `@minLength()`/`@maxLength()`, `@minValue()`/`@maxValue()`).

**Dependency (implicit / explicit)** - how Bicep knows what order to
deploy resources in. Implicit: referencing another resource's property
(like `.id`) automatically creates the dependency. Explicit: `dependsOn`,
used only when there's no property link to create it for free.

**Diagnostic setting** - configuration on an Azure resource that routes
its logs/metrics to a destination - most often a Log Analytics workspace.

## E

**Entra ID** - Microsoft's identity platform (formerly Azure Active
Directory). Manages users, groups, and directory roles - a separate
permission system from Azure RBAC. See RBAC vs Entra roles.

**Existing (keyword)** - marks a Bicep resource as a reference to
something already deployed, rather than something to create. Doesn't
provision anything; just lets the file read properties or attach new
resources to it.

**Extension (Bicep)** - the `extension` directive that loads a capability
Bicep doesn't have natively, most notably `extension microsoftGraphV1`,
which unlocks `Microsoft.Graph/*` resource types for managing Entra ID
resources.

**Extension (VM)** - a small agent Azure installs and runs on a VM after
it boots - not part of the OS image, layered on afterward (e.g. Custom
Script Extension, Azure Monitor Agent).

## F

**Fault domain** - a group of hardware (rack, power source) within a
single datacenter that could fail together. Availability Sets spread VMs
across fault domains.

**Flexible orchestration (VMSS)** - the current Microsoft-recommended
mode for VM Scale Sets, where each instance behaves like a standalone VM
(usable with normal VM APIs, Backup, tagging) while still getting
scale-set-level autoscaling and zone-spreading. Compare Uniform
orchestration.

## G

**guid() function** - a Bicep function that generates a deterministic
GUID from its inputs - same inputs, same output every time, which is why
it's used for role assignment names (so redeploying the same assignment
doesn't try to create a duplicate).

## H

**Hybrid identity** - the general concept of connecting an on-prem
Active Directory to Entra ID, so the same identity works in both places.
Password hash sync, pass-through authentication, and federation are the
three main methods.

## I

**Initiative (policy set)** - a bundle of multiple policy definitions
assigned together in one assignment, instead of one definition at a time
- typically used to represent a whole compliance standard.

## L

**Load Balancer** - distributes network traffic across backend VMs/
instances at Layer 4 (TCP/UDP - IP and port only, no awareness of HTTP
content). Compare Application Gateway, which operates at Layer 7.

**Log Analytics workspace** - the storage/query destination for logs and
metrics collected by Azure Monitor. Diagnostic settings and agents send
data here; you query it with KQL (Kusto Query Language).

## M

**Management group** - a container that sits above subscriptions, purely
for governance (RBAC and Policy inheritance) - not billing. See Tenant
Root Group.

**Module (Bicep)** - a way to call another `.bicep` file from within one,
used to split large deployments into reusable pieces or to deploy across
scope boundaries (e.g. a resource-group-scoped file deploying a module at
tenant scope).

## N

**Network Security Group (NSG)** - a set of allow/deny rules
(`securityRules`) applied to a subnet or NIC, evaluated in priority order
(lowest number first, first match wins).

**Network Watcher** - a diagnostic and monitoring service for Azure
networking (connection troubleshooting, packet capture, topology views).

## O

**Orchestration mode (VMSS)** - the deployment model a VM Scale Set uses,
set once at creation and unable to be changed afterward. See Uniform
orchestration, Flexible orchestration.

**OS disk** - the disk holding the operating system, created inline as
part of the VM resource itself - not optional, not a separate top-level
resource the way a data disk is.

## P

**Parameter (param)** - a Bicep input value supplied at deployment time,
the Bicep equivalent of a function argument.

**Parent / child resource** - a resource that only makes sense nested
under another (a role assignment under a role definition's scope, a
backup policy under a vault). Written either with the `parent:` property
or a manually slash-separated name - both compile to the same thing.

**Peering (VNet)** - a direct connection between two VNets over
Microsoft's backbone rather than the public internet. One-directional per
resource - two VNets need two peering resources, one on each side.

**Policy assignment** - turning a policy definition on at a specific
scope, optionally with parameters.

**Policy definition** - the rule itself: the logic describing what to
check and what to do about it (see Policy Effect). Azure ships hundreds
of built-in definitions.

**Policy effect** - what happens when a resource doesn't comply with a
policy: Deny (blocks the deployment), Audit (flags it as non-compliant,
still deploys), Append (adds a field/value automatically), Modify (alters
existing resource properties, often tags), DeployIfNotExists
(auto-deploys a companion resource if one is missing).

**Principal / principalId / principalType** - the identity (`principal`)
being granted a role, its unique ID (`principalId`), and what kind of
identity it is - User, Group, or ServicePrincipal (`principalType`).
Getting `principalType` wrong can make an assignment silently not work.

**Private DNS zone** - a DNS zone resolvable only from within a
connected VNet, letting internal resources find each other by name
instead of hardcoded IPs.

**Private endpoint** - a network interface with a private IP that
connects privately to a specific Azure service, so that service is
reachable only from inside your network, not the public internet.

## R

**RBAC (Role-Based Access Control)** - Azure's permission system for
resources: who can do what to a VM, storage account, resource group,
etc. Separate from Entra ID's directory roles. RBAC is additive:
permissions from every role assigned across every applicable scope
combine, they don't override each other.

**Recovery Services vault** - the container resource for Azure Backup
and Site Recovery configuration - holds backup policies and tracks
protected items.

**Redundancy (LRS / ZRS / GRS)** - how many copies of storage data Azure
keeps and where. LRS = 3 copies, one datacenter. ZRS = spread across
availability zones in one region. GRS = replicated to a second region
entirely. Each step up costs more.

**Resource group** - a container that holds related Azure resources
together, usually resources that share a lifecycle (deployed and deleted
as a unit).

**Resource lock** - a setting that prevents a resource from being deleted
(`CanNotDelete`) or deleted/modified at all (`ReadOnly`), regardless of
what RBAC role the person acting has. Locks override RBAC on purpose, and
inherit downward from resource group to everything inside it.

**Role assignment** - the act of granting a specific role (built-in or
custom) to a specific principal at a specific scope.

**Role definition** - the role itself, either built-in (Contributor,
Reader, Owner) or custom, describing what actions it permits.

## S

**SAS token (Shared Access Signature)** - a signed, time-limited
credential that grants scoped access to a storage resource, without
sharing the storage account's actual keys.

**Scope (Bicep)** - where a resource or deployment actually applies -
resource group, subscription, management group, or tenant. Most
resources default to resource group scope. Set per-file with
`targetScope`, or overridden per-resource with the `scope` property.

**Security group (Entra)** - a group object in Entra ID used to collect
users for access assignment (RBAC or Entra roles), as opposed to a
Microsoft 365 group.

**Self-Service Password Reset (SSPR)** - lets users reset their own
password without contacting IT, based on pre-registered verification
methods.

**Service principal** - an identity used by an application or automated
process (rather than a human) to authenticate to Azure.

**SKU** - short for "stock keeping unit" - in Azure this almost always
means the pricing tier / size of a resource (e.g. `Standard_LRS`,
`B1s`).

**Standard vs Premium disk** - Standard (HDD or SSD) is cheaper, lower
performance. Premium SSD is the default for performance-sensitive
workloads and requires certain VM sizes. Ultra Disk sits above Premium
for the heaviest, most configurable workloads.

**Subscription** - the billing and access-management boundary in Azure -
everything you deploy lives inside a subscription, and it's the unit
most budgets and a lot of RBAC/policy are scoped to.

## T

**targetScope** - a Bicep declaration at the top of a file that sets what
scope the whole file deploys to (resource group, subscription,
management group, or tenant). Defaults to resource group if not set.

**Tenant** - the top-level container representing an organization's
Entra ID directory. A subscription lives inside exactly one tenant.

**Tenant Root Group** - the single management group automatically created
at the top of every tenant's hierarchy. Cannot be deleted or moved; its
ID is the same as the tenant ID. Every subscription lands here by default
unless moved under a custom management group.

## U

**Uniform orchestration (VMSS)** - the older VM Scale Set mode where
every instance is identical and managed through the scale set's own API
rather than standard VM APIs. Compare Flexible orchestration, now the
Microsoft-recommended default for new scale sets.

**Update Management** - patch scheduling and compliance tracking for
VMs and Arc-connected machines, configured through Azure Update Manager
once a machine is onboarded.

**Upgrade policy (VMSS)** - controls whether changing a scale set's VM
model automatically starts replacing running instances (`Automatic`) or
waits for you to trigger it (`Manual`).

## V

**Variable (var)** - a Bicep value computed inside the file itself, not
passed in at deployment time (compare `param`).

**VM Scale Set (VMSS)** - a group of VM instances managed as one unit,
able to scale the instance count up or down, either manually or via
autoscale rules.

**VNet (Virtual Network)** - an isolated network within Azure that your
resources live inside, with its own IP address range, subnets, and
routing.

**VNet peering** - see Peering (VNet).

## W

**What-if** - `az deployment group what-if` (or the sub/mg/tenant
equivalents) - previews exactly what a deployment would create, change,
or delete before it actually runs, without making any changes.
"""

# =====================================================================
# DAY 00 - BICEP-CHEATSHEET.MD (new file)
# =====================================================================

DAY00_CHEATSHEET = """# Bicep Syntax Cheat Sheet

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
"""

# =====================================================================
# DAYS 01-06 - CORE CONCEPTS SECTIONS
# =====================================================================

CORE_CONCEPTS = {
    "day-01-rbac-and-management-groups": """## Core Concepts (Read This First)

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
""",

    "day-02-azure-policy": """## Core Concepts (Read This First)

### Policy vs RBAC - Two Different Questions
RBAC answers "is this person allowed to do this?" Azure Policy answers a
completely different question: "even if they're allowed, does what
they're about to create actually comply with the rules?" A Contributor
can have full permission to create a storage account, and Azure Policy
can still block that specific storage account from being created if it
violates a rule - e.g. a policy requiring HTTPS-only traffic, or
restricting which regions resources can be deployed to. The two systems
don't know about each other; they just both get checked.

### Definition, Assignment, Initiative
A **policy definition** is the rule itself - the logic describing what to
check and what to do about it. Azure ships hundreds of built-in ones; you
almost never write a definition from scratch as a beginner. A **policy
assignment** is turning a definition on, at a specific scope (management
group, subscription, or resource group), optionally with parameters
(like which regions are allowed). An **initiative** (sometimes called a
policy set) bundles multiple definitions together so you can assign a
whole group of related rules - like an entire compliance standard - in
one assignment instead of one at a time.

### Effects
Every policy definition has an **effect** - what actually happens when
something doesn't comply:
- **Deny** - blocks the deployment outright
- **Audit** - lets it deploy, but flags it as non-compliant in Policy's
  compliance dashboard
- **Append** - adds a field/value to the resource before it's created
  (e.g. force-adding a tag)
- **DeployIfNotExists** - automatically deploys a companion resource if a
  required one is missing (e.g. auto-attaching a diagnostic setting to
  anything that doesn't have one)
- **Modify** - alters existing properties on a resource, most often used
  to add or update tags

For the exam and for real work, Deny and Audit are the two you'll use
constantly; DeployIfNotExists and Modify are the ones that surprise
people the first time they see a resource get changed by "nothing."

### When Compliance Actually Gets Checked
Policy evaluates at deployment time for anything new - that's what blocks
a non-compliant `Deny` policy from ever creating the resource. But
existing resources aren't scanned continuously; Azure re-evaluates policy
compliance across your existing resources roughly every 24 hours (plus
whenever you edit the policy assignment itself). A resource that was
compliant when created can show as non-compliant the next day if the
policy or the resource changed - don't expect the compliance dashboard to
update instantly.
""",

    "day-03-locks-and-budgets": """## Core Concepts (Read This First)

### Locks Override RBAC - On Purpose
This is the detail that trips people up: a resource lock isn't a
permission, it's a hard stop that applies regardless of what RBAC role
someone holds. Even the Subscription Owner can't delete a
`CanNotDelete`-locked resource without first removing the lock. That's
the entire point - a lock protects against the exact scenario where
someone technically has full permission and still shouldn't act, like the
2am production-database scenario below. Locks inherit downward too: a
lock on a resource group applies to everything inside it, even resources
that don't have their own lock.

### Budgets Don't Stop Spending
A common assumption worth correcting early: an Azure budget is not a
spending cap. Nothing about a `Microsoft.Consumption/budgets` resource
stops a VM from running or blocks a deployment once you cross the
threshold - it only fires a notification. If you actually want spend to
trigger an automated response (like shutting something down), that
requires wiring the budget's alert to an Action Group and further
automation yourself; it doesn't happen by default. Treat the budget in
this lesson as a smoke alarm, not a circuit breaker - it tells you
something's on fire, it doesn't put the fire out.
""",

    "day-04-vm-availability-zones": """## Core Concepts (Read This First)

### Availability Zone vs Availability Set
These sound similar and get confused constantly, including on the exam.
An **Availability Set** is a logical grouping within a single Azure
datacenter - it spreads your VMs across separate physical racks (update
domains and fault domains) so a single hardware failure or planned
maintenance doesn't take out every VM at once. It protects you from
failures inside one datacenter. An **Availability Zone** is much bigger
blast-radius protection: each zone is a physically separate datacenter
within the region, with its own independent power, cooling, and
networking. Pinning VMs across multiple zones protects you even if an
entire datacenter goes down.

### SLA Differences
A genuine exam-relevant number worth knowing: a single VM using Premium
SSD gets a 99.9% SLA. VMs in an Availability Set get 99.95%. VMs spread
across Availability Zones get 99.99%. Each jump is a real, meaningfully
different amount of allowed downtime per year - 99.9% allows roughly 8.7
hours of downtime a year; 99.99% allows roughly 52 minutes.

### Not Every Region Supports Zones
Availability Zones require the region to physically have multiple
independent datacenters - not every Azure region does. Before you plan a
zone-based design, check that the target region actually supports zones
rather than assuming it does.
""",

    "day-05-vm-scale-sets": """## Core Concepts (Read This First)

### Orchestration Mode: The Decision You Can't Undo Later
Every VM Scale Set is built in one of two orchestration modes, and Azure
won't let you change it after the scale set is created - picking wrong
means recreating the whole thing. **Uniform** mode is the older approach:
every instance is identical, managed through the scale set's own API
rather than normal VM APIs, and individual instances can't use things
like Azure Backup or standard RBAC tagging the way a regular VM can.
**Flexible** mode is Microsoft's current recommendation for basically all
new scale sets - each instance behaves like a real, standalone VM under
the hood (so it works with the normal VM APIs, Backup, tagging,
everything), while still giving you scale-set-level autoscaling and
zone-spreading. If you don't explicitly set `orchestrationMode`, it
defaults to Uniform - worth setting on purpose:

```bicep
properties: {
  orchestrationMode: 'Flexible'
  // ...
}
```

Exam material and a lot of existing documentation (including patterns
you'll see online) still lean on Uniform because it's older and
better-documented - but for anything you'd actually build today, Flexible
is the right default.

### Autoscale Isn't Automatic Just Because You Have a VMSS
Deploying a scale set with `capacity: 3` gives you exactly 3 instances,
permanently, until you manually change that number - it does not scale on
its own. Actual autoscaling requires a separate
`Microsoft.Insights/autoscaleSettings` resource defining rules (e.g. "add
an instance when average CPU > 70% for 5 minutes"), which isn't in this
lesson's example. Worth knowing going in so you don't expect scale-out
behavior that the base VMSS resource alone doesn't provide.
""",

    "day-06-disks-and-extensions": """## Core Concepts (Read This First)

### Disk Tiers
Managed disks come in four performance tiers, and the exam expects you to
know the shape of the tradeoff even if not exact IOPS numbers:
**Standard HDD** (cheapest, spinning disk, fine for infrequent access or
backups), **Standard SSD** (better latency than HDD, still
budget-friendly, fine for lightly used production workloads),
**Premium SSD** (the default for anything performance-sensitive,
requires certain VM sizes to use), and **Ultra Disk** (highest
performance, configurable IOPS/throughput independent of size, used for
the heaviest database workloads). This lesson's data disk uses
`Standard_LRS`, deliberately the cheapest option, since the point here is
learning disk attachment, not performance tuning.

### OS Disk vs Data Disk
The OS disk is created inline as part of the VM resource itself - it's
not optional, and it holds the operating system. A data disk is its own
independent top-level resource (`Microsoft.Compute/disks`) that exists
whether or not it's attached to anything, and gets attached by
referencing it in the VM's `storageProfile.dataDisks` array. This
independence matters: you can detach a data disk from one VM and reattach
it to another without losing the data, which isn't true of an OS disk.

### What an Extension Actually Is
A VM extension is a small agent Azure installs and runs on the VM after
it boots - not part of the OS image itself, but layered on afterward. The
Custom Script Extension in this lesson just runs a shell/PowerShell
command, but the same mechanism is how things like the Azure Monitor
Agent, antimalware agents, or disk encryption get installed consistently
across a fleet of VMs without anyone manually logging into each one.
""",

    "day-07-app-service": """## Core Concepts (Read This First)

### App Service Plan Tiers
The plan (`serverfarms`) determines what the app is actually capable of,
not just how much it costs. Roughly, from bottom to top: **Free (F1)** and
**Shared (D1)** run on infrastructure shared with other customers' apps,
no custom domains or SSL, apps sleep after inactivity. **Basic (B1-B3)**
adds custom domains and SSL, still no autoscale. **Standard (S1-S3)** adds
autoscale and deployment slots. **Premium (P1v3-P3v3)** adds more scale
headroom and VNet integration. **Isolated** runs on fully dedicated
infrastructure (an App Service Environment) for the strictest network
isolation requirements. This lesson deploys F1 deliberately, to keep the
lab free - know going in that F1 can't do most of what production App
Service deployments actually rely on.

### Deployment Slots
Starting at Standard tier, an App Service Plan can host multiple
**deployment slots** for the same app - each slot is a fully live,
separately-addressable instance (e.g. a `staging` slot next to
`production`). You deploy new code to staging, test it against real
traffic patterns, then **swap** staging and production - which is a
near-instant DNS/routing switch, not a redeploy, so there's no downtime
and an easy way to roll back by swapping again. This lesson's F1 plan
can't use slots at all; it's worth knowing the feature exists before you
hit a lab or exam question assuming it.

### Multi-Tenant by Default
Every tier below Isolated runs your app on infrastructure Azure also uses
for other customers' apps - you're logically isolated (your app can't see
or affect theirs) but not physically isolated. This is normal and fine
for the overwhelming majority of workloads; Isolated tier/App Service
Environment exists specifically for the cases (regulatory, extreme
network control) where logical isolation isn't enough.
""",

    "day-08-container-apps": """## Core Concepts (Read This First)

### Where Container Apps Sits
Three ways to run a container in Azure, in order of how much you manage
yourself: **App Service** (Linux container support, simplest, closest to
"just run this container as a web app"), **Container Apps** (this
lesson - real container orchestration primitives like revisions and
traffic-splitting, without you managing a Kubernetes cluster), and
**AKS / Azure Kubernetes Service** (full Kubernetes, maximum control and
complexity, you own far more of the operational surface). Container Apps
is deliberately the middle option - Kubernetes-like capabilities, PaaS
levels of operational effort.

### Revisions
Every time you update a Container App's configuration, Azure creates a
new **revision** rather than overwriting the running one in place. By
default only the newest revision serves traffic, but you can run multiple
revisions simultaneously and split traffic between them by percentage -
this is how blue-green deployments or gradual rollouts work on Container
Apps, and it's not something this lesson's basic example shows, but it's
the reason Container Apps exists as a distinct product rather than "App
Service that happens to run containers."

### Consumption vs Dedicated
This lesson's example runs on the **Consumption** plan - pay per second
of actual usage, and the `minReplicas: 0` scale-to-zero behavior only
works here. A **Dedicated** workload profile exists for workloads that
need predictable, reserved capacity instead of consumption-based billing
- worth knowing the option exists even though this build stays on
Consumption to keep costs at zero when idle.
""",

    "day-11-vnet-subnets-nsg": """## Core Concepts (Read This First)

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
""",

    "day-12-peering-and-dns": """## Core Concepts (Read This First)

### What Private DNS Actually Solves
Without it, a VM in Azure has no way to resolve a custom internal
hostname (like `db.internal.contoso.com`) to another VM's private IP -
you'd be stuck hardcoding IP addresses everywhere, which breaks the
moment anything gets redeployed with a new IP. A private DNS zone gives
you that internal name resolution. To actually work, it has to be linked
to one or more VNets through a **virtual network link** - creating the
zone alone doesn't connect it to anything.

### Peering Is Not Transitive
A genuinely easy mistake to make, and a real exam topic: if VNet A is
peered with VNet B, and VNet B is peered with VNet C, that does **not**
mean A can reach C. Each peering relationship is a direct connection
between exactly two VNets - there's no automatic "pass it along" the way
routing sometimes works elsewhere. If A needs to reach C, A and C need
their own direct peering (or traffic needs to be routed through a
network appliance sitting in B on purpose).
""",

    "day-13-load-balancer-appgw": """## Core Concepts (Read This First)

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
""",

    "day-14-bastion-vpn-gateway": """## Core Concepts (Read This First)

### VPN Gateway Connection Types
The gateway resource in this lesson is the shared foundation both
connection types are built on - the actual "type" comes from the
connection resource layered on top of it, not the gateway itself.
**Site-to-Site** connects an entire on-prem network to a VNet, with a VPN
device on each end maintaining a persistent tunnel - this is how a whole
office gets access to Azure resources. **Point-to-Site** connects
individual devices (a single laptop, no VPN hardware needed on that end)
directly into the VNet - this is how one remote person gets in without
the company needing a site-to-site tunnel just for them.

### Bastion SKU Tiers
Bastion has Basic and Standard tiers. Basic (used in this lesson) covers
straightforward RDP/SSH access through the portal, which is all a lab
needs. Standard adds native client support (connecting via your own
RDP/SSH client instead of only the browser), IP-based connection, and the
ability to scale the host for more concurrent sessions - relevant at
organization scale, not for this build.
""",

    "day-16-storage-accounts-redundancy": """## Core Concepts (Read This First)

### What a Storage Account Actually Is
One storage account is a namespace that can hold up to four distinct
kinds of storage: **Blob** (object storage - files, images, backups,
addressed by name, not organized like a traditional filesystem), **Files**
(SMB/NFS network shares - behaves like a real network drive), **Queue**
(simple message queuing between application components), and **Table**
(NoSQL key-value storage). Redundancy and most account-wide settings
apply to the whole account regardless of which of these you're using;
individual blobs can still override some settings (like access tier) on
their own.

### Access Tier and Redundancy Are Two Separate Dials
Easy to conflate, genuinely different things. **Redundancy** (LRS / ZRS /
GRS) is about durability - how many copies exist and where. **Access
tier** (Hot / Cool / Cold / Archive) is about the tradeoff between
storage cost and retrieval cost - Hot costs more to store but nothing
extra to read; Archive costs almost nothing to store but is expensive
and slow to read back (see Day 17's note on rehydration time). You choose
a redundancy level and an access tier independently - a GRS account can
still have individual blobs sitting in the Cool or Archive tier.
""",

    "day-17-blob-lifecycle": """## Core Concepts (Read This First)

### Archive Tier Isn't Instantly Readable
Worth knowing before you rely on a lifecycle policy that tiers blobs to
Archive: data in the Archive tier isn't available for immediate read.
Retrieving it requires a **rehydration** step - moving the blob back to
Hot or Cool - which can take several hours depending on the priority you
choose. A lifecycle rule that archives old data is a great cost saver for
data you rarely need, and a real problem if you ever need that data back
in a hurry. This is exactly why this lesson's rule tiers to Cool at 30
days and Archive only at 90 - giving you a slower-but-still-readable
middle tier before anything becomes hours-to-retrieve.
""",

    "day-18-azure-files": """## Core Concepts (Read This First)

### Azure Files vs Blob Storage
Both live under the same storage account, and it's easy to assume they're
interchangeable - they're not. **Blob storage** is object storage:
everything is addressed by a flat name/key, accessed over HTTP/HTTPS, and
has no real concept of "mounting a drive." **Azure Files** is a genuine
network file share over SMB (or NFS) - the protocol Windows/Linux already
use for shared drives - so an existing application expecting a drive
letter or a mounted path can often point at an Azure Files share with
little to no code change. That's the whole reason Azure Files exists
separately from Blob: lift-and-shift compatibility with things that
already expect a traditional file share.
""",

    "day-19-sas-private-endpoints": """## Core Concepts (Read This First)

### Service Endpoint vs Private Endpoint
This lesson builds a private endpoint, but the exam expects you to know
there's a second, older option: a **service endpoint**. A service
endpoint extends your VNet's identity to the storage account - traffic
stays on the Azure backbone instead of the public internet, but it still
travels to the storage account's *public* IP, and no private IP is
created anywhere. A **private endpoint** goes further: it creates an
actual private IP address inside your VNet that represents the storage
account, so traffic never touches a public IP at all, and it's specific
to one resource (even one sub-resource, via `groupIds`) rather than an
entire service type. Service endpoints are simpler and free; private
endpoints are more isolated and cost a small hourly charge - Microsoft's
current guidance leans toward private endpoints where the added isolation
is worth that cost.

### SAS Token Types
Not all SAS tokens are the same scope. An **Account SAS** grants access
across multiple storage services within the account (blob, file, queue,
table) at once. A **Service SAS** scopes down to one specific service
(e.g. just blob). A **User Delegation SAS** is the most secure option -
it's secured with Entra ID credentials instead of the storage account's
own access keys, so it can be revoked by revoking Entra permissions
without having to rotate the account's keys (which would break every
other SAS token issued from those keys at the same time).
""",
}


def insert_after_title(text: str, section: str) -> str:
    """Insert `section` right after the first line (the H1 title) of `text`."""
    lines = text.split("\n", 1)
    if len(lines) == 1:
        return text + "\n\n" + section
    title, rest = lines
    return title + "\n\n" + section.strip("\n") + "\n\n" + rest.lstrip("\n")


def fix_day00():
    day00_dir = PHASE_1 / "day-00-bicep-fundamentals"
    lesson_path = day00_dir / "lesson.md"

    if not lesson_path.exists():
        print(f"SKIP: {lesson_path} not found")
        return

    text = lesson_path.read_text(encoding="utf-8")
    if DAY00_MARKER in text:
        print("SKIP: Day 00 lesson.md already has the fundamentals addition")
    else:
        lesson_path.write_text(text.rstrip("\n") + "\n" + DAY00_LESSON_ADDITION, encoding="utf-8")
        print("UPDATED: Day 00 lesson.md (added scope/existing/dependencies/decorators/loops/functions)")

    glossary_path = day00_dir / "glossary.md"
    if glossary_path.exists():
        print(f"SKIP: {glossary_path} already exists")
    else:
        glossary_path.write_text(DAY00_GLOSSARY, encoding="utf-8")
        print(f"CREATED: {glossary_path}")

    cheatsheet_path = day00_dir / "bicep-cheatsheet.md"
    if cheatsheet_path.exists():
        print(f"SKIP: {cheatsheet_path} already exists")
    else:
        cheatsheet_path.write_text(DAY00_CHEATSHEET, encoding="utf-8")
        print(f"CREATED: {cheatsheet_path}")


def fix_core_concepts():
    for day_slug, section in CORE_CONCEPTS.items():
        day_dir = find_day_dir(day_slug)
        if day_dir is None:
            print(f"SKIP: {day_slug} - folder not found in any phase directory")
            continue

        lesson_path = day_dir / "lesson.md"
        if not lesson_path.exists():
            print(f"SKIP: {lesson_path} not found")
            continue

        text = lesson_path.read_text(encoding="utf-8")
        if "## Core Concepts (Read This First)" in text:
            print(f"SKIP: {day_slug}/lesson.md already has Core Concepts")
            continue

        new_text = insert_after_title(text, section)
        lesson_path.write_text(new_text, encoding="utf-8")
        print(f"UPDATED: {day_slug}/lesson.md (inserted Core Concepts)")


def main():
    print(f"Repo root: {REPO_ROOT}\n")
    print("--- Day 00: reference hub ---")
    fix_day00()
    print("\n--- Days 01-06: Core Concepts retrofit ---")
    fix_core_concepts()

    print("\n" + "=" * 70)
    print("DONE - Days 00-19 fixed (00-06, 07-08, 11-14, 16-19).")
    print("=" * 70)
    print("""
NOT TOUCHED, ON PURPOSE (already fine as-is, no new-syntax content to
ground - these are checkpoint/self-test/teardown days):
  day-09-bicep-consolidation, day-10-self-test-teardown
  day-15-network-watcher-review
  day-20-review-teardown

  04-identity-access (21-25) and 05-monitoring-backup (26-30) already use
  the richer "Straight Talk First" template from the start and don't need
  this fix either.

Every AZ-104-mapped day from Day 00 through Day 20 now has conceptual
grounding before the syntax. That's the full Compute, Governance,
Networking, and Storage material covered.
""")


if __name__ == "__main__":
    main()