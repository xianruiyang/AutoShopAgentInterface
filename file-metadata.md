## 2026-06-21 CANopen I/O Mapping start sync 0.8.142

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.142`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步最小化离屏截图修复和 CANopen `dataConfig.ioMappings[].startRegister` / `slaves[].ioMappings[].startRegister` 写回能力；I/O Mapping 新增删除、方向、PDO 编号、映射索引和长度仍不可变。

## 2026-06-21 CANopen slave General sync 0.8.141

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.141`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen `dataConfig.slaves[].general.producerHeartbeatTimeMs` 写回能力；其它 General 字段仍只读。

## 2026-06-21 CANopen port mirror/no-op sync 0.8.140

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.140`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen port mirror/no-op apply 边界：canonical `canLink.portConfig.parameters` 写回不被旧 `canOpen.portConfig` 镜像阻止；未编辑 objectTable 不自动改 `canopen.data`。

## 2026-06-21 CANopen I/O mapping sync 0.8.139

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.140`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen `dataConfig.ioMappings[]` 只读导出和写回拒绝边界。

## 2026-06-21 UI screenshot fallback sync 0.8.138

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.138`。
- `README.md`、`references/AutoShopUiRefresh.md`、`references/AutoShopAgentWorkflow.md`、`references/AutoShopCliCommands.md` 已同步 `contentRatio`、低内容重试和 `PrintWindowClientFallback` 说明。
# File Metadata

- `README.md`: Public repository overview, supported AutoShop version, workflow boundaries, and usage notes.
- `README.md` Development Source section: records that this package is synced from a separate development source and must not be edited as the source of truth.
- `LICENSE`: MIT license for the distributable package.
- `.editorconfig`: Text-file encoding policy for this distributable package when opened directly; declares UTF-8 for Markdown, JSON, PowerShell, ST, and related text files.
- `.vscode/settings.json`: VSCode workspace setting forcing `files.encoding=utf8` and disabling encoding auto-guessing when this package folder is opened directly.
- `SKILL.md`: Codex skill instructions and operational rules for the bundled CLI.
- `scripts/autoshop-agent.exe`: Packaged CLI binary, currently `v0.8.142`.
- `references/`: Detailed command, format, UI refresh, testing, EtherCAT slave template references, motion-axis `outputDevice` JSON binding, CANLink `programConfig` editing including existing slave station-number migration and sampled send/receive add-edit-delete, explicit CANLink `slaves` omission/add-delete boundary, dynamic CANopen workspace path, raw `canopen.data` / `canopen.up` preservation, CANopen EDS catalog export, writable existing CANopen `dataConfig.objectTable`/`slaves[].general.producerHeartbeatTimeMs`/PDO summary values, and writable existing CANopen `dataConfig.ioMappings[].startRegister` values.
- `references/AutoShopEthercatSlaveTemplates.md`: Reusable JSON template reference for EtherCAT `templateKey` clone, `toolboxName` device-library add, current verified `IS620N_ECAT_v2.6.8`, and `Axis_0` binding parameters.
- `references/AutoShopSkillPathPolicy.md`: Path/privacy policy for packaged skill resources and placeholders.
- `references/AutoShopH5uQuickReference.md`: H5U AutoShop quick reference for communication, modules, EtherCAT, EtherNet/IP, and CAN(CANLink).
- `references/AutoShopAgentWorkflow.md`: Split operational workflow reference for workspace export/apply, AutoShop UI actions, real hardware boundaries, and validation.
- `references/AutoShopWorkspaceJsonReference.md`: Split workspace JSON reference for POU, variables, interrupts, H5U modules, EtherCAT, motion axes, EtherNet/IP, CAN(CANLink), CANopen catalog, writable existing CANopen objectTable/General producer heartbeat/PDO summary values, and writable existing CANopen I/O mapping D start register values.
- `references/AutoShopH5uEasyProgrammingApplicationManual.md`: Bundled Markdown conversion of the AutoShop H5U/Easy programming and application guide.
- `references/AutoShopH5uPlcInstructionManualCn.md`: Bundled Markdown conversion of the H5U PLC instruction manual.
- `references/AutoShopH5uSeriesUserManualCn.md`: Bundled H5U series user manual Markdown.
- `references/AutoShopH5uSeriesBrochureEn.md`: Bundled H5U brochure/spec overview Markdown.

