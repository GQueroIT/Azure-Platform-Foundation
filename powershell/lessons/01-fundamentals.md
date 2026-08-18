# Lesson 1 — Fundamentals

## What PowerShell actually is

PowerShell is two things at once: an interactive **shell** (like Bash — you type a command, it runs, you see output) and a full **scripting language** (you can save a sequence of commands to a file and run the whole thing at once). It was built by Microsoft on top of .NET, which is why — unlike Bash — its commands pass structured data around instead of plain text. That single fact shapes almost everything else in this lesson set, and it's covered properly in Lesson 3.

## Why it matters here specifically

AZ-104 tests Portal, CLI, and PowerShell administration — not Bicep authoring. PowerShell is also the tool most real Azure admin work runs on day to day: bulk operations, scheduled checks, anything you'd do by hand in the Portal a hundred times and don't want to. Learning it isn't a side quest — it's a core AZ-104 skill and a core Cloud Engineer skill, which is why it's getting the same depth of treatment as the Bicep side of this repo.

## Interactive vs. script

- **Interactive**: you type a command directly into the terminal (`pwsh` on RHEL) and it runs immediately. Good for exploring, checking one thing, testing a single line before it goes into a script.
- **Script**: a `.ps1` file containing a sequence of commands, saved and run as a unit. This is what "automation" means in practice — the whole point of a script is that you write it once and it does the same correct sequence of steps every time, instead of you retyping commands and risking a mistake on the tenth run.

On RHEL, PowerShell 7 runs as `pwsh`, not `powershell` (that name is Windows PowerShell 5.1, which doesn't exist on Linux). To run a script:

```bash
pwsh ./my-script.ps1
```

Unlike Windows, Linux doesn't enforce PowerShell's "execution policy" restrictions by default — you won't hit the classic "scripts are disabled on this system" error that trips up Windows beginners. You can run `.ps1` files directly once they're on disk.

## The help system — how to not memorize everything

You are not expected to know every cmdlet (PowerShell's term for a built-in command — covered fully in Lesson 3). You're expected to know how to find out what a cmdlet does, right from the terminal:

```powershell
Get-Help Get-AzVM              # shows syntax, description, examples
Get-Help Get-AzVM -Examples    # just the usage examples
Get-Help Get-AzVM -Full        # everything, including every parameter
```

```powershell
Get-Command -Module Az.Compute # lists every cmdlet in a given module
Get-Command *VM*               # search by wildcard if you don't know the exact name
```

```powershell
Get-Member                     # run after any command, piped in — shows every
                                # property and method on the object it returned
```

`Get-Member` gets its own full explanation in Lesson 3 once objects have been introduced properly, but know now that it exists — it's the single most useful "I don't know what this thing is" command in PowerShell.

## What's next

Lesson 2 covers variables and data types — the building blocks any script needs before it can do anything useful.
