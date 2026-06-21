# AutoShop POU 窗口刷新机制

## 背景

AutoShop 已打开的 ST/POU 编辑器会把内容保留在内存中。外部写回 `*.ST` 文件后，已打开的编辑器窗口不会立刻从磁盘刷新。

实测可靠方式是关闭同名 MDI 子窗口，再从工程树中重新打开同名程序块。

## CLI 刷新流程

`autoshop-agent refresh --program MAIN` 执行以下步骤：

1. 查找正在运行的 `AutoShop.exe`，不依赖安装目录。
2. 枚举主窗口的 MDI 子窗口，找到标题等于 `MAIN` 的窗口。
3. 向该 MDI 子窗口发送 `WM_CLOSE`。
4. 在工程树中查找路径 `编程/程序块/MAIN`。
5. 选中该树节点并发送双击消息。
6. 再次枚举 MDI 子窗口，确认 `MAIN` 已重新打开。

## 工程级刷新

变量表、模块配置、运动轴、EtherCAT/EtherNet/IP 等工程级缓存通常需要关闭工程再重新打开。`ui close-project` 会记录当前工程、已打开 MDI 窗口和活动窗口，然后通过 AutoShop 菜单关闭工程；`ui restore-project` 会优先复用记录的同一个 AutoShop 进程，通过“打开工程”对话框重新打开工程，再恢复窗口和焦点。只有原进程不存在时才回退到启动工程文件。

该流程默认通过指定窗口或控件句柄发送 Win32 消息：`close-project` 通过 `WM_COMMAND` 关闭工程，`restore-project` 通过 `WM_COMMAND` 打开工程对话框、`WM_SETTEXT` 写入工程路径并确认；优先匹配菜单文本，AutoShop 使用自绘菜单导致 `GetMenu` 不可用时，会回退到从 AutoShop V4.10 资源确认的命令号 `32860`（关闭工程）和 `32859`（打开工程）。所有 AutoShop UI 操作默认启用后台窗口保护：保存 `WINDOWPLACEMENT` 和操作前前台窗口，把 AutoShop 主窗口完全移动到当前虚拟屏幕右下角外侧执行，完成后恢复原窗口位置和最大化/最小化状态；如果 AutoShop 抢到前台，CLI 会先尝试把前台还给原用户窗口；若 Windows 前台限制导致恢复失败且 AutoShop 仍占前台，会把 AutoShop 最小化作为兜底。CLI 不使用全局键盘、全局鼠标或剪贴板。`ui close-project` / `ui refresh-project` 遇到“工程已修改，是否保存?”时默认保存关闭，也可用 `--save-prompt discard` 不保存关闭、`--save-prompt cancel` 取消关闭、`--save-prompt fail` 保持失败并交给人工处理。其他确认对话框仍会失败并要求人工处理。

## 可配置 UI 文本

如果 AutoShop 版本或语言包导致工程树文字不同，可在 JSON 配置中修改：

```json
{
  "ui": {
    "projectTreeTitle": "工程管理",
    "programmingNode": "编程",
    "programBlockNode": "程序块"
  }
}
```

## 限制

`ui close-project` / `ui refresh-project` 会自动处理 AutoShop 的“工程已修改，是否保存?”弹窗，默认保存关闭；可用 `--save-prompt discard` 不保存关闭、`--save-prompt cancel` 取消关闭、`--save-prompt fail` 保持失败。其他保存/放弃/确认弹窗仍不会自动点击，会失败并报告需要人工处理。

## 静默截图

`ui screenshot` 使用 Win32 `PrintWindow(hwnd, hdc, flags)` 将 AutoShop 主窗口或已打开的 MDI 子窗口绘制到内存位图，再保存为 PNG。截图默认也使用后台窗口保护，`--restore-offscreen` 仅作为兼容参数保留。CLI 会计算 `contentRatio`，当整窗截图疑似只有标题栏/白客户区时自动重试；如果重试后仍低内容，会尝试 client-only fallback，成功时 JSON 返回 `method=PrintWindowClientFallback`、`clientOnly=true` 并写入 `warnings`。

CLI 会保存顶层窗口 `WINDOWPLACEMENT`，按当前虚拟屏幕边界把窗口临时移动到右下角完全屏幕外，截图后恢复原窗口位置；若原来是最小化，会先隐藏窗口、写入离屏 normal placement，再不激活显示并确认离屏位置，结束后恢复最小化状态。`--offscreen-visible 0` 表示完全离屏；设置为正数时只用于诊断边缘可见像素。

限制：

- 目标窗口最小化时直接 `PrintWindow` 通常为空白；默认离屏恢复后截图。只有传入 `--allow-minimized` 且内部禁用离屏诊断时才应直接对最小化窗口输出空白诊断图。
- 后台窗口保护使用虚拟屏幕指标计算临时位置，兼容不同分辨率、缩放布局和带负坐标的多显示器；不要把 `WINDOWPLACEMENT` 的恢复坐标直接当作 `SetWindowPos` 的屏幕坐标使用。
- 对未响应 `PrintWindow` 的自绘/硬件加速控件，结果可能为空白；此时 `contentRatio` 会偏低，`warnings` 会提示疑似未绘制或 fallback 失败。
- JSON 输出中的 `contentRatio` 用于判断截图是否有足够真实内容，`nonBlank` 和 `uniqueProbe` 仅作为辅助探针；标题栏也可能让 `nonBlank=true`，不能单独作为验收依据。
