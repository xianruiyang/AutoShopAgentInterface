---
name: autoshop-agent-interface
description: "当 Codex 需要通过随包 CLI 操作汇川 Inovance AutoShop Lite ST 工程时使用：把工程导出成按 AutoShop 工程树排布的可编辑 workspace 文件夹、修改后应用回工程、检查工程、分析 LiteST 文本、查询本地指令资料摘要、查看或刷新 AutoShop 窗口；也可用 target transports/scan/connect --backend hardware 配置/测试 PLC 通讯，并用 ui download --yes 通过 AutoShop 官方 UI 下载到真实 PLC。真实 F9 上载与 F3 监控按钮分别用 ui upload 和 ui monitor。其余 target、online、monitor、comm、motion 等真实设备相关命令默认使用 simulator 后端。"
---

# AutoShop Agent Interface

## 核心规则

优先使用随 skill 打包的 CLI：

```text
scripts/autoshop-agent.exe
```

除非需要维护这个可执行文件本身，否则不要重新实现 AutoShop 二进制 ST 解析或 Win32 窗口刷新逻辑。

这个目录只是已开发好的 skill 包。除非用户明确要求安装，否则不要把它复制或安装到 Codex 的 skill 目录，也不要修改 Codex 配置。

在 `F:\program\PLC` 当前工作区，项目映射固定使用：

```text
F:\program\PLC\AutoShopAgentInterfaceWork\current-export
```

不要在 `F:\program\PLC` 根目录生成 `001-*` 映射目录；临时验证目录放到 `F:\program\PLC\AutoShopAgentInterfaceWork\archive` 下。不要把 workspace、smoke 工程或临时导出放进本 skill 文件夹；`AutoShopAgentInterface` 内只保留最终 CLI、说明文档和 skill 元数据。

## 能力边界

- H5U 等结构化 EtherNet/IP 从站的 `EtherNet/IP I/O映射` 页优先通过 `ethernetIP.devices[].ioMappings[].variableName` 编辑；apply 会同步首个数据集变量、连接派生变量、privateRecords 和 `SYS_EIP.eIPgvt`。避免在同一字段同时修改 `ioMappings` 与底层 `connections[].inputDatasets/outputDatasets`。
- 当前版本默认只做本地文件、LiteST 文本、AutoShop UI 窗口操作、静默窗口截图和安全的侧车文件；真实设备入口必须按命令边界显式使用。
- `target transports/scan/connect --backend hardware` 已接入 AutoShop 官方 `工具 -> 通讯设置` 流程：可读取下拉框通讯类型、搜索、选择通讯类型、写入并读回设备 IP、点击测试，并只在 AutoShop 返回已连通后确认设置；`--transport` 支持 `ethernet`、`usb`、`index:N` 或 AutoShop 下拉框可见文字；`--test=false` 只写入设置，不声明已连通。
- `online`、`monitor`、`comm`、`motion`、`build compile/down/updown` 以及除 scan/connect 外的 `target` 命令仍默认使用 `simulator` 后端，可执行并产出结构化状态或文件；不会 RUN/STOP 真实 PLC、下载真实设备或写真实设备。真实 RUN/STOP/下载/上载/监控按钮使用 `ui run`、`ui stop`、`ui download --yes`、`ui upload`、`ui monitor`，其中 `ui download --yes` 会确认 AutoShop 的下载设置和下载过程提示，默认不在下载完成后运行 PLC，只有显式 `--run-after` 才会同意下载后的运行提示；`ui upload` 只触发并采集上载弹窗/输出，不自动确认可能改写当前 AutoShop 会话的上载流程。
- 文件编辑主流程只用 `workspace export` 和 `workspace apply`。先导出成按 AutoShop 工程树排布的文件夹，再修改文件夹，最后应用回工程。工程内容的新增、删除、修改应通过 workspace JSON/文本镜像应用完成，不要为每类文件操作继续增加独立指令。
- 当目标工程当前已在 AutoShop 打开时，默认必须先通过 `ui windows --format json` 确认主窗口 `title` 中的工程路径就是目标工程，再执行 `ui close-project --project <dir> --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json` 记录并关闭工程；完成 workspace 编辑和 `workspace apply` 后，再执行 `ui restore-project --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json` 恢复工程和窗口。若 AutoShop 未打开目标工程则跳过关闭/恢复；若打开的是其他工程，不要关闭。不要把 `--allow-open-project` 作为常规写回路径；只有用户明确要求跳过关闭/恢复流程时才可作为例外使用，并要说明风险。
- `workspace apply` 写回后会自动回读工程文件并校验 SHA；JSON 输出里应检查 `verified=true` 和 `readBackSha256`。输出中的 `kind=project-index` / `kind=project-package` 表示 CLI 同步写入了 `.hcp` 工程索引和 `.hcpp` 工程包成员快照。
- POU 文件层能力已沉到 `workspace apply` 内部使用：程序块/中断是 `.ST` 容器并登记 `FileType=80`，功能块是 `.FB` 容器并登记 `FileType=81`/`ProgType=7`，函数是 `.FC` 容器并登记 `FileType=82`/`ProgType=8`；在 `编程/程序块`、`编程/功能块(FB)`、`编程/函数(FC)` 下新增 `*.pou.json` 可由 `workspace apply` 创建对应 POU 文件、维护 `folder.txt`，并同步 `.hcp` 工程索引和 `.hcpp` 工程包。`pou add` 与 `pou remove` 都会同步 `folder.txt`、`.hcp`、`.hcpp`；`pou remove` 也可清理 `.hcp` 中 `FileName` 为空的隐藏损坏 POU 登记。`pou add` 属于底层兼容/诊断入口，不作为推荐编辑流程。
- 配置树节点会导出为 `配置/<节点名>/_node.config.json`，覆盖输入滤波、模块配置、电子凸轮、运动控制轴、轴组设置、EtherCAT、COM0、CAN(CANLink)、以太网、EtherNet/IP 等节点；编辑 `files[].contentHex` 或 `files[].contentBase64` 后由 `workspace apply` 写回对应工程文件并回读校验。输入滤波节点若能识别 `Config.sdt`，会额外导出 `inputFilter.parameters`；模块配置节点若能识别 `h5u_moduleCfg.data`，会额外导出 `moduleConfig.modules`，每个槽位包含 `slot`、`model`、`identity`、`moduleTypeCode`、`instance`、`ioSignals`、`moduleParameters` 和保底回写用 `parametersHex`，`workspace apply` 会按该数组重建模块配置文件；已知 GL10 模块可只填 `model` 让 CLI 使用样本默认参数生成，`ioSignals` 可修改已有 X/Y 地址但数量必须与该模块参数中的地址字段一致。`moduleParameters` 把模块内重复 UI 页面映射成数组：4DA/4AD 是同一通道页重复 4 次，8TC/4TC/4PT 的 `通道X-通道Y` 是同一通道 schema 的分组数组；已确认字段可直接编辑，尚未拆清的模块基本配置位域保留 `rawCode`，未知私有字节继续由 `parametersHex` 保真兜底。电子凸轮节点若能识别 `Ecam.tr`，会额外导出 `electronicCam.cams`：当前已通过 AutoShop 实际界面验证并开放名称、增删凸轮、`masterRange/slaveRange` 和 18 字节点表多点 `points` 写回；后续点 `type` 支持 AutoShop 下拉项 `Line` 与 `Spline`，`NA` 只用于首行或空/无效点，不作为后续点普通插补类型；非 ASCII 名称和未知保留位尚未开放，必须先采样验证后再进入语义 JSON。运动控制轴节点若能识别 `EtherCat.dat`，会额外导出 `motionAxis.axes`：常用字段在每个轴的 `parameters`，底层 UI/编译记录在 `uiRecords`/`compilerRecords`；当前支持修改既有轴参数、在 `axes` 末尾追加默认轴，空轴工程会导出空数组并可从 0 开始追加，并同步写回 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`，删除或中间插入轴会被拒绝；模式/参数设置里的 `encoderMode` 使用 `增量模式|绝对模式`，并会同步 AutoShop 实际保存的 `encoderModeEffective` 与 `encoderModeLinkedFlag` 编译记录、可见 UI 记录和 `ignoreLimitAfterErrorStop` 联动值；`axisMotionMode` 使用 `线性模式|旋转模式`，`softwareLimitEnabled` 为软件限位使能布尔值；为匹配 AutoShop 手动保存行为，`axisMotionMode` 或 `encoderMode` 改动时会同步 `ignoreLimitAfterErrorStop`：增量模式或旋转模式为 `true`，绝对+线性模式为 `false`；AutoShop 手动保存可能保留旧的 `encoderModeLegacy` compilerRecord，语义 apply 不强行改这个旧编译记录；原点返回设置里的 `homeOriginSignal`、`homeZSignal`、`homePositiveLimit`、`homeNegativeLimit` 使用 `未分配|使用|不使用`，`homeReturnDirection`、`homeInputDetectionDirection` 使用 `未分配|正向|负向`；`workspace apply` 会拒绝正限位和负限位同时为 `使用`，并对已由样本确认的下拉项组合自动同步 `homeMethodNumber`，未知组合不猜测。EtherCAT 节点若能识别 `EtherCat.dat`，会额外导出 `ethercat.parameters` 和 `ethercat.slaves`：`parameters` 用于主站常规设置字段 `cycleTimeUs`、`syncOffsetPercent`、`autoRestartSlave`、`aliasEnabled`；`slaves` 是顶层从站数组，每个对象含 `parameters`、完整私有 `records`、断线输出语义 `disconnectOutput`、页面化语义索引 `pages` 和 `segmentBase64` 模板；`disconnectOutput` 对应数字量输出从站页面；`mode` 写 AutoShop 私有记录 `0x50200001` 并镜像已有 CoE `0x6206:1`，`channels[].level` 写页面实际使用的 `0x50200002` 并仅镜像已有 `0x6207:n`，raw hex 字段仅用于诊断；`pages` 按 identity、topology、sync/DC、ESI SyncManager、RxPDO、TxPDO、CoE Object Dictionary、disconnectOutput、AutoShop objectDictionary/deviceParameter/private records 等页面分组，`editable:true` 字段可直接改 `value`。修改既有从站优先改 `slaves[].parameters`、`slaves[].disconnectOutput` 或 `slaves[].pages`，未命名型号专属字段可改 `slaves[].records[].value`；删除从站直接移除数组对象；新增同型号从站在末尾追加对象并填写 `templateKey` 指向已有从站 `key`，新增设备库型号优先填写 `toolboxName`，值必须是 AutoShop 工具箱里的叶子名称；`catalogKey` 仅作为高级诊断字段；catalog 会过滤没有真实设备名或 ProductCode 的 ESI 父占位项，并导出每个型号的 SyncManager、Rx/Tx PDO、CoE `objectDictionary` 和 DC 模式；同型号 `templateAvailable=true` 时会克隆完整模板，并同步对应主站记录和 `SYS_ETHERCAT.ecgvt` 系统变量行；无模板时默认拒绝，以保证 AutoShop UI 参数保真。确实只需要基础 ESI 实例时，必须显式设置 `allowGeneratedFromCatalog=true`；该基础实例不保证被 AutoShop 工程树识别为可见从站。需要 100% 保留厂家私有页面隐藏字段并在界面可见时，仍应优先使用同型号模板或复制带 `segmentBase64` 的 AutoShop 手动创建从站对象。状态页的循环时间、执行时间、丢帧次数等为在线任务监控值，不作为离线工程配置承诺写回。Windows 保留设备名会使用安全目录名，例如 AutoShop 的 `配置/COM0` 镜像为 `配置/COM0_/_node.config.json`，JSON 内 `treePath` 仍保留原始树路径。监控表、交叉引用表、元件使用表等未解析的私有二进制内容仍导出为 JSON 包装文件；全局变量表 `变量表.gvt` 若能识别，会导出为专用语义 JSON，`variables` 是可直接编辑的变量数组。`STRING<128>`、结构体、数组等带显式 `dataType` 的变量由 CLI 写入记录扩展，可以在 `variables` 中按需要排序。变量行支持 `powerRetain`=`保持|不保持` 和 `networkAccess`=`私有|公有|输入/输出`，对应 AutoShop 变量表中的掉电保持和网络公开列。
- CAN(CANLink) 根页面位于 `配置/CAN(CANLink)/_node.config.json` 的 `canLink.portConfig`，优先编辑 `parameters.protocol`、`stationNumber`、`baudRateKbps`；右键“添加CAN配置”生成的 `CANLink.data`、`CANLink.prg` 会在 `rightClickConfig` 和 `files` 中显式标出，缺失时当前版本不伪造未验证格式。
- `ui compile`、`ui compile-all`、`ui run`、`ui stop`、`ui download`、`ui upload`、`ui monitor` 分别对应 AutoShop 工具栏/快捷键 `Ctrl+F7`、`F7`、`F5`、`F6`、`F8`、`F9`、`F3`，默认通过主窗口 `WM_COMMAND` 静默触发，并返回底部“信息输出窗口”输出及本次新弹出的 AutoShop 对话框文本；`ui monitor/run/stop` 默认会读取并立即确认连接状态类 `确定` 弹窗，避免弹窗堆积；`ui download --yes` 会确认下载相关弹窗并返回 `confirmedDialogs`；`ui upload` 不自动确认上载弹窗。`ui output` 可单独读取 `compile|communication|transfer|search|visible|all` 输出页。输出默认 `--lines errors` 只返回错误行；完整日志使用 `--lines all --tail 0`。
- `ui screenshot` 使用 Win32 `PrintWindow` 按窗口句柄输出 PNG，默认强制离屏截图并恢复原状态；如果 AutoShop 抢到前台，会使用最小化兜底保护用户前台窗口；`--restore-offscreen` 仅作为兼容参数保留，`--offscreen-visible 0` 表示完全离屏，设置为正数时仅用于诊断边缘可见像素。
- 批量人工验证参数页时，先用 `ui open-path --path <工程树路径> --format json` 离屏打开 MDI 参数页，截图后用 `ui close --title <窗口标题> --format json` 关闭该页，避免 AutoShop 子窗口数量上限影响后续页面打开。需要打开归档验证工程且没有历史状态文件时，可使用 `ui restore-project --project <工程目录> --format json`；传入 `--state` 时仍按记录状态严格恢复。

## 常用命令

导出工程 workspace，修改后应用回工程；如果 `ui windows --format json` 确认目标工程当前已打开，使用首尾的关闭/恢复命令包围写回流程，未打开则跳过首尾两条：

```powershell
.\scripts\autoshop-agent.exe ui close-project --project F:\program\PLC\001 --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
.\scripts\autoshop-agent.exe workspace export --project F:\program\PLC\001 --out F:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
.\scripts\autoshop-agent.exe workspace apply --project F:\program\PLC\001 --in F:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project F:\program\PLC\001 --in F:\program\PLC\AutoShopAgentInterfaceWork\current-export --format json
.\scripts\autoshop-agent.exe ui restore-project --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

全局变量表位于 `全局变量/变量表/变量表.gvt.json`，优先编辑其中的 `variables` 数组，不要手工编辑 `.gvt` 或伪造 `contentBase64`。输入滤波参数位于 `配置/输入滤波/_node.config.json` 的 `inputFilter.parameters`；模块配置槽位位于 `配置/模块配置/_node.config.json` 的 `moduleConfig.modules`，其中模块内页面参数优先编辑每个槽位的 `moduleParameters`；电子凸轮位于 `配置/电子凸轮/_node.config.json` 的 `electronicCam.cams`，优先编辑凸轮名称、`parameters.masterRange/slaveRange` 和 18 字节点表多点 `points`，新增/删除凸轮直接改 `cams` 数组；运动控制轴位于 `配置/运动控制轴/_node.config.json` 的 `motionAxis.axes`，优先编辑 `parameters`，支持在末尾追加默认轴，空轴工程可从 0 开始追加，基本设置可改 `virtualAxisMode`（虚轴模式）和 `autoMappingEnabled`（自动映射），模式/参数设置可改 `encoderMode`、`axisMotionMode`、`softwareLimitEnabled`，`encoderMode` 会同步 `encoderModeEffective`、`encoderModeLinkedFlag`、可见 UI 记录和 `ignoreLimitAfterErrorStop` 联动值，`axisMotionMode` 也会自动同步 `ignoreLimitAfterErrorStop`（增量或旋转为 `true`、绝对+线性为 `false`），但不强行改 AutoShop 手动保存可能保留旧值的 `encoderModeLegacy` compilerRecord；原点返回下拉项使用中文枚举，正/负限位不能同时为 `使用`，已确认组合会自动同步 `homeMethodNumber`；轴组设置位于 `配置/轴组设置/_node.config.json` 的 `axisGroup.groups`，优先编辑 `parameters` 中的 X/Y/Z/辅助轴、最大速度、最大加速度和停止方式，支持在末尾追加默认轴组，空轴组工程可从 0 开始追加；EtherNet/IP 位于 `配置/EtherNet/IP/_node.config.json` 的 `ethernetIP`，优先编辑 `devices`、`devices[].general`、`devices[].connections/tagConnections`、生产者标签、服务消息标签、Adapter 连接和 I/O 数据集；其余从站页面/底层记录通过 `devices[].pages` 分组查看和受控编辑，其中 Adapter 数据集类型只能是 `INT|DINT|REAL`，新增 EtherNet/IP 设备优先写 AutoShop 工具箱名称 `toolboxName`，`catalogKey` 仅用于高级诊断，若 `deviceLibraryPath` 指向外部语义模板库则可从库中克隆 EIP_Card/Easy/H5U 完整 `records + privateRecords`，并按真实 `_IPn_*` 引用只补齐缺失的 `SYS_EIP.eIPgvt` 系统变量；无语义模板新增时需显式 `allowGeneratedFromCatalog=true`；EtherCAT 位于 `配置/EtherCAT/_node.config.json`，主站常规参数在 `ethercat.parameters`，从站增删改在 `ethercat.slaves`，新增从站优先写 AutoShop 工具箱名称 `toolboxName`，`catalogKey` 仅用于高级诊断，无模板新增时需显式 `allowGeneratedFromCatalog=true`；其他配置树节点位于 `配置/<节点名>/_node.config.json`，必要时改对应文件的 `contentHex` 或 `contentBase64`。已按当前样本验证 BOOL、BYTE、INT、DINT、REAL、ARRAY、IP、STRING/STRING<...>、自定义结构体、以 _s/_u 开头的系统结构/联合类型，以及 `powerRetain` 和 `networkAccess`。

CAN(CANLink) 位于 `配置/CAN(CANLink)/_node.config.json` 的 `canLink`，根配置优先编辑 `canLink.portConfig.parameters.protocol/stationNumber/baudRateKbps`；`stationSource/baudRateSource` 当前样本只读；右键子配置文件缺失时只标状态，不生成未验证文件。

运动控制轴单位换算页的 `reverseDirection` 对应 AutoShop “反向”复选框；CLI 会同时同步 `0x80000118` 可见复选框位和 `0x80000117` 联动标志。`gearDeviceEnabled` 对应“使用变速装置”。`pulsesPerRevolution` 用十进制数写入，AutoShop 里的 `16#1000000` 对应 JSON 值 `16777216`。

检查工程和 ST 容器：

```powershell
.\scripts\autoshop-agent.exe project check --project F:\program\PLC\001 --format json
.\scripts\autoshop-agent.exe pou list --project F:\program\PLC\001
```

导出单个程序到 txt：

```powershell
.\scripts\autoshop-agent.exe pou export --project F:\program\PLC\001 --name MAIN --out D:\tmp\MAIN.st.txt
```

导出全部 ST 程序：

```powershell
.\scripts\autoshop-agent.exe pou export-all --project F:\program\PLC\001 --out D:\tmp\st-export
```

从 txt 写回既有程序：

```powershell
.\scripts\autoshop-agent.exe pou import --project F:\program\PLC\001 --name MAIN --in D:\tmp\MAIN.st.txt
```

如果 `ui windows --format json` 确认 AutoShop 正在打开同一工程，先关闭工程、写回后再恢复；`--allow-open-project` 只作为用户明确要求跳过关闭/恢复流程时的例外。

写回前先做不落盘验证：

```powershell
.\scripts\autoshop-agent.exe pou import --project F:\program\PLC\001 --name MAIN --in D:\tmp\MAIN.st.txt --dry-run --format json
```

如果写回目标工程当前在 AutoShop 中打开：

```powershell
.\scripts\autoshop-agent.exe ui close-project --project F:\program\PLC\001 --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
.\scripts\autoshop-agent.exe pou import --project F:\program\PLC\001 --name MAIN --in D:\tmp\MAIN.st.txt --format json
.\scripts\autoshop-agent.exe ui restore-project --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

变量表等工程级缓存刷新：
```powershell
.\scripts\autoshop-agent.exe ui close-project --project F:\program\PLC\001 --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
.\scripts\autoshop-agent.exe ui restore-project --state F:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

查看 AutoShop 窗口和工程树：

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui tree --format json
.\scripts\autoshop-agent.exe ui compile-all --tail 50 --format json
.\scripts\autoshop-agent.exe ui output --pane compile --tail 50 --format json
.\scripts\autoshop-agent.exe ui output --pane compile --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui download --yes --timeout-ms 60000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui upload --timeout-ms 8000 --lines all --tail 0 --format json
.\scripts\autoshop-agent.exe ui monitor --timeout-ms 4000 --format json
```

静默截取 AutoShop 主窗口或已打开的 MDI 子窗口：

```powershell
.\scripts\autoshop-agent.exe ui screenshot --out D:\tmp\autoshop.png --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --out D:\tmp\变量表.png --format json
.\scripts\autoshop-agent.exe ui screenshot --program MAIN --out D:\tmp\MAIN.png --client --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --out D:\tmp\变量表.png --format json
```

截图 JSON 里检查 `nonBlank=true` 和 `uniqueProbe` 大于 `1`。如果 `offscreen=true`，表示 CLI 已在虚拟屏幕外完成截图，并已恢复 AutoShop 原窗口状态。

LiteST 文本分析：

```powershell
.\scripts\autoshop-agent.exe st lint --in D:\tmp\MAIN.st.txt
.\scripts\autoshop-agent.exe st parse --in D:\tmp\MAIN.st.txt --format json
.\scripts\autoshop-agent.exe st refs --in D:\tmp\MAIN.st.txt --symbol M123
.\scripts\autoshop-agent.exe st instruction search modbus --format json
```

工程归档、变量和通讯配置文件查看：

```powershell
.\scripts\autoshop-agent.exe project archive pack --project F:\program\PLC\001-copy --out D:\tmp\project.agent.zip
.\scripts\autoshop-agent.exe var export --project F:\program\PLC\001 --out D:\tmp\vars.json
.\scripts\autoshop-agent.exe var system list --project F:\program\PLC\001 --format json
.\scripts\autoshop-agent.exe var table list --project F:\program\PLC\001 --format json
.\scripts\autoshop-agent.exe var table export --project F:\program\PLC\001 --name variable --out D:\tmp\变量表.gvt
.\scripts\autoshop-agent.exe var table import --project F:\program\PLC\001 --name variable --in D:\tmp\变量表.gvt --dry-run --format json
.\scripts\autoshop-agent.exe project node list --project F:\program\PLC\001 --category program --format json
.\scripts\autoshop-agent.exe project node info --project F:\program\PLC\001 --name MAIN --format json
.\scripts\autoshop-agent.exe project node list --project F:\program\PLC\001 --category config --format json
.\scripts\autoshop-agent.exe project node list --project F:\program\PLC\001 --category variable --format json
.\scripts\autoshop-agent.exe project node export --project F:\program\PLC\001 --name ethercat --out D:\tmp\ethercat-node.zip
.\scripts\autoshop-agent.exe project node import --project F:\program\PLC\001 --name ethercat --in D:\tmp\ethercat-node.zip --dry-run --format json
.\scripts\autoshop-agent.exe comm serial show --project F:\program\PLC\001 --format json
```

刷新变量表、软元件表、功能块实例或系统变量表窗口：

```powershell
.\scripts\autoshop-agent.exe var table refresh --project F:\program\PLC\001 --name variable
.\scripts\autoshop-agent.exe project node refresh --project F:\program\PLC\001 --name MAIN
.\scripts\autoshop-agent.exe project node refresh --project F:\program\PLC\001 --name ethercat
.\scripts\autoshop-agent.exe ui refresh-path --path "全局变量/软元件表" --title 软元件表
.\scripts\autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" --title _SYS_COM
```

Trace 本地侧车定义，不启动 PLC 采样：

```powershell
.\scripts\autoshop-agent.exe trace add --project F:\program\PLC\001-copy --name bench --items D100,M0
.\scripts\autoshop-agent.exe trace list --project F:\program\PLC\001-copy --format json
.\scripts\autoshop-agent.exe trace export --project F:\program\PLC\001-copy --name bench --out D:\tmp\trace.csv
```

无 PLC simulator 后端示例：

```powershell
.\scripts\autoshop-agent.exe target scan --format json
.\scripts\autoshop-agent.exe monitor read --profile bench --device D100 --format json
```

真实 AutoShop 通讯设置示例：
```powershell
.\scripts\autoshop-agent.exe target scan --backend hardware --transport ethernet --format json
.\scripts\autoshop-agent.exe target connect --backend hardware --transport ethernet --ip 192.168.1.10 --format json
.\scripts\autoshop-agent.exe target transports --backend hardware --format json
.\scripts\autoshop-agent.exe target connect --backend hardware --profile h5u --format json
```

全命令 simulator 后端示例：

```powershell
.\scripts\autoshop-agent.exe target connect --profile sim --format json
.\scripts\autoshop-agent.exe target run --profile sim --yes --format json
.\scripts\autoshop-agent.exe monitor write --device D100 --value 123 --yes --format json
.\scripts\autoshop-agent.exe build down --project F:\program\PLC\001-copy --out D:\tmp\program.down --format json
.\scripts\autoshop-agent.exe online enter --profile sim --project F:\program\PLC\001-copy --format json
.\scripts\autoshop-agent.exe comm ethercat scan --profile sim --format json
.\scripts\autoshop-agent.exe motion axis add --project F:\program\PLC\001-copy --name Axis1 --format json
```

## 兼容别名

以下旧命令仍可用：

```powershell
.\scripts\autoshop-agent.exe list --project F:\program\PLC\001
.\scripts\autoshop-agent.exe export --project F:\program\PLC\001 --program MAIN --out D:\tmp\MAIN.st.txt
.\scripts\autoshop-agent.exe import --project F:\program\PLC\001 --program MAIN --in D:\tmp\MAIN.st.txt
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
.\scripts\autoshop-agent.exe config init --project F:\program\PLC\001 --force
```

关键 JSON 字段：

```json
{
  "defaultProjectDir": "D:\\program\\PLC\\001",
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
