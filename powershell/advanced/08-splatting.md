# Advanced 08 - Splatting

## Why

Azure cmdlets become difficult to read when they have many parameters.

Splatting stores command parameters in a hashtable.

## Practice

Start with:

```powershell
$params = @{
    Name     = "example"
    Location = "eastus"
}
```

Inspect the hashtable.

Then use splatting with a harmless local or read-only command before applying it to an Azure create/change command.

## Azure Application

Take one Azure cmdlet from a completed lab that uses several parameters.

Write it once normally.

Then rewrite it with a splatting hashtable.

## Challenge

Add or remove one optional parameter by changing only the hashtable.

## Why It Matters

This becomes important when scripts later construct parameters conditionally.
