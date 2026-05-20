# AutoShop Agent CLI Command Set Design

Status: design only. Do not treat the commands in this document as implemented.

## Purpose

Design a complete future CLI surface for AutoShop Lite ST development. The CLI should support repeatable project development, source editing, validation, packaging, deployment, online diagnostics, and AutoShop UI refresh without hard-coding the user's AutoShop installation path.

Current executable coverage is intentionally small: ST text list/export/import, open POU window listing, and close/reopen refresh. Everything else below is a target interface.

## Source Documents Reviewed

Local installed documents:

- `D:\software\AutoShop\Manual\AutoShop.chm`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U&Easy系列可编程逻辑控制器编程与应用手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U&Easy系列可编程逻辑控制器指令手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\Easy系列可编程逻辑控制器用户手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U系列可编程逻辑控制器用户手册.pdf`

External confirmation sources:

- Inovance H5U Series product page: `https://www.inovance.com/global/content/details_815_403258.html`
- Inovance Easy Series product page: `https://www.inovance.com/global/content/details_815_555452.html`
- Inovance Easy301 User Guide PDF, "More Documents" table listing the H5U/Easy Programming and Application Guide and Instruction Guide: `https://portal-file.inovance.com/owfile/ProdDoc/SC/PS00006239_PDF_EN/A05/Easy301%20Programmable%20Logic%20Controller%20User%20Guide-EN-A05.PDF`
- Inovance H5U User Guide PDF, related-documents table listing the Programming and Application Guide: `https://portal-file.inovance.com/owfile/ProdDoc/SC/19011517-SC/A02/19011517-SC_A02%E3%80%8AH5U%20Series%20Programmable%20Logic%20Controller%20User%20Guide%E3%80%8B-EN.pdf`

## Document Findings That Shape The CLI

### Development Flow

The programming and application manual defines a typical workflow around:

- Communication setup by Ethernet or USB.
- Project creation and hardware configuration.
- Editing `MAIN`.
- Program compile.
- Optional PLC login.
- Program download.
- PLC run/stop.
- HMI/online monitoring.
- Online modification mode.
- Program scan cycle and EtherCAT task cycle settings.
- Project archive pack/unpack.
- Trace monitoring import/export.

Implication: the future CLI must not stop at file editing. It needs project, build, target connection, download/upload, run-state, online modification, monitoring, and archive commands.

### LiteST Source Model

The manual describes LiteST as a high-level text language for automation systems, with Pascal-like syntax, variables, operators, expressions, control-flow statements, FB/FC/subprogram/interrupt invocation, and exception behavior for divide-by-zero and array bounds.

The instruction manual defines LiteST instructions as instruction name + parameters + return value, and separates:

- LD and LiteST shared instructions.
- LiteST-only instructions.
- Communication instructions.
- Motion-control instructions.
- String and array instructions.
- Error-code tables.

Implication: the CLI should include syntax-aware `st` and instruction-reference commands, not only binary container import/export.

### Online Operation And Safety

The manuals describe RUN/STOP modes, online modification limits, login password behavior, download behavior, and warnings around power loss or safety-critical control.

Implication: all target-affecting commands must be explicit, should require a selected connection profile, and must default to dry-run or confirmation unless a noninteractive flag is supplied.

### Debug And Diagnostics

The manuals cover Trace, memory management, project comparison, software diagnostics, running logs, error-code lists, Modbus errors, and panel indicator status.

Implication: the CLI should provide inspectable, machine-readable JSON output for diagnostics and monitoring, and should preserve raw exports for audit.

### Packaging

The programming and application manual documents `.down` and `.updown` generation:

- `.down` can be generated from a compiled project for download without opening the original project.
- `.updown` supports upload/download and may include source for later editing.
- Down/updown operations include options around source inclusion, retain-variable handling, login password, and password modification.

Implication: the CLI needs package-generation commands even if implementation may require AutoShop automation or compiler entry-point discovery.

## Global CLI Conventions

Executable:

```powershell
autoshop-agent.exe <command> [subcommand] [flags]
```

Common flags:

```text
--config <path>              JSON config path. Overrides AUTOSHOP_AGENT_CONFIG.
--project <dir|file>         Project directory or project file.
--profile <name>             Connection/profile name from config.
--format text|json|ndjson    Output format. Default text for humans, json for automation.
--dry-run                    Resolve and validate without writing or affecting PLC/AutoShop.
--yes                        Noninteractive confirmation for dangerous operations.
--timeout <duration>         Operation timeout, for example 30s or 2m.
--log <path>                 Write structured runtime log.
--verbose                    Include additional detail.
--quiet                      Print only essential output.
```

Exit codes:

```text
0   success
1   generic error
2   usage/config error
3   project parse error
4   compile/build error
5   target connection error
6   target rejected operation
7   AutoShop UI automation error
8   validation/check failed
9   unsupported project feature
10  safety guard blocked operation
```

Default config path:

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

Config should be the only place for user-specific paths such as AutoShop executable path, compiler/tool paths, preferred project directory, connection profiles, UI labels, and wait timings.

## Command Groups

### 1. `config`

Purpose: create, view, and validate persistent settings.

```powershell
autoshop-agent.exe config init [--config path] [--project dir] [--autoshop-exe path] [--force]
autoshop-agent.exe config show [--config path] [--format json]
autoshop-agent.exe config validate [--config path]
autoshop-agent.exe config set <key> <value> [--config path]
autoshop-agent.exe config get <key> [--config path]
autoshop-agent.exe config profile add <name> --transport ethernet --ip <ip> [--port <port>]
autoshop-agent.exe config profile add <name> --transport usb
autoshop-agent.exe config profile list
autoshop-agent.exe config profile remove <name>
```

Design notes:

- `autoShopExePath` is optional for file-only commands.
- `ui.projectTreeTitle`, `ui.programmingNode`, and `ui.programBlockNode` stay configurable because AutoShop UI labels are localized.

### 2. `project`

Purpose: inspect and manage project-level structure.

```powershell
autoshop-agent.exe project info --project <dir|hcp|hcpp|updown>
autoshop-agent.exe project tree --project <dir> [--format json]
autoshop-agent.exe project check --project <dir> [--strict]
autoshop-agent.exe project backup --project <dir> --out <zip|dir>
autoshop-agent.exe project archive pack --project <dir> --out <hclib>
autoshop-agent.exe project archive unpack --in <hclib> --out <dir>
autoshop-agent.exe project compare --left <project> --right <project|target> [--detail]
```

Implementation status:

- `project info/tree/check` can start from local file parsing.
- `archive pack/unpack` and full compare may require AutoShop automation or `.hclib/.hcp/.hcpp` reverse engineering.

### 3. `pou`

Purpose: list and manage program organization units.

```powershell
autoshop-agent.exe pou list --project <dir> [--format json]
autoshop-agent.exe pou show --project <dir> --name MAIN
autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt
autoshop-agent.exe pou export-all --project <dir> --out <dir>
autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--backup] [--refresh]
autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW
autoshop-agent.exe pou add --project <dir> --name SBR_002 --type main|subprogram|interrupt|fb|fc --language litest|ld|sfc
autoshop-agent.exe pou remove --project <dir> --name SBR_002
```

Implementation status:

- `list/show/export/export-all/import` are current or near-current scope for existing `*.ST` containers.
- `add/remove/rename` are future-only because they likely require updating `.hcp` and project tables.

### 4. `st`

Purpose: LiteST-specific source operations.

```powershell
autoshop-agent.exe st format --in source.st --out source.formatted.st
autoshop-agent.exe st lint --in source.st [--target h5u|easy] [--firmware <version>]
autoshop-agent.exe st parse --in source.st --format json
autoshop-agent.exe st symbols --in source.st --format json
autoshop-agent.exe st refs --in source.st --symbol <name>
autoshop-agent.exe st scaffold mb-master --out example.st
autoshop-agent.exe st scaffold fb-call --name <FB> --out call.st
autoshop-agent.exe st instruction search <keyword>
autoshop-agent.exe st instruction show <name> [--format json]
```

Design notes:

- `lint` should validate obvious LiteST syntax, comments, statement terminators, control-flow pairing, FB/FC call form, device/register spelling, and instruction availability by target/firmware.
- `instruction search/show` should be generated from the instruction manual data, not hand-maintained free text.

### 5. `var`

Purpose: variable and device/register table management.

```powershell
autoshop-agent.exe var list --project <dir> [--scope global|local|system]
autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json
autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace]
autoshop-agent.exe var bind --project <dir> --name <var> --device D100
autoshop-agent.exe var validate --project <dir>
autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info]
```

Implementation status:

- Requires reverse engineering variable table files such as `.gvt`, `.svt`, `.gdt`, `.gdtx`, and related metadata.

### 6. `build`

Purpose: compile and package project artifacts.

```powershell
autoshop-agent.exe build check --project <dir>
autoshop-agent.exe build compile --project <dir> [--clean] [--format json]
autoshop-agent.exe build diagnostics --project <dir> [--format json]
autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
```

Implementation status:

- `compile` may be possible through installed compiler binaries after entry points are identified.
- `down/updown` are documented AutoShop features but may require AutoShop automation if no public CLI entry point exists.

### 7. `target`

Purpose: connect to PLC, inspect state, and control lifecycle.

```powershell
autoshop-agent.exe target scan [--transport ethernet|usb]
autoshop-agent.exe target connect --profile <name>
autoshop-agent.exe target info --profile <name>
autoshop-agent.exe target login --profile <name> --password <value>
autoshop-agent.exe target logout --profile <name>
autoshop-agent.exe target run --profile <name> [--yes]
autoshop-agent.exe target stop --profile <name> [--yes]
autoshop-agent.exe target mode --profile <name>
autoshop-agent.exe target download --profile <name> --project <dir> [--yes]
autoshop-agent.exe target upload --profile <name> --out <dir|updown>
autoshop-agent.exe target download-file --profile <name> --in <down|updown> [--yes]
autoshop-agent.exe target upload-updown --profile <name> --out <file.updown>
```

Safety rules:

- `run`, `stop`, `download`, and password operations require `--yes` for noninteractive use.
- Download commands should state whether the PLC is currently RUN or STOP before proceeding.

Implementation status:

- Requires communication protocol discovery or driving AutoShop/HMI documented flows.

### 8. `online`

Purpose: online modification and online comparison workflows.

```powershell
autoshop-agent.exe online enter --profile <name> --project <dir>
autoshop-agent.exe online status --profile <name>
autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes]
autoshop-agent.exe online commit --profile <name> [--yes]
autoshop-agent.exe online exit --profile <name>
autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]
```

Design notes:

- The manual lists online-modification restrictions. The CLI must validate that a patch does not add/delete/rename program files or alter unsupported properties before attempting online commit.

### 9. `monitor`

Purpose: watch variables/devices and export runtime observations.

```powershell
autoshop-agent.exe monitor read --profile <name> --device D100
autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes]
autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json
autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes]
autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json
autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes]
```

Implementation status:

- Requires target communication support or AutoShop memory-management automation.

### 10. `trace`

Purpose: configure, start, stop, and export Trace captures.

```powershell
autoshop-agent.exe trace list --project <dir>
autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST
autoshop-agent.exe trace start --profile <name> --name <trace>
autoshop-agent.exe trace stop --profile <name> --name <trace>
autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv
autoshop-agent.exe trace remove --project <dir> --name <trace>
```

Design notes:

- The manual documents Trace as a time-stamped variable history feature and documents export after stopping collection. The CLI should preserve this state machine.

### 11. `diagnose`

Purpose: collect errors and diagnostic evidence.

```powershell
autoshop-agent.exe diagnose target --profile <name> [--format json]
autoshop-agent.exe diagnose logs --profile <name> --out logs.json
autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system]
autoshop-agent.exe diagnose project --project <dir> [--format json]
autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip
```

Design notes:

- `error-code` should combine program error codes, Modbus communication error codes, EtherCAT fault codes, motion faults, and system diagnostics as separate domains.

### 12. `comm`

Purpose: inspect and edit communication configuration.

```powershell
autoshop-agent.exe comm serial show --project <dir>
autoshop-agent.exe comm serial set --project <dir> --port COM1 --baud 9600 --data-bits 8 --parity none --stop-bits 1
autoshop-agent.exe comm modbus-rtu master add --project <dir> --name <name> --port COM1 --addr <id>
autoshop-agent.exe comm modbus-tcp master add --project <dir> --name <name> --ip <ip> --port 502
autoshop-agent.exe comm ethernet show --project <dir>
autoshop-agent.exe comm ethernet set-ip --profile <name> --ip <ip> --mask <mask> --gateway <gateway> [--yes]
autoshop-agent.exe comm can show --project <dir>
autoshop-agent.exe comm canopen import-eds --project <dir> --in <file.eds>
autoshop-agent.exe comm ethercat import-xml --project <dir> --in <file.xml>
autoshop-agent.exe comm ethercat scan --profile <name>
autoshop-agent.exe comm ethercat status --profile <name>
```

Implementation status:

- Most commands require project table/config parsing or AutoShop automation.

### 13. `motion`

Purpose: support documented motion, high-speed counter, interpolation, cam, and gear workflows.

```powershell
autoshop-agent.exe motion axis list --project <dir>
autoshop-agent.exe motion axis add --project <dir> --name Axis1 --type ethercat|pulse
autoshop-agent.exe motion axis set --project <dir> --name Axis1 --param <key=value>
autoshop-agent.exe motion axis status --profile <name> --name Axis1
autoshop-agent.exe motion group list --project <dir>
autoshop-agent.exe motion group add --project <dir> --name Group1 --axes Axis1,Axis2
autoshop-agent.exe motion cam import --project <dir> --name Cam1 --in cam.csv
autoshop-agent.exe motion cam export --project <dir> --name Cam1 --out cam.csv
autoshop-agent.exe motion hsc list --project <dir>
autoshop-agent.exe motion hsc add --project <dir> --name Counter1 --mode linear|rotary
```

Design notes:

- These commands map to manual sections for motion axis setup, PLCopen state, axis parameters, high-speed counters, interpolation, bus encoder axes, and electronic cam/gear.
- Implementation should start read-only until project file formats are known.

### 14. `ui`

Purpose: AutoShop window automation.

```powershell
autoshop-agent.exe ui windows
autoshop-agent.exe ui refresh --program MAIN
autoshop-agent.exe ui close --program MAIN
autoshop-agent.exe ui open --program MAIN
autoshop-agent.exe ui focus --program MAIN
autoshop-agent.exe ui tree --format json
```

Compatibility aliases:

```powershell
autoshop-agent.exe windows
autoshop-agent.exe refresh --program MAIN
```

Design notes:

- UI commands are allowed to depend on a running AutoShop process but not on a fixed installation path.
- The CLI must not auto-answer dirty-buffer save prompts.

### 15. `doc`

Purpose: expose local and generated reference information.

```powershell
autoshop-agent.exe doc sources
autoshop-agent.exe doc outline --manual programming|instruction|user|autoshop
autoshop-agent.exe doc search <keyword> [--manual programming|instruction|all]
autoshop-agent.exe doc command-set --out AutoShopCliCommandSetDesign.md
```

Design notes:

- This is not a replacement for official manuals.
- Use it for quick lookup, command planning, and error-code mapping.

## Backward-Compatible Current Commands

Keep these current commands working:

```powershell
autoshop-agent.exe list --project <dir>
autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
autoshop-agent.exe windows
autoshop-agent.exe refresh --program MAIN
```

Add aliases to the new hierarchy:

```text
list       -> pou list
export     -> pou export or pou export-all
import     -> pou import
windows    -> ui windows
refresh    -> ui refresh
```

## Suggested Implementation Phases

### Phase 1: File-Level Development

- `project info/tree/check`
- `pou list/show/export/export-all/import`
- `ui windows/refresh`
- `st parse/lint` with a conservative parser
- `doc sources/outline/search`

### Phase 2: Project Metadata

- `var list/export/import/validate`
- `comm serial/ethernet show`
- `project compare` for local file-level differences
- `pou add/remove/rename` only after `.hcp` and related tables are understood

### Phase 3: Build And Packaging

- `build compile`
- `build diagnostics`
- `build down`
- `build updown`

This phase depends on identifying stable AutoShop compiler/package entry points or robust UI automation.

### Phase 4: PLC Target Operations

- `target scan/info/login/logout/run/stop`
- `target download/upload`
- `monitor read/write/watch`
- `trace start/stop/export`
- `diagnose target/logs/error-code`

This phase depends on discovering communication protocols or safely driving AutoShop.

### Phase 5: Advanced Configuration

- `comm modbus/canopen/ethercat`
- `motion axis/group/cam/hsc`
- `online enter/patch/commit/exit`

Start read-only and validation-only before allowing writes.

## Non-Goals For The First Full CLI

- No silent PLC RUN/STOP or download operations.
- No automatic save/overwrite response in AutoShop modal dialogs.
- No project file creation/deletion until all affected project tables are understood.
- No password storage in plaintext by default.
- No claims that generated code is safe for machinery without user review and proper physical safety circuits.

## Acceptance Criteria For Future Implementation

Every implemented command must have:

- `--help` output.
- Human text output and JSON output where automation is expected.
- Dry-run behavior for write or target-affecting operations.
- Structured errors and stable exit codes.
- A runtime log option.
- A smoke test on a copied project or mock target.
- Documentation update in this reference file or a successor command reference.
