# AutoShop Agent Operational Workflow

This reference contains the operational rules that do not belong in `SKILL.md`.

## Table of Contents

- Core rule
- Standard edit workflow
- AutoShop UI workflow
- Real hardware boundary
- Validation checklist
- Reference routing

## Core Rule

Use the bundled CLI first:

```text
scripts/autoshop-agent.exe
```

Do not reimplement AutoShop binary ST parsing, workspace apply logic, HCP/HCPP synchronization, or Win32 UI automation unless the task is to maintain the CLI itself.

Keep package-internal resource paths relative to the skill root. Use caller-provided placeholders such as `<project-dir>`, `<workspace-dir>`, `<state-json>`, `<tmp-dir>`, `<archive-dir>`, `<plc-ip>`, and `<device-library-dir>` for external paths and hardware values.

## Standard Edit Workflow

For normal AutoShop project content changes, use the workspace mirror:

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui close-project --project <project-dir> --state <state-json> --format json
.\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
.\scripts\autoshop-agent.exe ui restore-project --state <state-json> --format json
```

If AutoShop is not currently opening the target project, skip `close-project` and `restore-project`. If AutoShop is opening another project, do not close it.

Use `--allow-open-project` only when the user explicitly accepts bypassing the close/export/apply/restore path. This is not the default path.

After `workspace apply`, inspect JSON output for:

- `verified=true`
- `readBackSha256`
- expected `kind=project-index` and `kind=project-package` entries when `.hcp` or `.hcpp` must change

## AutoShop UI Workflow

Use UI commands for AutoShop actions that must go through the official application:

```powershell
.\scripts\autoshop-agent.exe ui compile-all --tail 50 --format json
.\scripts\autoshop-agent.exe ui output --pane compile --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui download --yes --timeout-ms 60000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui upload --timeout-ms 8000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui monitor --timeout-ms 4000 --format json
.\scripts\autoshop-agent.exe ui screenshot --out <tmp-dir>\autoshop.png --format json
```

`ui compile`, `ui compile-all`, `ui run`, `ui stop`, `ui download`, `ui upload`, and `ui monitor` map to AutoShop `Ctrl+F7`, `F7`, `F5`, `F6`, `F8`, `F9`, and `F3`.

`ui download --yes` confirms AutoShop download dialogs, but does not run the PLC after download unless `--run-after` is explicitly passed.

`ui upload` triggers upload and collects output/dialog evidence; it does not automatically confirm an upload flow that could rewrite the current AutoShop session.

Use `ui screenshot` for visual verification. Check screenshot JSON for a healthy `contentRatio` and no blank-capture warning; `nonBlank=true` and `uniqueProbe > 1` are only auxiliary probes because title bars can make a blank client area look non-empty.

## Real Hardware Boundary

Most target-like commands default to simulator behavior. Treat these as simulator/local unless the command explicitly says otherwise:

- `target`
- `online`
- `monitor`
- `comm`
- `motion`
- `build compile/down/updown`

Real AutoShop communication setup is only:

```powershell
.\scripts\autoshop-agent.exe target transports --backend hardware --format json
.\scripts\autoshop-agent.exe target scan --backend hardware --transport <transport> --format json
.\scripts\autoshop-agent.exe target connect --backend hardware --transport <transport> --ip <plc-ip> --format json
.\scripts\autoshop-agent.exe target connect --backend hardware --profile h5u --format json
```

`--transport` may be `ethernet`, `usb`, `index:N`, or the exact visible text from AutoShop's communication type combo box. For H5U, prefer the exact AutoShop-visible adapter entry when the generic Ethernet entry does not connect.

Real PLC actions through AutoShop UI are:

- RUN: `ui run`
- STOP: `ui stop`
- Download: `ui download --yes`
- Upload: `ui upload`
- Monitor: `ui monitor`

Do not describe simulator `target run`, `monitor write`, `build down`, or `motion axis` commands as real PLC operations.

## Validation Checklist

For file-only edits:

1. Run `workspace apply --dry-run`.
2. Run `workspace apply`.
3. Re-export or inspect readback SHA from CLI output.
4. Restore/open the project in AutoShop if UI visibility matters.
5. Compile with `ui compile-all`.

For AutoShop UI changes:

1. Read command JSON output.
2. Read the relevant output pane with `ui output`.
3. Capture screenshot when page visibility matters.
4. Confirm no modal dialogs are left open.

For hardware actions:

1. Connect with `target connect --backend hardware`.
2. Compile before download.
3. Use `ui download --yes` for real download.
4. Use `ui monitor` and screenshots/output panes for online verification.

## Reference Routing

- CLI syntax and command catalog: `references/AutoShopCliCommands.md`
- Workspace JSON editable surfaces: `references/AutoShopWorkspaceJsonReference.md`
- AutoShop UI refresh/screenshot behavior: `references/AutoShopUiRefresh.md`
- ST container format and LiteST text rules: `references/AutoShopLiteStFormat.md`
- H5U quick hardware/config guide: `references/AutoShopH5uQuickReference.md`
- Full H5U/AutoShop manuals: `references/AutoShopH5uEasyProgrammingApplicationManual.md`, `references/AutoShopH5uPlcInstructionManualCn.md`, `references/AutoShopH5uSeriesUserManualCn.md`, `references/AutoShopH5uSeriesBrochureEn.md`
- EtherCAT/IS620N template work: `references/AutoShopEthercatSlaveTemplates.md`
- Skill packaging path/privacy rules: `references/AutoShopSkillPathPolicy.md`
- Test and maintenance commands: `references/AutoShopCliTesting.md`
