## 2026-06-21 CANopen PDO canId sync 0.8.148

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.148`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen PDO `canId` 语义：`canId` 是 AutoShop PDO 属性页显示的低 29 位 CAN-ID，写回保留 raw `cobId` 高位控制位，`cobId` 仍作为完整通信对象值入口。
- `references/AutoShopCliCommands.md` 已补 `ui dev-clicks --direct` 开发采样参数；release/installed `quick_validate.py --expect-version 0.8.148 --json` 均通过，README 包装说明无开发路径词。

## 2026-06-21 CANopen master record0 sync 0.8.147

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.147`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen `dataConfig.network` 主站 record0 已采样字段写回能力：心跳生产时间、SDO 超时、从站接收/发送自动映射 D 起始和站点监控 D 起始；record 站号/波特率与 raw/tail 字段保持只读。
- `quick_validate.py --expect-version 0.8.147 --json` 对发布包和已安装 skill 均通过，隐私扫描无本机路径命中。
## 2026-06-21 offscreen screenshot minimized fallback sync 0.8.146

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.146`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopUiRefresh.md` 已同步最小化窗口离屏截图说明：先写离屏 normal placement，若窗口仍是 iconic，再在离屏状态下用 `SW_RESTORE` 兜底并恢复原最小化状态。
- `quick_validate.py --expect-version 0.8.146 --json` 已对发布包和已安装 skill 通过，隐私扫描无本机路径命中。

## 2026-06-21 CANopen value field presence sync 0.8.145

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.145`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen 数值/布尔字段存在性语义：字段省略表示 no-op，显式 `0` 或 `false` 才写入。
- `quick_validate.py --expect-version 0.8.145 --json` 对发布包和已安装 skill 均通过，隐私扫描无本机路径命中。

## 2026-06-21 CANopen SDO Init/service-data-object alias sync 0.8.144

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.144`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANopen `slaves[].sdoInit[]` 服务数据对象页 alias 规则：既有行可写 `valueUnsigned`、`dataHex` 或 `rawValueHex`，新增/删除行和下载列标记仍拒绝。
- `quick_validate.py --expect-version 0.8.144 --json` 对发布包和已安装 skill 均通过，隐私扫描无本机路径命中。

## 2026-06-21 CANopen SDO Init empty boundary and offscreen screenshot sync 0.8.143

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.143`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md`、`references/AutoShopUiRefresh.md`、`references/AutoShopAgentWorkflow.md`、`references/AutoShopCliTesting.md` 已同步 CANopen `slaves[].sdoInit` 空表导出/非空拒绝边界，以及最小化离屏截图不闪屏、不空白的后台窗口保护说明。
- 新增 `quick_validate.py`，用于检查发布包/已安装 skill 的必需文件、CLI 版本和本机路径泄漏。

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
- `README.md` Skill maintenance section: records that this package is synced from a development source and must not be edited as the source of truth.
- `LICENSE`: MIT license for the distributable package.
- `.editorconfig`: Text-file encoding policy for this distributable package when opened directly; declares UTF-8 for Markdown, JSON, PowerShell, ST, and related text files.
- `.vscode/settings.json`: VSCode workspace setting forcing `files.encoding=utf8` and disabling encoding auto-guessing when this package folder is opened directly.
- `SKILL.md`: Codex skill instructions and operational rules for the bundled CLI.
- `scripts/autoshop-agent.exe`: Packaged CLI binary, currently `v0.8.148`.
- `quick_validate.py`: Package validation helper for required files, CLI version, and path/privacy scans.
- `references/`: Detailed command, format, UI refresh, testing, EtherCAT slave template references, motion-axis `outputDevice` JSON binding, CANLink `programConfig` editing including existing slave station-number migration and sampled send/receive add-edit-delete, explicit CANLink `slaves` omission/add-delete boundary, dynamic CANopen workspace path, raw `canopen.data` / `canopen.up` preservation, CANopen EDS catalog export, writable sampled CANopen `dataConfig.network` master record0 fields, writable existing CANopen `dataConfig.objectTable`/`slaves[].general.producerHeartbeatTimeMs`/PDO summary values including PDO `canId`, writable existing CANopen `slaves[].sdoInit` service-data-object alias values, writable existing CANopen `dataConfig.ioMappings[].startRegister` values, and `ui dev-clicks --direct` development sampling support.
- `references/AutoShopEthercatSlaveTemplates.md`: Reusable JSON template reference for EtherCAT `templateKey` clone, `toolboxName` device-library add, current verified `IS620N_ECAT_v2.6.8`, and `Axis_0` binding parameters.
- `references/AutoShopSkillPathPolicy.md`: Path/privacy policy for packaged skill resources and placeholders.
- `references/AutoShopH5uQuickReference.md`: H5U AutoShop quick reference for communication, modules, EtherCAT, EtherNet/IP, and CAN(CANLink).
- `references/AutoShopAgentWorkflow.md`: Split operational workflow reference for workspace export/apply, AutoShop UI actions, real hardware boundaries, and validation.
- `references/AutoShopWorkspaceJsonReference.md`: Split workspace JSON reference for POU, variables, interrupts, H5U modules, EtherCAT, motion axes, EtherNet/IP, CAN(CANLink), CANopen catalog, writable sampled CANopen master record0 fields, writable existing CANopen objectTable/General producer heartbeat/PDO summary `canId`/SDO Init alias/I/O mapping D start register values, and remaining CANopen add-delete boundaries.
- `references/AutoShopH5uEasyProgrammingApplicationManual.md`: Bundled Markdown conversion of the AutoShop H5U/Easy programming and application guide.
- `references/AutoShopH5uPlcInstructionManualCn.md`: Bundled Markdown conversion of the H5U PLC instruction manual.
- `references/AutoShopH5uSeriesUserManualCn.md`: Bundled H5U series user manual Markdown.
- `references/AutoShopH5uSeriesBrochureEn.md`: Bundled H5U brochure/spec overview Markdown.

