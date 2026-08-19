# Advanced 10 - Error Handling and Logging

## Error Handling

Learn the difference between errors that stop execution and errors that continue.

For Az cmdlets used inside `try/catch`, use `-ErrorAction Stop` when failure should be caught.

## Practice

Write a script that intentionally queries a nonexistent Azure resource group.

Handle the failure and produce a clear message.

## Logging

Create structured log records with:

```text
Timestamp
Operation
Target
Status
Message
```

Represent each record as a PowerShell object.

Export the log to CSV.

## Challenge

Run an operation over multiple resources.

One failure should be logged clearly.

Decide whether the remaining resources should continue or whether the script should stop, and explain why.

## Stretch

Add a `-Verbose` mode for troubleshooting without cluttering normal output.
