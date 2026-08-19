# Practice 04 - Control Flow

## Goal

Make scripts react to the state they discover.

## Local Practice

Create:

```powershell
$cost = 18
```

Write logic:

```text
If cost is 0 -> "No cost"
If cost is less than 20 -> "Within lab range"
Otherwise -> "Investigate"
```

Then rebuild it with `switch` if appropriate.

## Operator Drill

Practice:

- `-eq`
- `-ne`
- `-gt`
- `-lt`
- `-like`
- `-contains`
- `-and`
- `-or`
- `-not`

## Azure Application

Pick a resource from the current lab.

Use PowerShell to determine whether it has a required tag.

Pseudocode:

```text
Get resource
If Service tag exists
    print its value
Else
    print "Missing Service tag"
```

At this point, only report the problem. Do not fix it automatically yet.

## Challenge

Check whether the active Azure context points at the expected subscription.

If not, print a warning and stop your practice script.
