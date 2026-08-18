# PowerShell — Lessons

Foundational PowerShell curriculum, built from zero, aimed at AZ-104 and real Azure administration. Read in order — each lesson assumes the ones before it.

1. [Fundamentals](lessons/01-fundamentals.md) — what PowerShell is, the help system, running scripts on RHEL
2. [Variables and Data Types](lessons/02-variables-and-data-types.md)
3. [The Pipeline and Objects](lessons/03-pipeline-and-objects.md) — the concept that makes PowerShell different from Bash
4. [Control Flow](lessons/04-control-flow.md) — if/switch/loops
5. [Functions and Parameters](lessons/05-functions-and-parameters.md)
6. [Connecting to Azure](lessons/06-connecting-to-azure.md) — Az module, Microsoft Graph, authentication
7. [Script Structure and Your First Automation Script](lessons/07-script-structure-and-first-automation-script.md) — error handling, plus a full worked script built line by line

`GLOSSARY.md` collects every term across all seven lessons in one place.

## How this fits the rest of the repo

This is the foundation — read once, reference as needed. The **weekend study guide** (`powershell-weekend-study-guide.md`, already in the repo root) is the weekly practice ritual: every Saturday, pick a resource type from that week's Azure lab and write a script against it using what these lessons taught. Lessons teach the language; the weekend guide is where it gets used against real, freshly-built resources.

## Suggested placement

Matches the existing `python-scripts/` convention at repo root:

```
Azure-Platform-Foundation/
├── powershell/
│   ├── README.md
│   ├── GLOSSARY.md
│   └── lessons/
│       ├── 01-fundamentals.md
│       ├── 02-variables-and-data-types.md
│       ├── 03-pipeline-and-objects.md
│       ├── 04-control-flow.md
│       ├── 05-functions-and-parameters.md
│       ├── 06-connecting-to-azure.md
│       └── 07-script-structure-and-first-automation-script.md
├── python-scripts/
├── powershell-weekend-study-guide.md
└── python-weekend-study-guide.md
```

As you write your own weekly scripts (starting from Lesson 7's pattern), a `powershell/scripts/` folder alongside `lessons/` would mirror how `python-scripts/` already holds your own work — naming's your call.
