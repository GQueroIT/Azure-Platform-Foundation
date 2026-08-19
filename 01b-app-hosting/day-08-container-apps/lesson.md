# Day 08 Lesson - Azure Container Apps

## Core Concepts (Read This First)

### Where Container Apps Sits
Three ways to run a container in Azure, in order of how much you manage
yourself: **App Service** (Linux container support, simplest, closest to
"just run this container as a web app"), **Container Apps** (this
lesson - real container orchestration primitives like revisions and
traffic-splitting, without you managing a Kubernetes cluster), and
**AKS / Azure Kubernetes Service** (full Kubernetes, maximum control and
complexity, you own far more of the operational surface). Container Apps
is deliberately the middle option - Kubernetes-like capabilities, PaaS
levels of operational effort.

### Revisions
Every time you update a Container App's configuration, Azure creates a
new **revision** rather than overwriting the running one in place. By
default only the newest revision serves traffic, but you can run multiple
revisions simultaneously and split traffic between them by percentage -
this is how blue-green deployments or gradual rollouts work on Container
Apps, and it's not something this lesson's basic example shows, but it's
the reason Container Apps exists as a distinct product rather than "App
Service that happens to run containers."

### Consumption vs Dedicated
This lesson's example runs on the **Consumption** plan - pay per second
of actual usage, and the `minReplicas: 0` scale-to-zero behavior only
works here. A **Dedicated** workload profile exists for workloads that
need predictable, reserved capacity instead of consumption-based billing
- worth knowing the option exists even though this build stays on
Consumption to keep costs at zero when idle.

## What You're Building Today
A container deployed to Container Apps on the consumption plan.

## New Bicep Concepts
- `Microsoft.App/managedEnvironments` - the environment a container app
  runs inside (roughly the Container Apps equivalent of an App Service Plan)
- `ingress` block for exposing the container publicly
- `scale` block that lets an app scale to zero

## Annotated Example
```bicep
resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-demo'
  location: resourceGroup().location
  properties: {}
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-demo'
  location: resourceGroup().location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
      }
    }
    template: {
      containers: [
        {
          name: 'demo-container'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}
```

## Why It's Written This Way
- Container Apps has three layers: the environment (`managedEnvironments`),
  the app (`containerApps`), and inside that, the `template.containers`
  array. This is a deeper nesting than App Service because Container Apps
  is designed to run several containers as one logical app (sidecars,
  etc), even though this example only runs one.
- `cpu: json('0.25')` looks odd - CPU has to be passed as a JSON number,
  not a Bicep number literal, because Azure's API expects a specific
  numeric type here. This is one of the few places Bicep makes you reach
  for the `json()` function explicitly.
- `minReplicas: 0` is the reason Container Apps was worth learning
  alongside App Service - it can scale all the way down to zero
  containers running (and zero cost) when there's no traffic, which
  Free-tier App Service can't do in the same way.

## Service Deep Dive

### What It Can't Do
Container Apps doesn't support vertical scaling - there's no "give this
replica more CPU under load," only horizontal scale-out to more
replicas. Replica counts are also a target, not a guarantee - Container
Apps aims for what the scale rule computes, not a contractual exact
number at every instant. Dapr actors specifically can't scale to zero
even if the rest of the app's scale rule would otherwise allow it,
because actor state depends on the replica staying alive.

The Consumption plan's `minReplicas: 0` means the first request after
idle always pays a real cold start - pulling the image, provisioning,
and starting the app. And the default resource allocation when nothing
is specified (0.25 vCPU / 0.5 Gi) is genuinely too small for most
real workloads; it doesn't fail loudly, it just throttles, which looks
exactly like an app bug with no obvious log entry pointing at resource
limits.

### Nuances Worth Knowing
- Editing a scale rule doesn't update the running revision in place - it
  creates an entirely new revision. In multiple-revisions mode, the old
  one keeps running under its old rules until traffic allocation is
  managed manually.
- CPU throttling from an undersized allocation produces no error at all -
  the process just runs slower. That absence of any obvious signal is
  exactly what makes it look like a code problem instead of a sizing one.
- Java apps in particular are known for slow startup, which can trip the
  default readiness probe (the probe times out before the app is
  actually ready) and get a replica stuck restarting in a loop, even
  though it would have started fine given a few more seconds.

### Troubleshooting You'll Actually Hit
- **Symptom:** log stream shows "This revision is scaled to zero" and
  nothing appears to be running -> **Cause:** exactly what it says -
  `minReplicas` is 0 and nothing has triggered scale-out yet ->
  **Fix:** send a request to trigger scale-out, or temporarily deploy a
  revision with `minReplicas: 1` while actively debugging so logs
  actually populate.
- **Symptom:** a revision cycles between Running and Degraded, with
  cryptic exit codes or nothing useful in the logs -> **Cause:** almost
  always one of three things: the process crashes on startup (bad
  config/missing secret), the readiness/liveness probe fails because the
  app takes too long to start, or the app is listening on the wrong port
  -> **Fix:** check system logs first (not just application logs) for
  the actual exit reason, then increase the probe's initial delay if
  slow startup is the real cause.
- **Symptom:** the app feels slow under load with no clear cause in the
  code -> **Cause:** CPU throttling from the default 0.25 vCPU/0.5 Gi
  allocation being too small -> **Fix:** measure actual CPU/memory usage
  first, then explicitly set `resources` on the container to match
  rather than guessing.

*Checked against: Microsoft Learn's "Scaling in Azure Container Apps,"
"Troubleshooting in Azure Container Apps," and "Troubleshoot start
failures in Azure Container Apps" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.app/containerapps>

## Why This Matters (Business Context)
A startup's API gets almost no traffic overnight and spikes hard during business hours. Paying for a server that sits idle sixteen hours a day is real money at scale. Scaling to zero means the meter stops when nobody's using it - you pay for requests, not for a machine sitting there waiting.
