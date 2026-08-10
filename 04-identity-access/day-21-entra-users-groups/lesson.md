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

## Source
<https://devblogs.microsoft.com/identity/bicep-templates-for-microsoft-entra-id-resources-is-ga/>
<https://learn.microsoft.com/en-us/graph/templates/overview-bicep-templates-for-graph>

## Why This Matters (Business Context)
A company onboards dozens of new hires a quarter and manually adds each one to the right groups by hand, in the portal. Every mistake in that process is either someone with access they shouldn't have, or someone missing access they need on day one. Automating group membership is how that scales past a handful of people.
