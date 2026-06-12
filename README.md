# AutoShopAgentInterface

AutoShopAgentInterface is a Codex skill package and bundled CLI for operating Inovance AutoShop Lite ST projects from automation tools.

This repository is the distributable skill package. It contains the packaged CLI, skill instructions, and reference documents. The development source lives in a separate repository and is not part of the installed skill.

## Development Source

Do not develop skill instructions or references from this distributable package or from the installed Codex skill directory. Update the development source first, then sync this package and the installed skill.

Normal sync order:

1. Update `AutoShopAgentInterfaceDev` source, `knowledge/`, metadata, and runtime records.
2. Sync the distributable package in this repository.
3. Sync the installed Codex skill.

For the EtherCAT/IS620N template reference, sync the development-source knowledge file into this repository's `references\AutoShopEthercatSlaveTemplates.md`.

## Supported AutoShop Version

Verified environment:

- AutoShop: `V4.10.0.0`
- CLI: `scripts/autoshop-agent.exe` `v0.8.129`
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
- Bind motion-axis output devices through workspace JSON, including EtherCAT CiA402 servo PDO mappings such as `motionAxis.axes[].parameters.outputDevice = "IS620N"`.
- Drive selected AutoShop UI actions such as compile, download, upload, monitor, run, stop, screenshot, close project, and restore project.
- Configure and test PLC communication through AutoShop's official communication settings dialog for supported hardware flows.

## Normal Editing Workflow

For project content changes, use the workspace workflow:

```powershell
.\scripts\autoshop-agent.exe ui close-project --project <project-dir> --state <state-json> --format json
.\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
.\scripts\autoshop-agent.exe ui restore-project --state <state-json> --format json
```

If the target project is already open in AutoShop, close and restore it around `workspace apply`. Do not use `--allow-open-project` as a normal write path.

After `workspace apply`, check JSON results for:

- `verified=true`
- `readBackSha256`
- `kind=project-index`
- `kind=project-package`

Those fields indicate that the project file, project index, and package snapshot were written and read back successfully.

Existing interrupt routine trigger settings are exported to `编程/程序块/_interrupt-triggers.json`. Edit `interrupts[].trigger`; `workspace apply` writes the AutoShop 4.10 `.hcp` interrupt `<POUID>` value, keeps `<Timer>0</Timer>`, verifies the readback, and syncs `.hcpp`. Use `trigger.type=raw` with `rawCode` for unknown or ambiguous AutoShop POUID encodings.

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
.\scripts\autoshop-agent.exe config init --project <project-dir> --force
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
