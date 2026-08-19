# Day 21 Lesson - Entra ID Users and Groups (Microsoft Graph Bicep Extension)

## Straight Talk First
Bicep was originally built ONLY for Azure Resource Manager (ARM) resources
- things like VMs, storage accounts, VNets. Entra ID (users, groups, app
registrations) technically lives outside ARM, in Microsoft Graph. For a
long time, Bicep genuinely could not touch Entra ID at all.

That changed: the Microsoft Graph Bicep extension went generally available
on July 29, 2025. It lets you manage a specific set of Entra ID resources
- Groups, Applications, Service Principals, App Role Assignments, OAuth2
permission grants, Federated Identity Credentials - directly in Bicep,
alongside your normal Azure resources. Full user creation isn't in that
supported list; you can REFERENCE an existing user, but you're not
creating brand-new user accounts through this extension.

## New Bicep Concepts
- The `extension` directive - loading a capability Bicep doesn't have
  by default
- `Microsoft.Graph/*` resource types, which look like normal Bicep but
  deploy to Entra ID, not ARM

## Annotated Example
```bicep
extension microsoftGraphV1

param ownerUpn string

resource owner 'Microsoft.Graph/users@v1.0' existing = {
  userPrincipalName: ownerUpn
}

resource securityGroup 'Microsoft.Graph/groups@v1.0' = {
  displayName: 'AZ104-Lab-Admins'
  description: 'Security group created for the AZ-104 lab build'
  mailEnabled: false
  mailNickname: 'az104-lab-admins'
  securityEnabled: true
  owners: {
    relationships: [ owner.id ]
  }
}
```

## Why It's Written This Way
- `extension microsoftGraphV1` at the top of the file is what unlocks the
  `Microsoft.Graph/*` resource types below it. Without that line, Bicep
  has no idea what `Microsoft.Graph/groups` even is.
- The user is referenced with `existing`, keyed on `userPrincipalName`
  (their sign-in email, essentially) - this is deliberate. The extension
  supports READING existing users so you can reference them as group
  owners or members, without supporting full user account creation.
- `mailEnabled: false` + `securityEnabled: true` is the standard
  combination for a plain security group (as opposed to a Microsoft 365
  group, which is the opposite).

## Service Deep Dive

### What It Can't Do
The Graph extension's supported resource list is genuinely narrow, and
even within Groups real gaps exist. A single Groups resource can't
declare more than 20 members or owners - go over that and deployment
fails outright with a 400 error, with nothing in the syntax warning
about the wall in advance. Role-assignable groups (`isAssignableToRole:
true`) look fully supported in the schema, but deploying one fails
regardless of permissions - it's declared but not actually deployable
through this extension yet; the documented workaround is a
`DeploymentScript` resource calling Microsoft Graph directly instead.

`what-if` doesn't work against Graph resources at all - none of the
preview-before-deploy safety net this repo has relied on since Day 00
applies here. Neither do deployment stacks or verbose deployment output.
And deployed Graph resources genuinely don't show up on the Azure
portal's deployment details page - only true ARM resources do, so
confirming a Graph deployment succeeded means checking Entra ID
directly, not the deployment history checked for everything else in
this repo.

### Nuances Worth Knowing
- If a Graph resource created through Bicep gets deleted some other way
  (portal, PowerShell, Graph API directly), redeploying the same Bicep
  file doesn't recreate it cleanly - it throws a conflict error about
  the unique name still technically existing in a deleted state. The fix
  is one of three specific paths: permanently purge the deleted item,
  restore it, or change the unique name in the Bicep file and redeploy
  under a new identity.
- App-only deployment (the kind used in most CI/CD pipelines) can't
  declare a group with a `membershipRule` (dynamic membership) - that
  combination fails with an explicit "AppOnly OBO tokens not supported"
  error, because dynamic membership evaluation doesn't support the
  automation flow app-only deployments use.
- Application passwords (`passwordCredentials`) aren't supported on
  `applications` or `servicePrincipals` resources - only `keyCredentials`
  (certificates) are. A genuinely required password/secret is another
  `DeploymentScript`-calls-Graph workaround, not a native Bicep property.

### Troubleshooting You'll Actually Hit
- **Error:** a Groups resource deployment fails with a 400 error and no
  obviously wrong syntax -> **Cause:** likely more than 20 members
  and/or owners declared on that single group -> **Fix:** split
  membership assignment across multiple deployments/operations rather
  than declaring everyone in one Groups resource block.
- **Error:** redeploying a previously-working file fails with a
  conflict about a group name that "already exists" even though it's
  gone from the portal -> **Cause:** the group was deleted outside of
  Bicep and Entra still holds it in a soft-deleted state under that
  unique name -> **Fix:** purge or restore the deleted item through
  Graph, or change the Bicep file's unique name and redeploy fresh.
- **Symptom:** a deployment managing Graph resources "succeeds" per the
  CLI, but nothing shows up in the Azure portal's deployment history ->
  **Cause:** expected, not a failure - the portal's deployment details
  page doesn't display Microsoft Graph resources at all -> **Fix:**
  verify success directly in Entra ID or via Graph API/PowerShell.

*Checked against: Microsoft Learn's "Known issues: Microsoft Graph Bicep
Templates" and "Microsoft Graph Bicep Feature Limitations and
Restrictions" docs.*


## Source
<https://devblogs.microsoft.com/identity/bicep-templates-for-microsoft-entra-id-resources-is-ga/>
<https://learn.microsoft.com/en-us/graph/templates/overview-bicep-templates-for-graph>

## Why This Matters (Business Context)
A company onboards dozens of new hires a quarter and manually adds each one to the right groups by hand, in the portal. Every mistake in that process is either someone with access they shouldn't have, or someone missing access they need on day one. Automating group membership is how that scales past a handful of people.
