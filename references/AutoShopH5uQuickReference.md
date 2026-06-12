# AutoShop H5U Quick Reference

Use this reference when a task involves H5U PLC work in AutoShop, especially communication setup, local extension modules, EtherCAT motion, EtherNet/IP, CAN/CANLink, or offline/online validation.

The packaged CLI and current validated templates are based on H5U/Easy AutoShop behavior. Confirm the exact H5U model, firmware, and AutoShop target type when hardware limits matter.

## AutoShop Scope

- AutoShop is the programming/configuration environment for H5U/Easy-family small PLC projects.
- H5U projects commonly use LiteST, ladder, function blocks, functions, system variables, module configuration, EtherCAT, EtherNet/IP, CAN(CANLink), COM, and motion-axis nodes.
- Normal project edits through this skill must still use:

```powershell
.\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
```

## Communication

- Use `target transports --backend hardware` to inspect AutoShop's visible communication types.
- Use `target connect --backend hardware --transport <transport> --ip <plc-ip>` to set and test the PLC communication path through AutoShop's official communication dialog.
- Do not hard-code a bench IP in a reusable skill workflow. Use `<plc-ip>` or a named user-provided profile.
- H5U Ethernet communication commonly uses Modbus-TCP capabilities; confirm the actual protocol and port in the user's project before assuming a runtime data path.

## Local Extension Modules

- H5U can use local extension modules; AutoShop module configuration controls the final X/Y/D mapping.
- In workspace JSON, local module configuration is represented under `配置/模块配置/_node.config.json` as `moduleConfig.modules`.
- For digital GL10 modules, use `model`, `ioSignals`, and verified module parameters rather than editing binary payloads directly.
- Address mapping must be verified by re-export after `workspace apply`, and by opening the corresponding AutoShop module configuration page when UI confirmation matters.

## EtherCAT Motion

- H5U/Easy-family projects can use EtherCAT motion axes; AutoShop motion control follows PLCopen-style function blocks.
- EtherCAT master settings are under `配置/EtherCAT/_node.config.json`.
- Motion axes are under `配置/运动控制轴/_node.config.json`.
- When binding a servo drive such as IS620N, read `references/AutoShopEthercatSlaveTemplates.md` before editing JSON.
- Offline compile only proves project structure. Connected hardware must be checked with AutoShop monitor/screenshots and expected EtherCAT state, for example OP state where applicable.

## EtherNet/IP

- H5U can appear as an EtherNet/IP device/template in AutoShop projects.
- Workspace JSON represents this under `配置/EtherNet/IP/_node.config.json` as `ethernetIP`.
- Prefer structured fields:
  - `devices[].general`
  - `devices[].connections`
  - `devices[].tagConnections`
  - `devices[].serviceMessageTags`
  - `devices[].ioMappings`
- Use `devices[].pages` only as a field index and fallback for editable raw fields. If a field has an `editPath`, use the higher-level semantic path.

## CAN / CANLink

- H5U projects may use CAN(CANLink) configuration under `配置/CAN(CANLink)/_node.config.json`.
- Prefer `canLink.portConfig.parameters.protocol`, `stationNumber`, and `baudRateKbps`.
- Do not generate missing right-click CAN subconfiguration files unless their binary format has been verified for the exact target.

## Verification Checklist

- Use `workspace apply --dry-run --format json` before writing.
- After apply, check `verified=true` and readback hashes.
- Re-export and confirm the semantic JSON still matches the intended values.
- Compile through AutoShop UI with `ui compile-all`.
- For live PLC work, explicitly run communication test, download/run/monitor only when the user asks for hardware actions.

## Source Basis

This reference is condensed from converted H5U/Easy AutoShop manuals and project validation notes, plus public Inovance H5U product documentation. It is intentionally a short operational reference, not a full manual dump.
