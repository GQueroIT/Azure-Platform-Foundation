# Day 02 Lesson - Azure Policy

## What You're Building Today
A tag enforcement policy and a region restriction policy, assigned via Bicep.

## New Bicep Concepts
- `policyDefinitionId` - pointing at a built-in policy instead of writing
  your own policy logic
- `parameters` object on a policy assignment - passing values into someone
  else's policy definition

## Annotated Example
```bicep
param allowedLocations array = [
  'eastus'
  'eastus2'
]

resource locationPolicyAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'allowed-locations'
  properties: {
    displayName: 'Allowed locations for resources'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitionDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c'
    parameters: {
      listOfAllowedLocations: {
        value: allowedLocations
      }
    }
  }
}
```
Note the policy definition ID above is the pattern for a subscription-built-in
policy - the actual GUID for "Allowed locations" is `e56962a6-4747-49cd-b67b-bf8b01975c4c`,
findable in the Azure Policy portal under Definitions.

## Why It's Written This Way
- You are almost never writing a brand-new policy *definition* from scratch
  as a beginner - Azure ships dozens of built-in ones (allowed locations,
  require a tag, allowed VM SKUs, etc). What you're actually doing is
  *assigning* an existing definition and feeding it parameters. That's why
  `policyDefinitionId` points at a Microsoft-owned resource ID, not
  something you defined yourself.
- The `parameters` object structure - `{ paramName: { value: ... } }` - is
  the standard shape for feeding any built-in policy or initiative its
  inputs. It looks redundant (why wrap `value` in another object?) but it's
  consistent across every policy assignment you'll ever write.
- Some built-in policies (the "Modify" and "DeployIfNotExists" kind) need a
  managed identity to actually make changes, not just report on them. A
  location restriction is just a "Deny" policy, so it doesn't need one -
  you'll see identity blocks show up in later, more complex policies.

## Source
<https://learn.microsoft.com/en-us/azure/governance/policy/assign-policy-bicep>

## Why This Matters (Business Context)
A developer spins up a storage account in a region the company isn't allowed to operate in for compliance reasons, and nobody notices until an audit six months later. Policy is how a company enforces rules automatically instead of hoping people remember them - tag enforcement is what lets finance actually bill costs back to the right department, and region restriction is what lets legal stop manually reviewing every deployment.
