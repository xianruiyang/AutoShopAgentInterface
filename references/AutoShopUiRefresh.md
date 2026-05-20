# AutoShop POU 窗口刷新记录

AutoShop 会把已经打开的 ST/POU 编辑器内容保留在内存中。外部写回 `*.ST` 后，可见编辑器不会立即从磁盘重新加载。

已验证的刷新流程：

1. 查找正在运行的 `AutoShop.exe` 进程。
2. 枚举 MDI 子窗口，找到标题等于目标程序名的 POU。
3. 向该 MDI 子窗口发送 `WM_CLOSE`。
4. 查找 `工程管理` 面板下的工程树。
5. 在工程树中查找路径 `编程/程序块/<program>`。
6. 选中并双击该节点。
7. 再次枚举 MDI 子窗口，确认目标 POU 已重新打开。

CLI 不会点击保存、确认或放弃之类的弹窗。如果编辑器存在未保存内容，AutoShop 可能拒绝关闭窗口，此时命令必须失败，并提示需要用户手动处理弹窗。

## 工程级刷新

变量表等内容在 AutoShop 中属于工程级内存模型。直接修改工程文件后，关闭再打开变量表 MDI 页签不会强制 AutoShop 重新读取 `.gvt`。此时使用工程级刷新：

```powershell
.\scripts\autoshop-agent.exe ui refresh-project --project D:\program\PLC\project001 --dry-run --format json
.\scripts\autoshop-agent.exe ui refresh-project --project D:\program\PLC\project001 --format json
```

流程：
1. 记录当前 AutoShop 主窗口、工程路径、`.hcp/.hcpp` 工程文件、已打开 MDI 子窗口，以及当前活动 MDI 窗口。
2. 通过 AutoShop 的“文件/关闭工程”菜单关闭当前工程，不自动保存旧内存模型。
3. 使用当前 AutoShop 进程路径、配置中的 `autoShopExePath` 或文件关联重新打开工程文件。
4. 按刷新前记录的窗口列表重新打开对应工程树节点，最后把焦点切回刷新前的活动窗口。

若 AutoShop 弹出保存提示或关闭工程失败，命令会停止并报错；先处理未保存内容后再执行。

本地化 UI 文本可配置：

```json
{
  "ui": {
    "projectTreeTitle": "工程管理",
    "programmingNode": "编程",
    "programBlockNode": "程序块"
  }
}
```

## 静默截图

`ui screenshot` 使用 Win32 `PrintWindow(hwnd, hdc, flags)` 将 AutoShop 主窗口或已打开的 MDI 子窗口绘制到内存位图，再保存为 PNG。该流程不调用 `SetForegroundWindow`，不会把 AutoShop 切到前台。

若 AutoShop 当前最小化，使用 `--restore-offscreen`。CLI 会保存顶层窗口位置，把窗口临时恢复到虚拟屏幕右下角几乎屏幕外，只露出少量像素，截图后若原来是最小化则立即执行最小化。

常用命令：

```powershell
.\scripts\autoshop-agent.exe ui screenshot --out D:\tmp\autoshop.png --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --out D:\tmp\变量表.png --format json
.\scripts\autoshop-agent.exe ui screenshot --program MAIN --out D:\tmp\MAIN.png --client --format json
.\scripts\autoshop-agent.exe ui screenshot --title 变量表 --restore-offscreen --out D:\tmp\变量表.png --format json
```

限制：

- 目标窗口最小化时直接 `PrintWindow` 通常为空白；应使用 `--restore-offscreen`。只有传入 `--allow-minimized` 时才会直接对最小化窗口输出诊断图。
- 对未响应 `PrintWindow` 的自绘/硬件加速控件，结果可能为空白。
- JSON 输出中的 `minimized`、`nonBlank` 和 `uniqueProbe` 用于快速判断截图是否有效。
