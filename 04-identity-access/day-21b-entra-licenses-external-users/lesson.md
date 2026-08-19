# Day 21b Lesson - Entra ID Licenses and External (Guest) Users

## Straight Talk First
Neither license assignment nor B2B guest invitations have a Bicep
resource type, and neither is in the Microsoft Graph Bicep extension's
supported list from Day 21 (Groups, Applications, Service Principals,
App Role Assignments, OAuth2 permission grants, Federated Identity
Credentials - licenses and invitations aren't on that list). Both are
configured through the portal, Microsoft Graph PowerShell, or direct
Graph API calls - a real gap the same way Conditional Access and SSPR
were on Day 23, and for the same underlying reason: this is Entra ID
directory-management territory, not an ARM resource.

## What Actually Configures This
- **Group-based licensing**: assign a product license (Microsoft 365,
  Entra ID P1/P2, etc.) to a *group* instead of individual users - every
  current and future member inherits the license automatically, and it's
  removed automatically the moment someone leaves the group. Configured
  in the Entra admin center or via Microsoft Graph PowerShell
  (`Set-MgGroupLicense` and related cmdlets).
- **External/guest users (B2B collaboration)**: inviting someone outside
  the tenant to collaborate without creating them a full local account -
  configured under External Identities > External collaboration settings,
  or via the Graph invitation API/PowerShell for bulk or automated
  invites.

## Why This Matters For the Exam
AZ-104 tests understanding of *what* group-based licensing and external
users are, how they behave, and what governs them - not Bicep syntax for
either, since none exists. Expect scenario questions ("a user was removed
from a group, what happens to their license") more than deployment
questions.

## What To Actually Do Today
1. In the portal, create (or reuse) an Entra security group, assign it a
   license under Licenses > group-based licensing, and confirm at least
   one member shows the license as "inherited (group)" rather than
   "direct."
2. Under External Identities, invite a guest user with an email address
   you control, and confirm the invitation email actually arrives and
   the guest object appears with `userType: Guest`.

## Service Deep Dive

### What It Can't Do
Group-based licensing can't assign a license to a user in an unsupported
usage location - Entra ID needs a usage location set on the user before
group licensing can apply, and if it's missing or unsupported for that
specific license SKU, the assignment fails silently in the background,
recorded as an error state on that user rather than surfaced immediately.
External users specifically can only be added to groups that are
"assigned" type or Security groups - not to groups mastered on-premises
via Entra Connect, since on-prem-sourced groups aren't something Entra ID
directly manages membership for.

### Nuances Worth Knowing
- License errors from group-based licensing don't interrupt anything or
  alert in real time - they're recorded silently on the user object
  within the group and have to be actively checked (M365 Admin Center >
  Billing > Licenses > that product > Users, filtered to error states) to
  even discover they exist.
- A common, specific license error: two products assigned to the same
  user (one directly, one via a group) contain conflicting service plans
  that can't coexist - resolving that conflict is always a manual
  administrator decision, not something Entra resolves automatically.
- B2B guest invitations can fail with "insufficient privileges" even for
  an account that was inviting guests successfully yesterday - a
  documented pattern usually traced to changed external collaboration
  settings or a role assignment change, not a broken account.
- Guest objects aren't visible in the organization's global address list
  by default - a deliberate default, not a bug, and there's a separate
  explicit step to make guests visible there if that's actually wanted.
- Role-assignable groups (letting a group itself hold an Entra directory
  role) require an Entra ID P1 license or higher - a real licensing
  prerequisite, not just a feature toggle.

### Troubleshooting You'll Actually Hit
- **Symptom:** a user in a licensed group doesn't actually show the
  license applied -> **Cause:** commonly a missing or unsupported usage
  location on that user, or a conflicting service plan from another
  license -> **Fix:** check the product's Users list in the M365 Admin
  Center for that user's specific error state rather than assuming the
  group assignment itself is broken - the group did its job; the
  individual assignment hit a business-logic error.
- **Symptom:** guest invitations suddenly fail with "insufficient
  privileges," despite no obvious account changes -> **Cause:** most
  commonly a change to External collaboration settings (guest invites
  restricted to certain roles, or a domain allow/deny list change) rather
  than the inviting account itself losing permission -> **Fix:** check
  External Identities > External collaboration settings for recent
  changes before assuming a role assignment problem.
- **Symptom:** an external user can't be added to a specific group ->
  **Cause:** the group is mastered on-premises via Entra Connect, and
  external users can only join assigned/Security groups managed natively
  in Entra ID -> **Fix:** use a cloud-native assigned group for external
  user membership instead.

*Checked against: Microsoft Learn's "Identify and resolve license
assignment problems" and "Troubleshoot B2B collaboration issues" docs.*

## Source
<https://learn.microsoft.com/en-us/entra/fundamentals/licensing-groups-resolve-problems>
<https://learn.microsoft.com/en-us/entra/external-id/troubleshoot>
<https://learn.microsoft.com/en-us/entra/fundamentals/licensing-group-advanced>

## Why This Matters (Business Context)
A company onboards fifty new hires in one department at once - assigning fifty individual licenses by hand is exactly the kind of manual, error-prone task group-based licensing exists to eliminate. A vendor needs temporary access to review a shared document without becoming a full employee in the directory - that's precisely the scenario B2B guest access is built for, instead of creating (and later remembering to delete) a real local account for someone who was never actually staff.
