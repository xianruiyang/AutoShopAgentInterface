## 2026-06-22 CANopen right-side device-library sync 0.8.153

- `scripts/autoshop-agent.exe`：同步开发版 `0.8.153`。
- `device-library/canopen/index.json` 与 `device-library/canopen/templates/**/default.json`：新增 15 个 AutoShop 右侧 Inovance CANopen 真实模板，发布包和已安装 skill 均可自动发现。
- `references/AutoShopCliCommands.md`：同步 `ui dev-tree-read`、`ui dev-tree-click`、`ui dev-command` 开发采样命令及 CANopen 模板新增说明。
- `references/DeviceTemplateCollectionStatus.md`：更新 CANopen 正式采集数为 15，记录 JSON 新增、删除和 heartbeat 参数编辑回读验证。
- 验证：release/installed `quick_validate.py --expect-version 0.8.153 --json` 通过；两侧 workspace export 均发现 15 个 CANopen `libraryTemplatePath`。

## 2026-06-22 CANopen 右侧设备模板库入口 0.8.152

- `scripts/autoshop-agent.exe`：同步开发版 `0.8.152`，支持 CANopen 当前工程模板或 `deviceLibraryPath/canopen` 真实模板新增/删除从站，并保持缺真实模板时拒绝纯 EDS 生成。
- `README.md`、`SKILL.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md`：同步 CANopen `toolboxName` / `catalogKey` 模板新增、`templateAvailable` 和模板库边界说明。
- `references/DeviceTemplateCollectionStatus.md`：新增发布参考，记录 EtherCAT、EtherNet/IP、CANopen 设备模板采集状态；明确 CANopen 右侧 14 个设备尚未正式采集入库。
- `quick_validate.py`：新增 `references/DeviceTemplateCollectionStatus.md` 必需文件检查；release/installed `--expect-version 0.8.152 --json` 均通过且无隐私命中。

## 2026-06-22 CANopen template slave add/delete sync 0.8.151

- `scripts/autoshop-agent.exe` is synced to `0.8.151`; exe SHA256 is `F9187C59C4468CE57C262800E18FD9C9AD524B64A85B2AA228A502588F925DFA`.
- `README.md`, `references/AutoShopCliCommands.md`, and `references/AutoShopWorkspaceJsonReference.md` now document CANopen `canOpen.dataConfig.slaves[]` template-based add/delete with optional `templateNodeId`, plus the no-template EDS/catalog generation boundary.
- CANopen existing device parameter editing remains documented for `slaves[].general.producerHeartbeatTimeMs`, objectTable, PDO summaries, SDO Init alias values, and I/O Mapping D start registers.
- Release and installed validation command: `quick_validate.py <root> --expect-version 0.8.151 --json`.

## 2026-06-22 CANLink station add/delete sync 0.8.150

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.150`，exe SHA256 为 `D5392185755C8C568FD8C41267DCBA6CF0881C6C4FD6DE60F622802A387E417A`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANLink `slaves[]` station table add/delete 语义：可新增/删除未被 send/receive 引用的从站行，重建 record 1/6；空从站表和删除仍被引用的站点会拒绝。
- `references/AutoShopCliCommands.md` 已补 `ui dev-button-click` 开发采样命令；release/installed `quick_validate.py <root> --expect-version 0.8.150 --json` 均通过，无隐私命中。
## 2026-06-22 CANLink syncMappings alias sync 0.8.149

- 发布包和已安装 skill 的 `scripts/autoshop-agent.exe` 已同步到 `0.8.149`。
- `README.md`、`references/AutoShopCliCommands.md`、`references/AutoShopWorkspaceJsonReference.md` 已同步 CANLink `syncMappings[]` 语义：它是 AutoShop “同步写”页既有行的可写 alias，底层回写 `sendConfigurations[]`，`syncView[]` 保持只读。
- release/installed `quick_validate.py --expect-version 0.8.149 --json` 均通过；exe SHA256 为 `77DF55F9ED172A7174304F8C656493A9A8DCE9C3354A75909C0A2D81382BF401`。

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
- `scripts/autoshop-agent.exe`: Packaged CLI binary, currently `v0.8.151`.
- `quick_validate.py`: Package validation helper for required files, CLI version, and path/privacy scans.
- `references/`: Detailed command, format, UI refresh, testing, EtherCAT slave template references, motion-axis `outputDevice` JSON binding, CANLink `programConfig` editing including existing slave station-number migration, sampled send/receive add-edit-delete, writable existing `syncMappings[]` sync-write alias, CANLink `slaves[]` station add/delete for unreferenced rows with clear/referenced-delete guards, dynamic CANopen workspace path, raw `canopen.data` / `canopen.up` preservation, CANopen EDS catalog export, writable sampled CANopen `dataConfig.network` master record0 fields, writable CANopen `dataConfig.slaves[]` template add/delete, existing CANopen `dataConfig.objectTable`/`slaves[].general.producerHeartbeatTimeMs`/PDO summary values including PDO `canId`, writable existing CANopen `slaves[].sdoInit` service-data-object alias values, writable existing CANopen `dataConfig.ioMappings[].startRegister` values, and `ui dev-clicks --direct` / `ui dev-button-click` development sampling support.
- `references/AutoShopEthercatSlaveTemplates.md`: Reusable JSON template reference for EtherCAT `templateKey` clone, `toolboxName` device-library add, current verified `IS620N_ECAT_v2.6.8`, and `Axis_0` binding parameters.
- `references/AutoShopSkillPathPolicy.md`: Path/privacy policy for packaged skill resources and placeholders.
- `references/AutoShopH5uQuickReference.md`: H5U AutoShop quick reference for communication, modules, EtherCAT, EtherNet/IP, and CAN(CANLink).
- `references/AutoShopAgentWorkflow.md`: Split operational workflow reference for workspace export/apply, AutoShop UI actions, real hardware boundaries, and validation.
- `references/AutoShopWorkspaceJsonReference.md`: Split workspace JSON reference for POU, variables, interrupts, H5U modules, EtherCAT, motion axes, EtherNet/IP, CAN(CANLink) station add/delete, CANopen catalog, writable sampled CANopen master record0 fields, writable existing CANopen objectTable/General producer heartbeat/PDO summary `canId`/SDO Init alias/I/O mapping D start register values, and CANopen template slave add/delete and remaining no-template/PDO/SDO/I/O Mapping add-delete boundaries.
- `references/AutoShopH5uEasyProgrammingApplicationManual.md`: Bundled Markdown conversion of the AutoShop H5U/Easy programming and application guide.
- `references/AutoShopH5uPlcInstructionManualCn.md`: Bundled Markdown conversion of the H5U PLC instruction manual.
- `references/AutoShopH5uSeriesUserManualCn.md`: Bundled H5U series user manual Markdown.
- `references/AutoShopH5uSeriesBrochureEn.md`: Bundled H5U brochure/spec overview Markdown.
