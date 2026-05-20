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
