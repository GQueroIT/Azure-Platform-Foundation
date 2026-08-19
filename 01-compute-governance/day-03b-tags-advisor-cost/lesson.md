# Day 03b Lesson - Tags, Azure Advisor, and Deeper Cost Management

## Core Concepts (Read This First)

### Tags Don't Inherit - a Real, Common Mistake
Tagging a resource group `Environment: Production` does not tag the
resources inside it. Tags are metadata attached to one specific resource,
resource group, or subscription at a time - there's no automatic
flow-down the way RBAC or Policy inherit. The only way to get
inheritance-like behavior is Azure Policy with a `modify` effect copying
the parent's tag onto children as they're created - a policy doing the
work, not a native tag feature.

### Advisor Is Free and Already Running
Azure Advisor isn't something you deploy - it's a built-in recommendation
engine continuously scanning the subscription across four categories
(Cost, Security, Reliability, Performance) and surfacing specific,
actionable findings, like a VM sitting at 3% CPU that should be
downsized. There's no Bicep resource for "Advisor" itself; the lab today
is reviewing what it's already found, not building anything.

## What You're Building Today
A tag object applied consistently to a resource group and a resource
inside it, plus a review of Advisor's current recommendations.

## New Bicep Concepts
- `tags` as a property available on nearly every resource type
- Deploying a `Microsoft.Resources/tags` resource to tag a subscription
  or resource group itself, not just individual resources

## Annotated Example
```bicep
param tags object = {
  Environment: 'Lab'
  Project: 'AZ-104-Prep'
  Owner: 'gabe'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: 'stg${uniqueString(resourceGroup().id)}'
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  tags: tags
}
```

Tagging the resource group itself (a subscription-scoped file):
```bicep
targetScope = 'subscription'

param tags object = {
  Environment: 'Lab'
  Project: 'AZ-104-Prep'
}

resource applyTags 'Microsoft.Resources/tags@2021-04-01' = {
  scope: resourceGroup('rg-lab')
  name: 'default'
  properties: { tags: tags }
}
```

## Why It's Written This Way
- Passing the same `tags` object into every resource keeps tagging
  consistent without retyping key-value pairs on each one - the pattern
  scales the moment a deployment has more than one or two resources.
- Tags applied through Bicep **replace** whatever tags already exist on
  that resource, not merge with them - if a resource already has manual
  tags and you deploy without including them in the object, they're
  gone, not preserved.
- The `Microsoft.Resources/tags` resource's `name` is always literally
  `'default'` - same pattern as the lifecycle policy and file services
  resources from Storage week, one tag document per scope.

## Service Deep Dive

### What It Can't Do
Every resource, resource group, and subscription is capped at 50 tag
name-value pairs - hit the limit and the workaround is folding multiple
values into one tag's value as a JSON string, not requesting a higher
cap. Classic resources (like Cloud Services) don't support tags at all,
and a handful of resource types - Azure IP Groups and Firewall Policies
among them - don't support the PATCH operations tags normally use,
meaning those specific resource types need their own update commands to
change tags rather than the generic tag-update path.

Advisor also can't act on your behalf - it only recommends. Downsizing
that underutilized VM, tightening that open NSG rule, or right-sizing
that storage account is still a manual (or separately automated) action
after Advisor points it out.

### Nuances Worth Knowing
- Tag names are case-insensitive but tag values are case-preserving and
  case-sensitive - `environment: prod` and `Environment: Prod` collide
  on the name but are treated as different values, a real source of
  fragmented cost reports when a team isn't consistent about casing.
- Storage accounts specifically cap tag *names* at 128 characters instead
  of the usual 512 - one of several resource-type-specific exceptions to
  the general tag limits.
- "Hidden tags" (any tag name starting with `hidden-`) don't show up in
  the portal's Tags UI at all, but still exist in the resource's metadata
  and are queryable - a real, if obscure, pattern for metadata that
  shouldn't clutter the normal tagging view.
- Azure Policy can enforce tag inheritance from a resource group down to
  its resources using a `modify` effect - this is the actual mechanism
  behind "inherited tags," not a native tag behavior.

### Troubleshooting You'll Actually Hit
- **Symptom:** a resource group is tagged correctly but cost reports
  filtered by that tag show nothing for the resources inside it ->
  **Cause:** tags don't inherit automatically - the resources themselves
  were never actually tagged -> **Fix:** tag resources directly, or
  assign a tag-inheritance Azure Policy scoped to the resource group so
  new resources pick up the parent tag going forward.
- **Symptom:** redeploying a Bicep file wipes out tags someone added
  manually in the portal -> **Cause:** Bicep's `tags` property replaces
  the full tag set on that resource, it doesn't merge -> **Fix:** read
  the resource's existing tags (via `existing` or `reference()`) and
  merge them into the object being deployed if manual additions need to
  survive a redeploy.
- **Symptom:** a cost report shows the same logical environment split
  across two different-looking tag buckets -> **Cause:** inconsistent
  casing in tag values across resources (`prod` vs `Prod`) -> **Fix:**
  standardize on one casing convention and consider an Azure Policy that
  enforces allowed values for that tag.

*Checked against: Microsoft Learn's "Use tags to organize your Azure
resources" and "Tag resources, resource groups, and subscriptions with
Bicep" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources-bicep>
<https://learn.microsoft.com/en-us/azure/advisor/advisor-overview>

## Why This Matters (Business Context)
A finance team asks which team owns a $4,000/month resource group and nobody can answer without opening every resource one at a time. Consistent tags turn that into a five-second filter in Cost Management. Advisor is the free second opinion that catches the VM someone forgot to resize six months after a traffic spike ended.
