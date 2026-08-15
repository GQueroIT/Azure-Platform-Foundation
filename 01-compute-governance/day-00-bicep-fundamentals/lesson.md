# Day 00 Lesson - Bicep Fundamentals

Read this before Day 01. Every later lesson assumes you know what's here.

## What Bicep Actually Is
Bicep is not a programming language in the sense Python or JavaScript are.
It is a declarative syntax for describing Azure resources - you write what
you want to exist, not the steps to create it. Bicep compiles down to an
ARM (Azure Resource Manager) JSON template behind the scenes, but you never
have to touch that JSON yourself.

"Declarative" is the key word. You are not writing "create a VM, then
attach a disk, then start it." You are writing "here is a VM resource with
these properties" and Azure Resource Manager figures out how to make that
true.

## The Five Building Blocks
Every Bicep file is built from some combination of these:

```bicep
param environmentName string = 'dev'          // input, supplied at deploy time
var fullName = 'proj-${environmentName}'       // computed value, not passed in
resource myVm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: fullName
  location: resourceGroup().location
  // ...properties go here
}
module network './network.bicep' = {           // calls another Bicep file
  name: 'networkDeployment'
  params: { }
}
output vmId string = myVm.id                   // value returned after deploy
```

- **param** - a value you supply when you deploy (like a function argument)
- **var** - a value computed inside the file, not passed in
- **resource** - an actual Azure thing getting created: `resource <your-name-for-it> '<type>@<api-version>' = { ... }`
- **module** - a way to call another .bicep file, for splitting big deployments into pieces
- **output** - a value handed back after deployment finishes, often used to feed the next module

## Reading a Resource Declaration
```bicep
resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: 'mystorageacct001'
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}
```
Break this down:
- `storageAccount` - the symbolic name. This is what YOU call it inside this
  Bicep file, to reference it elsewhere. It is not the Azure resource name.
- `'Microsoft.Storage/storageAccounts@2025-06-01'` - the resource type, then
  an `@` and the API version. Every resource type has one. Azure changes
  these over time; the lessons in this repo will tell you which one to use.
- Everything inside `{ }` is the resource's properties. What's required
  varies by resource type - the lessons ahead show you exactly what each
  one needs.

## String Interpolation
Bicep builds strings using `${ }` inside single quotes:
```bicep
var uniqueName = 'stg${uniqueString(resourceGroup().id)}'
```
This is the same idea as an f-string in Python or a template literal in
JavaScript if you've seen either. `uniqueString()` is a built-in Bicep
function that generates a short, deterministic hash - it is used constantly
for resource names that have to be globally unique (like storage accounts).

## Referencing an Existing Resource
Sometimes you need to point at something that already exists instead of
creating it. Add the `existing` keyword:
```bicep
resource existingVnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: 'my-existing-vnet'
}
```
You'll use this constantly once resources start depending on each other
across different Bicep files.

## Deploying What You Write
Once a .bicep file exists, you deploy it with Azure CLI:
```bash
az deployment group create \
  --resource-group my-rg \
  --template-file main.bicep
```
That command reads the file, compiles it to ARM JSON internally, and sends
it to Azure Resource Manager to actually create the resources.

## Why It's Written This Way
Bicep's whole design goal is to make ARM templates (which are raw JSON, and
genuinely painful to hand-write) readable and maintainable. Every piece of
syntax above exists to cut down on repetition and make the relationships
between resources explicit.

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/file>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/parameters>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/variables>

## Why This Matters (Business Context)
Every cloud team eventually hits the same wall: someone changes a setting by hand in the portal, nobody documents it, and six months later no one can reproduce the environment or explain why it works. Infrastructure as code closes that gap - the Bicep file itself becomes the documentation, the audit trail, and the disaster-recovery plan all at once. A company that can redeploy its entire environment from a git repo during an outage recovers in hours; a company that can't is rebuilding from memory and screenshots.


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
