# Advanced 11 - Idempotent and State-Aware Automation

## Goal

Stop writing scripts that blindly perform actions.

Ask:

```text
What is the current state?
What is the desired state?
Is a change actually required?
```

## Tag Example

```text
Correct tag already exists -> do nothing
Tag missing -> add it
Tag has wrong value -> update it
```

## Lock Example

```text
Correct CanNotDelete lock exists -> do nothing
No lock -> create it
Wrong lock level -> report or change based on script purpose
```

## VM Example

```text
VM already deallocated -> do nothing
VM running and should be stopped -> stop it
```

## Practice

Take one lab task previously performed manually.

Write pseudocode for current state vs desired state before writing PowerShell.

Then implement version 1 as reporting only.

Only after the report is correct should version 2 make changes.
