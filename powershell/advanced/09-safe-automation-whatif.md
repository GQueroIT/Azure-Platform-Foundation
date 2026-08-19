# Advanced 09 - Safe Automation with WhatIf

## Goal

Never make destructive automation the first version of a script.

PowerShell advanced functions can implement `SupportsShouldProcess`, which provides `-WhatIf` and `-Confirm` behavior.

## Practice

Create a local function that would delete a temporary file.

Wrap the change with:

```powershell
[CmdletBinding(SupportsShouldProcess)]
```

and:

```powershell
$PSCmdlet.ShouldProcess(...)
```

Run it with:

```powershell
-WhatIf
```

before allowing a real deletion.

## Azure Application

Choose a lab action that changes or removes a resource.

Build a wrapper function that:

1. discovers the target
2. validates the target
3. calls `ShouldProcess` immediately around the change
4. supports `-WhatIf`

## Rule

Read-only functions do not need `ShouldProcess`.

Functions that change state should be designed with safety from the beginning.
