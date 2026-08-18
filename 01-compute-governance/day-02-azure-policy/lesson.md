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

## Service Deep Dive

### What It Can't Do
Policy can't retroactively fix anything by itself. A `Deny` effect blocks
non-compliant resources at creation time, but existing resources that were
compliant when created and later drift (or existed before the policy was
assigned) just sit there marked non-compliant - Policy doesn't reach out
and fix them. `DeployIfNotExists` and `Modify` effects *can* fix existing
resources, but only through an explicitly triggered **remediation task**;
nothing runs automatically against your existing environment just because
you assigned a policy.

Those same `DeployIfNotExists` and `Modify` effects also can't function
without a managed identity attached to the policy assignment - that
identity is what actually performs the remediation deployment, separate
from whatever evaluates the policy's compliance logic in the first place.
Forget to give the assignment an identity (or the identity the right RBAC
role), and remediation tasks fail even though the policy itself looks
correctly assigned.

Policy also isn't real-time for existing resources: Azure re-evaluates
compliance across everything already deployed roughly every 24 hours,
plus whenever you edit the assignment. Don't expect the compliance
dashboard to reflect a change the moment it happens.

### Nuances Worth Knowing
- **`DeployIfNotExists` has a configurable evaluation delay, defaulting to
  10 minutes.** Immediately after a resource is created, Policy waits
  that long before checking whether the required companion resource
  exists and deploying it if not. Checking compliance one minute after
  creating a resource and seeing "non-compliant, nothing happened yet" is
  expected, not broken.
- **Remediation only ever touches existing resources, once.** If a
  remediation task fixes a resource and someone later reverts the change
  back to non-compliant, the policy will flag it non-compliant again on
  the next evaluation cycle, but it will not automatically re-remediate -
  you have to run another remediation task.
- **`Deny` and `Audit` are what you'll use almost constantly**; `Append`,
  `Modify`, and `DeployIfNotExists` are the ones that quietly change or
  add something without you doing anything, which is exactly why they
  need their own identity and permissions.

### Troubleshooting You'll Actually Hit
- **Symptom:** a `DeployIfNotExists` policy assignment shows resources as
  non-compliant, but nothing ever gets deployed for them ->
  **Cause:** the assignment has no managed identity, or the identity
  exists but lacks the RBAC role the policy definition requires ->
  **Fix:** `az policy assignment show --name <name> --query identity` to
  confirm an identity exists, then check that identity has been granted
  the role the policy definition specifies it needs.
- **Symptom:** existing resources from before the policy was assigned
  stay non-compliant indefinitely -> **Cause:** `DeployIfNotExists`/
  `Modify` never auto-remediate pre-existing resources -> **Fix:**
  manually trigger a remediation task against the policy assignment; it's
  a separate step from assigning the policy itself.
- **Symptom:** compliance dashboard doesn't reflect a change made minutes
  ago -> **Cause:** compliance re-evaluation on existing resources runs
  on roughly a 24-hour cycle, not continuously -> **Fix:** trust
  `az deployment group what-if` and deployment-time enforcement for
  anything time-sensitive; treat the dashboard as eventually-consistent,
  not live.

*Checked against: Microsoft Learn's "deployIfNotExists effect" and
"Remediate non-compliant resources" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/governance/policy/assign-policy-bicep>

## Why This Matters (Business Context)
A developer spins up a storage account in a region the company isn't allowed to operate in for compliance reasons, and nobody notices until an audit six months later. Policy is how a company enforces rules automatically instead of hoping people remember them - tag enforcement is what lets finance actually bill costs back to the right department, and region restriction is what lets legal stop manually reviewing every deployment.
