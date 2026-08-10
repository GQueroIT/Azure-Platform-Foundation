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