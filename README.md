# AutoShop Agent CLI

`AutoShopAgentInterface` 是 Codex skill 发布包，CLI 可执行文件作为 skill 资源放在：

```text
scripts\autoshop-agent.exe
```

包内使用说明和参考资料放在 `references/`；源码、开发记录和样例配置不随发布包分发。

## Skill 维护顺序

本目录是 `autoshop-agent-interface` skill 的发布包。修改 skill 说明、reference、CLI 能力或同步规则时，先在开发源头更新源码、知识文档、README 和运行记录；再同步到发布包 `<package-dir>`；最后同步到 Codex 已安装目录 `<installed-skill-dir>`。不要把已安装 skill 或发布包当成源头直接反向开发。

当前 EtherCAT/IS620N 从站模板的源文件是：

```text
knowledge\AutoShopEthercatSlaveTemplates.md
```

发布包路径与隐私策略的源文件是：

```text
knowledge\AutoShopSkillPathPolicy.md
```

H5U AutoShop 快速资料的源文件是：

```text
knowledge\AutoShopH5uQuickReference.md
```

瘦身后的 skill 入口源文件是：

```text
knowledge\AutoShopSkillEntry.md
```

操作流程和 workspace JSON 细节拆分为：

```text
knowledge\AutoShopAgentWorkflow.md
knowledge\AutoShopWorkspaceJsonReference.md
```

随包 H5U Markdown 手册源文件是：

```text
knowledge\AutoShopH5uEasyProgrammingApplicationManual.md
knowledge\AutoShopH5uPlcInstructionManualCn.md
knowledge\AutoShopH5uSeriesUserManualCn.md
knowledge\AutoShopH5uSeriesBrochureEn.md
```

同步目标是：

```text
references\AutoShopEthercatSlaveTemplates.md
references\AutoShopSkillPathPolicy.md
references\AutoShopH5uQuickReference.md
references\AutoShopAgentWorkflow.md
references\AutoShopWorkspaceJsonReference.md
references\AutoShopH5uEasyProgrammingApplicationManual.md
references\AutoShopH5uPlcInstructionManualCn.md
references\AutoShopH5uSeriesUserManualCn.md
references\AutoShopH5uSeriesBrochureEn.md
```

在 `<dev-workspace-root>` 当前工作区，项目映射固定使用：

```text
<workspace-dir>
```

不要在 `<dev-workspace-root>` 根目录生成 `001-*` workspace/readback/smoke 目录；临时验证目录统一放到 `<archive-dir>` 下。不要把 workspace、smoke 工程或临时导出放进 `AutoShopAgentInterface` skill 文件夹。

## 构建

在 `src\autoshop-agent` 下执行：

```powershell
go build -trimpath -ldflags "-s -w" -o <package-dir>\scripts\autoshop-agent.exe .
```

当前实现使用 Go + Win32 API，不依赖 PowerShell 脚本作为运行时。

## 当前能力

离线可用：

- `config init/show/validate/get/set/profile`
- `workspace export/apply`
- `project info/tree/check/backup/compare`
- `project archive pack/unpack`
- `pou list/show/export/export-all/import`
- `pou` 底层兼容/诊断入口；工程内容新增、删除、修改的主流程必须走 `workspace export/apply` 的 JSON/文本镜像
- `st lint/parse/symbols/refs/format/scaffold/instruction`
- `var list/export/system list/validate`
- `workspace` 语义/节点 JSON：全局变量表 `variables`、自定义结构体 `definition.members`、POU `*.pou.json`、中断触发 `_interrupt-triggers.json`、功能块实例 `instances`、输入滤波 `inputFilter.parameters`、模块配置 `moduleConfig.modules`、电子凸轮 `electronicCam.cams`、CAN(CANLink) `canLink.portConfig/programConfig`、CANopen `canOpen.catalog` 与可写既有 `canOpen.dataConfig.network/objectTable/slaves[].general.producerHeartbeatTimeMs/rxPdos/txPdos/sdoInit/ioMappings[].startRegister`、EtherCAT `ethercat.parameters/slaves`、EtherNet/IP `ethernetIP.devices/producerTags/serverMessageTags/adapter`（含从站 `general/info/status/pages`、H5U `connections/tagConnections` 连接详情）、运动控制轴 `motionAxis.axes`、轴组设置 `axisGroup.groups`、配置树 `_node.config.json`
- `build check/diagnostics`
- `diagnose project/error-code`
- `ui windows/refresh/refresh-path/close-project/restore-project/refresh-project/close/open/focus/tree/screenshot/compile/compile-all/run/stop/download/upload/monitor/output`
- `doc sources/outline/search/command-set`
- `comm serial/ethernet/can show`
- `trace list/add/remove/export` 本地侧车定义
- `target transports/scan/connect --backend hardware`：通过 AutoShop `工具 -> 通讯设置` 读取可用通讯类型、做 PLC 搜索、通讯类型选择、设备 IP 写入/读回和连接测试；`--transport` 支持 `ethernet`、`usb`、`index:N` 或 AutoShop 下拉框可见文字

默认 simulator 后端已实现：

- `target`
- `online`
- `monitor`
- `comm`
- `motion`
- `build compile/down/updown`

除 `target transports/scan/connect --backend hardware` 外，这些命令会执行、保存模拟状态或产出模拟文件；不会 RUN/STOP 真实 PLC、下载真实设备或写真实设备。真实 RUN/STOP/下载/上载/监控按钮通过 `ui run`、`ui stop`、`ui download --yes`、`ui upload`、`ui monitor` 走 AutoShop UI 动作；`ui download --yes` 默认不在下载完成后运行 PLC，只有显式 `--run-after` 才会同意下载后的运行提示；`ui upload` 只触发并采集上载弹窗/输出，不自动确认可能改写当前 AutoShop 会话的上载流程。

## 测试

默认离线测试：

```powershell
cd src\autoshop-agent
go test ./...
```

真机调试用例已经写入 `cli_test.go`，默认跳过。只有显式设置环境变量后才会运行：

```powershell
$env:AUTOSHOP_AGENT_RUN_HARDWARE_TESTS = "1"
$env:AUTOSHOP_AGENT_HARDWARE_CONFIG = "<hardware-config.json>"
$env:AUTOSHOP_AGENT_HARDWARE_PROFILE = "bench"
go test ./... -run Hardware -v
```

当前默认命令由 simulator 后端通过；真机用例用于验证 `target transports/scan/connect --backend hardware` 的 AutoShop 通讯设置流程，真实 PLC 操作仍按命令文档边界处理。

## 配置

默认配置路径：

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

也可以通过环境变量或命令参数指定：

```powershell
$env:AUTOSHOP_AGENT_CONFIG = "<config.json>"
<package-dir>\scripts\autoshop-agent.exe project check --config <config.json>
```

生成配置：

```powershell
<package-dir>\scripts\autoshop-agent.exe config init --project <project-dir> --force
```

如果需要从外部模板库新增 EtherNet/IP 设备，配置里的 `deviceLibraryPath` 指向模板库根目录，例如 `<package-dir>Work\device-library`。也可以用环境变量 `AUTOSHOP_AGENT_DEVICE_LIBRARY` 临时覆盖。

查看配置：

```powershell
<package-dir>\scripts\autoshop-agent.exe config show --format json
```

`autoShopExePath` 当前不参与导出、写回、刷新逻辑；刷新会查找正在运行的 `AutoShop.exe`，所以不会受安装目录不同影响。该字段保留给后续自动启动 AutoShop。

## 常用命令

检查工程：

```powershell
<package-dir>\scripts\autoshop-agent.exe project check --project <project-dir> --format json
```

列出工程内 ST 容器：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou list --project <project-dir>
```

导出单个程序到 txt：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou export --project <project-dir> --name MAIN --out <tmp-dir>\MAIN.st.txt
```

导出全部 ST 程序：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou export-all --project <project-dir> --out <tmp-dir>\st-export
```

写回前 dry-run：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou import --project <project-dir> --name MAIN --in <tmp-dir>\MAIN.st.txt --dry-run --format json
```

从 txt 写回：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou import --project <project-dir> --name MAIN --in <tmp-dir>\MAIN.st.txt
```

如果 AutoShop 正打开同一工程，默认会拒绝写回。确认接受风险时显式添加：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou import --project <project-dir> --name MAIN --in <tmp-dir>\MAIN.st.txt --allow-open-project
```

写回后刷新 AutoShop 内同名窗口：

```powershell
<package-dir>\scripts\autoshop-agent.exe pou import --project <project-dir> --name MAIN --in <tmp-dir>\MAIN.st.txt --allow-open-project --refresh
```

按工程树导出整个工程工作区：

```powershell
<package-dir>\scripts\autoshop-agent.exe workspace export --project <project-dir> --out <workspace-dir> --force
```

既有中断程序触发设置会导出为 `编程/程序块/_interrupt-triggers.json`；优先编辑 `interrupts[].trigger`，支持外部中断 `X0..X3 + falling|rising|both`、定时中断通道、比较中断 `compareIndex=1..16`，未知或歧义编码可用 `type=raw` 写 `rawCode`。应用时会写回 AutoShop 4.10 `.hcp` 中断 `<POUID>` 并保持 `<Timer>0</Timer>`，同时同步 `.hcpp`。

CAN(CANLink) 根口参数仍通过 `canLink.portConfig` 编辑；AutoShop 4.10 H5U 样本中的 `CANLink.prg` 会导出为 `canLink.programConfig`，当前已支持修改既有 IS/SV 从站的 `stationNumber`、`statusRegister`/`startStopElement`，并支持已采样 `time-ms`/`event-ms`/`event-m` 发送配置和接收许可表的新增、删除、修改、CRC 重算；既有从站改号时会同步迁移已采样发送/接收配置里的旧站号引用。`slaves` 省略表示不改从站列表，空数组或数量变化表示新增/删除尝试并会被拒绝。`syncView` 是只读派生视图；从站新增/删除和完整同步触发语义还需要继续按真实样本反解。切到 CANopen 时，配置节点会按 UI 树导出为 `配置/CAN(CANopen)/_node.config.json`，并附加 `canOpen.catalog` 和 `canOpen.dataConfig`：`catalog` 从 AutoShop `sys/eds` 解析 EDS identity、支持波特率、PDO 摘要和对象字典；`dataConfig` 从已有 `canopen.data` 的 `NOC` header、`E3/E4` records 和 CRC16/MODBUS 中回读节点、主站 record0、匹配 EDS、对象表、从站 General 摘要、RxPDO/TxPDO 摘要、服务数据对象页别名、I/O 映射 D 寄存器分配和 raw records。`canopen.data` / `canopen.up` 仍作为 CAN 节点原始 `files[]` 成员保真导出和回写；当前已验证可修改 `canOpen.dataConfig.network.producerHeartbeatTimeMs`、`sdoTimeoutMs`、`slaveReceiveMappingStartRegister`、`slaveTransmitMappingStartRegister`、`nodeStateMonitorStartRegister` 这些主站 record0 已采样字段并重算 CRC；也可修改既有 `canOpen.dataConfig.objectTable[]` 的 `valueUnsigned`/`dataHex`/`rawValueHex`，或通过 `canOpen.dataConfig.slaves[].general.producerHeartbeatTimeMs` 修改同一个 `0x1017:0` 心跳生产时间，写回时会同步 AutoShop record 3 运行镜像和启用标志；既有 `rxPdos[]`/`txPdos[]` 摘要可写 `enabled`、`canId`、`cobId`、`transmissionType`、`eventTimeMs` 和现有 `mappedObjects[]` 值，其中 `canId` 对应 AutoShop PDO 属性页显示的低 29 位 CAN-ID，写回会保留 raw `cobId` 高位控制位；`slaves[].sdoInit[]` 是服务数据对象页既有行对 objectTable 的别名，可写既有行的 `valueUnsigned`/`dataHex`/`rawValueHex` 并重算 CRC，新增/删除行和下载列标记仍拒绝；既有 `ioMappings[]` 的 `startRegister`/`variableRange`/`endRegister` 可调整 D 起始地址，写回会更新 record 5 并重算 CRC，方向、PDO 编号、映射索引和长度仍不可变。CANopen 数值/布尔字段按 JSON 字段存在性判断编辑：删除 `valueUnsigned`、`enabled`、`canId`、`transmissionType`、`eventTimeMs` 表示不改，显式写 `0` 或 `false` 才会应用。CANopen 主站 record0 未命名字节、从站新增/删除、General 其它字段与 PDO/SDO/I/O Mapping 新增删除仍未开放语义写回，直接编辑 `canOpen` 从站或 `canOpen.portConfig` 会被拒绝，根口参数请改 `canLink.portConfig.parameters`；导出 JSON 中未改动的 `canOpen.portConfig` 旧镜像不会阻止 canonical 写回。

全局变量表会导出为 `全局变量/变量表/变量表.gvt.json`，其中 `variables` 是可直接编辑的变量数组；结构体定义会导出为 `全局变量/结构体/*.stru.json`，编辑 `definition.members`，新增 `*.stru.json` 可创建结构体；新增程序块/中断/FB/FC 时在 `编程/...` 对应目录新增 `*.pou.json`，apply 会同步 `folder.txt`、`.hcp` 和 `.hcpp`；功能块实例会导出为 `全局变量/功能块实例/功能块实例.fbi.json`，编辑 `instances`；配置树节点会导出为 `配置/<节点名>/_node.config.json`。输入滤波参数编辑 `配置/输入滤波/_node.config.json` 里的 `inputFilter.parameters`；模块配置编辑 `配置/模块配置/_node.config.json` 里的 `moduleConfig.modules`，每个槽位包含 `slot`、`model`、`identity`、`moduleTypeCode`、`instance`、`ioSignals`、`moduleParameters` 和保底回写用 `parametersHex`，可用已知 `model` 加空 `parametersHex` 创建样本支持的 GL10 模块，`ioSignals` 可修改已有 X/Y 地址但数量必须与该模块私有参数中的地址字段一致。`moduleParameters` 把同一类 UI 页面映射成可重复结构：4DA/4AD 是同一通道页重复 4 次，8TC/4TC/4PT 的 `通道X-通道Y` 是同一通道 schema 的分组数组；已确认字段可直接编辑，基本配置页中尚未拆清的位域保留 `rawCode`，未知私有字节继续由 `parametersHex` 保真兜底。运动控制轴编辑 `配置/运动控制轴/_node.config.json` 里的 `motionAxis.axes`：常用字段在 `parameters`，底层 UI/编译记录在 `uiRecords`/`compilerRecords`，当前支持修改既有轴参数、在数组末尾追加默认轴，空轴工程会导出空数组并可从 0 开始追加，并同步写回 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`，删除或中间插入轴会拒绝；基本设置里的 `virtualAxisMode` 对应“虚轴模式”，`autoMappingEnabled` 对应“自动映射”，`outputDevice` 对应“输出设备”，可写 `未分配` 清除绑定，也可写 EtherCAT 从站名、`deviceVersion`、`productCode`、从站 `key` 或 `index:N`，由 CLI 根据该从站已选 CiA402 PDO 生成运动轴绑定 UI/编译记录；模式/参数设置里的 `encoderMode` 使用 `增量模式`/`绝对模式`，并会同步 AutoShop 实际保存的 `encoderModeEffective` 与 `encoderModeLinkedFlag` 编译记录、可见 UI 记录和 `ignoreLimitAfterErrorStop` 联动值；`axisMotionMode` 使用 `线性模式`/`旋转模式`，`softwareLimitEnabled` 为软件限位使能布尔值；单位换算里的 `reverseDirection` 对应“反向”复选框，写回时会同步 `0x80000118` 可见复选框位和 `0x80000117` 联动标志，`gearDeviceEnabled` 对应“使用变速装置”，`pulsesPerRevolution` 使用十进制数，AutoShop 的 `16#1000000` 对应 `16777216`；为匹配 AutoShop 手动保存行为，`axisMotionMode` 或 `encoderMode` 改动时会同步 `ignoreLimitAfterErrorStop`：增量模式或旋转模式为 `true`，绝对+线性模式为 `false`；AutoShop 手动保存可能保留旧的 `encoderModeLegacy` compilerRecord，语义 apply 不强行改这个旧编译记录；原点返回设置里的 `homeOriginSignal`、`homeZSignal`、`homePositiveLimit`、`homeNegativeLimit` 使用 `未分配`/`使用`/`不使用`，`homeReturnDirection`、`homeInputDetectionDirection` 使用 `未分配`/`正向`/`负向`，apply 会拒绝正负限位同时使用，并对已确认组合自动同步 `homeMethodNumber`。轴组设置编辑 `配置/轴组设置/_node.config.json` 里的 `axisGroup.groups`：当前支持修改既有轴组、在数组末尾追加默认轴组，空轴组工程会导出空数组并可从 0 开始追加，`xAxis`/`yAxis`/`zAxis`/`auxiliaryAxis` 可填轴名或 `未分配`，删除或中间插入轴组会拒绝；同一次 apply 同时修改运动轴和轴组时，会对同一个 `EtherCat.dat` 串行叠加语义改动。EtherCAT 常规参数优先编辑 `配置/EtherCAT/_node.config.json` 里的 `ethercat.parameters`；当前只允许编辑已确认的 `cycleTimeUs`、`syncOffsetPercent`、`autoRestartSlave`、`aliasEnabled`，其他可解析私有记录只在 `ethercat.records` 中以 `parameter_0x...` 展示且 `editable=false`，不允许写回。其他配置节点编辑 `files[].contentHex` 或 `files[].contentBase64` 后应用。Windows 保留设备名会使用安全目录名，例如 AutoShop 的 `配置/COM0` 镜像为 `配置/COM0_/_node.config.json`，JSON 内 `treePath` 仍保留原始树路径。保存后统一应用并刷新：

EtherCAT/EtherNet/IP 从站新增时，JSON 面向用户的字段使用 AutoShop 工具箱叶子名称 `toolboxName`，例如 `SV820_3Axis_V3.03`、`GL10-RTU-ECTA_2.0.7.0`、`H5U`；`model/name/catalogKey/templateKey` 是导出补全和高级诊断字段，不要求普通编辑手写。EtherNet/IP 参数位于 `配置/EtherNet/IP/_node.config.json` 的 `ethernetIP`；`devices` 映射工程树下的 EIP_Card/H5U/Easy/Generic 等设备，可通过 `toolboxName`、`templateKey`、完整 `records` 或 `privateRecords` 增删改；从站通用/信息/状态页导出为 `devices[].general/info/status`，底层页面字段按 `devices[].pages` 分组导出并可在 `editable:true` 时改 `value`，H5U 连接页导出为 `connections/tagConnections`，连接详情可编辑 RPI、超时倍数、传输类型、连接类型、优先级、固定/变量和传输格式。如果当前工程没有同型号样本，且 `deviceLibraryPath` 下存在模板，apply 会从模板库克隆完整设备记录和私有工程树记录。`producerTags`、`serverMessageTags` 和 `adapter.connections[].outputDatasets/inputDatasets` 分别映射生产者标签、服务消息标签、Adapter 连接与 I/O 数据集，设备页同名字段是从站窗口别名；应用时重建 `EIP.dat`、同步 `EIP.datBAK` 并重算 CRC32。`Generic_EtherNet_IP_device` 是 private-only 模板，可通过 `toolboxName` 新增、删除和保真回读，不生成 primary device records。

```powershell
<package-dir>\scripts\autoshop-agent.exe workspace apply --project <project-dir> --in <workspace-dir> --allow-open-project --refresh --format json
```

不要手工编辑 `.gvt`、`.stru`、`.fbi`。普通私有二进制包装文件的 `contentBase64` 仍保留作兼容；配置节点优先改 `_node.config.json` 中对应的语义字段，未解析时再改 `contentHex` 或 `contentBase64`。`STRING<128>`、结构体、数组等带显式 `dataType` 的变量由 CLI 写入记录扩展，可以在 `variables` 中按需要排序。

只按名称关闭并重新打开窗口：

```powershell
<package-dir>\scripts\autoshop-agent.exe ui refresh --program MAIN
```

变量表等工程级缓存需要关闭并重新打开工程才能让 AutoShop UI 看到磁盘上的更新。推荐拆成关闭和恢复两步，这样可以在中间执行文件层写回：
```powershell
<package-dir>\scripts\autoshop-agent.exe ui close-project --project <project-dir> --state <package-dir>Work\current-project-state.json --format json
<package-dir>\scripts\autoshop-agent.exe ui restore-project --state <package-dir>Work\current-project-state.json --format json
```

`restore-project` 会优先复用记录的同一个 AutoShop 进程，通过打开工程对话框恢复工程；原进程不存在时才回退到启动工程文件。当 AutoShop 原本最小化时，CLI 会把主窗口和打开工程对话框临时移动到虚拟屏幕右下角边缘，完成后恢复原最小化状态。

查看 AutoShop 已打开 POU 和工程树：

```powershell
<package-dir>\scripts\autoshop-agent.exe ui windows --format json
<package-dir>\scripts\autoshop-agent.exe ui tree --format json
```

静默截取 AutoShop 主窗口或已打开的 MDI 子窗口，不切前台：

```powershell
<package-dir>\scripts\autoshop-agent.exe ui screenshot --out <tmp-dir>\autoshop.png --format json
<package-dir>\scripts\autoshop-agent.exe ui screenshot --title 变量表 --out <tmp-dir>\variables.png --format json
<package-dir>\scripts\autoshop-agent.exe ui screenshot --title 变量表 --restore-offscreen --out <tmp-dir>\variables.png --format json
```

截图命令使用 Win32 `PrintWindow`。目标窗口最小化时使用 `--restore-offscreen`：CLI 会按当前虚拟屏幕边界把 AutoShop 临时恢复到右下角屏幕外，截图后恢复原窗口状态；若原来是最小化，则先隐藏窗口、写入离屏 normal placement，再不激活显示并确认离屏位置；如果 MFC 窗口仍保持最小化，会在 normal placement 已经离屏后执行 `SW_RESTORE` 兜底并再次确认离屏位置，完成后恢复最小化状态。CLI 会返回 `contentRatio`；整窗截图低内容时会重试，仍疑似白客户区时自动尝试 client-only fallback，成功时 JSON 中 `method=PrintWindowClientFallback`、`clientOnly=true` 并带 `warnings`。`nonBlank` 和 `uniqueProbe` 只作为辅助探针，不能单独作为截图有效依据。

