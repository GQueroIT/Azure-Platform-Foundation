# Practice 01 - Fundamentals

## Goal

Become comfortable discovering PowerShell commands instead of waiting to be told the exact syntax.

## Local Warm-Up

Run:

```powershell
Get-Command Get-*
Get-Command *Process*
Get-Help Get-Process -Examples
Get-Help Get-ChildItem -Full
```

### Questions

1. What is the verb in `Get-ChildItem`?
2. What is the noun?
3. What parameter examples did `Get-Help` show?
4. Find a command that writes data to a file without searching the web.

## Azure Discovery Drill

Without looking up the exact answers first, use `Get-Command` to find cmdlets related to:

- resource groups
- management groups
- role assignments
- policy
- locks
- storage accounts
- virtual networks

Example discovery pattern:

```powershell
Get-Command *Az*Lock*
```

Do not stop at finding the cmdlet. Run:

```powershell
Get-Help <cmdlet> -Examples
```

## Lab Application

For the current Azure lab, identify at least three Get-* cmdlets that can inspect what you built.

Do not make changes yet.

## Challenge

Create `command-notes.md` containing:

| Task | Cmdlet I Found | How I Found It |
|---|---|---|

Add five commands discovered without being given their names.
