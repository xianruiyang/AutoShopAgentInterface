# AutoShop Agent CLI 指令文档

适用版本：`autoshop-agent.exe` v0.4.0。

可执行文件：

```text
scripts/autoshop-agent.exe
```

本文只记录当前 CLI 的使用方式、能力边界和安全约束，不记录开发计划。

## 能力边界

- 默认后端为 `simulator`。涉及 PLC、在线监控、通讯扫描、运动控制和构建交付的命令会执行并保存模拟状态或生成模拟文件，但不会连接、扫描、运行、停止、下载、上传或写入真实 PLC。
- 显式指定 `--backend hardware` 时，当前版本会拒绝执行并提示硬件后端尚未实现。
- `.ST` 写回只支持既有 POU 容器。`pou add/remove/rename` 只输出结构化计划，不修改 AutoShop 工程元数据。
- 外部写回后，AutoShop 已打开的编辑窗口不会自动刷新。需要执行 `ui refresh --program <name>` 或在 `pou import` 时加 `--refresh`。
- `project backup` 会读取工程文件。如果 AutoShop 独占锁定 `.hcp` 等文件，备份可能失败，应关闭 AutoShop 或对离线副本操作。

## 通用格式

```powershell
autoshop-agent.exe <command> [subcommand] [flags]
```

通用参数：

```text
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

## `config`

管理持久配置和连接配置。

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

用户机器相关路径、UI 文本和连接配置都应写入 JSON 配置，不写死安装路径。

## `project`

检查、备份、比较和归档工程。

```powershell
autoshop-agent.exe project info --project <dir|hcp|hcpp|updown>
autoshop-agent.exe project tree --project <dir> [--format json]
autoshop-agent.exe project check --project <dir> [--strict]
autoshop-agent.exe project backup --project <dir> --out <zip|dir>
autoshop-agent.exe project archive pack --project <dir> --out <zip>
autoshop-agent.exe project archive unpack --in <zip> --out <dir>
autoshop-agent.exe project compare --left <project> --right <project|target> [--detail]
```

`archive pack/unpack` 使用 `autoshop-agent` 自有 ZIP 归档格式，不声称等同 AutoShop 官方 `.hclib`。

## `pou`

列出、查看、导出和写回既有 POU。

```powershell
autoshop-agent.exe pou list --project <dir> [--format json]
autoshop-agent.exe pou show --project <dir> --name MAIN
autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt
autoshop-agent.exe pou export-all --project <dir> --out <dir>
autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--dry-run] [--refresh]
autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW
autoshop-agent.exe pou add --project <dir> --name SBR_002 --type main|subprogram|interrupt|fb|fc --language litest|ld|sfc
autoshop-agent.exe pou remove --project <dir> --name SBR_002
```

如果 AutoShop 正打开同一工程，写回默认拒绝。用户确认接受风险时添加 `--allow-open-project`。

## `st`

处理 LiteST 文本。

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

当前 `lint/parse/symbols/refs` 是保守文本分析，不替代 AutoShop 编译。

## `var`

查看和校验变量、软元件引用和系统变量文件。

```powershell
autoshop-agent.exe var list --project <dir> [--scope global|local|system]
autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json
autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace]
autoshop-agent.exe var bind --project <dir> --name <var> --device D100
autoshop-agent.exe var validate --project <dir>
autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info]
```

`var import/bind` 在默认后端中写入 simulator 状态，不修改 AutoShop 变量表。

## `build`

检查工程并在 simulator 后端生成构建交付模拟产物。

```powershell
autoshop-agent.exe build check --project <dir>
autoshop-agent.exe build compile --project <dir> [--clean] [--format json]
autoshop-agent.exe build diagnostics --project <dir> [--format json]
autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init] [--login-password <value>] [--set-password <value>]
```

当前版本不会调用真实 AutoShop 编译器或生成可用于真机下载的官方交付文件。

## `target`

使用 simulator 后端模拟 PLC 目标连接和生命周期操作。

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

`run`、`stop`、`download`、`download-file` 等危险操作在非交互自动化中应使用 `--yes` 明确确认。当前 simulator 不影响真实 PLC。

## `online`

使用 simulator 后端模拟在线修改流程。

```powershell
autoshop-agent.exe online enter --profile <name> --project <dir>
autoshop-agent.exe online status --profile <name>
autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes]
autoshop-agent.exe online commit --profile <name> [--yes]
autoshop-agent.exe online exit --profile <name>
autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]
```

## `monitor`

使用 simulator 后端读写软元件、观察采样和保存快照。

```powershell
autoshop-agent.exe monitor read --profile <name> --device D100
autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes]
autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json
autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes]
autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json
autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes]
```

`write/load/apply` 当前只改 simulator 状态。

## `trace`

管理本地 Trace 定义并在 simulator 后端模拟采样启动/停止。

```powershell
autoshop-agent.exe trace list --project <dir>
autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST
autoshop-agent.exe trace start --profile <name> --name <trace>
autoshop-agent.exe trace stop --profile <name> --name <trace>
autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv
autoshop-agent.exe trace remove --project <dir> --name <trace>
```

## `diagnose`

输出工程、目标和错误码诊断信息。

```powershell
autoshop-agent.exe diagnose target --profile <name> [--format json]
autoshop-agent.exe diagnose logs --profile <name> --out logs.json
autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system]
autoshop-agent.exe diagnose project --project <dir> [--format json]
autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip
```

`diagnose bundle` 生成支持包；含工程副本或日志时注意脱敏。

## `comm`

查看本地通讯配置文件，或在 simulator 后端记录通讯配置/扫描/状态操作。

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

## `motion`

在 simulator 后端记录运动轴、轴组、凸轮和高速计数器相关操作。

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

## `ui`

查看和刷新 AutoShop 窗口。

```powershell
autoshop-agent.exe ui windows
autoshop-agent.exe ui refresh --program MAIN
autoshop-agent.exe ui close --program MAIN
autoshop-agent.exe ui open --program MAIN
autoshop-agent.exe ui focus --program MAIN
autoshop-agent.exe ui tree --format json
```

UI 命令查找正在运行的 AutoShop 进程，不依赖固定安装目录。CLI 不自动处理未保存缓冲区弹窗。

## `doc`

查询 CLI 内置参考摘要。

```powershell
autoshop-agent.exe doc sources
autoshop-agent.exe doc outline --manual programming|instruction|user|autoshop
autoshop-agent.exe doc search <keyword> [--manual programming|instruction|all]
autoshop-agent.exe doc command-set --out AutoShopCliCommands.md
```

## 兼容别名

旧命令仍可用：

```powershell
autoshop-agent.exe list --project <dir>
autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
autoshop-agent.exe windows
autoshop-agent.exe refresh --program MAIN
```

对应关系：

```text
list       -> pou list
export     -> pou export 或 pou export-all
import     -> pou import
windows    -> ui windows
refresh    -> ui refresh
```
