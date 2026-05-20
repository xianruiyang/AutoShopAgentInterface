---
name: autoshop-agent-interface
description: "当 Codex 需要通过随包 CLI 操作汇川 Inovance AutoShop Lite ST 工程时使用：列出现有 ST 程序容器、导出内嵌 ST 文本到 txt、从 txt 写回既有 .ST 文件、查看 AutoShop 已打开的 POU 窗口，或在外部写回后按名称关闭并重新打开 AutoShop POU 窗口。"
---

# AutoShop Agent Interface

## 核心规则

优先使用随 skill 打包的 CLI：

```text
scripts/autoshop-agent.exe
```

除非需要维护这个可执行文件本身，否则不要重新实现 AutoShop 二进制 ST 解析或 Win32 窗口刷新逻辑。

这个目录只是一个已开发好的 skill 包。除非用户明确要求安装，否则不要把它复制或安装到 Codex 的 skill 目录，也不要修改 Codex 配置。

## 快速命令

列出工程内 ST 容器：

```powershell
.\scripts\autoshop-agent.exe list --project D:\program\PLC\project001
```

导出单个程序到 txt：

```powershell
.\scripts\autoshop-agent.exe export --project D:\program\PLC\project001 --program MAIN --out D:\tmp\MAIN.st.txt
```

导出全部 ST 程序：

```powershell
.\scripts\autoshop-agent.exe export --project D:\program\PLC\project001 --out D:\tmp\st-export
```

从 txt 写回既有程序：

```powershell
.\scripts\autoshop-agent.exe import --project D:\program\PLC\project001 --program MAIN --in D:\tmp\MAIN.st.txt
```

如果 AutoShop 正在打开同一工程，并且用户明确接受风险，添加：

```text
--allow-open-project
```

写回后刷新 AutoShop 内已打开的 POU 窗口：

```powershell
.\scripts\autoshop-agent.exe import --project D:\program\PLC\project001 --program MAIN --in D:\tmp\MAIN.st.txt --allow-open-project --refresh
```

只刷新窗口：

```powershell
.\scripts\autoshop-agent.exe refresh --program MAIN
```

查看 AutoShop 当前打开的 POU 窗口：

```powershell
.\scripts\autoshop-agent.exe windows
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
  }
}
```

`autoShopExePath` 目前只为未来“自动启动 AutoShop”保留。当前 `list`、`export`、`import`、`refresh` 不依赖 AutoShop 安装路径。

## 参考资料

修改写回行为前，先读：

```text
references/AutoShopLiteStFormat.md
```

修改或排查窗口刷新行为前，先读：

```text
references/AutoShopUiRefresh.md
```

扩展 CLI 到当前已实现的 ST 导入导出和 UI 刷新之外前，先读：

```text
references/AutoShopCliCommandSetDesign.md
```
