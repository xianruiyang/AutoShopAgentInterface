# AutoShop POU Window Refresh Notes

AutoShop keeps already-open ST/POU editor buffers in memory. After external `*.ST` writeback, the visible editor does not reload immediately.

The tested refresh flow is:

1. Find the running `AutoShop.exe` process.
2. Enumerate MDI child windows and find the POU whose title equals the requested program name.
3. Send `WM_CLOSE` to that MDI child.
4. Find the project tree under the `工程管理` pane.
5. Find the tree path `编程/程序块/<program>`.
6. Select and double-click that node.
7. Verify the POU window is open again.

The CLI does not click save/confirm dialogs. If the editor is dirty and AutoShop refuses to close it, the command must fail and report that user action is required.

Localized tree labels are configurable:

```json
{
  "ui": {
    "projectTreeTitle": "工程管理",
    "programmingNode": "编程",
    "programBlockNode": "程序块"
  }
}
```
