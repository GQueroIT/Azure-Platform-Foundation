# Day 23 Lesson - Conditional Access and SSPR

## Straight Talk First
Conditional Access policies and Self-Service Password Reset (SSPR)
configuration are NOT in the Microsoft Graph Bicep extension's supported
resource list (that list is Applications, App role assignments, Federated
identity credentials, Groups, OAuth2 permission grants, and Service
principals as of this extension's GA release). There is no
`Microsoft.Graph/conditionalAccessPolicies` you can safely lean on the same
way you leaned on `Microsoft.Graph/groups` on Day 21.

That means today isn't a Bicep lesson at all - it's a "know what tool
actually does this job" lesson, which matters just as much for the exam
and for real work.

## What Actually Configures This
- **Conditional Access policies**: Microsoft Graph PowerShell SDK
  (`New-MgIdentityConditionalAccessPolicy`) or the Azure Portal. Some
  teams manage CA policies as JSON exported/imported via Graph API calls
  in a script, which is "infrastructure as code" in spirit even though
  it isn't Bicep.
- **SSPR**: configured entirely through the Entra ID portal's
  Authentication Methods and Password Reset blades, or via Graph API/
  PowerShell for the authentication methods policy object.

## Why This Matters For The Exam
AZ-104 does test Conditional Access and SSPR concepts - what they do, how
they're scoped, what "report-only" mode means - but it is testing your
understanding of the FEATURE, not asking you to write Bicep for it. Don't
walk into the exam expecting a Bicep-code question here.

## What To Actually Do Today
Cross-reference your identity-security-entra project - if Conditional
Access and SSPR are already built there via PowerShell/Graph API, this is
mostly a review day: go confirm you can explain, out loud, what each
policy does and why, without looking at the config.

## Source
<https://devblogs.microsoft.com/identity/bicep-templates-for-microsoft-entra-id-resources-is-ga/>
(confirms the supported resource list, which is how we know this is out
of scope for Bicep specifically)

## Why This Matters (Business Context)
An employee's password gets phished, and the attacker logs in from a country the company has never had an employee travel to, with no resistance at all. Conditional Access is the policy layer that catches exactly that pattern and blocks or challenges it. SSPR exists because 'call IT to reset your password' doesn't scale past about 50 employees - it becomes the single most common helpdesk ticket at any company without it.
