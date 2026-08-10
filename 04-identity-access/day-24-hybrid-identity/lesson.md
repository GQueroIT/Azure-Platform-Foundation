# Day 24 Lesson - Hybrid Identity

## Straight Talk First
Microsoft Entra Connect (the sync engine that connects an on-prem Active
Directory to Entra ID) is an installed agent running on a Windows server,
not an Azure resource and not something Bicep deploys. There is no
`Microsoft.Graph/entraConnect` or ARM equivalent - this is fundamentally
outside both Bicep and the Graph extension's scope, the same way installing
a piece of desktop software isn't something Terraform or Bicep would model
either.

## What This Day Actually Is
Concept and theory, since standing up a real hybrid identity lab needs an
on-prem AD domain controller, which is a heavier lift than this repo's
scope. Focus on:
- What Entra Connect actually syncs (users, groups, password hashes or
  pass-through auth) and on what schedule
- The difference between password hash sync, pass-through authentication,
  and federation (ADFS) - the three ways hybrid auth can work
- Why hybrid identity is still extremely common in real enterprise
  environments, even as cloud-only tenants grow

## If You Want Hands-On Later
This is a good candidate for a future lab once you have spare capacity for
a Windows Server VM: install Entra Connect against a test AD forest, and
watch objects sync into a test Entra tenant. Not this build's scope, but
worth flagging for later.

## Source
General Entra Connect architecture concepts - no Bicep-specific source
applies here since this isn't a Bicep-deployable resource.