---
name: autoshop-agent-interface
description: "Use when Codex needs to operate Inovance AutoShop Lite ST projects through the bundled CLI: list existing ST program containers, export embedded ST text to txt, import txt back into existing .ST files, inspect open AutoShop POU windows, or close and reopen an AutoShop POU window by name after external writeback."
---

# AutoShop Agent Interface

## Core Rule

Use the bundled CLI at `scripts/autoshop-agent.exe`. Do not reimplement AutoShop binary ST parsing or Win32 window refresh logic unless the executable itself needs maintenance.

This skill is a developed package only. Do not install it into a Codex skill directory unless the user explicitly asks.

## Quick Commands

List ST containers:

```powershell
.\scripts\autoshop-agent.exe list --project D:\program\PLC\project001
```

Export one program to txt:

```powershell
.\scripts\autoshop-agent.exe export --project D:\program\PLC\project001 --program MAIN --out D:\tmp\MAIN.st.txt
```

Export all ST programs:

```powershell
.\scripts\autoshop-agent.exe export --project D:\program\PLC\project001 --out D:\tmp\st-export
```

Import txt back into an existing program:

```powershell
.\scripts\autoshop-agent.exe import --project D:\program\PLC\project001 --program MAIN --in D:\tmp\MAIN.st.txt
```

If AutoShop is opening the same project and the user accepts the risk, add `--allow-open-project`.

Write back and refresh the opened POU window:

```powershell
.\scripts\autoshop-agent.exe import --project D:\program\PLC\project001 --program MAIN --in D:\tmp\MAIN.st.txt --allow-open-project --refresh
```

Refresh only:

```powershell
.\scripts\autoshop-agent.exe refresh --program MAIN
```

Inspect open AutoShop POU windows:

```powershell
.\scripts\autoshop-agent.exe windows
```

## Config

Default config path:

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

Use `AUTOSHOP_AGENT_CONFIG` or `--config` to override it.

Create or update config:

```powershell
.\scripts\autoshop-agent.exe config init --project D:\program\PLC\project001 --force
```

Relevant JSON fields:

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
    "projectTreeTitle": "<localized project tree pane title>",
    "programmingNode": "<localized programming node>",
    "programBlockNode": "<localized program block node>"
  }
}
```

`autoShopExePath` is reserved for future launch support. Current list/export/import/refresh operations do not depend on the AutoShop installation path.

## References

Read `references/AutoShopLiteStFormat.md` before changing writeback behavior.

Read `references/AutoShopUiRefresh.md` before changing or troubleshooting window refresh behavior.

Read `references/AutoShopCliCommandSetDesign.md` before expanding the CLI beyond the currently implemented ST import/export and UI refresh commands.
