---
name: autoshop-agent-interface
description: "当 Codex 需要通过随包 CLI 操作汇川 Inovance AutoShop Lite ST / H5U 工程时使用：导出/应用 workspace JSON，编辑 POU、变量、模块配置、EtherCAT、EtherNet/IP、运动轴、CAN(CANLink)，控制 AutoShop UI 编译/下载/上载/监控，或查询随包 H5U/AutoShop Markdown 手册。真实 PLC 操作必须显式使用 hardware/UI 命令；默认 target/online/monitor/comm/motion/build 后端是 simulator。"
---

# AutoShop Agent Interface

Use the bundled CLI first:

```text
scripts/autoshop-agent.exe
```

Do not reimplement AutoShop binary ST parsing, workspace apply logic, HCP/HCPP synchronization, or Win32 UI automation unless the task is to maintain this CLI.

## Required Workflow

For normal project edits, use the full workspace flow:

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui close-project --project <project-dir> --state <state-json> --format json
.\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
.\scripts\autoshop-agent.exe ui restore-project --state <state-json> --format json
```

Skip close/restore only when AutoShop is not opening the target project. If AutoShop is opening another project, do not close it. Use `--allow-open-project` only when the user explicitly accepts that exception.

After `workspace apply`, verify `verified=true`, `readBackSha256`, and expected `.hcp/.hcpp` sync entries in the JSON output. Compile with AutoShop when UI/project validity matters.

## Hardware Boundary

Treat `target`, `online`, `monitor`, `comm`, `motion`, and `build compile/down/updown` as simulator/local unless the command explicitly uses `--backend hardware` or an AutoShop `ui ...` command.

Real PLC communication setup:

```powershell
.\scripts\autoshop-agent.exe target transports --backend hardware --format json
.\scripts\autoshop-agent.exe target connect --backend hardware --transport <transport> --ip <plc-ip> --format json
```

Real AutoShop buttons:

```powershell
.\scripts\autoshop-agent.exe ui compile-all --tail 50 --format json
.\scripts\autoshop-agent.exe ui download --yes --timeout-ms 60000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui upload --timeout-ms 8000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui monitor --timeout-ms 4000 --format json
```

`ui download --yes` does not run the PLC after download unless `--run-after` is explicitly passed. `ui upload` does not automatically confirm a flow that may overwrite the current AutoShop session.

## Read References By Task

Always load the relevant reference before editing:

- Normal operation, UI commands, hardware boundaries, and validation: `references/AutoShopAgentWorkflow.md`
- Workspace JSON layout and editable fields: `references/AutoShopWorkspaceJsonReference.md`
- Complete CLI command catalog: `references/AutoShopCliCommands.md`
- CLI maintenance/testing: `references/AutoShopCliTesting.md`
- AutoShop ST container/LiteST format: `references/AutoShopLiteStFormat.md`
- AutoShop UI refresh and screenshot details: `references/AutoShopUiRefresh.md`
- Skill packaging path/privacy rules: `references/AutoShopSkillPathPolicy.md`
- EtherCAT/IS620N slave templates and motion-axis binding: `references/AutoShopEthercatSlaveTemplates.md`
- H5U quick configuration guide: `references/AutoShopH5uQuickReference.md`
- Full AutoShop H5U/Easy programming manual: `references/AutoShopH5uEasyProgrammingApplicationManual.md`
- Full H5U PLC instruction manual: `references/AutoShopH5uPlcInstructionManualCn.md`
- H5U user manual: `references/AutoShopH5uSeriesUserManualCn.md`
- H5U brochure/spec overview: `references/AutoShopH5uSeriesBrochureEn.md`

For large H5U manuals, search before reading large spans. Useful terms include `EtherCAT`, `CANLink`, `EtherNet/IP`, `高速`, `中断`, `高速计数`, `运动控制`, `模块配置`, `GL10`, `H5U`, and `AutoShop`.

## Package Rules

All package-internal resources must be referenced relative to the skill root, for example `scripts/autoshop-agent.exe` and `references/AutoShopCliCommands.md`.

Project paths, workspace paths, temporary directories, hardware config paths, PLC IPs, and device-library paths are caller-provided values. Use placeholders such as `<project-dir>`, `<workspace-dir>`, `<state-json>`, `<tmp-dir>`, `<archive-dir>`, `<plc-ip>`, and `<device-library-dir>` in examples.

When maintaining this skill, update the development source first, then sync the distributable package and installed skill. Do not treat the installed skill as the source of truth.
