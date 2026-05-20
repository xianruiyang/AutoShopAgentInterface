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
- 文件编辑主流程只用 `workspace export` 和 `workspace apply`。先导出成按 AutoShop 工程树排布的文件夹，再修改文件夹，最后应用回工程。
- `workspace apply` 写回后会自动回读工程文件并校验 SHA；JSON 输出里应检查 `verified=true` 和 `readBackSha256`。输出中的 `kind=project-index` 表示 CLI 同步写入了 `.hcp` 工程索引。
- `pou add` 可新增 LiteST POU：创建 `.ST` 容器，更新 `folder.txt` 的 `PROG`/`FB`/`FC` 区域，并同步 `.hcp` 中 `FileType=80` 的 POU 登记；workspace 里的 `编程/程序块`、`编程/功能块(FB)`、`编程/函数(FC)` 下现有 `.st.txt` 用于替换对应 `.ST` 容器中的 LiteST 文本块。
- 配置、监控表、交叉引用表、元件使用表等未解析的私有二进制内容导出为 JSON 包装文件；全局变量表 `变量表.gvt` 若能识别，会导出为专用语义 JSON，`variables` 是可直接编辑的变量数组。`STRING<128>`、结构体、数组等带显式 `dataType` 的变量由 CLI 写入记录扩展，可以在 `variables` 中按需要排序。变量行支持 `powerRetain`=`保持|不保持` 和 `networkAccess`=`私有|公有|输入/输出`，对应 AutoShop 变量表中的掉电保持和网络公开列。
- `全局变量/结构体/*.stru.json` 的 `definition.members` 可编辑自定义结构体成员；在该目录新增符合 `autoshop-agent-struct-definition.v1` 的 `*.stru.json` 后，`workspace apply` 会创建新的 `.stru` 自定义结构体文件，并同步维护 `.hcp` 中 `FileType=31` 的结构体登记。若工程里已有未登记的 `.stru`，`workspace apply` 也会补齐工程索引。`全局变量/功能块实例/功能块实例.fbi.json` 的 `instances` 可编辑功能块实例。它们都通过 `workspace apply` 重建 AutoShop 私有二进制文件。
- `pou`、`var table`、`project node` 保留为底层/兼容命令；正常文件编辑优先使用 workspace。
- 外部写回后，AutoShop 已打开编辑窗口不会自动刷新；ST/普通树节点可用 `workspace apply --refresh`、`ui refresh --program <name>`、`ui refresh-path --path <tree-path>` 或旧别名 `refresh --program <name>` 关闭并重新打开对应窗口。变量表等工程级缓存需要用 `ui refresh-project`：先记录当前工程、已打开窗口和活动窗口，再关闭工程、重新打开工程、恢复窗口和焦点。
- `ui screenshot` 使用 Win32 `PrintWindow` 按窗口句柄输出 PNG，不会把 AutoShop 切到前台。目标窗口最小化时使用 `--restore-offscreen`：CLI 会把 AutoShop 临时恢复到虚拟屏幕右下角几乎屏幕外，截图后若原来是最小化则立即最小化回去。

## 常用命令

导出工程 workspace，修改后应用回工程：

```powershell
.\scripts\autoshop-agent.exe workspace export --project D:\program\PLC\project001 --out D:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
.\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
.\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --allow-open-project --refresh
```

全局变量表位于 `全局变量/变量表/变量表.gvt.json`，优先编辑其中的 `variables` 数组，不要手工编辑 `.gvt` 或伪造 `contentBase64`。已按当前样本验证 BOOL、BYTE、INT、DINT、REAL、ARRAY、IP、STRING/STRING<...>、自定义结构体、以 _s/_u 开头的系统结构/联合类型，以及 `powerRetain` 和 `networkAccess`。

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
.\scripts\autoshop-agent.exe ui refresh-project --project D:\program\PLC\project001 --dry-run --format json
.\scripts\autoshop-agent.exe ui refresh-project --project D:\program\PLC\project001 --format json
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
