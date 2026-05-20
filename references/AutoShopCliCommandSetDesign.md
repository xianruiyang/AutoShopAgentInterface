# AutoShop Agent CLI 指令集设计

状态：仅设计文档。本文中的目标命令不代表已经实现。

## 目标

设计一套面向 AutoShop Lite ST 开发的完整 CLI。未来 CLI 应支持可重复的工程开发流程，包括工程检查、源码编辑、编译验证、打包、下载、在线诊断、监控、Trace、通信配置、运动控制配置，以及外部写回后的 AutoShop UI 刷新。

当前可执行文件只覆盖小范围能力：ST 文本列出、导出、写回，AutoShop 已打开 POU 窗口枚举，以及按名称关闭再打开窗口。本文其余部分是目标接口，不是当前实现。

## 已分析资料

本机安装资料：

- `D:\software\AutoShop\Manual\AutoShop.chm`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U&Easy系列可编程逻辑控制器编程与应用手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U&Easy系列可编程逻辑控制器指令手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\Easy系列可编程逻辑控制器用户手册.PDF`
- `D:\software\AutoShop\Manual\H5U&Easy_Manual\H5U系列可编程逻辑控制器用户手册.pdf`

外部确认资料：

- Inovance H5U Series 产品页：`https://www.inovance.com/global/content/details_815_403258.html`
- Inovance Easy Series 产品页：`https://www.inovance.com/global/content/details_815_555452.html`
- Inovance Easy301 User Guide PDF：其中“More Documents”表列出 H5U/Easy 编程与应用指南、指令指南。
- Inovance H5U User Guide PDF：相关文档表列出 H5U 编程与应用指南。

## 文档结论

### 开发流程

编程与应用手册覆盖的典型流程包括：

- 以太网或 USB 通信连接。
- 新建工程和硬件组态。
- 编辑 `MAIN`。
- 编译程序。
- 可选的 PLC 登录。
- 下载程序。
- PLC 运行和停止。
- HMI 或在线监控。
- 在线修改模式。
- 程序扫描周期和 EtherCAT 任务周期设置。
- 工程档案打包和解压。
- Trace 监控变量与 Trace 数据导出。

因此未来 CLI 不能只停留在文件编辑层面，需要覆盖工程、构建、目标连接、下载上传、运行状态、在线修改、监控和归档。

### LiteST 源码模型

手册将 LiteST 描述为面向自动化系统的高级文本语言，语法类似 Pascal，包含变量、操作符、表达式、控制流程语句、FB/FC/子程序/中断调用，以及除 0、数组越界等异常处理行为。

指令手册将 LiteST 指令描述为“指令名、参数、返回值”结构，并区分：

- LD 与 LiteST 共用指令。
- LiteST 专用指令。
- 通信指令。
- 运动控制指令。
- 字符串和数组指令。
- 错误代码表。

因此 CLI 应包含语法感知的 `st` 命令和指令资料命令，而不是只做二进制容器导入导出。

### 在线操作与安全

手册覆盖 RUN/STOP、在线修改限制、登录密码、下载行为，以及供电、安全回路、通信故障等注意事项。

因此所有影响 PLC 或设备运行状态的命令都必须显式选择连接配置，默认应 dry-run 或要求确认；非交互场景必须使用明确的 `--yes`。

### 调试和诊断

手册覆盖 Trace、内存管理、工程比较、软件诊断、运行日志、错误代码、Modbus 错误、面板指示灯状态。

因此诊断和监控命令应提供稳定 JSON 输出，并保留原始导出数据，便于审计和复现。

### 打包和交付

编程与应用手册记录了 `.down` 和 `.updown`：

- `.down` 可由已编译工程生成，用于不打开原工程时下载。
- `.updown` 支持上传和下载，也可包含源工程用于后续编辑。
- 生成时涉及是否包含源代码、保持型变量处理、登录密码、修改登录密码等选项。

因此 CLI 需要有包生成命令；具体实现可能依赖 AutoShop 自动化或继续寻找编译器/打包入口。

## 全局约定

命令形式：

```powershell
autoshop-agent.exe <command> [subcommand] [flags]
```

通用参数：

```text
--config <path>              JSON 配置路径，优先级高于 AUTOSHOP_AGENT_CONFIG。
--project <dir|file>         工程目录或工程文件。
--profile <name>             配置文件中的连接配置名称。
--format text|json|ndjson    输出格式。默认 text，自动化场景使用 json。
--dry-run                    只解析和验证，不写文件，不影响 PLC 或 AutoShop。
--yes                        对危险操作进行非交互确认。
--timeout <duration>         超时时间，例如 30s 或 2m。
--log <path>                 写结构化运行日志。
--verbose                    输出更多细节。
--quiet                      只输出必要结果。
```

退出码：

```text
0   成功
1   通用错误
2   用法或配置错误
3   工程解析错误
4   编译或构建错误
5   目标连接错误
6   目标拒绝操作
7   AutoShop UI 自动化错误
8   校验或检查失败
9   不支持的工程特性
10  安全保护阻止操作
```

默认配置路径：

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

所有用户机器相关路径都应放在配置中，例如 AutoShop 可执行文件路径、编译器或工具路径、默认工程目录、连接配置、UI 标签、等待时间。代码里不要写死安装路径。

## 命令组设计

### 1. `config`

用途：创建、查看、校验持久配置。

```powershell
autoshop-agent.exe config init [--config path] [--project dir] [--autoshop-exe path] [--force]
autoshop-agent.exe config show [--config path] [--format json]
autoshop-agent.exe config validate [--config path]
autoshop-agent.exe config set <key> <value> [--config path]
autoshop-agent.exe config get <key> [--config path]
autoshop-agent.exe config profile add <name> --transport ethernet --ip <ip> [--port <port>]
autoshop-agent.exe config profile add <name> --transport usb
autoshop-agent.exe config profile list
autoshop-agent.exe config profile remove <name>
```

设计要点：

- 文件级命令不需要 `autoShopExePath`。
- `ui.projectTreeTitle`、`ui.programmingNode`、`ui.programBlockNode` 必须可配置，因为 AutoShop UI 文本会受语言和版本影响。

### 2. `project`

用途：检查和管理工程结构。

```powershell
autoshop-agent.exe project info --project <dir|hcp|hcpp|updown>
autoshop-agent.exe project tree --project <dir> [--format json]
autoshop-agent.exe project check --project <dir> [--strict]
autoshop-agent.exe project backup --project <dir> --out <zip|dir>
autoshop-agent.exe project archive pack --project <dir> --out <hclib>
autoshop-agent.exe project archive unpack --in <hclib> --out <dir>
autoshop-agent.exe project compare --left <project> --right <project|target> [--detail]
```

实现备注：

- `project info`、`project tree`、`project check` 可以从本地文件解析开始。
- `archive pack/unpack` 和完整比较可能需要 AutoShop 自动化或继续逆向 `.hclib`、`.hcp`、`.hcpp`。

### 3. `pou`

用途：管理 POU 和程序文本。

```powershell
autoshop-agent.exe pou list --project <dir> [--format json]
autoshop-agent.exe pou show --project <dir> --name MAIN
autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt
autoshop-agent.exe pou export-all --project <dir> --out <dir>
autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--backup] [--refresh]
autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW
autoshop-agent.exe pou add --project <dir> --name SBR_002 --type main|subprogram|interrupt|fb|fc --language litest|ld|sfc
autoshop-agent.exe pou remove --project <dir> --name SBR_002
```

实现备注：

- `list/show/export/export-all/import` 是当前或近期可实现范围，前提是只操作既有 `*.ST` 容器。
- `add/remove/rename` 属于未来能力，因为它们很可能需要同步更新 `.hcp` 和其他工程表。

### 4. `st`

用途：LiteST 源码级处理。

```powershell
autoshop-agent.exe st format --in source.st --out source.formatted.st
autoshop-agent.exe st lint --in source.st [--target h5u|easy] [--firmware <version>]
autoshop-agent.exe st parse --in source.st --format json
autoshop-agent.exe st symbols --in source.st --format json
autoshop-agent.exe st refs --in source.st --symbol <name>
autoshop-agent.exe st scaffold mb-master --out example.st
autoshop-agent.exe st scaffold fb-call --name <FB> --out call.st
autoshop-agent.exe st instruction search <keyword>
autoshop-agent.exe st instruction show <name> [--format json]
```

设计要点：

- `lint` 至少检查 LiteST 基本语法、注释、语句分号、控制结构配对、FB/FC 调用形式、软元件拼写、指令是否适用于目标和固件版本。
- `instruction search/show` 应从指令手册整理出的结构化资料生成，不能靠手写散文维护。

### 5. `var`

用途：变量和软元件表管理。

```powershell
autoshop-agent.exe var list --project <dir> [--scope global|local|system]
autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json
autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace]
autoshop-agent.exe var bind --project <dir> --name <var> --device D100
autoshop-agent.exe var validate --project <dir>
autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info]
```

实现备注：

- 需要继续解析 `.gvt`、`.svt`、`.gdt`、`.gdtx` 等变量表和元数据文件。

### 6. `build`

用途：编译和生成交付文件。

```powershell
autoshop-agent.exe build check --project <dir>
autoshop-agent.exe build compile --project <dir> [--clean] [--format json]
autoshop-agent.exe build diagnostics --project <dir> [--format json]
autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
```

实现备注：

- `compile` 可能可通过已安装编译器入口实现，但需要先确认稳定调用方式。
- `down/updown` 是手册记录的 AutoShop 功能。如果没有公开 CLI 入口，可能需要 AutoShop UI 自动化。

### 7. `target`

用途：连接 PLC、查看状态、控制生命周期。

```powershell
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
```

安全规则：

- `run`、`stop`、`download` 和密码相关操作在非交互模式必须要求 `--yes`。
- 下载前必须报告 PLC 当前是 RUN 还是 STOP。

实现备注：

- 需要发现通信协议，或安全驱动 AutoShop/HMI 已有流程。

### 8. `online`

用途：在线修改和在线比较。

```powershell
autoshop-agent.exe online enter --profile <name> --project <dir>
autoshop-agent.exe online status --profile <name>
autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes]
autoshop-agent.exe online commit --profile <name> [--yes]
autoshop-agent.exe online exit --profile <name>
autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]
```

设计要点：

- 手册列出了在线修改限制。CLI 在尝试在线提交前，必须验证补丁没有新增、删除、重命名程序文件，也没有修改不支持在线修改的属性。

### 9. `monitor`

用途：读写和观察变量、软元件、内存快照。

```powershell
autoshop-agent.exe monitor read --profile <name> --device D100
autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes]
autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json
autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes]
autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json
autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes]
```

实现备注：

- 需要 PLC 通信能力，或通过 AutoShop 内存管理功能自动化实现。

### 10. `trace`

用途：配置、启动、停止、导出 Trace。

```powershell
autoshop-agent.exe trace list --project <dir>
autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST
autoshop-agent.exe trace start --profile <name> --name <trace>
autoshop-agent.exe trace stop --profile <name> --name <trace>
autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv
autoshop-agent.exe trace remove --project <dir> --name <trace>
```

设计要点：

- 手册将 Trace 描述为带时间标记的变量历史记录功能，并要求停止采集后导出。CLI 应保留这个状态机。

### 11. `diagnose`

用途：收集错误和诊断证据。

```powershell
autoshop-agent.exe diagnose target --profile <name> [--format json]
autoshop-agent.exe diagnose logs --profile <name> --out logs.json
autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system]
autoshop-agent.exe diagnose project --project <dir> [--format json]
autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip
```

设计要点：

- `error-code` 应将程序错误、Modbus 通信错误、EtherCAT 故障、运动控制故障、系统诊断分成不同域。

### 12. `comm`

用途：查看和编辑通信配置。

```powershell
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
```

实现备注：

- 多数命令需要解析工程配置表，或通过 AutoShop 自动化执行。

### 13. `motion`

用途：支持运动控制、高速计数、插补、电子凸轮、电子齿轮相关流程。

```powershell
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
```

设计要点：

- 这些命令对应手册中的运动轴、PLCopen 状态机、轴参数、高速计数器、插补、总线编码器轴、电子凸轮和齿轮。
- 在工程文件格式完全明确前，先实现只读和校验功能，不急于开放写入。

### 14. `ui`

用途：AutoShop 窗口自动化。

```powershell
autoshop-agent.exe ui windows
autoshop-agent.exe ui refresh --program MAIN
autoshop-agent.exe ui close --program MAIN
autoshop-agent.exe ui open --program MAIN
autoshop-agent.exe ui focus --program MAIN
autoshop-agent.exe ui tree --format json
```

兼容别名：

```powershell
autoshop-agent.exe windows
autoshop-agent.exe refresh --program MAIN
```

设计要点：

- UI 命令可以依赖正在运行的 AutoShop 进程，但不能依赖固定安装路径。
- CLI 不得自动响应未保存编辑器缓冲区引发的弹窗。

### 15. `doc`

用途：暴露本地和生成的参考资料。

```powershell
autoshop-agent.exe doc sources
autoshop-agent.exe doc outline --manual programming|instruction|user|autoshop
autoshop-agent.exe doc search <keyword> [--manual programming|instruction|all]
autoshop-agent.exe doc command-set --out AutoShopCliCommandSetDesign.md
```

设计要点：

- 这不是官方手册替代品。
- 用于快速查找、命令规划和错误码映射。

## 当前命令兼容要求

保持以下现有命令可用：

```powershell
autoshop-agent.exe list --project <dir>
autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
autoshop-agent.exe windows
autoshop-agent.exe refresh --program MAIN
```

新增分层命令时保留别名：

```text
list       -> pou list
export     -> pou export 或 pou export-all
import     -> pou import
windows    -> ui windows
refresh    -> ui refresh
```

## 建议实现阶段

### 阶段 1：文件级开发

- `project info/tree/check`
- `pou list/show/export/export-all/import`
- `ui windows/refresh`
- `st parse/lint`，先做保守解析器
- `doc sources/outline/search`

### 阶段 2：工程元数据

- `var list/export/import/validate`
- `comm serial/ethernet show`
- 本地文件级 `project compare`
- 只有在 `.hcp` 和相关表明确后才实现 `pou add/remove/rename`

### 阶段 3：构建与打包

- `build compile`
- `build diagnostics`
- `build down`
- `build updown`

这一阶段依赖稳定的 AutoShop 编译/打包入口，或足够可靠的 UI 自动化。

### 阶段 4：PLC 目标操作

- `target scan/info/login/logout/run/stop`
- `target download/upload`
- `monitor read/write/watch`
- `trace start/stop/export`
- `diagnose target/logs/error-code`

这一阶段依赖通信协议发现，或安全驱动 AutoShop。

### 阶段 5：高级配置

- `comm modbus/canopen/ethercat`
- `motion axis/group/cam/hsc`
- `online enter/patch/commit/exit`

这类能力应先从只读和校验开始，再逐步开放写入。

## 第一版完整 CLI 的非目标

- 不静默执行 PLC RUN、STOP 或下载。
- 不自动点击 AutoShop 弹窗中的保存、覆盖、放弃。
- 在所有相关工程表未明确前，不做工程文件创建或删除。
- 默认不明文保存密码。
- 不声称生成代码可直接用于真实设备安全控制；用户必须自行审核程序并配置必要的外部安全回路。

## 后续实现验收标准

每个实现的命令都必须具备：

- `--help` 输出。
- 面向人的文本输出；自动化场景需要 JSON 输出。
- 对写入或影响目标的操作提供 dry-run。
- 结构化错误和稳定退出码。
- 可选运行日志。
- 在工程副本或模拟目标上的 smoke 测试。
- 同步更新本文档或后续命令参考文档。
