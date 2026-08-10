# Troubleshooting Log

Real errors you actually hit, and what fixed them. Don't pre-fill this -
it's only useful if it's true.

## How to Read an Azure Error (general, applies everywhere)
Azure CLI and deployment errors almost always follow the same shape:
a `code` (a short category, like `InvalidTemplateDeployment` or
`ResourceNotFound`) and a `message` (a plain-English explanation, usually
telling you exactly what's wrong). Read the full `message` before
searching anything online - it's more specific to your actual situation
than a generic search result will be.

If a deployment fails with a generic top-level error, look for an
`inner error` or run `az deployment operation group list` against that
deployment name - the real cause is often one level deeper than the
first message shown.

Common categories worth recognizing on sight:
- **Naming conflicts** - something with that name already exists, often
  globally (storage accounts, App Service names)
- **Quota/permission errors** - your subscription doesn't allow that VM
  size/region, or your account lacks a specific permission
- **Schema errors** - a property that doesn't exist on that resource
  type, or is spelled/cased wrong
- **Dependency errors** - something referenced (a subnet, a role
  definition) doesn't exist yet or isn't in the state your Bicep assumes

## Log

| Date | Day | Error Message (short) | What I Tried | What Fixed It | Root Cause |
|------|-----|------------------------|---------------|-----------------|--------------|
|      |     |                        |               |                 |              |

By week 3-4 this table is genuinely one of the more valuable things in
this repo - it's proof of real hands-on struggle, not just clean
successes, and it's exactly the kind of detail that makes a portfolio
believable.
