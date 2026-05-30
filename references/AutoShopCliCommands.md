# AutoShop Agent CLI 指令文档

适用版本：`autoshop-agent.exe v0.8.43`。

本文是当前 CLI 的使用文档，只记录已经存在的指令、推荐工作流、JSON 映射和能力边界，不记录开发计划。正常工程内容编辑统一走 `workspace export` / `workspace apply`，不要为变量、结构体、FB/FC、模块参数等再绕开 workspace 增加零散编辑指令。

## 1. 首选工作流

### 1.1 固定工程映射目录

在 `D:\program\PLC` 当前工作区，固定使用：

```text
D:\program\PLC\AutoShopAgentInterfaceWork\current-export
```

临时验证目录只放在：

```text
D:\program\PLC\AutoShopAgentInterfaceWork\archive
```

不要在 `D:\program\PLC` 根目录继续生成 `project001-*` 目录，也不要把 workspace、smoke、临时导出放进 `D:\program\PLC\AutoShopAgentInterface` skill 文件夹。

### 1.2 导出、修改、预检查、应用

```powershell
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace export --project D:\program\PLC\project001 --out D:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --allow-open-project --format json
```

`workspace apply` 写入后会立刻从工程文件回读并校验 SHA。JSON 输出中的 `verified=true` 和 `readBackSha256` 表示该项已经实际写回到磁盘工程文件。写回 POU、结构体等会同步 `.hcp` 工程索引，输出中的 `kind=project-index` 表示索引也被更新。

### 1.3 AutoShop UI 刷新边界

外部写回后，AutoShop 已打开窗口不一定立即刷新。ST/普通树节点可用 `--refresh`、`ui refresh` 或 `ui refresh-path` 关闭并重开窗口。变量表、模块配置、运动轴等工程级缓存经常需要关闭工程再重新打开工程才能在 AutoShop 里看到磁盘更新。

工程级刷新拆成两步：

```powershell
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui close-project --project D:\program\PLC\project001 --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui restore-project --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

当前用户使用电脑时不要执行会弹窗、切前台或输入键鼠的 UI 命令。`ui screenshot` 使用 Win32 `PrintWindow`，通常不会切到前台；目标最小化时可用 `--restore-offscreen` 临时移到屏幕边缘截图再最小化回去。

## 2. 通用格式和参数

```text
autoshop-agent.exe <command> [subcommand] [flags]
```

常用通用参数：

| 参数 | 说明 |
| --- | --- |
| `--config <path>` | JSON 配置路径，优先级高于 `AUTOSHOP_AGENT_CONFIG`。 |
| `--project <dir|file>` | 工程目录或工程文件。 |
| `--project-text-encoding <encoding>` | 覆盖工程 ST 文本编码；当前 `project001` 默认 `gb2312`。 |
| `--profile <name>` | 配置文件中的连接配置名。 |
| `--backend simulator|hardware` | 后端。默认 `simulator`；`hardware` 当前会拒绝执行。 |
| `--format text|json|ndjson` | 输出格式。自动化调用优先用 `json`。 |
| `--dry-run` | 只解析和验证，不写文件，不影响 AutoShop 或 PLC。 |
| `--allow-open-project` | AutoShop 可能打开同一工程时仍允许文件写回。 |
| `--no-backup` | 不生成备份；默认会备份被覆盖的工程文件。 |
| `--force` | 允许覆盖已有导出或忽略导出后工程源文件变化等保护。 |
| `--refresh` | 写回后尝试刷新相关 AutoShop 窗口。 |
| `--yes` | 对模拟目标命令进行非交互确认。 |
| `--timeout` / `--timeout-ms` | 超时时间；不同命令使用字符串或毫秒参数。 |

默认配置路径：

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

## 3. Workspace 映射文件

导出的 workspace 按 AutoShop 工程树排布。普通文件编辑只改 workspace 里的 `.st.txt` 或 JSON，再统一 `workspace apply`。

| AutoShop 树节点 | workspace 文件 | 编辑方式 |
| --- | --- | --- |
| 编程/程序块 | `编程/程序块/*.st.txt` | 编辑既有程序块 ST 正文。 |
| 编程/程序块 | `编程/程序块/*.pou.json` | 新增程序块、子程序或中断；`type=program|subprogram|interrupt`。 |
| 编程/功能块(FB) | `编程/功能块(FB)/*.pou.json` | 新增 FB；`type=fb`，会创建 `.FB` 并注册 `FileType=81`、`ProgType=7`。 |
| 编程/函数(FC) | `编程/函数(FC)/*.pou.json` | 新增 FC；`type=fc`，会创建 `.FC` 并注册 `FileType=82`、`ProgType=8`。 |
| 全局变量/变量表 | `全局变量/变量表/变量表.gvt.json` | 编辑 `variables` 数组；不要手工改 `.gvt`。 |
| 全局变量/结构体 | `全局变量/结构体/*.stru.json` | 编辑 `definition.members`；新增符合格式的 JSON 可创建结构体。 |
| 全局变量/功能块实例 | `全局变量/功能块实例/功能块实例.fbi.json` | 编辑 `instances`。 |
| 配置/输入滤波 | `配置/输入滤波/_node.config.json` | 优先改 `inputFilter.parameters`。 |
| 配置/模块配置 | `配置/模块配置/_node.config.json` | 优先改 `moduleConfig.modules` 和每槽位 `moduleParameters`。 |
| 配置/运动控制轴 | `配置/运动控制轴/_node.config.json` | 优先改 `motionAxis.axes[].parameters`。 |
| 配置/EtherCAT | `配置/EtherCAT/_node.config.json` | 只改已确认可写的 `ethercat.parameters`。 |
| 配置/EtherNet/IP | `配置/EtherNet/IP/_node.config.json` | 改 `ethernetIP` 下的标签、连接和 I/O 数据集。 |
| 其他配置节点 | `配置/<节点名>/_node.config.json` | 语义字段不存在时才改 `files[].contentHex` 或 `files[].contentBase64`。 |

Windows 保留设备名会使用安全目录名，例如 AutoShop 树里的 `配置/COM0` 在 workspace 中是 `配置/COM0_/_node.config.json`，JSON 内 `treePath` 仍保留原始树路径。

## 4. 语义 JSON 字段

### 4.1 POU 定义

新增 `*.pou.json` 使用：

```json
{
  "format": "autoshop-agent-pou-definition.v1",
  "kind": "pou-definition",
  "name": "JSON_FB_001",
  "type": "fb",
  "language": "litest",
  "encoding": "utf8",
  "sourceRelative": "JSON_FB_001.FB",
  "text": "VAR\n    t1 : BOOL := OFF;\nEND_VAR\n"
}
```

`workspace apply` 会创建对应 `.ST`、`.FB` 或 `.FC` 容器，维护 `folder.txt`，并同步 `.hcp` 工程索引。`pou add` 是底层兼容/诊断入口，不是推荐新增流程。

### 4.2 全局变量表

`变量表.gvt.json` 使用：

```json
{
  "format": "autoshop-agent-global-variable-table.v1",
  "kind": "global-variable-table",
  "variables": [
    {
      "name": "stubid",
      "dataType": "BOOL",
      "initialValue": "OFF",
      "powerRetain": "保持",
      "networkAccess": "私有",
      "comment": ""
    }
  ]
}
```

支持已验证类型：`BOOL`、`BYTE`、`INT`、`DINT`、`REAL`、`ARRAY`、`IP`、`STRING` / `STRING<...>`、自定义结构体、以 `_s` / `_u` 开头的系统结构/联合类型。`powerRetain` 对应“掉电保持”，使用 `保持|不保持`；`networkAccess` 对应“网络公开”，使用 `私有|公有|输入|输出`。

### 4.3 结构体和 FB 实例

结构体 JSON 的关键字段是 `definition.members`，可创建和修改自定义结构体成员。新增结构体时，`sourceRelative` 指向新的 `.stru` 文件，`workspace apply` 会注册 `.hcp` 中 `FileType=31`。

功能块实例 JSON 的关键字段是 `instances`。编辑后由 `workspace apply` 重建 `.fbi`。

### 4.4 输入滤波

`inputFilter.parameters` 当前已确认字段：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `normalX0ToX7Ms` | 普通输入滤波 `X0-X7`，单位 `ms`。 |
| `highSpeedX0ToX3_100ns` | 高速输入滤波 `X0-X3`，单位 `100ns`。 |
| `highSpeedX4ToX7Us` | 高速输入滤波 `X4-X7`，单位 `us`。 |

### 4.5 模块配置

`moduleConfig.modules` 是槽位数组。常用字段：

| 字段 | 说明 |
| --- | --- |
| `slot` | 机槽号。 |
| `model` | 模块型号，例如 `GL10(AM600)-4DA`。已知 GL10 样本可只填型号生成默认参数。 |
| `identity` / `moduleTypeCode` / `instance` | AutoShop 私有模块标识。 |
| `ioSignals` | 已有 X/Y 地址映射；可改地址，数量必须与该模块参数中地址字段一致。 |
| `moduleParameters` | 模块内部页面参数。4DA/4AD 是 4 个通道页；8TC/4TC/4PT 是通道组页数组。 |
| `parametersHex` | 未完全拆解时的保真兜底字节。 |

已按样本映射的模块包括 `GL10(AM600)-1600END`、`GL10(AM600)-3200END`、`GL10(AM600)-0032ETN`、`GL10(AM600)-4DA`、`GL10(AM600)-4AD`、`GL10(AM600)-8TC`、`GL10(AM600)-4TC`、`GL10(AM600)-4PT`。已确认字段可以语义编辑；未知私有位域保留 `rawCode` 或 `parametersHex`。

### 4.6 EtherCAT

`ethercat.parameters` 当前只承诺写回常规设置：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `cycleTimeUs` | 分布式时钟循环时间，单位 `us`。 |
| `syncOffsetPercent` | 同步偏移，单位 `%`。 |
| `autoRestartSlave` | 自动重启从站。 |
| `aliasEnabled` | 别名模式使能。 |

`ethercat.records` 里的 `parameter_0x...` 私有记录只读，`editable=false`。状态页里的循环时间、执行时间、丢帧次数等是在线任务监控值，不作为离线工程配置写回。

### 4.7 运动控制轴

运动轴位于 `motionAxis.axes`。当前支持修改既有轴参数，并同步 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`；新增/删除轴暂不承诺。优先编辑每个轴的 `parameters`，`uiRecords` / `compilerRecords` 只用于底层诊断或未命名字段回写。

常用字段：

| 字段 | 含义 |
| --- | --- |
| `virtualAxisMode` | 基本设置“虚轴模式”。 |
| `autoMappingEnabled` | 基本设置“自动映射”。 |
| `encoderMode` | `增量模式|绝对模式`。写回时同步可见 UI 记录、`encoderModeEffective` 和 `encoderModeLinkedFlag`。 |
| `axisMotionMode` | `线性模式|旋转模式`。 |
| `softwareLimitEnabled` | 软件限位使能。 |
| `ignoreLimitAfterErrorStop` | 由 `encoderMode` / `axisMotionMode` 改动时按 AutoShop 样本联动归一化：增量或旋转为 `true`，绝对+线性为 `false`。 |
| `reverseDirection` | 单位换算页“反向”；同步可见复选框位和联动标志。 |
| `gearDeviceEnabled` | 单位换算页“使用变速装置”。 |
| `pulsesPerRevolution` | 十进制数；AutoShop 里的 `16#1000000` 对应 JSON `16777216`。 |
| `homeOriginSignal` / `homeZSignal` / `homePositiveLimit` / `homeNegativeLimit` | `未分配|使用|不使用`。正负限位不能同时为 `使用`。 |
| `homeReturnDirection` / `homeInputDetectionDirection` | `未分配|正向|负向`。 |
| `homeMethodNumber` | 对已由样本确认的下拉项组合自动同步；未知组合不猜测。 |

AutoShop 手动保存可能保留旧的 `encoderModeLegacy` compilerRecord。语义 `apply` 不强行改这个旧编译记录，除非用户明确编辑底层 `compilerRecords`。

### 4.8 EtherNet/IP

`ethernetIP` 当前映射：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `producerTags` | 生产者标签。 |
| `serverMessageTags` | 服务消息标签。 |
| `adapter.connections` | EtherNet/IP Adapter 连接，包含 O->T/T->O 实例 ID 和大小。 |
| `adapter.connections[].outputDatasets` | 输出数据集。 |
| `adapter.connections[].inputDatasets` | 输入数据集。 |

`workspace apply` 会重建 `EIP.dat` 并在原文件带有效尾部 CRC32 时重算校验；`EIP.data`、`EIP.datBAK`、`SYS_EIP.eIPgvt` 仍作为真实成员文件保留在 `files` 中。

## 5. 完整指令索引

### 5.1 config

```powershell
autoshop-agent.exe config init [--config path] [--project dir] [--autoshop-exe path] [--force]
autoshop-agent.exe config show [--config path] [--format json]
autoshop-agent.exe config validate [--config path]
autoshop-agent.exe config get <key> [--config path]
autoshop-agent.exe config set <key> <value> [--config path]
autoshop-agent.exe config profile add <name> --transport ethernet --ip <ip> [--port <port>]
autoshop-agent.exe config profile add <name> --transport usb
autoshop-agent.exe config profile list
autoshop-agent.exe config profile remove <name>
```

### 5.2 workspace

```powershell
autoshop-agent.exe workspace export --project <dir> --out <workspace-dir> [--force] [--format json]
autoshop-agent.exe workspace apply --project <dir> --in <workspace-dir> [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
```

### 5.3 project 和 project node

```powershell
autoshop-agent.exe project info --project <dir|hcp|hcpp|updown> [--format json]
autoshop-agent.exe project tree --project <dir> [--format json]
autoshop-agent.exe project check --project <dir> [--strict] [--format json]
autoshop-agent.exe project backup --project <dir> --out <zip|dir> [--format json]
autoshop-agent.exe project archive pack --project <dir> --out <zip> [--format json]
autoshop-agent.exe project archive unpack --in <zip> --out <dir> [--format json]
autoshop-agent.exe project compare --left <project> --right <project|target> [--detail] [--format json]
autoshop-agent.exe project node list --project <dir> [--category program|config|monitor|report|trace|variable|all] [--format json]
autoshop-agent.exe project node info --project <dir> --name <node> [--format json]
autoshop-agent.exe project node export --project <dir> --name <node> --out <path> [--as auto|binary|json|zip] [--format json]
autoshop-agent.exe project node import --project <dir> --name <node> --in <path> [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
autoshop-agent.exe project node refresh --project <dir> --name <node> [--format json]
```

`project node` 是节点级诊断/兼容入口。能用 workspace JSON 表达的内容，优先走 `workspace export/apply`。

### 5.4 pou

```powershell
autoshop-agent.exe pou list --project <dir> [--format json]
autoshop-agent.exe pou show --project <dir> --name MAIN [--format json]
autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt [--format json]
autoshop-agent.exe pou export-all --project <dir> --out <dir> [--format json]
autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--dry-run] [--allow-open-project] [--refresh] [--format json]
autoshop-agent.exe pou add --project <dir> --name SBR_002 --type program|subprogram|interrupt|fb|fc [--language litest] [--text <litest>] [--dry-run] [--allow-open-project] [--no-backup] [--format json]
autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW [--format json]
autoshop-agent.exe pou remove --project <dir> --name SBR_002 [--format json]
```

`pou rename` 和 `pou remove` 当前只返回安全计划，不实际改工程。新增 POU 的推荐方式仍是在 workspace 中新增 `*.pou.json` 后 `workspace apply`。

### 5.5 st

```powershell
autoshop-agent.exe st format --in source.st --out source.formatted.st
autoshop-agent.exe st lint --in source.st [--target h5u|easy] [--firmware <version>] [--format json]
autoshop-agent.exe st parse --in source.st [--format json]
autoshop-agent.exe st symbols --in source.st [--format json]
autoshop-agent.exe st refs --in source.st --symbol <name> [--format json]
autoshop-agent.exe st scaffold mb-master --out example.st
autoshop-agent.exe st scaffold fb-call --name <FB> --out call.st
autoshop-agent.exe st instruction search <keyword> [--format json]
autoshop-agent.exe st instruction show <name> [--format json]
```

### 5.6 var 和 var table

```powershell
autoshop-agent.exe var list --project <dir> [--scope global|local|system] [--format json]
autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json [--format json]
autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace] [--format json]
autoshop-agent.exe var bind --project <dir> --name <var> --device D100 [--format json]
autoshop-agent.exe var validate --project <dir> [--format json]
autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info] [--format json]
autoshop-agent.exe var system show --project <dir> --name _SYS_COM [--format json]
autoshop-agent.exe var system export --project <dir> --name _SYS_COM --out _SYS_COM.svt [--format json]
autoshop-agent.exe var system import --project <dir> --name _SYS_COM --in _SYS_COM.svt [--dry-run] [--allow-open-project] [--refresh] [--format json]
autoshop-agent.exe var system refresh --project <dir> --name _SYS_COM [--format json]
autoshop-agent.exe var table list --project <dir> [--category system|global|internal|all] [--all] [--format json]
autoshop-agent.exe var table info --project <dir> --name variable|device|struct|fb-instance|_SYS_COM [--format json]
autoshop-agent.exe var table export --project <dir> --name variable --out 变量表.gvt [--as binary|json|hex|base64] [--format json]
autoshop-agent.exe var table import --project <dir> --name variable --in 变量表.gvt [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
autoshop-agent.exe var table refresh --project <dir> --name variable [--format json]
```

变量内容编辑不要用 `var table import` 直接替换私有二进制；优先改 workspace 中的 `variables`、`definition.members`、`instances`。

### 5.7 build

```powershell
autoshop-agent.exe build check --project <dir> [--format json]
autoshop-agent.exe build diagnostics --project <dir> [--format json]
autoshop-agent.exe build compile --project <dir> [--clean] [--backend simulator] [--format json]
autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init] [--backend simulator] [--format json]
autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init] [--backend simulator] [--format json]
```

当前 `compile/down/updown` 是 simulator 后端产物，不等同于 AutoShop 官方私有编译器生成的可下载文件。

### 5.8 target / online / monitor

```powershell
autoshop-agent.exe target scan [--transport ethernet|usb] [--backend simulator] [--format json]
autoshop-agent.exe target connect --profile <name> [--backend simulator] [--format json]
autoshop-agent.exe target info --profile <name> [--format json]
autoshop-agent.exe target login --profile <name> [--password <value>] [--format json]
autoshop-agent.exe target logout --profile <name> [--format json]
autoshop-agent.exe target run --profile <name> [--yes] [--format json]
autoshop-agent.exe target stop --profile <name> [--yes] [--format json]
autoshop-agent.exe target mode --profile <name> [--format json]
autoshop-agent.exe target download --profile <name> --project <dir> [--yes] [--format json]
autoshop-agent.exe target upload --profile <name> --out <dir|updown> [--format json]
autoshop-agent.exe target download-file --profile <name> --in <down|updown> [--yes] [--format json]
autoshop-agent.exe target upload-updown --profile <name> --out <file.updown> [--format json]
autoshop-agent.exe online enter --profile <name> --project <dir> [--format json]
autoshop-agent.exe online status --profile <name> [--format json]
autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes] [--format json]
autoshop-agent.exe online commit --profile <name> [--yes] [--format json]
autoshop-agent.exe online exit --profile <name> [--format json]
autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]
autoshop-agent.exe monitor read --profile <name> --device D100 [--format json]
autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes] [--format json]
autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json [--format json]
autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes] [--format json]
autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json [--format json]
autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes] [--format json]
```

这些命令当前只操作本地模拟状态，不连接、不扫描、不运行、不停止、不下载、不上传真实 PLC。显式传 `--backend hardware` 会失败并提示硬件后端尚未实现。

### 5.9 trace / diagnose

```powershell
autoshop-agent.exe trace list --project <dir> [--format json]
autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST [--format json]
autoshop-agent.exe trace start --profile <name> --name <trace> [--format json]
autoshop-agent.exe trace stop --profile <name> --name <trace> [--format json]
autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv [--format json]
autoshop-agent.exe trace remove --project <dir> --name <trace> [--format json]
autoshop-agent.exe diagnose target --profile <name> [--format json]
autoshop-agent.exe diagnose logs --profile <name> --out logs.json [--format json]
autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system] [--format json]
autoshop-agent.exe diagnose project --project <dir> [--format json]
autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip [--format json]
```

`trace` 当前是本地侧车定义和导出，不启动真实 PLC 采样。

### 5.10 comm / motion

```powershell
autoshop-agent.exe comm serial show --project <dir> [--format json]
autoshop-agent.exe comm serial set --project <dir> --port COM1 --baud 9600 --data-bits 8 --parity none --stop-bits 1 [--format json]
autoshop-agent.exe comm modbus-rtu master add --project <dir> --name <name> --port COM1 --addr <id> [--format json]
autoshop-agent.exe comm modbus-tcp master add --project <dir> --name <name> --ip <ip> --port 502 [--format json]
autoshop-agent.exe comm ethernet show --project <dir> [--format json]
autoshop-agent.exe comm ethernet set-ip --profile <name> --ip <ip> --mask <mask> --gateway <gateway> [--yes] [--format json]
autoshop-agent.exe comm can show --project <dir> [--format json]
autoshop-agent.exe comm canopen import-eds --project <dir> --in <file.eds> [--format json]
autoshop-agent.exe comm ethercat import-xml --project <dir> --in <file.xml> [--format json]
autoshop-agent.exe comm ethercat scan --profile <name> [--format json]
autoshop-agent.exe comm ethercat status --profile <name> [--format json]
autoshop-agent.exe motion axis list --project <dir> [--format json]
autoshop-agent.exe motion axis add --project <dir> --name Axis1 --type ethercat|pulse [--format json]
autoshop-agent.exe motion axis set --project <dir> --name Axis1 --param <key=value> [--format json]
autoshop-agent.exe motion axis status --profile <name> --name Axis1 [--format json]
autoshop-agent.exe motion group list --project <dir> [--format json]
autoshop-agent.exe motion group add --project <dir> --name Group1 --axes Axis1,Axis2 [--format json]
autoshop-agent.exe motion cam import --project <dir> --name Cam1 --in cam.csv [--format json]
autoshop-agent.exe motion cam export --project <dir> --name Cam1 --out cam.csv [--format json]
autoshop-agent.exe motion hsc list --project <dir> [--format json]
autoshop-agent.exe motion hsc add --project <dir> --name Counter1 --mode linear|rotary [--format json]
```

这些组当前是 simulator / 本地侧车能力。真实工程配置优先通过 workspace 中的配置 JSON 修改。

### 5.11 ui

```powershell
autoshop-agent.exe ui windows [--format json]
autoshop-agent.exe ui tree [--format json]
autoshop-agent.exe ui refresh --program MAIN [--format json]
autoshop-agent.exe ui refresh-path --path "全局变量/变量表" [--title 变量表] [--format json]
autoshop-agent.exe ui close-project --project <dir> [--project-file <hcp|hcpp>] [--autoshop-exe <path>] [--state project-state.json] [--timeout-ms 20000] [--dry-run] [--format json]
autoshop-agent.exe ui restore-project [--project <dir>] [--state project-state.json] [--project-file <hcp|hcpp>] [--autoshop-exe <path>] [--timeout-ms 20000] [--dry-run] [--format json]
autoshop-agent.exe ui refresh-project --project <dir> [--dry-run] [--format json]
autoshop-agent.exe ui close --program MAIN [--format json]
autoshop-agent.exe ui open --program MAIN [--format json]
autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" [--title _SYS_COM] [--format json]
autoshop-agent.exe ui focus --program MAIN [--format json]
autoshop-agent.exe ui screenshot --out autoshop.png [--format json]
autoshop-agent.exe ui screenshot --title 变量表 --out var-table.png [--format json]
autoshop-agent.exe ui screenshot --program MAIN --out main-editor.png [--client] [--format json]
autoshop-agent.exe ui screenshot --title 变量表 --restore-offscreen --out var-table.png [--offscreen-visible 4] [--format json]
autoshop-agent.exe ui screenshot --hwnd 0x1234 --out window.png [--allow-minimized] [--format json]
```

`ui focus` 会切前台；`ui open` / `ui refresh` / `ui close-project` / `ui restore-project` 可能操作 AutoShop 界面。用户正在使用电脑时不要执行这些命令，除非用户明确同意。

### 5.12 doc

```powershell
autoshop-agent.exe doc sources [--format json]
autoshop-agent.exe doc outline [--manual programming|instruction|user|autoshop|all] [--format json]
autoshop-agent.exe doc search <keyword> [--manual programming|instruction|user|autoshop|all] [--format json]
autoshop-agent.exe doc command-set [--out AutoShopCliCommands.md] [--format json]
```

`doc command-set` 输出的内容与本文件同源，用于重新生成指令文档。

## 6. 兼容别名

旧入口仍可用，但新流程应优先使用完整命令：

```powershell
autoshop-agent.exe list --project <dir> [--json]
autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
autoshop-agent.exe refresh --program MAIN
autoshop-agent.exe windows [--json]
```

## 7. 验收建议

文件层编辑的最小验收顺序：

1. `workspace apply --dry-run --format json`，确认没有格式错误、冲突或只读字段修改。
2. 正式 `workspace apply --format json`，检查每个变更项的 `verified=true`。
3. 重新 `workspace export --force` 到固定目录，读取 JSON 确认语义字段已回读为预期值。
4. 如需 AutoShop 画面同步，由用户手动关闭/打开工程，或在用户同意时执行 `ui close-project` / `ui restore-project`。

当前没有 PLC 真机后端。所有真机相关指令只能作为接口占位和离线测试入口使用。
