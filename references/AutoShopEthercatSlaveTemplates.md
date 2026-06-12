# AutoShop EtherCAT Slave Templates

This development knowledge file is the source for the packaged skill reference:

- `references/AutoShopEthercatSlaveTemplates.md`

Update this file first, then sync it downstream. Use this reference when adding or changing EtherCAT slaves, especially IS620N servo drives, through the workspace JSON mirror.

## Files

- EtherCAT slaves: `配置/EtherCAT/_node.config.json`
- Motion axes: `配置/运动控制轴/_node.config.json`

Always edit the exported workspace mirror, not AutoShop project files directly. Use explicit UTF-8 when reading these JSON files in PowerShell:

```powershell
$j = Get-Content -LiteralPath '<workspace-dir>\配置\EtherCAT\_node.config.json' -Raw -Encoding UTF8 | ConvertFrom-Json
```

## Required Workflow

1. If the target project is open, run `ui windows --format json`, then `ui close-project --project <project> --state <state.json> --format json`.
2. Run `workspace export --project <project> --out <workspace> --force --format json`.
3. Edit the JSON mirror.
4. Run `workspace apply --dry-run --format json`; confirm expected changes only.
5. Run `workspace apply --format json`; confirm `verified=true`.
6. Run `ui restore-project --state <state.json> --format json`.
7. Compile with AutoShop UI: `ui compile-all --lines all --tail 0 --format json`.
8. For real hardware, download/run/monitor only with explicit UI commands.

## Find a Template

Prefer a verified template over a generated-from-catalog instance.

```powershell
$p = '<workspace-dir>\配置\EtherCAT\_node.config.json'
$j = Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json
$j.ethercat.slaves | Select-Object key,toolboxName,catalogKey
$j.ethercat.catalog.devices |
  Where-Object { $_.toolboxName -like '*IS620N*' -or $_.name -like '*IS620N*' } |
  Select-Object key,name,toolboxName,productCode,revisionNo,templateAvailable,libraryTemplateVerified,libraryTemplateHasSegment
```

Current verified IS620N catalog entry from the local project/device library:

```json
{
  "key": "ecat:IS620N-Ecat_v2_6_8:IS620N:c0108:10001",
  "name": "IS620N",
  "toolboxName": "IS620N_ECAT_v2.6.8",
  "productCode": "c0108",
  "revisionNo": "65537",
  "templateAvailable": true,
  "libraryTemplateVerified": "file-level-capture",
  "libraryTemplateHasSegment": true
}
```

If `templateAvailable` is false, do not add that device unless the user accepts `allowGeneratedFromCatalog=true` and the risk that AutoShop may not show the slave as a normal visible device.

## Same-Model Clone Template

Use this when the project already contains the same slave model. Append to `ethercat.slaves` and point `templateKey` to an existing `slaves[].key`.

```json
{
  "templateKey": "slave_000_IS620N",
  "parameters": {
    "deviceName": "IS620N_2",
    "slaveTreeIndex": 1,
    "positionIndex": 1,
    "stationIndex": 1,
    "physicalAddress": 1002
  }
}
```

Notes:

- Keep the new object small. Let the CLI clone records, segment data, PDOs, CoE objects, and system variables from the template.
- Do not copy and hand-edit `segmentBase64` unless preserving a hand-created AutoShop object is the only viable path.
- After apply, re-export and verify the new `slaves[].key`, visible name, and generated records before binding motion axes.

## Device-Library Template

Use this when the model exists in `ethercat.catalog.devices` and has `templateAvailable=true`. Append to `ethercat.slaves` with the AutoShop toolbox leaf name.

```json
{
  "toolboxName": "IS620N_ECAT_v2.6.8",
  "parameters": {
    "deviceName": "IS620N",
    "positionIndex": 0,
    "stationIndex": 0,
    "physicalAddress": 1001
  }
}
```

Notes:

- `toolboxName`, not display text or user shorthand, is the primary field for adding a device-library slave.
- `catalogKey` is diagnostic; do not use it as the first-choice add field.
- When adding the first IS620N, apply and re-export before editing `motionAxis.axes`; the axis `outputDevice` must match AutoShop's generated visible device name.

## IS620N Axis Binding Template

Edit `配置/运动控制轴/_node.config.json` after the IS620N slave exists and has been re-exported. Modify an existing axis or append an axis at the end of `motionAxis.axes`.

Minimal verified parameter set for `Axis_0` bound to IS620N:

```json
{
  "name": "Axis_0",
  "parameters": {
    "axisName": "Axis_0",
    "axisNumber": 0,
    "virtualAxisMode": false,
    "autoMappingEnabled": true,
    "outputDevice": "IS620N",
    "encoderMode": "增量模式",
    "axisMotionMode": "旋转模式",
    "reverseDirection": false,
    "distancePerRevolutionNoGear": 1,
    "distancePerRevolutionWithGear": 1,
    "pulsesPerRevolution": 1048576,
    "softwareLimitEnabled": false,
    "ignoreLimitAfterErrorStop": true,
    "maxSpeed": 3000,
    "maxAcceleration": 30000,
    "jogMaxSpeed": 300
  }
}
```

Notes:

- Use `outputDevice` equal to the AutoShop slave display name, for example `IS620N`.
- Use `autoMappingEnabled=true` for the common servo-drive case unless the user explicitly needs manual PDO mapping.
- `axisMotionMode=旋转模式` is appropriate when 1.0 engineering unit is intended to mean one revolution after unit conversion is set to 1 revolution.
- If the physical direction is reversed, prefer `reverseDirection=true` in the axis unit conversion page rather than changing every motion command sign.

## Verification Checklist

After applying EtherCAT or axis templates:

```powershell
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --format json
.\scripts\autoshop-agent.exe ui restore-project --state <state-json> --format json
.\scripts\autoshop-agent.exe ui compile-all --lines all --tail 0 --format json
```

Then verify AutoShop UI:

```powershell
.\scripts\autoshop-agent.exe ui open-path --path "配置/EtherCAT" --format json
.\scripts\autoshop-agent.exe ui screenshot --title EtherCat --out <tmp-dir>\ethercat_after_template.png --format json
.\scripts\autoshop-agent.exe ui open-path --path "配置/运动控制轴/Axis_0" --format json
.\scripts\autoshop-agent.exe ui screenshot --title Axis_0 --out <tmp-dir>\axis_after_template.png --format json
```

For connected hardware, confirm online state with `ui monitor` and screenshots. Offline compile success only proves the configuration is structurally valid; it does not prove the physical slave is present, powered, wired, or in OP state.
