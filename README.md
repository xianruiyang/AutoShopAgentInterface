# AutoShopAgentInterface

AutoShopAgentInterface is a Codex skill package and bundled CLI for operating Inovance AutoShop Lite ST projects from automation tools.

This repository is the distributable skill package. It contains the packaged CLI, skill instructions, and reference documents. The development source lives in the separate `AutoShopAgentInterfaceDev` repository.

## Supported AutoShop Version

Verified environment:

- AutoShop: `V4.10.0.0`
- CLI: `scripts/autoshop-agent.exe` `v0.8.125`
- OS: Windows
- PLC family used for hardware validation: Inovance H5U

Known version boundary:

- `V4.10.0.0` is the current supported target.
- `V4.11.0.5` is not the supported baseline for this package. Local testing showed behavior differences around project editing and UI automation, so do not assume it is compatible without re-validation.
- Other AutoShop versions may work for offline project parsing, but UI commands, command IDs, dialogs, and binary project formats must be validated before real use.

## What This Package Does

The CLI entrypoint is:

```powershell
.\scripts\autoshop-agent.exe
```

Main capabilities:

- Export an AutoShop project into an editable workspace mirror.
- Apply workspace JSON/text changes back into the AutoShop project.
- Read and write LiteST POU text through the workspace flow.
- Inspect ST text, project metadata, variable tables, and supported configuration nodes.
- Drive selected AutoShop UI actions such as compile, download, upload, monitor, run, stop, screenshot, close project, and restore project.
- Configure and test PLC communication through AutoShop's official communication settings dialog for supported hardware flows.

## Normal Editing Workflow

For project content changes, use the workspace workflow:

```powershell
.\scripts\autoshop-agent.exe ui close-project --project F:\program\PLC\001 --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
.\scripts\autoshop-agent.exe workspace export --project F:\program\PLC\001 --out F:\program\PLC\AutoShopAgentInterfaceWork\current-export --force --format json
.\scripts\autoshop-agent.exe workspace apply --project F:\program\PLC\001 --in F:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project F:\program\PLC\001 --in F:\program\PLC\AutoShopAgentInterfaceWork\current-export --format json
.\scripts\autoshop-agent.exe ui restore-project --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

If the target project is already open in AutoShop, close and restore it around `workspace apply`. Do not use `--allow-open-project` as a normal write path.

After `workspace apply`, check JSON results for:

- `verified=true`
- `readBackSha256`
- `kind=project-index`
- `kind=project-package`

Those fields indicate that the project file, project index, and package snapshot were written and read back successfully.

## Real PLC Boundary

Only the following command families intentionally use AutoShop hardware/UI paths:

- `target transports --backend hardware`
- `target scan --backend hardware`
- `target connect --backend hardware`
- `ui run`
- `ui stop`
- `ui download --yes`
- `ui upload`
- `ui monitor`

Important notes:

- `target scan/connect --backend hardware` drives AutoShop communication settings and can select communication type, set PLC IP, search, and test connection.
- `ui download --yes` triggers AutoShop's real F8 download flow. It does not run the PLC after download unless `--run-after` is explicitly used.
- `ui run` and `ui stop` map to AutoShop F5/F6 and control the connected PLC in the normal AutoShop online workflow.
- `online`, `monitor`, `comm`, `motion`, `build compile/down/updown`, and most `target` commands are simulator/local placeholder commands unless explicitly documented otherwise.

Do not treat simulator output as confirmation that a real PLC changed state.

## UI Automation Notes

AutoShop uses native Windows UI and modal dialogs. The CLI uses Win32 window messages and attempts to keep AutoShop offscreen or minimized when possible, but UI commands can still interact with the running AutoShop process.

Before relying on UI automation:

- Make sure the expected AutoShop version is installed.
- Make sure the target project path in AutoShop matches the project being edited.
- Prefer `--format json` and inspect returned dialogs and output panes.
- For screenshots, check `nonBlank=true` and `uniqueProbe > 1`.

## Encoding And Project Files

Typical H5U/Easy LiteST project text uses `gb2312` project text encoding, while exported workspace text and JSON are intended for UTF-8 editing.

Do not hand-edit AutoShop binary project files directly. Edit the workspace mirror and use `workspace apply`.

## Configuration

Default configuration path:

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

Create or update a config:

```powershell
.\scripts\autoshop-agent.exe config init --project F:\program\PLC\001 --force
```

The `autoShopExePath` field is currently reserved for launch support. Normal offline export/apply and UI refresh logic find the running AutoShop process instead of depending on that path.

## References

More detailed command documentation is in:

- `SKILL.md`
- `references/AutoShopCliCommands.md`
- `references/AutoShopLiteStFormat.md`
- `references/AutoShopUiRefresh.md`
- `references/AutoShopCliTesting.md`

## License

MIT. See `LICENSE`.
