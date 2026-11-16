# Concepts

These pages explain *why* NativeHTMLKit behaves the way it does. They contain no step-by-step instructions; for those see the [tutorials](../index.md) and [how-to guides](../sdk/python/guides/events-and-callbacks.md) ([PowerShell](../sdk/powershell/guides/events-and-callbacks.md)).

| Page | Read it when you want to understand… |
|---|---|
| [Architecture](architecture.md) | which component owns windows, rendering, language APIs and UI helpers |
| [Process and lifecycle model](lifecycle.md) | why your script runs twice, what `ready` and `shutdown` mean, how quitting is negotiated |
| [Threading and callbacks](threading.md) | where your callbacks run, what may block, how to do background work safely |
| [Documents and stale handles](documents-and-handles.md) | windows vs documents, why an old handle suddenly raises a stale error |
| [Security model](security.md) | what is trusted, what is escaped, what the host refuses |
| [Why native?](why-native.md) | the trade-offs compared with Electron or an embedded browser |

All statements describe the released packages: Core 1.0.3, CLI 0.1.2, Python SDK 0.1.2, PowerShell SDK 0.1.2 and UI 0.1.1.
