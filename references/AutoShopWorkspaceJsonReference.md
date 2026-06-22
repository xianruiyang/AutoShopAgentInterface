# AutoShop Workspace JSON Reference

Use this reference when editing the workspace exported by `workspace export`.

## Table of Contents

- General rules
- POU and program blocks
- Variables and structures
- Interrupts
- Configuration nodes
- H5U modules
- EtherCAT
- Motion axes and axis groups
- EtherNet/IP and H5U devices
- CAN(CANLink)
- Fallback fields

## General Rules

Edit the exported workspace, then apply it back with `workspace apply`.

Prefer semantic JSON fields over raw hex/base64. Use raw fields only when no semantic field exists and when preserving unknown binary content is required.

Do not hand-edit AutoShop private binary files in place when the CLI exports a semantic JSON surface for the same item.

## POU and Program Blocks

POU JSON files live under the programming folders:

- `编程/程序块/*.pou.json`
- `编程/功能块(FB)/*.pou.json`
- `编程/函数(FC)/*.pou.json`

Program blocks and interrupt programs are `.ST` containers and use `FileType=80`.

Function blocks are `.FB` containers and use `FileType=81` / `ProgType=7`.

Functions are `.FC` containers and use `FileType=82` / `ProgType=8`.

When a new POU JSON file is added, `workspace apply` must maintain:

- the POU container file
- `folder.txt`
- `.hcp`
- `.hcpp`

`pou add` and `pou remove` are compatibility/diagnostic entries. Use workspace JSON as the normal edit path.

## Variables and Structures

Global variables:

```text
全局变量/变量表/变量表.gvt.json
```

Edit the `variables` array. Do not hand-edit `.gvt` when the JSON representation exists.

Supported variable features include:

- explicit `dataType`
- `STRING<...>`
- arrays
- custom structures
- system structure/union types beginning with `_s` or `_u`
- `powerRetain`
- `networkAccess`

Structure definitions:

```text
全局变量/结构体/*.stru.json
```

Edit `definition.members`. Adding a new `*.stru.json` creates a new structure definition.

Function block instances:

```text
全局变量/功能块实例/功能块实例.fbi.json
```

Edit `instances`.

## Interrupts

Interrupt trigger metadata:

```text
编程/程序块/_interrupt-triggers.json
```

Edit `interrupts[].trigger`.

Supported trigger types:

- external input: `X0..X3` with `falling`, `rising`, or `both`
- timed interrupt
- comparison interrupt `compareIndex=1..16`
- raw fallback with `rawCode`

AutoShop 4.10 uses `.hcp` interrupt `<POUID>` while `<Timer>` stays `0`. Unknown encodings must use `rawCode`; do not guess new fields.

## Configuration Nodes

Configuration nodes export as:

```text
配置/<node-name>/_node.config.json
```

Known semantic fields include:

- input filter: `inputFilter.parameters`
- module configuration: `moduleConfig.modules`
- electronic cam: `electronicCam.cams`
- motion axes: `motionAxis.axes`
- axis groups: `axisGroup.groups`
- EtherCAT: `ethercat.parameters`, `ethercat.slaves`
- EtherNet/IP: `ethernetIP`
- CAN(CANLink): `canLink.portConfig`, `canLink.programConfig`
- CANopen: dynamic `配置/CAN(CANopen)/_node.config.json`, diagnostic `canOpen.catalog` from AutoShop `sys/eds` plus optional `deviceLibraryPath/canopen` templates, writable sampled `canOpen.dataConfig.network` fields, existing `objectTable[]` values, current-project or external-template `slaves[]` add/delete with optional `templateNodeId` / `toolboxName` / `catalogKey`, `slaves[].general.producerHeartbeatTimeMs`, existing `rxPdos[]`/`txPdos[]` summary values, existing `slaves[].sdoInit[]` value fields, existing `ioMappings[].startRegister` D start registers parsed from `canopen.data`, plus raw `canopen.data` / `canopen.up` preservation when those files exist

## H5U Modules

Module configuration is under:

```text
配置/模块配置/_node.config.json
```

Edit `moduleConfig.modules`.

Each module slot may contain:

- `slot`
- `model`
- `identity`
- `moduleTypeCode`
- `instance`
- `ioSignals`
- `moduleParameters`
- `parametersHex`

Known GL10 modules may be created from `model` using sampled default parameters. `ioSignals` may change existing X/Y addresses, but the signal count must match the module parameter address fields.

`moduleParameters` maps repeated UI pages into arrays. For example, 4DA/4AD use four repeated channel pages, and 8TC/4TC/4PT use channel-group arrays.

Keep unknown private bytes in `parametersHex`.

## EtherCAT

EtherCAT node:

```text
配置/EtherCAT/_node.config.json
```

Main station fields live in `ethercat.parameters`. Confirmed editable fields include:

- `cycleTimeUs`
- `syncOffsetPercent`
- `autoRestartSlave`
- `aliasEnabled`

Slave entries live in `ethercat.slaves`.

Use these paths in order:

1. `slaves[].parameters`
2. `slaves[].disconnectOutput`
3. `slaves[].pages`
4. `slaves[].records[]` for unnamed model-specific fields

Add a same-model slave by appending a new slave object with `templateKey` pointing to an existing `slaves[].key`.

Add a toolbox/catalog device with `toolboxName` from AutoShop's toolbox leaf name. Do not guess this value from a product model; read it from exported `ethercat.catalog.devices` or an existing slave/template reference.

Use `allowGeneratedFromCatalog=true` only when a basic ESI-derived instance is acceptable. A generated catalog-only instance may not preserve all AutoShop private UI pages.

For IS620N or motion-axis binding, read `references/AutoShopEthercatSlaveTemplates.md`.

## Motion Axes and Axis Groups

Motion axes:

```text
配置/运动控制轴/_node.config.json
```

Edit `motionAxis.axes[].parameters`.

Supported operations:

- modify existing axis parameters
- append a default axis at the end
- create axes from an empty axis array

Unsupported operations:

- delete an axis
- insert in the middle

Important fields:

- `virtualAxisMode`
- `autoMappingEnabled`
- `outputDevice`
- `encoderMode`
- `axisMotionMode`
- `softwareLimitEnabled`
- `reverseDirection`
- `gearDeviceEnabled`
- `pulsesPerRevolution`
- homing fields such as `homeOriginSignal`, `homeZSignal`, `homePositiveLimit`, `homeNegativeLimit`

`outputDevice` may be `未分配`, an EtherCAT slave name, `deviceVersion`, `productCode`, slave `key`, or `index:N`. The CLI generates CiA402 PDO binding records from the selected EtherCAT slave.

Axis groups:

```text
配置/轴组设置/_node.config.json
```

Edit `axisGroup.groups[].parameters`. Append-only creation is supported; delete/middle insertion is rejected.

## EtherNet/IP and H5U Devices

EtherNet/IP node:

```text
配置/EtherNet/IP/_node.config.json
```

Top-level field:

```text
ethernetIP
```

Key sections:

- `devices`
- `devices[].general`
- `devices[].info`
- `devices[].status`
- `devices[].pages`
- `devices[].connections`
- `devices[].tagConnections`
- `devices[].ioMappings`
- `producerTags`
- `serverMessageTags`
- `adapter.connections[].outputDatasets`
- `adapter.connections[].inputDatasets`

For H5U structured devices, use semantic fields first:

- ordinary connections: `devices[].connections`
- tag connections: `devices[].tagConnections`
- I/O mapping variable names: `devices[].ioMappings[].variableName`

Connection details may include RPI, timeout multiplier, trigger type, transport type, connection type, priority, fixed/variable size, and transfer format.

`devices[].pages` exposes lower-level page fields. If a field is `editable=true`, change `value`. If it has an `editPath`, prefer the referenced semantic field instead.

Add EtherNet/IP toolbox devices with `toolboxName`. If `deviceLibraryPath` points to a semantic template library, apply may clone full EIP_Card/Easy/H5U records and private records. Without a template, generated devices require explicit `allowGeneratedFromCatalog=true`.

`Generic_EtherNet_IP_device` is private-only and should be treated as a preserved private template unless a sampled template exists.

## CAN(CANLink)

CAN(CANLink) node:

```text
配置/CAN(CANLink)/_node.config.json
```

Edit:

```text
canLink.portConfig.parameters.protocol
canLink.portConfig.parameters.stationNumber
canLink.portConfig.parameters.baudRateKbps
```

`stationSource` and `baudRateSource` are read-only in the current sampled H5U data.

AutoShop 4.10 H5U CANLink3.0 samples can store station configuration in `CANLink.prg` without `CANLink.data`. When that file is present, export adds `canLink.programConfig`:

```text
canLink.programConfig.network.masterStationNumber
canLink.programConfig.network.baudRateKbps
canLink.programConfig.network.heartbeatMs
canLink.programConfig.slaves[].stationNumber
canLink.programConfig.slaves[].statusRegister
canLink.programConfig.slaves[].startStopElement
canLink.programConfig.sendConfigurations[]
canLink.programConfig.receiveConfigurations[]
canLink.programConfig.syncMappings[]
canLink.programConfig.syncView[]
```

`programConfig` is parsed from KLC records in `CANLink.prg`; the tail checksum is `CRC16/MODBUS` stored big-endian. Unknown records stay in `programConfig.records[].dataHex`.

Current semantic write support is deliberately narrow: edit the sampled `slaves[]` station table, existing `slaves[].stationNumber`, `slaves[].statusRegister`, `slaves[].startStopElement`, sampled `sendConfigurations[]`, sampled existing `syncMappings[]` rows, and sampled `receiveConfigurations[]` values in the exported object. When an existing slave station number changes, sampled send/sync/receive station references are migrated from the old station to the new station. Omitting `slaves` leaves the current station list unchanged. When `slaves` is present, apply rebuilds CANLink KLC record 1 and record 6 from the target station list and may add/delete station rows that are not referenced by send/receive configuration. A new station row must provide `stationNumber`, `typeCode` or `type`, `statusRegister`, and `startStopElement`. An empty `slaves` array is rejected because the AutoShop clear-config sample reports no configuration data instead of a downloadable host-only station table. Deleting a station still referenced by `sendConfigurations[]` or `receiveConfigurations[]` is also rejected unless those arrays are updated in the same JSON. `sendConfigurations[]` supports add/delete/edit for sampled `time-ms`, `event-ms`, and `event-m` trigger modes. `syncMappings[]` is a writable alias for existing AutoShop sync-write rows backed by `sendConfigurations[]`; keep the exported row identity and change trigger/register/count fields there when you want the sync-write-oriented view. If both `sendConfigurations[]` and `syncMappings[]` are edited in one JSON, they must be semantically identical. `receiveConfigurations[]` supports add/delete/edit for sampled receive allow-list entries. If a send or receive array appears in JSON, apply rebuilds the corresponding KLC record from the array; an empty array deletes that sampled configuration class, while an omitted array leaves it unchanged. `syncView[]` is a read-only derived AutoShop view. Add/delete sync rows and CANopen EDS/PDO/SDO/I/O Mapping add/delete still require real AutoShop samples before they can become semantic JSON.

When `canLink.portConfig.parameters.protocol` is `CANOpen`, export also adds:

```text
canOpen.catalog
canOpen.dataConfig
```

`canOpen.catalog` is parsed from AutoShop `sys/eds` EDS files and, when configured, merged with sampled CANopen templates from `deviceLibraryPath/canopen/index.json`. It exposes device identity, supported baud rates, RxPDO/TxPDO object summaries, the object dictionary, `templateAvailable`, current-project `templateNodeIds`, and external template diagnostics such as `libraryTemplateId`, `libraryPath`, `libraryVerified`, and `librarySha256`. It is a diagnostic/catalog surface and template-discovery surface, not a pure EDS generation surface. Do not edit `canOpen.slaves`, PDO, SDO, or I/O mapping fields directly; current apply rejects direct `canOpen` slave edits and treats `canOpen.portConfig` as a read-only mirror. Edit CAN root protocol, station number, and baud rate through `canLink.portConfig.parameters`; an unchanged exported `canOpen.portConfig` mirror does not block those canonical edits.

For CANopen projects, the CAN node mirrors AutoShop UI path as `配置/CAN(CANopen)/_node.config.json`. AutoShop 4.10 stores saved CANopen detail data in `canopen.data`, with `NOC` header, `E3/E4` records, and a big-endian CRC16/MODBUS tail. When `canopen.data` exists, export adds `canOpen.dataConfig` with header/checksum, node IDs, master record0 network fields, matched EDS device identity, object table, derived slave General summary, derived RxPDO/TxPDO mapping summaries, service-data-object page aliases, calibrated I/O mapping register assignments, and raw records. Existing `canOpen.dataConfig.network.producerHeartbeatTimeMs`, `sdoTimeoutMs`, `slaveReceiveMappingStartRegister`, `slaveTransmitMappingStartRegister`, and `nodeStateMonitorStartRegister` may be edited; apply rewrites sampled record0 offsets and rebuilds CRC. `recordMasterNodeId`, `recordBaudRateCode`, `record0TailHex`, `sourceRecordId`, and `sourceRecordHex` are read-only; canonical station number and baud rate still use `canLink.portConfig.parameters`. Existing `canOpen.dataConfig.objectTable[]` values may be edited through `valueUnsigned`, `dataHex`, or `rawValueHex`; apply preserves object identity and length, rebuilds CRC, and syncs known mirrors such as `0x1017:0` heartbeat producer time into record 3. `canOpen.dataConfig.slaves[]` may add/delete slaves when the current project already contains a template slave record set or `deviceLibraryPath/canopen` provides a sampled AutoShop `canopen.data` template. A new slave can provide `nodeId` and optional `templateNodeId`, or use `toolboxName` / `catalogKey` to match an exported catalog device; in a single-template project, omitting `templateNodeId` uses the existing slave as the template. Apply clones and rewrites sampled record 2/3/4/5 node blocks, objectTable, PDO/I/O mapping records, and CRC. Pure EDS/catalog generation without a current-project or external real template remains rejected. External CANopen library entries must reference a sampled template JSON through `canopen/index.json`; the template may carry full `canopen.data` bytes using `instanceTemplate.canopenDataHex`, `canopenDataBase64`, or raw files. `canOpen.dataConfig.slaves[].general.producerHeartbeatTimeMs` is a verified alias for the same `0x1017:0` producer heartbeat value; other General fields are exported as read-only until their AutoShop pages are sampled. Existing `canOpen.dataConfig.slaves[].rxPdos[]` and `txPdos[]` may edit `enabled`, `canId`, `cobId`, `transmissionType`, `eventTimeMs`, and existing `mappedObjects[]` values; `canId` matches AutoShop PDO property-page COB-ID display and changes only the low 29-bit CAN-ID while preserving raw `cobId` control bits. Apply synchronizes those summaries back into the matching objectTable entries and rejects PDO or mapped-object count changes. `canOpen.dataConfig.slaves[].sdoInit[]` is the AutoShop `服务数据对象` page alias for existing objectTable rows; existing rows allow changing `valueUnsigned`, `dataHex`, or `rawValueHex`, then apply synchronizes back into objectTable and rebuilds CRC. SDO row add/delete and download-column marker edits are rejected. `canOpen.dataConfig.ioMappings[]` is parsed from record 5 and calibrated against AutoShop's `I/O映射` page; existing entries allow changing only the D start address through `startRegister`, `variableRange`, or `endRegister`, then apply rewrites record 5 and rebuilds CRC. Direction, PDO `number`, `mappingIndex`, byte/word/bit length, source offsets, and add/delete remain immutable; `slaves[].ioMappings[]` is an alias for the same records and conflicts are rejected if both aliases set different D starts. CANopen numeric/boolean edit fields use JSON field presence for intent: omitting `valueUnsigned`, `enabled`, `canId`, `transmissionType`, or `eventTimeMs` means no edit, while explicitly writing `0` or `false` applies that value. `dataHex` and `rawValueHex` remain the preferred exact-byte edit fields when value-size ambiguity matters. `canopen.data` / `canopen.up` still remain in the CAN node `files[]` array for byte-preserving apply. Direct semantic writes for top-level `canOpen.slaves`, General fields other than producer heartbeat, pure EDS/no-template slave generation, and PDO/SDO/I/O Mapping add-delete/property pages remain disabled until those AutoShop setting pages are sampled and verified.

## Fallback Fields

When a semantic field does not exist, use:

- `files[].contentHex`
- `files[].contentBase64`
- page fields with `editable=true`

Keep raw edits narrow and validate with `workspace apply --dry-run`, readback SHA, and AutoShop UI when visibility matters.

