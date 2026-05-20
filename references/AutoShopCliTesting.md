# AutoShop CLI 测试说明

## 默认离线测试

源码仓库：

```text
D:\program\PLC\AutoShopAgentInterfaceDev\src\autoshop-agent
```

运行：

```powershell
go test ./...
```

默认测试只使用临时目录和构造的 AutoShop ST 容器，不连接 PLC，不扫描网络，不修改真实工程。

覆盖范围：

- ST 容器导出/写回 round-trip
- `project check/info/archive pack/archive unpack`
- `pou list/export/import --dry-run/add/remove/rename`
- `st lint/parse/refs/instruction`
- `config init/get/set/profile`
- `var export/system list`
- `comm serial/ethernet show`
- `trace add/list/export`
- `target/online/monitor/comm/motion/build` 的安全占位 JSON

## 真机调试用例

真机用例已经写在 `cli_test.go` 中，默认跳过。只有同时设置以下环境变量才会运行：

```powershell
$env:AUTOSHOP_AGENT_RUN_HARDWARE_TESTS = "1"
$env:AUTOSHOP_AGENT_HARDWARE_CONFIG = "D:\path\hardware-config.json"
$env:AUTOSHOP_AGENT_HARDWARE_PROFILE = "bench"
go test ./... -run Hardware -v
```

当前版本的硬件命令仍是安全占位，因此真机测试启用后会在发现占位实现时失败。这样做是故意的：只有在后续真正实现 PLC 通讯、模式读取、监控读取等能力后，才允许这些测试通过。

## 真机测试前置条件

- PLC 与 PC 的连接方式、IP/USB/串口参数已经由人工确认。
- 测试工程和 PLC 均处于可调试状态，不连接生产设备。
- 运行/停止/下载类测试必须单独确认，并使用专门的测试程序。
- 测试失败时先保留 CLI JSON 输出和 AutoShop 输出窗口日志，再分析通讯或目标状态。
