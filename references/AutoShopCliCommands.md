# AutoShop Agent CLI 指令文档

适用版本：autoshop-agent.exe v0.8.33。

本文只记录当前 CLI 的使用方式、能力边界和安全约束，不记录开发计划。

## 能力边界

- 默认后端为 simulator。涉及 PLC、在线监控、通讯扫描、运动控制和构建交付的命令会执行并保存模拟状态或生成模拟文件，但不会连接、扫描、运行、停止、下载、上传或写入真实 PLC。
- 显式指定 --backend hardware 时，当前版本会拒绝执行并提示硬件后端尚未实现。
- 文件编辑主流程是 workspace export 和 workspace apply：先把 AutoShop 工程按软件工程树导出成可编辑文件夹，修改文件夹里的 .st.txt 或 JSON，再统一应用回工程。工程内容的新增、删除、修改应通过 workspace JSON/文本镜像应用完成，不应为每类文件操作继续增加独立指令。
- 在 D:\program\PLC 当前工作区，项目映射固定使用 D:\program\PLC\AutoShopAgentInterfaceWork\current-export；临时验证目录放在 D:\program\PLC\AutoShopAgentInterfaceWork\archive 下。不要在根目录生成 project001-* 映射目录，也不要把 workspace 或 smoke 工程放进 AutoShopAgentInterface skill 文件夹。
- workspace apply 实际写入后会立即从工程文件回读并比对内容 SHA；JSON 输出中的 verified=true 和 readBackSha256 表示该项已经回读确认。
- POU 文件层能力已沉到 workspace apply 内部使用：程序块/中断是 .ST 容器并登记 FileType=80，功能块是 .FB 容器并登记 FileType=81/ProgType=7，函数是 .FC 容器并登记 FileType=82/ProgType=8；在 编程/程序块、编程/功能块(FB)、编程/函数(FC) 下新增 *.pou.json 可由 workspace apply 创建对应 POU 文件、维护 folder.txt，并同步 .hcp 工程索引。pou add 属于底层兼容/诊断入口，不作为推荐编辑流程。
- 配置树节点会额外导出为 kind=config-node 的 _node.config.json，覆盖输入滤波、模块配置、电子凸轮、运动控制轴、轴组设置、EtherCAT、COM0、CAN(CANLink)、以太网、EtherNet/IP 等节点。每个节点 JSON 的 files 数组列出真实工程文件，包含 sourceRelative、SHA、contentHex、contentBase64 和可读字符串预览；修改 contentHex 或 contentBase64 后，workspace apply 会写回对应工程文件并回读校验。输入滤波节点若能识别 Config.sdt，会额外导出 inputFilter.parameters 语义参数；当前已确认字段为 normalX0ToX7Ms、highSpeedX0ToX3_100ns、highSpeedX4ToX7Us。模块配置节点若能识别 h5u_moduleCfg.data，会额外导出 moduleConfig.modules 语义槽位数组；每个槽位包含 slot、model、identity、moduleTypeCode、instance、ioSignals、moduleParameters 和用于保底回写的 parametersHex，workspace apply 会按 modules 重建 h5u_moduleCfg.data；已知 GL10 模块可只填 model 让 CLI 使用样本默认参数生成，ioSignals 可修改已有 X/Y 地址但数量必须与该模块参数中的地址字段一致。moduleParameters 把模块内重复 UI 页面映射成数组：4DA/4AD 是同一通道页重复 4 次，8TC/4TC/4PT 的 通道X-通道Y 是同一通道 schema 的分组数组；已确认字段可直接编辑，尚未拆清的基本配置位域保留 rawCode，未知私有字节继续由 parametersHex 保真兜底。EtherCAT 节点若能识别 EtherCat.dat，会额外导出 ethercat.parameters 语义参数；当前只允许编辑已确认的 常规设置 字段 cycleTimeUs、syncOffsetPercent、autoRestartSlave、aliasEnabled。其他可解析私有记录只在 ethercat.records 中以 parameter_0x... 展示，editable=false，workspace apply 会拒绝修改这些未确认语义的私有记录，避免破坏 AutoShop 数据结构。已确认参数 apply 会重建并同步写回 EtherCat.dat、EtherCat.tmp、EtherCat.datBAK，并在原文件带有效尾部 CRC32 时自动重算该校验。状态 页里的循环时间、执行时间、丢帧次数等为在线任务监控值，不作为离线工程配置承诺写回。COM0 等 Windows 保留设备名会在镜像目录中使用安全名称（例如 COM0_），JSON 内的 treePath 仍保持 AutoShop 原始树路径。若两种编码同时被改且内容不一致，会拒绝应用。未解析的监控、交叉引用、元件使用表等私有二进制内容仍以普通 JSON 包装文件导出，字段包含来源、SHA 和 contentBase64。全局变量/变量表/变量表.gvt 若能识别，会导出为专用语义 JSON：format=autoshop-agent-global-variable-table.v1，kind=global-variable-table，用户只编辑 variables 数组，workspace apply 会根据当前工程里的 .gvt 模板重建私有二进制。变量记录支持 BOOL、BYTE、INT、DINT、REAL、ARRAY、IP、STRING/STRING<...>、自定义结构体和以 _s/_u 开头的系统结构/联合类型；STRING、ARRAY 和结构体等带显式 dataType 的行可位于任意位置。变量记录的 powerRetain 使用 保持/不保持，networkAccess 使用 私有/公有/输入/输出，对应 AutoShop 变量表中的 掉电保持 和 网络公开 列。
- EtherNet/IP 节点若能识别 EIP.dat，会额外导出 ethernetIP 语义配置；producerTags 对应生产者标签，serverMessageTags 对应服务消息标签，adapter.connections 对应 EtherNet/IP Adapter 连接、O->T/T->O 实例与大小、输入/输出数据集 I/O 映射。workspace apply 会重建 EIP.dat 并在原文件带有效尾部 CRC32 时自动重算校验；EIP.data、EIP.datBAK、SYS_EIP.eIPgvt 仍在 files 中保留为真实成员文件映射。
- 全局变量/结构体/*.stru 若能识别，会导出为 kind=struct-definition 的语义 JSON，编辑 definition.members 后由 workspace apply 重建 .stru。在 全局变量/结构体 目录新增符合 autoshop-agent-struct-definition.v1 的 *.stru.json，且 sourceRelative 指向新的 .stru 文件时，workspace apply 会创建新的自定义结构体文件，并同步维护 .hcp 工程索引中的 FileType=31 结构体文件登记；结构体相关 apply 会顺带补齐工程里已有但未登记的 .stru 的 project-index 变更。全局变量/功能块实例/功能块实例.fbi 若能识别，会导出为 kind=fb-instance-table 的语义 JSON，编辑 instances 后由 workspace apply 重建 .fbi。
- var table、project node、pou 等细粒度命令只保留为底层/兼容/诊断命令；正常文件编辑必须优先使用 workspace export/apply。
- 外部写回后，AutoShop 已打开的编辑窗口不会自动刷新。ST/普通树节点可执行 ui refresh --program <name>、ui refresh-path --path <tree-path>，或在 workspace apply / pou import 时加 --refresh。变量表这类工程级缓存需要执行工程级刷新；可用 ui close-project 先记录当前工程、已打开 MDI 窗口和活动窗口并关闭工程，再用 ui restore-project 读取状态文件、重新打开工程文件、恢复窗口并把焦点切回原活动窗口。ui refresh-project 保留为一次性兼容封装。
- ui screenshot 使用 Win32 PrintWindow 按窗口句柄输出 PNG，不会把 AutoShop 切到前台。目标窗口最小化时可传入 --restore-offscreen：CLI 会把 AutoShop 临时恢复到虚拟屏幕右下角几乎屏幕外，截图后若原来是最小化则立即最小化回去。若传入 --allow-minimized，输出可能为空白，JSON 中的 nonBlank/uniqueProbe 可用于快速判断。

## 通用格式

    autoshop-agent.exe <command> [subcommand] [flags]

通用参数：

    --config <path>              JSON 配置路径，优先级高于 AUTOSHOP_AGENT_CONFIG。
    --project <dir|file>         工程目录或工程文件。
    --profile <name>             配置文件中的连接配置名称。
    --backend simulator|hardware 后端。默认 simulator；hardware 当前未实现。
    --format text|json|ndjson    输出格式。默认 text。
    --dry-run                    只解析和验证，不写文件，不影响 PLC 或 AutoShop。
    --yes                        对危险操作进行非交互确认。
    --timeout <duration>         超时时间，例如 30s 或 2m。
    --log <path>                 写结构化运行日志。
    --verbose                    输出更多细节。
    --quiet                      只输出必要结果。

## 指令

### config

    autoshop-agent.exe config init [--config path] [--project dir] [--autoshop-exe path] [--force]
    autoshop-agent.exe config show [--config path] [--format json]
    autoshop-agent.exe config validate [--config path]
    autoshop-agent.exe config set <key> <value> [--config path]
    autoshop-agent.exe config get <key> [--config path]
    autoshop-agent.exe config profile add <name> --transport ethernet --ip <ip> [--port <port>]
    autoshop-agent.exe config profile add <name> --transport usb
    autoshop-agent.exe config profile list
    autoshop-agent.exe config profile remove <name>

### workspace

    autoshop-agent.exe workspace export --project <dir> --out <workspace-dir> [--force]
    autoshop-agent.exe workspace apply --project <dir> --in <workspace-dir> [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh]

运动控制轴参数位于 配置/运动控制轴/_node.config.json 的 motionAxis.axes。优先编辑每个轴的 parameters；uiRecords 和 compilerRecords 保留底层记录映射，供未完全命名字段按 valueType/value 回写。当前支持修改既有轴参数并同步写回 EtherCat.dat、EtherCat.tmp、EtherCat.datBAK；新增/删除轴暂不承诺。模式/参数设置中的 encoderMode 使用 增量模式/绝对模式，axisMotionMode 使用 线性模式/旋转模式，softwareLimitEnabled 为软件限位使能布尔值。原点返回设置已确认的下拉项可直接用中文枚举编辑：homeOriginSignal、homeZSignal、homePositiveLimit、homeNegativeLimit 使用 未分配/使用/不使用，homeReturnDirection、homeInputDetectionDirection 使用 未分配/正向/负向。workspace apply 会拒绝正限位和负限位同时为 使用；对已由样本确认的下拉项组合，会自动同步 homeMethodNumber。

EtherNet/IP 参数位于 配置/EtherNet/IP/_node.config.json 的 ethernetIP。producerTags 是生产者标签，serverMessageTags 是服务消息标签，adapter.connections 是 Adapter 连接列表；每条连接下 outputDatasets/inputDatasets 分别映射输出/输入数据集，支持修改名称、数据类型、位长度和关联变量名。

导出的文件夹按 AutoShop 工程树排布。程序块代码改 编程/程序块 下的 *.st.txt；新增程序块/中断/功能块(FB)/函数(FC) 时，在对应目录新增 *.pou.json，格式为 autoshop-agent-pou-definition.v1，字段包含 name、type、sourceRelative、language=litest、text；全局变量表改 全局变量/变量表/变量表.gvt.json 里的 variables 数组；结构体改 全局变量/结构体/*.stru.json 里的 definition.members，也可以在该目录新增新的 *.stru.json 来创建自定义结构体；功能块实例改 全局变量/功能块实例/功能块实例.fbi.json 里的 instances；输入滤波参数改 配置/输入滤波/_node.config.json 里的 inputFilter.parameters；模块配置槽位改 配置/模块配置/_node.config.json 里的 moduleConfig.modules，模块内部页面参数优先改每个槽位的 moduleParameters；EtherCAT 常规参数只改 配置/EtherCAT/_node.config.json 里的 ethercat.parameters，editable=false 的 ethercat.records 只读；其他配置树节点可改 配置/<节点名>/_node.config.json 里的 files[].contentHex 或 files[].contentBase64，其中 Windows 保留名会带安全后缀，例如 COM0 节点路径为 配置/COM0_/_node.config.json。不需要也不应手工编辑 .gvt/.stru/.fbi。workspace apply 会自动检查 POU、.stru 与 .hcp 工程索引一致性，JSON 输出中 kind=project-index 表示写入了工程索引。写回前建议先执行 workspace apply --dry-run --format json。

本工作区示例固定路径：

    autoshop-agent.exe workspace export --project D:\program\PLC\project001 --out D:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
    autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json

### project

    autoshop-agent.exe project info --project <dir|hcp|hcpp|updown>
    autoshop-agent.exe project tree --project <dir> [--format json]
    autoshop-agent.exe project check --project <dir> [--strict]
    autoshop-agent.exe project backup --project <dir> --out <zip|dir>
    autoshop-agent.exe project archive pack --project <dir> --out <zip>
    autoshop-agent.exe project archive unpack --in <zip> --out <dir>
    autoshop-agent.exe project compare --left <project> --right <project|target> [--detail]
    autoshop-agent.exe project node list --project <dir> [--category program|config|monitor|report|trace|variable|all]
    autoshop-agent.exe project node info --project <dir> --name MAIN|program-blocks|fb-folder|ethercat|com0|monitor-main|cross-reference
    autoshop-agent.exe project node export --project <dir> --name ethercat --out ethercat.zip [--as auto|binary|json|zip]
    autoshop-agent.exe project node import --project <dir> --name ethercat --in ethercat.zip [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh]
    autoshop-agent.exe project node refresh --project <dir> --name MAIN|ethercat

### pou

    autoshop-agent.exe pou list --project <dir> [--format json]
    autoshop-agent.exe pou show --project <dir> --name MAIN
    autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt
    autoshop-agent.exe pou export-all --project <dir> --out <dir>
    autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--dry-run] [--refresh]
    autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW
    autoshop-agent.exe pou add --project <dir> --name SBR_002 --type program|subprogram|interrupt|fb|fc [--text <litest>] [--dry-run] [--allow-open-project] [--no-backup]
    autoshop-agent.exe pou remove --project <dir> --name SBR_002

### st

    autoshop-agent.exe st format --in source.st --out source.formatted.st
    autoshop-agent.exe st lint --in source.st [--target h5u|easy] [--firmware <version>]
    autoshop-agent.exe st parse --in source.st --format json
    autoshop-agent.exe st symbols --in source.st --format json
    autoshop-agent.exe st refs --in source.st --symbol <name>
    autoshop-agent.exe st scaffold mb-master --out example.st
    autoshop-agent.exe st scaffold fb-call --name <FB> --out call.st
    autoshop-agent.exe st instruction search <keyword>
    autoshop-agent.exe st instruction show <name> [--format json]

### var

    autoshop-agent.exe var list --project <dir> [--scope global|local|system]
    autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json
    autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace]
    autoshop-agent.exe var bind --project <dir> --name <var> --device D100
    autoshop-agent.exe var validate --project <dir>
    autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info]
    autoshop-agent.exe var system show --project <dir> --name _SYS_COM
    autoshop-agent.exe var system export --project <dir> --name _SYS_COM --out _SYS_COM.svt
    autoshop-agent.exe var system import --project <dir> --name _SYS_COM --in _SYS_COM.svt [--dry-run] [--allow-open-project] [--refresh]
    autoshop-agent.exe var system refresh --project <dir> --name _SYS_COM
    autoshop-agent.exe var table list --project <dir> [--category system|global|internal|all] [--all]
    autoshop-agent.exe var table info --project <dir> --name variable|device|struct|fb-instance|_SYS_COM
    autoshop-agent.exe var table export --project <dir> --name variable --out 变量表.gvt [--as binary|json|hex|base64]
    autoshop-agent.exe var table import --project <dir> --name variable --in 变量表.gvt [--dry-run] [--allow-open-project] [--no-backup] [--refresh]
    autoshop-agent.exe var table refresh --project <dir> --name variable

### build

    autoshop-agent.exe build check --project <dir>
    autoshop-agent.exe build compile --project <dir> [--clean] [--format json]
    autoshop-agent.exe build diagnostics --project <dir> [--format json]
    autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init]
    autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init]

### target

    autoshop-agent.exe target scan [--transport ethernet|usb]
    autoshop-agent.exe target connect --profile <name>
    autoshop-agent.exe target info --profile <name>
    autoshop-agent.exe target login --profile <name> --password <value>
    autoshop-agent.exe target logout --profile <name>
    autoshop-agent.exe target run --profile <name> [--yes]
    autoshop-agent.exe target stop --profile <name> [--yes]
    autoshop-agent.exe target mode --profile <name>
    autoshop-agent.exe target download --profile <name> --project <dir> [--yes]
    autoshop-agent.exe target upload --profile <name> --out <dir|updown>
    autoshop-agent.exe target download-file --profile <name> --in <down|updown> [--yes]
    autoshop-agent.exe target upload-updown --profile <name> --out <file.updown>

### online

    autoshop-agent.exe online enter --profile <name> --project <dir>
    autoshop-agent.exe online status --profile <name>
    autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes]
    autoshop-agent.exe online commit --profile <name> [--yes]
    autoshop-agent.exe online exit --profile <name>
    autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]

### monitor

    autoshop-agent.exe monitor read --profile <name> --device D100
    autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes]
    autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
    autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json
    autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes]
    autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json
    autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes]

### trace

    autoshop-agent.exe trace list --project <dir>
    autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST
    autoshop-agent.exe trace start --profile <name> --name <trace>
    autoshop-agent.exe trace stop --profile <name> --name <trace>
    autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv
    autoshop-agent.exe trace remove --project <dir> --name <trace>

### diagnose

    autoshop-agent.exe diagnose target --profile <name> [--format json]
    autoshop-agent.exe diagnose logs --profile <name> --out logs.json
    autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system]
    autoshop-agent.exe diagnose project --project <dir> [--format json]
    autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip

### comm

    autoshop-agent.exe comm serial show --project <dir>
    autoshop-agent.exe comm serial set --project <dir> --port COM1 --baud 9600 --data-bits 8 --parity none --stop-bits 1
    autoshop-agent.exe comm modbus-rtu master add --project <dir> --name <name> --port COM1 --addr <id>
    autoshop-agent.exe comm modbus-tcp master add --project <dir> --name <name> --ip <ip> --port 502
    autoshop-agent.exe comm ethernet show --project <dir>
    autoshop-agent.exe comm ethernet set-ip --profile <name> --ip <ip> --mask <mask> --gateway <gateway> [--yes]
    autoshop-agent.exe comm can show --project <dir>
    autoshop-agent.exe comm canopen import-eds --project <dir> --in <file.eds>
    autoshop-agent.exe comm ethercat import-xml --project <dir> --in <file.xml>
    autoshop-agent.exe comm ethercat scan --profile <name>
    autoshop-agent.exe comm ethercat status --profile <name>

### motion

    autoshop-agent.exe motion axis list --project <dir>
    autoshop-agent.exe motion axis add --project <dir> --name Axis1 --type ethercat|pulse
    autoshop-agent.exe motion axis set --project <dir> --name Axis1 --param <key=value>
    autoshop-agent.exe motion axis status --profile <name> --name Axis1
    autoshop-agent.exe motion group list --project <dir>
    autoshop-agent.exe motion group add --project <dir> --name Group1 --axes Axis1,Axis2
    autoshop-agent.exe motion cam import --project <dir> --name Cam1 --in cam.csv
    autoshop-agent.exe motion cam export --project <dir> --name Cam1 --out cam.csv
    autoshop-agent.exe motion hsc list --project <dir>
    autoshop-agent.exe motion hsc add --project <dir> --name Counter1 --mode linear|rotary

### ui

    autoshop-agent.exe ui windows
    autoshop-agent.exe ui refresh --program MAIN
    autoshop-agent.exe ui refresh-path --path "全局变量/变量表" --title 变量表
    autoshop-agent.exe ui close-project --project <dir> [--state project-state.json] [--dry-run] --format json
    autoshop-agent.exe ui restore-project --state project-state.json [--dry-run] --format json
    autoshop-agent.exe ui restore-project --project <dir> [--dry-run] --format json
    autoshop-agent.exe ui refresh-project --project <dir> --dry-run --format json
    autoshop-agent.exe ui refresh-project --project <dir> --format json
    autoshop-agent.exe ui close --program MAIN
    autoshop-agent.exe ui open --program MAIN
    autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" --title _SYS_COM
    autoshop-agent.exe ui focus --program MAIN
    autoshop-agent.exe ui tree --format json
    autoshop-agent.exe ui screenshot --out autoshop.png
    autoshop-agent.exe ui screenshot --title 变量表 --out var-table.png --format json
    autoshop-agent.exe ui screenshot --program MAIN --out main-editor.png --client
    autoshop-agent.exe ui screenshot --title 变量表 --restore-offscreen --out var-table.png --format json
    autoshop-agent.exe ui screenshot --title 变量表 --out diagnostic.png --allow-minimized

### doc

    autoshop-agent.exe doc sources
    autoshop-agent.exe doc outline --manual programming|instruction|user|autoshop
    autoshop-agent.exe doc search <keyword> [--manual programming|instruction|all]
    autoshop-agent.exe doc command-set --out AutoShopCliCommands.md

## 兼容别名

    autoshop-agent.exe list --project <dir>
    autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
    autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
    autoshop-agent.exe windows
    autoshop-agent.exe refresh --program MAIN
