# AutoShop Agent CLI 指令文档

适用版本：autoshop-agent.exe v0.8.3。

本文只记录当前 CLI 的使用方式、能力边界和安全约束，不记录开发计划。

## 能力边界

- 默认后端为 simulator。涉及 PLC、在线监控、通讯扫描、运动控制和构建交付的命令会执行并保存模拟状态或生成模拟文件，但不会连接、扫描、运行、停止、下载、上传或写入真实 PLC。
- 显式指定 --backend hardware 时，当前版本会拒绝执行并提示硬件后端尚未实现。
- 文件编辑主流程是 workspace export 和 workspace apply：先把 AutoShop 工程按软件工程树导出成可编辑文件夹，修改文件夹里的 .st.txt 或 JSON，再统一应用回工程。
- workspace apply 实际写入后会立即从工程文件回读并比对内容 SHA；JSON 输出中的 verified=true 和 readBackSha256 表示该项已经回读确认。
- .ST 写回只支持既有 POU 容器。workspace 里的 编程/程序块/*.st.txt 会写回对应 .ST 容器的 LiteST 文本块。
- 配置、监控、交叉引用、元件使用表等私有二进制内容会以 JSON 包装文件导出，字段包含来源、SHA 和 contentBase64。全局变量/变量表/变量表.gvt 会额外导出 semanticType=global-variable-table-v5.03 和 globalVariableRows，可通过 JSON 槽位编辑已有样本格式的变量行。
- var table、project node、pou 等细粒度命令保留为底层/兼容命令；正常文件编辑优先使用 workspace export/apply。
- 外部写回后，AutoShop 已打开的编辑窗口不会自动刷新。需要执行 ui refresh --program <name>、ui refresh-path --path <tree-path>，或在 workspace apply / pou import 时加 --refresh。

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

导出的文件夹按 AutoShop 工程树排布。代码改 编程/程序块/*.st.txt；全局变量表改 全局变量/变量表/变量表.gvt.json 里的 globalVariableRows，保留 contentBase64 作为字节级兜底。写回前建议先执行 workspace apply --dry-run --format json。

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
    autoshop-agent.exe pou add --project <dir> --name SBR_002 --type main|subprogram|interrupt|fb|fc --language litest|ld|sfc
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
    autoshop-agent.exe ui close --program MAIN
    autoshop-agent.exe ui open --program MAIN
    autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" --title _SYS_COM
    autoshop-agent.exe ui focus --program MAIN
    autoshop-agent.exe ui tree --format json

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
