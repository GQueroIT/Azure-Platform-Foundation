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

## Service Deep Dive

### What It Can't Do
Conditional Access can't retroactively kill an already-issued sign-in
token - policies are evaluated at sign-in time, so a session established
before a new or tightened policy takes effect keeps running under the
old rules until the token naturally expires or the user is forced to
reauthenticate. It also can't protect against legacy authentication a
third-party app still uses under the hood - if an app authenticates
using a protocol Conditional Access doesn't evaluate, CA simply never
gets a chance to apply. And Conditional Access for workload identities
(service principals, managed identities) is a related-but-distinct
capability from user-focused CA - a policy scoped to "All users" doesn't
automatically cover a service principal's sign-ins unless workload
identity CA is specifically configured for it.

### Nuances Worth Knowing
- Report-only mode is genuinely load-bearing, not a formality: it
  evaluates every sign-in against the policy and logs exactly what
  *would* have happened, without blocking or requiring anything. The
  universally repeated guidance across real incident write-ups is that
  every new policy starts in Report-only and gets checked against
  sign-in logs before ever switching to On, no exceptions.
- The single most common cause of a full tenant lockout isn't an
  attacker - it's an admin publishing a policy scoped to "All users"
  (instead of a pilot group) directly to On, with no break-glass account
  excluded. When every admin loses access at once, there's no way to fix
  it from inside the tenant - it becomes an out-of-band recovery
  problem.
- Break-glass accounts (at least two, cloud-only, excluded from every CA
  policy) exist specifically as the last resort for that failure mode.
  Best practice explicitly recommends two, not one - a single account is
  itself a single point of failure if its password expires or its
  credential is lost.
- A Conditional Access policy that blocks legacy authentication or
  requires a compliant device can end up blocking the very sign-in flow
  a user needs to reach the SSPR password reset page, if the reset
  portal itself isn't explicitly accounted for in policy scope.

### Troubleshooting You'll Actually Hit
- **Symptom:** every administrator is suddenly unable to sign in
  shortly after a Conditional Access change -> **Cause:** almost always
  a policy scoped too broadly, pushed straight to On without a
  break-glass exclusion, matching the classic full-tenant-lockout
  pattern -> **Fix:** if a working break-glass account exists, sign in
  with it and disable/fix the offending policy immediately; if none
  works, this becomes a Microsoft Support recovery case, not something
  fixable from inside the tenant.
- **Symptom:** a new policy switched to On and specific users report
  being blocked unexpectedly -> **Cause:** the policy wasn't validated
  in Report-only first, so edge cases weren't caught before enforcement
  -> **Fix:** revert to Report-only, review sign-in logs filtered to
  that policy name for every would-be-blocked result, and resolve or
  explicitly exclude each case before re-enabling.
- **Symptom:** a user can't complete SSPR after a Conditional Access
  rollout despite correct credentials -> **Cause:** the policy is
  blocking the authentication step needed to reach the reset flow itself
  -> **Fix:** confirm the SSPR path is accounted for in the policy's
  scope or exclusions, not just the main sign-in flow.

*Checked against: Microsoft Q&A and Microsoft Learn guidance on
Conditional Access lockout recovery and Report-only rollout practices.*


## Source
<https://devblogs.microsoft.com/identity/bicep-templates-for-microsoft-entra-id-resources-is-ga/>
(confirms the supported resource list, which is how we know this is out
of scope for Bicep specifically)

## Why This Matters (Business Context)
An employee's password gets phished, and the attacker logs in from a country the company has never had an employee travel to, with no resistance at all. Conditional Access is the policy layer that catches exactly that pattern and blocks or challenges it. SSPR exists because 'call IT to reset your password' doesn't scale past about 50 employees - it becomes the single most common helpdesk ticket at any company without it.
