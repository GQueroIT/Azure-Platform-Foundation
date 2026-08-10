# Validating a Bicep Deployment Before You Run It

You said you wouldn't know to do this without being told, so here's the
full explanation, not just the command.

## The Problem This Solves
Right now, your only way to know if a Bicep file is correct is to deploy
it and see what happens. That's slow, and on a bad day it means deploying
something broken, paying for it while it exists, then tearing it down and
starting over. Validation catches most mistakes in seconds, before
anything is actually created in Azure.

## Two Different Commands, Two Different Jobs

### 1. `az bicep build` - "Is this file even valid syntax?"
```bash
az bicep build --file main.bicep
```
This compiles your Bicep into an ARM JSON file and fails loudly if there's
a syntax error - a missing bracket, a typo in a property name, a resource
type that doesn't exist. It does NOT check Azure at all. It's the fastest
possible check, and it's free, so there's no reason not to run it every
time you save a file.

### 2. `az deployment group validate` - "Would Azure actually accept this?"
```bash
az deployment group validate \
  --resource-group your-rg-name \
  --template-file main.bicep
```
This goes further than `bicep build` - it actually sends your template to
Azure Resource Manager and asks "if I deployed this right now, would it
succeed?" It catches things a syntax check can't: a VM size that isn't
available in your region, a name that's already taken, a parameter that's
missing. It still creates nothing. It's a dry run against the real API.

### 3. `az deployment group what-if` - "What would actually change?"
```bash
az deployment group what-if \
  --resource-group your-rg-name \
  --template-file main.bicep
```
This is the most useful one once you're editing something that already
exists. It shows you a diff: what would be created, what would be
modified, what would be deleted, before any of it happens. If you expect
it to say "1 resource created" and it says "1 resource created, 3
resources deleted," that's your warning, not a surprise after the fact.

## Reading the Output
- `validate` gives you either a clean success, or an error object with a
  `code` and a `message`. The `message` almost always tells you exactly
  what's wrong - read it fully before assuming you need to search for the
  error online.
- `what-if` color-codes its output: green for create, orange for modify,
  red for delete. If you see red and didn't expect it, stop and figure
  out why before deploying.

## Where This Fits In Your Daily Loop
Add this between "translate to Bicep" and "deploy" - see the root
README's Daily Loop section.

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-cli>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-what-if>
