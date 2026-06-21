# AutoShop Agent Interface

AutoShop Agent Interface packages a Codex skill and the `autoshop-agent.exe` CLI for operating Inovance AutoShop Lite/H5U projects through a JSON workspace workflow.

- Supported AutoShop baseline: AutoShop V4.10.0.0.
- Packaged CLI version: `0.8.137`.
- License: MIT.

## Contents

```text
scripts/autoshop-agent.exe
SKILL.md
references/
```

Use paths inside this package relative to the package root. Caller-specific values such as project directories, workspace export directories, PLC IPs, temporary folders, and device-library folders should be supplied as `<project-dir>`, `<workspace-dir>`, `<state-json>`, `<plc-ip>`, and `<device-library-dir>`.

## Standard Workflow

For normal project edits, export the workspace JSON, edit it, dry-run apply, then apply for real:

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui close-project --project <project-dir> --state <state-json> --format json
.\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
.\scripts\autoshop-agent.exe ui restore-project --state <state-json> --format json
```

After apply, check `verified=true`, `readBackSha256`, and any `.hcp/.hcpp` synchronization entries in the JSON output. Use AutoShop UI commands such as `ui compile-all` when UI/project validity matters.

## Current Scope

The workspace JSON flow supports editing ST/POU content, variables, structures, FB instances, interrupt triggers, H5U module configuration, EtherCAT, EtherNet/IP, motion axes, axis groups, electronic cams, and CAN configuration.

For CAN(CANLink), `canLink.portConfig` edits the CAN root parameters. AutoShop 4.10 H5U `CANLink.prg` is exported as `canLink.programConfig`; current semantic writes support existing IS/SV slave `stationNumber`, `statusRegister`, `startStopElement`, sampled send configuration add/edit/delete, and sampled receive allow-list add/edit/delete. Changing an existing slave station number migrates sampled send/receive references from the old station to the new station and recalculates the `CANLink.prg` CRC. Omitting `slaves` leaves the station list unchanged; keeping the exported array length allows existing station edits; an empty `slaves` array or any length change is rejected as unsupported station add/delete. Empty `sendConfigurations` or `receiveConfigurations` arrays intentionally delete that class; omitted arrays leave it unchanged.

For CANopen, the CAN node is exported as `配置/CAN(CANopen)/_node.config.json` when the root protocol is CANOpen. The CLI exports `canOpen.catalog` from AutoShop EDS files and `canOpen.dataConfig` from existing `canopen.data` files, including NOC header/checksum, node IDs, EDS identity matches, object table entries, PDO summaries, and raw records. Existing `canOpen.dataConfig.objectTable[]` values can be edited through `valueUnsigned`, `dataHex`, or `rawValueHex`; known mirrors such as `0x1017:0` heartbeat producer time are synchronized for AutoShop UI readback. Raw `canopen.data` / `canopen.up` files are still preserved byte-for-byte when present. CANopen master/slave add-delete/PDO/SDO/I/O mapping semantic writes still require AutoShop setting-page samples and are rejected when unsupported.

## Hardware Boundary

`target`, `online`, `monitor`, `comm`, `motion`, and legacy `build` commands are simulator/local unless the command explicitly uses `--backend hardware` or an AutoShop `ui ...` command. Real PLC download/upload/monitor operations should use the UI commands documented in `references/AutoShopAgentWorkflow.md` and `references/AutoShopCliCommands.md`.

## References

- `references/AutoShopAgentWorkflow.md`: operational workflow and validation checklist.
- `references/AutoShopCliCommands.md`: full command catalog and JSON edit surfaces.
- `references/AutoShopWorkspaceJsonReference.md`: workspace JSON layout and editable fields.
- `references/AutoShopH5uQuickReference.md` and bundled H5U manuals: H5U hardware and AutoShop references.
- `references/AutoShopSkillPathPolicy.md`: package path and privacy policy.

