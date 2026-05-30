---
name: autoshop-agent-interface
description: "当 Codex 需要通过随包 CLI 操作汇川 Inovance AutoShop Lite ST 工程时使用：把工程导出成按 AutoShop 工程树排布的可编辑 workspace 文件夹、修改后应用回工程、检查工程、分析 LiteST 文本、查询本地指令资料摘要、查看或刷新 AutoShop 窗口。当前 CLI 支持无 PLC 真机的离线开发流程；target、online、monitor、comm、motion 等真实设备相关命令默认使用 simulator 后端，不会连接或修改 PLC。"
---

# AutoShop Agent Interface

## 核心规则

优先使用随 skill 打包的 CLI：

```text
scripts/autoshop-agent.exe
```

除非需要维护这个可执行文件本身，否则不要重新实现 AutoShop 二进制 ST 解析或 Win32 窗口刷新逻辑。

这个目录只是已开发好的 skill 包。除非用户明确要求安装，否则不要把它复制或安装到 Codex 的 skill 目录，也不要修改 Codex 配置。

在 `D:\program\PLC` 当前工作区，项目映射固定使用：

```text
D:\program\PLC\AutoShopAgentInterfaceWork\current-export
```

不要在 `D:\program\PLC` 根目录生成 `project001-*` 映射目录；临时验证目录放到 `D:\program\PLC\AutoShopAgentInterfaceWork\archive` 下。不要把 workspace、smoke 工程或临时导出放进本 skill 文件夹；`AutoShopAgentInterface` 内只保留最终 CLI、说明文档和 skill 元数据。

## 能力边界

- 当前版本面向无 PLC 真机环境，默认只做本地文件、LiteST 文本、AutoShop UI 窗口操作、静默窗口截图和安全的侧车文件。
- `target`、`online`、`monitor`、`comm`、`motion` 以及 `build compile/down/updown` 已有默认 `simulator` 后端实现，可执行并产出结构化状态或文件；不会扫描网段、连接 USB、RUN/STOP 真实 PLC、下载真实设备或写真实设备。
- 如显式指定 `--backend hardware`，当前版本会拒绝并提示硬件后端尚未实现；真机接入应复用同一命令接口。
- 文件编辑主流程只用 `workspace export` 和 `workspace apply`。先导出成按 AutoShop 工程树排布的文件夹，再修改文件夹，最后应用回工程。工程内容的新增、删除、修改应通过 workspace JSON/文本镜像应用完成，不要为每类文件操作继续增加独立指令。
- `workspace apply` 写回后会自动回读工程文件并校验 SHA；JSON 输出里应检查 `verified=true` 和 `readBackSha256`。输出中的 `kind=project-index` 表示 CLI 同步写入了 `.hcp` 工程索引。
- POU 文件层能力已沉到 `workspace apply` 内部使用：程序块/中断是 `.ST` 容器并登记 `FileType=80`，功能块是 `.FB` 容器并登记 `FileType=81`/`ProgType=7`，函数是 `.FC` 容器并登记 `FileType=82`/`ProgType=8`；在 `编程/程序块`、`编程/功能块(FB)`、`编程/函数(FC)` 下新增 `*.pou.json` 可由 `workspace apply` 创建对应 POU 文件、维护 `folder.txt`，并同步 `.hcp` 工程索引。`pou add` 属于底层兼容/诊断入口，不作为推荐编辑流程。
- 配置树节点会导出为 `配置/<节点名>/_node.config.json`，覆盖输入滤波、模块配置、电子凸轮、运动控制轴、轴组设置、EtherCAT、COM0、CAN(CANLink)、以太网、EtherNet/IP 等节点；编辑 `files[].contentHex` 或 `files[].contentBase64` 后由 `workspace apply` 写回对应工程文件并回读校验。输入滤波节点若能识别 `Config.sdt`，会额外导出 `inputFilter.parameters`；模块配置节点若能识别 `h5u_moduleCfg.data`，会额外导出 `moduleConfig.modules`，每个槽位包含 `slot`、`model`、`identity`、`moduleTypeCode`、`instance`、`ioSignals`、`moduleParameters` 和保底回写用 `parametersHex`，`workspace apply` 会按该数组重建模块配置文件；已知 GL10 模块可只填 `model` 让 CLI 使用样本默认参数生成，`ioSignals` 可修改已有 X/Y 地址但数量必须与该模块参数中的地址字段一致。`moduleParameters` 把模块内重复 UI 页面映射成数组：4DA/4AD 是同一通道页重复 4 次，8TC/4TC/4PT 的 `通道X-通道Y` 是同一通道 schema 的分组数组；已确认字段可直接编辑，尚未拆清的模块基本配置位域保留 `rawCode`，未知私有字节继续由 `parametersHex` 保真兜底。运动控制轴节点若能识别 `EtherCat.dat`，会额外导出 `motionAxis.axes`：常用字段在每个轴的 `parameters`，底层 UI/编译记录在 `uiRecords`/`compilerRecords`；当前支持修改既有轴参数、在 `axes` 末尾追加默认轴，空轴工程会导出空数组并可从 0 开始追加，并同步写回 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`，删除或中间插入轴会被拒绝；模式/参数设置里的 `encoderMode` 使用 `增量模式|绝对模式`，并会同步 AutoShop 实际保存的 `encoderModeEffective` 与 `encoderModeLinkedFlag` 编译记录、可见 UI 记录和 `ignoreLimitAfterErrorStop` 联动值；`axisMotionMode` 使用 `线性模式|旋转模式`，`softwareLimitEnabled` 为软件限位使能布尔值；为匹配 AutoShop 手动保存行为，`axisMotionMode` 或 `encoderMode` 改动时会同步 `ignoreLimitAfterErrorStop`：增量模式或旋转模式为 `true`，绝对+线性模式为 `false`；AutoShop 手动保存可能保留旧的 `encoderModeLegacy` compilerRecord，语义 apply 不强行改这个旧编译记录；原点返回设置里的 `homeOriginSignal`、`homeZSignal`、`homePositiveLimit`、`homeNegativeLimit` 使用 `未分配|使用|不使用`，`homeReturnDirection`、`homeInputDetectionDirection` 使用 `未分配|正向|负向`；`workspace apply` 会拒绝正限位和负限位同时为 `使用`，并对已由样本确认的下拉项组合自动同步 `homeMethodNumber`，未知组合不猜测。EtherCAT 节点若能识别 `EtherCat.dat`，会额外导出 `ethercat.parameters`：当前只允许编辑已确认的常规设置字段 `cycleTimeUs`、`syncOffsetPercent`、`autoRestartSlave`、`aliasEnabled`；其他可解析私有记录只在 `ethercat.records` 中以 `parameter_0x...` 展示且 `editable=false`，`workspace apply` 会拒绝修改它们，避免破坏 AutoShop 私有数据结构。状态页的循环时间、执行时间、丢帧次数等为在线任务监控值，不作为离线工程配置承诺写回。Windows 保留设备名会使用安全目录名，例如 AutoShop 的 `配置/COM0` 镜像为 `配置/COM0_/_node.config.json`，JSON 内 `treePath` 仍保留原始树路径。监控表、交叉引用表、元件使用表等未解析的私有二进制内容仍导出为 JSON 包装文件；全局变量表 `变量表.gvt` 若能识别，会导出为专用语义 JSON，`variables` 是可直接编辑的变量数组。`STRING<128>`、结构体、数组等带显式 `dataType` 的变量由 CLI 写入记录扩展，可以在 `variables` 中按需要排序。变量行支持 `powerRetain`=`保持|不保持` 和 `networkAccess`=`私有|公有|输入/输出`，对应 AutoShop 变量表中的掉电保持和网络公开列。
- 轴组设置节点若能识别 `EtherCat.dat`，会额外导出 `axisGroup.groups`：优先编辑每个轴组的 `parameters`，支持 `xAxis`、`yAxis`、`zAxis`、`auxiliaryAxis`、`maxSpeed`、`maxAcceleration`、`stopMode`、`groupName`、`groupNumber`，并同步写回 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`。当前支持在 `groups` 末尾追加默认轴组；空轴组工程会导出空数组并可从 0 开始追加；删除或中间插入轴组会被拒绝。`axisGroup.availableAxes` 列出可选轴名；未分配导出为 `未分配`，应用未变化时保留原始空字符串或 GB2312 字节。同一次 `workspace apply` 可以同时修改运动轴和轴组，CLI 会对同一个 `EtherCat.dat` 串行叠加语义改动。
- EtherNet/IP 节点若能识别 `EIP.dat`，会额外导出 `ethernetIP`：`producerTags` 是生产者标签，`serverMessageTags` 是服务消息标签，`adapter.connections` 是 Adapter 连接列表；每条连接下的 `outputDatasets`/`inputDatasets` 映射 I/O 数据集。Adapter I/O 数据集的 `dataType` 只能使用 AutoShop 下拉实际支持的 `INT|DINT|REAL`，导出 JSON 会在 `availableAdapterDataTypes` 中列出；`BOOL`、`BYTE`、`STRING` 等只属于标签层通用类型，不能写入 Adapter 数据集。`workspace apply` 会重建 `EIP.dat` 并重算尾部 CRC32；`EIP.data`、`EIP.datBAK`、`SYS_EIP.eIPgvt` 仍作为真实成员文件保留在 `files` 中。
- `全局变量/结构体/*.stru.json` 的 `definition.members` 可编辑自定义结构体成员；在该目录新增符合 `autoshop-agent-struct-definition.v1` 的 `*.stru.json` 后，`workspace apply` 会创建新的 `.stru` 自定义结构体文件，并同步维护 `.hcp` 中 `FileType=31` 的结构体登记。结构体相关 apply 会顺带补齐工程里已有但未登记的 `.stru` 的工程索引。`全局变量/功能块实例/功能块实例.fbi.json` 的 `instances` 可编辑功能块实例。它们都通过 `workspace apply` 重建 AutoShop 私有二进制文件。
- `pou`、`var table`、`project node` 只保留为底层/兼容/诊断命令；正常文件编辑必须优先使用 workspace。
- 外部写回后，AutoShop 已打开编辑窗口不会自动刷新；ST/普通树节点可用 `workspace apply --refresh`、`ui refresh --program <name>`、`ui refresh-path --path <tree-path>` 或旧别名 `refresh --program <name>` 关闭并重新打开对应窗口。变量表等工程级缓存优先用 `ui close-project` 记录当前工程、已打开窗口和活动窗口并关闭工程，再用 `ui restore-project` 读取状态文件、重新打开工程、恢复窗口和焦点；`ui refresh-project` 只保留为一次性兼容封装。
- `ui screenshot` 使用 Win32 `PrintWindow` 按窗口句柄输出 PNG，不会把 AutoShop 切到前台。目标窗口最小化时使用 `--restore-offscreen`：CLI 会把 AutoShop 临时恢复到虚拟屏幕右下角几乎屏幕外，截图后若原来是最小化则立即最小化回去。

## 常用命令

导出工程 workspace，修改后应用回工程：

```powershell
.\scripts\autoshop-agent.exe workspace export --project D:\program\PLC\project001 --out D:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
.\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --allow-open-project --refresh
```

全局变量表位于 `全局变量/变量表/变量表.gvt.json`，优先编辑其中的 `variables` 数组，不要手工编辑 `.gvt` 或伪造 `contentBase64`。输入滤波参数位于 `配置/输入滤波/_node.config.json` 的 `inputFilter.parameters`；模块配置槽位位于 `配置/模块配置/_node.config.json` 的 `moduleConfig.modules`，其中模块内页面参数优先编辑每个槽位的 `moduleParameters`；运动控制轴位于 `配置/运动控制轴/_node.config.json` 的 `motionAxis.axes`，优先编辑 `parameters`，支持在末尾追加默认轴，空轴工程可从 0 开始追加，基本设置可改 `virtualAxisMode`（虚轴模式）和 `autoMappingEnabled`（自动映射），模式/参数设置可改 `encoderMode`、`axisMotionMode`、`softwareLimitEnabled`，`encoderMode` 会同步 `encoderModeEffective`、`encoderModeLinkedFlag`、可见 UI 记录和 `ignoreLimitAfterErrorStop` 联动值，`axisMotionMode` 也会自动同步 `ignoreLimitAfterErrorStop`（增量或旋转为 `true`、绝对+线性为 `false`），但不强行改 AutoShop 手动保存可能保留旧值的 `encoderModeLegacy` compilerRecord；原点返回下拉项使用中文枚举，正/负限位不能同时为 `使用`，已确认组合会自动同步 `homeMethodNumber`；轴组设置位于 `配置/轴组设置/_node.config.json` 的 `axisGroup.groups`，优先编辑 `parameters` 中的 X/Y/Z/辅助轴、最大速度、最大加速度和停止方式，支持在末尾追加默认轴组，空轴组工程可从 0 开始追加；EtherNet/IP 位于 `配置/EtherNet/IP/_node.config.json` 的 `ethernetIP`，优先编辑生产者标签、服务消息标签、Adapter 连接和 I/O 数据集，其中 Adapter 数据集类型只能是 `INT|DINT|REAL`；EtherCAT 常规参数位于 `配置/EtherCAT/_node.config.json` 的 `ethercat.parameters`；其他配置树节点位于 `配置/<节点名>/_node.config.json`，必要时改对应文件的 `contentHex` 或 `contentBase64`。已按当前样本验证 BOOL、BYTE、INT、DINT、REAL、ARRAY、IP、STRING/STRING<...>、自定义结构体、以 _s/_u 开头的系统结构/联合类型，以及 `powerRetain` 和 `networkAccess`。

运动控制轴单位换算页的 `reverseDirection` 对应 AutoShop “反向”复选框；CLI 会同时同步 `0x80000118` 可见复选框位和 `0x80000117` 联动标志。`gearDeviceEnabled` 对应“使用变速装置”。`pulsesPerRevolution` 用十进制数写入，AutoShop 里的 `16#1000000` 对应 JSON 值 `16777216`。

检查工程和 ST 容器：

```powershell
.\scripts\autoshop-agent.exe project check --project D:\program\PLC\project001 --format json
.\scripts\autoshop-agent.exe pou list --project D:\program\PLC\project001
```

导出单个程序到 txt：

```powershell
.\scripts\autoshop-agent.exe pou export --project D:\program\PLC\project001 --name MAIN --out D:\tmp\MAIN.st.txt
```

导出全部 ST 程序：

```powershell
.\scripts\autoshop-agent.exe pou export-all --project D:\program\PLC\project001 --out D:\tmp\st-export
```

从 txt 写回既有程序：

```powershell
.\scripts\autoshop-agent.exe pou import --project D:\program\PLC\project001 --name MAIN --in D:\tmp\MAIN.st.txt
```

如果 AutoShop 正在打开同一工程，并且用户明确接受风险，添加：

```text
--allow-open-project
```

写回前先做不落盘验证：

```powershell
.\scripts\autoshop-agent.exe pou import --project D:\program\PLC\project001 --name MAIN --in D:\tmp\MAIN.st.txt --dry-run --format json
```

写回后刷新 AutoShop 内已打开的 POU 窗口：

```powershell
.\scripts\autoshop-agent.exe pou import --project D:\program\PLC\project001 --name MAIN --in D:\tmp\MAIN.st.txt --allow-open-project --refresh
.\scripts\autoshop-agent.exe ui refresh --program MAIN
```

变量表等工程级缓存刷新：
```powershell
.\scripts\autoshop-agent.exe ui close-project --project D:\program\PLC\project001 --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
.\scripts\autoshop-agent.exe ui restore-project --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

查看 AutoShop 窗口和工程树：

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui tree --format json
```

静默截取 AutoShop 主窗口或已打开的 MDI 子窗口：

```powershell
.\scripts\autoshop-agent.exe ui screenshot --out D:\tmp\autoshop.png --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --out D:\tmp\变量表.png --format json
.\scripts\autoshop-agent.exe ui screenshot --program MAIN --out D:\tmp\MAIN.png --client --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --restore-offscreen --out D:\tmp\变量表.png --format json
```

截图 JSON 里检查 `nonBlank=true` 和 `uniqueProbe` 大于 `1`。如果 `minimized=true` 且 `offscreen=true`，表示 CLI 从最小化状态临时移到屏幕边缘完成了截图，并已按原状态最小化回去。

LiteST 文本分析：

```powershell
.\scripts\autoshop-agent.exe st lint --in D:\tmp\MAIN.st.txt
.\scripts\autoshop-agent.exe st parse --in D:\tmp\MAIN.st.txt --format json
.\scripts\autoshop-agent.exe st refs --in D:\tmp\MAIN.st.txt --symbol M123
.\scripts\autoshop-agent.exe st instruction search modbus --format json
```

工程归档、变量和通讯配置文件查看：

```powershell
.\scripts\autoshop-agent.exe project archive pack --project D:\program\PLC\project001-copy --out D:\tmp\project.agent.zip
.\scripts\autoshop-agent.exe var export --project D:\program\PLC\project001 --out D:\tmp\vars.json
.\scripts\autoshop-agent.exe var system list --project D:\program\PLC\project001 --format json
.\scripts\autoshop-agent.exe var table list --project D:\program\PLC\project001 --format json
.\scripts\autoshop-agent.exe var table export --project D:\program\PLC\project001 --name variable --out D:\tmp\变量表.gvt
.\scripts\autoshop-agent.exe var table import --project D:\program\PLC\project001 --name variable --in D:\tmp\变量表.gvt --dry-run --format json
.\scripts\autoshop-agent.exe project node list --project D:\program\PLC\project001 --category program --format json
.\scripts\autoshop-agent.exe project node info --project D:\program\PLC\project001 --name MAIN --format json
.\scripts\autoshop-agent.exe project node list --project D:\program\PLC\project001 --category config --format json
.\scripts\autoshop-agent.exe project node list --project D:\program\PLC\project001 --category variable --format json
.\scripts\autoshop-agent.exe project node export --project D:\program\PLC\project001 --name ethercat --out D:\tmp\ethercat-node.zip
.\scripts\autoshop-agent.exe project node import --project D:\program\PLC\project001 --name ethercat --in D:\tmp\ethercat-node.zip --dry-run --format json
.\scripts\autoshop-agent.exe comm serial show --project D:\program\PLC\project001 --format json
```

刷新变量表、软元件表、功能块实例或系统变量表窗口：

```powershell
.\scripts\autoshop-agent.exe var table refresh --project D:\program\PLC\project001 --name variable
.\scripts\autoshop-agent.exe project node refresh --project D:\program\PLC\project001 --name MAIN
.\scripts\autoshop-agent.exe project node refresh --project D:\program\PLC\project001 --name ethercat
.\scripts\autoshop-agent.exe ui refresh-path --path "全局变量/软元件表" --title 软元件表
.\scripts\autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" --title _SYS_COM
```

Trace 本地侧车定义，不启动 PLC 采样：

```powershell
.\scripts\autoshop-agent.exe trace add --project D:\program\PLC\project001-copy --name bench --items D100,M0
.\scripts\autoshop-agent.exe trace list --project D:\program\PLC\project001-copy --format json
.\scripts\autoshop-agent.exe trace export --project D:\program\PLC\project001-copy --name bench --out D:\tmp\trace.csv
```

无 PLC simulator 后端示例：

```powershell
.\scripts\autoshop-agent.exe target scan --format json
.\scripts\autoshop-agent.exe monitor read --profile bench --device D100 --format json
```

全命令 simulator 后端示例：

```powershell
.\scripts\autoshop-agent.exe target connect --profile sim --format json
.\scripts\autoshop-agent.exe target run --profile sim --yes --format json
.\scripts\autoshop-agent.exe monitor write --device D100 --value 123 --yes --format json
.\scripts\autoshop-agent.exe build down --project D:\program\PLC\project001-copy --out D:\tmp\program.down --format json
.\scripts\autoshop-agent.exe online enter --profile sim --project D:\program\PLC\project001-copy --format json
.\scripts\autoshop-agent.exe comm ethercat scan --profile sim --format json
.\scripts\autoshop-agent.exe motion axis add --project D:\program\PLC\project001-copy --name Axis1 --format json
```

## 兼容别名

以下旧命令仍可用：

```powershell
.\scripts\autoshop-agent.exe list --project D:\program\PLC\project001
.\scripts\autoshop-agent.exe export --project D:\program\PLC\project001 --program MAIN --out D:\tmp\MAIN.st.txt
.\scripts\autoshop-agent.exe import --project D:\program\PLC\project001 --program MAIN --in D:\tmp\MAIN.st.txt
.\scripts\autoshop-agent.exe windows --json
.\scripts\autoshop-agent.exe refresh --program MAIN
```

## 配置

默认配置路径：

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

也可以使用 `AUTOSHOP_AGENT_CONFIG` 环境变量或 `--config` 参数覆盖。

创建或更新配置：

```powershell
.\scripts\autoshop-agent.exe config init --project D:\program\PLC\project001 --force
```

关键 JSON 字段：

```json
{
  "defaultProjectDir": "D:\\program\\PLC\\project001",
  "autoShopExePath": "",
  "projectTextEncoding": "gb2312",
  "textEncoding": "utf8",
  "closeWaitMs": 700,
  "openWaitMs": 900,
  "processId": 0,
  "ui": {
    "projectTreeTitle": "工程管理",
    "programmingNode": "编程",
    "programBlockNode": "程序块"
  },
  "profiles": {}
}
```

`autoShopExePath` 目前只为未来“自动启动 AutoShop”保留。当前离线命令和 UI 刷新命令不依赖 AutoShop 安装路径。

## 参考资料

修改写回行为前，先读：

```text
references/AutoShopLiteStFormat.md
```

修改或排查窗口刷新行为前，先读：

```text
references/AutoShopUiRefresh.md
```

查询完整 CLI 指令前，先读：

```text
references/AutoShopCliCommands.md
```

维护或运行测试前，先读：

```text
references/AutoShopCliTesting.md
```
