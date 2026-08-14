# Resource Reference

A running lookup of every Bicep resource type used in this repo — the
full `Provider/resourceType@apiVersion` string, in one place, so you
never have to hunt for it mid-lab. Grows day by day as new resource
types get introduced.

Each entry is checked against Microsoft Learn's template reference
(`learn.microsoft.com/en-us/azure/templates/<namespace>/<resourcetype>`)
at the time it's added — that page is the actual source of truth, this
file is just a fast local copy of what you've already used. If a version
here ever looks stale, that Learn page is where to re-check it, or type
the resource type into VS Code with the Bicep extension and let
IntelliSense confirm the current version.

## How to read this table
- **Resource** — plain-language name
- **Type + API version** — the exact string that goes after `resource
  symbolicname` in a `.bicep` file
- **What it does** — one line
- **Day** — which day's lesson first introduced it, so you can jump back
  to the fuller explanation in that day's `lesson.md`

---

## 01-compute-governance

| Resource | Type + API version | What it does | Day |
|---|---|---|---|
| Management group | `Microsoft.Management/managementGroups@2021-04-01` | Creates a governance container above a subscription | Day 01 |
| Custom role definition | `Microsoft.Authorization/roleDefinitions@2022-04-01` | Defines a named, custom set of permissions | Day 01 |
| Role assignment | `Microsoft.Authorization/roleAssignments@2022-04-01` | Attaches a role (built-in or custom) to a person/group at a scope | Day 01 |

---

*(New sections get added here as each phase folder's days introduce new
resource types — 01b-app-hosting, 02-networking, 03-storage,
04-identity-access, 05-monitoring-backup.)*