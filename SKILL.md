---
name: autoshop-agent-interface
description: "当 Codex 需要通过随包 CLI 操作汇川 Inovance AutoShop Lite ST 工程时使用：检查工程、列出/导出/写回既有 ST 程序容器、分析 LiteST 文本、查询本地指令资料摘要、查看或刷新 AutoShop POU 窗口。当前 CLI 支持无 PLC 真机的离线开发流程；target、online、monitor、comm、motion 等真实设备相关命令默认使用 simulator 后端，不会连接或修改 PLC。"
---

# AutoShop Agent Interface

## 核心规则

优先使用随 skill 打包的 CLI：

```text
scripts/autoshop-agent.exe
```

除非需要维护这个可执行文件本身，否则不要重新实现 AutoShop 二进制 ST 解析或 Win32 窗口刷新逻辑。

这个目录只是已开发好的 skill 包。除非用户明确要求安装，否则不要把它复制或安装到 Codex 的 skill 目录，也不要修改 Codex 配置。

## 能力边界

- 当前版本面向无 PLC 真机环境，默认只做本地文件、LiteST 文本、AutoShop UI 窗口操作和安全的侧车文件。
- `target`、`online`、`monitor`、`comm`、`motion` 以及 `build compile/down/updown` 已有默认 `simulator` 后端实现，可执行并产出结构化状态或文件；不会扫描网段、连接 USB、RUN/STOP 真实 PLC、下载真实设备或写真实设备。
- 如显式指定 `--backend hardware`，当前版本会拒绝并提示硬件后端尚未实现；真机接入应复用同一命令接口。
- 写回 `.ST` 容器只支持既有程序文件；不要用 CLI 新增、删除或重命名 POU，除非后续已经明确工程元数据格式。
- `var table` 可对 AutoShop 工程树里的系统变量表、结构体、软元件表、功能块实例和变量表做表级内容操作：列出、信息、导出、导入替换和刷新。当前版本不逐行解析或改写这些私有二进制表。
- `project node` 可对 AutoShop 工程树里的编程、配置、变量表、监控表、交叉引用表、元件使用表和 Trace 节点做表级内容操作。当前版本不逐字段解析这些私有二进制配置文件。
- 外部写回后，AutoShop 已打开编辑窗口不会自动刷新；需要用 `ui refresh --program <name>` 或旧别名 `refresh --program <name>` 关闭并重新打开对应窗口。

## 常用命令

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

查看 AutoShop 窗口和工程树：

```powershell
.\scripts\autoshop-agent.exe ui windows --format json
.\scripts\autoshop-agent.exe ui tree --format json
```

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
