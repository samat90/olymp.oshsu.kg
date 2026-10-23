# Microsoft C# / .NET 10

`CSHARP.py` is the OshSU executor for the Linux DMOJ judge-server. The website
alone cannot execute submissions; this module must also be installed on every
judge advertising `CSHARP`.

## Install on the judge (Ubuntu 24.04)

```sh
sudo apt-get install dotnet-sdk-10.0
cp scripts/judge/CSHARP.py /home/admin/judge-server/dmoj/executors/CSHARP.py
cd /home/admin/judge-server
venv/bin/python /path/to/scripts/judge/test_csharp_executor.py
```

Only after the suite passes, add this entry to `runtime` in the judge YAML:

```yaml
runtime:
  dotnet: /usr/bin/dotnet
```

Keep the existing compiler entries. Mono remains installed for historical
submissions. Back up the website database and judge configuration before rollout.
Apply website migration `0153_modern_csharp`, then restart `olymp-judge` and
`olymp-web`. Verify `/status/` and submit an A+B solution through the website.

The migration switches only problems that previously allowed Mono, copies their
language-specific limits, and updates Mono preferences. It preserves historical
submission language IDs and does not enable C# for restricted problems. The small
language fixture uses natural keys so reloading it cannot overwrite old language
IDs. Migration rollback restores Mono choices while retaining C# submissions.

## Execution contract

- Microsoft Roslyn, C# 14, .NET 10 standard library; one UTF-8 `.cs` file.
- Both top-level programs and `static Main` are supported. No NuGet packages,
  MSBuild files, analyzers, or user-controlled build steps are run.
- Compilation and execution both use DMOJ's traced sandbox. No unsandboxed
  subprocess fallback is used.
- CoreCLR needs threads and anonymous executable mappings. `memfd` files are
  limited to 64 MiB each; ordinary filesystem writes remain forbidden. The
  virtual address allowance does not increase the problem's RSS memory limit.
- Diagnostics/telemetry are disabled. Only private process memory barriers are
  permitted; locking physical memory and querying NUMA policy return permission
  errors. Network sockets and process creation remain restricted by DMOJ.
- The regression suite covers modern syntax, standard libraries, Unicode,
  compilation errors, runtime errors, cached binaries, CPU/wall-time limits,
  memory limits, private files, writes, network access, and child processes.

References: [Microsoft's Ubuntu installation guide](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-install)
and [DMOJ judge-server](https://github.com/DMOJ/judge-server).
