# Day 02 Lesson - Azure Policy

## Core Concepts (Read This First)

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
