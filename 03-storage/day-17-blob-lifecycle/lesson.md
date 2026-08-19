# Day 17 Lesson - Blob Storage and Lifecycle Management

## Core Concepts (Read This First)

### Archive Tier Isn't Instantly Readable
Worth knowing before you rely on a lifecycle policy that tiers blobs to
Archive: data in the Archive tier isn't available for immediate read.
Retrieving it requires a **rehydration** step - moving the blob back to
Hot or Cool - which can take several hours depending on the priority you
choose. A lifecycle rule that archives old data is a great cost saver for
data you rarely need, and a real problem if you ever need that data back
in a hurry. This is exactly why this lesson's rule tiers to Cool at 30
days and Archive only at 90 - giving you a slower-but-still-readable
middle tier before anything becomes hours-to-retrieve.

## What You're Building Today
A lifecycle management policy that moves blobs to cheaper tiers over time
and eventually deletes them.

## New Bicep Concepts
- A resource nested under a storage account using `parent`, with the fixed
  name `'default'`
- Rule-based policy structure (`filters` + `actions`, not imperative code)

## Annotated Example
```bicep
resource lifecyclePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    policy: {
      rules: [
        {
          name: 'auto-tier-rule'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [ 'blockBlob' ]
            }
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 30
                }
                tierToArchive: {
                  daysAfterModificationGreaterThan: 90
                }
                delete: {
                  daysAfterModificationGreaterThan: 365
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

## Why It's Written This Way
- The resource name is always literally `'default'` - a storage account
  only ever has one management policy resource, so there's nothing to
  parameterize about the name itself.
- This is a declarative rules engine, not a script - you're not writing
  "check age, then move it." You're describing conditions (`filters`) and
  outcomes (`actions`), and Azure's platform runs this check on a schedule
  in the background. There's no Bicep-side loop or logic here at all.
- The three actions chain naturally: cool after 30 days, archive after 90,
  delete after 365. Each threshold is evaluated independently against the
  blob's last-modified date, not against each other, so a blob doesn't
  have to pass through cool and archive to reach delete - if you skip
  archive, delete still fires on schedule.
- `filters.blobTypes` can scope this to just block blobs, or you can add a
  `prefixMatch` array to only affect blobs in a specific
  container/folder path.

## Service Deep Dive

### What It Can't Do
A lifecycle management policy can't rehydrate a blob back to an online
tier - it only ever moves things toward colder/cheaper tiers or deletes
them; getting a blob out of Archive requires a separate, manual
rehydration operation. It also can't run retroactively against its own
creation - it applies going forward from its first evaluation, so blobs
that already qualify at the moment the policy is created don't get swept
up instantly; they wait for the first evaluation cycle like everything
else.

The delete action specifically won't touch a blob in an immutable
container, or a blob currently in a soft-deleted state - the policy
engine respects both protections rather than overriding them. And a
policy can't be partially updated - the whole JSON policy is one
document, so a small edit means resubmitting the entire policy, not
patching one rule in place.

### Nuances Worth Knowing
- Nothing here runs on demand or continuously - Azure evaluates
  lifecycle policies roughly once per day, and after creating or editing
  a policy, the first evaluation can take up to 24 hours to even start.
  "I set the rule five minutes ago and nothing moved" isn't broken, it's
  just before the first scheduled run.
- The clock a rule uses depends on what it's evaluating: current blob
  versions use last-modified time (or last-access time, if access
  tracking is explicitly enabled - it's off by default), previous
  versions use their own creation time, and snapshots use the time the
  snapshot itself was taken.
- Moving a blob out of Cool into Archive before it's spent Cool's
  minimum retention window (30 days) triggers an early-deletion charge -
  a real, billed penalty for a rule that tiers too aggressively.
- If a blob gets manually rehydrated back to Hot/Cool while a lifecycle
  policy targeting it is still active, the same policy can tier it right
  back to Archive on its next run - rehydrating doesn't exempt a blob
  from the rule that archived it unless the rule or blob itself changes.

### Troubleshooting You'll Actually Hit
- **Symptom:** a rule was created or edited, and blobs that clearly meet
  its conditions haven't moved or deleted after a day or more ->
  **Cause:** either still within the up-to-24-hour window before the
  first evaluation, or the modification/access timestamp hasn't actually
  crossed the threshold yet -> **Fix:** confirm the actual timestamp on
  the blob itself, and wait out the full evaluation window before
  assuming the rule is broken.
- **Symptom:** blobs that should be deleted remain in place indefinitely
  -> **Cause:** commonly the blob is in an immutable container, or in a
  soft-deleted state, both of which the delete action deliberately won't
  touch -> **Fix:** check the container's immutability policy and the
  blob's soft-delete status before assuming the rule is misconfigured.
- **Symptom:** a rule using `daysAfterLastAccessTimeGreaterThan` never
  triggers -> **Cause:** access time tracking wasn't explicitly enabled
  on the account, so `LastAccessTime` isn't being recorded at all ->
  **Fix:** enable last-access-time tracking first; a last-access rule
  with tracking off will silently never fire.

*Checked against: Microsoft Learn's "Azure Blob Storage lifecycle
management overview" and "lifecycle management policy structure"
docs.*


## Source
<https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-policy-configure>

## Why This Matters (Business Context)
A company keeps every log file it's ever generated on the same expensive storage tier it uses for active data, because nobody set up a policy to move it. Lifecycle management is the unglamorous rule that quietly saves real money every month without anyone having to remember to run a cleanup script.
