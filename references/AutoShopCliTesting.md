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
- `workspace export/apply`：导出工程镜像文件夹，修改 `编程/程序块/MAIN.st.txt` 和语义 JSON，dry-run 后应用回工程，并检查每个写入项 `verified=true` 与 `readBackSha256`
- `全局变量/变量表/变量表.gvt.json` 的专用 `variables` 语义导出、未改动逐字节重建、按内部变量行数组新增 BOOL 后回读解析，以及 BOOL、BYTE、INT、DINT、REAL、ARRAY、IP、STRING<128>、系统结构体、自定义结构体等样本回读
- `全局变量/结构体/*.stru.json` 的 `definition.members` 语义导出、未改动逐字节重建、新增成员后回读解析，以及 workspace 中新增 `*.stru.json` 后创建新结构体文件、同步 `.hcp` 工程索引并配套创建结构体变量的回读验证
- `.hcp` 工程索引的 AutoShop UCode 加密/解密 round-trip，以及结构体 `FileType=31` 登记和 `MaxFileID` 更新
- `全局变量/功能块实例/功能块实例.fbi.json` 的 `instances` 语义导出、未改动逐字节重建、新增实例后回读解析
- `project check/info/archive pack/archive unpack`
- `project node list/info/export/import --dry-run`，包含 `program`、`config`、`variable` 等分类
- `pou list/export/import --dry-run/add/remove/rename`
- `st lint/parse/refs/instruction`
- `config init/get/set/profile`
- `var export/system list`
- `var table list/info/export/import --dry-run` 和表级二进制替换用例
- `comm serial/ethernet show`
- `ui screenshot` 的窗口句柄解析单元测试；真实 AutoShop 截图需在窗口未最小化时手动 smoke
- `ui close-project` / `ui restore-project` / `ui refresh-project` 的纯函数测试覆盖 AutoShop 标题工程路径解析、`.hcp/.hcpp` 工程文件选择、工程刷新状态 JSON 往返，以及打开窗口到工程树恢复目标的推断；真实关闭/重新打开工程属于手动 UI smoke
- `trace add/list/export`
- `target/online/monitor/comm/motion/build` 的 simulator JSON
- `target/online/monitor/comm/motion/build` 的 simulator 后端执行结果，要求 `implemented=true` 且 `safe=true`

## 真机调试用例

真机用例已经写在 `cli_test.go` 中，默认跳过。只有同时设置以下环境变量才会运行：

```powershell
$env:AUTOSHOP_AGENT_RUN_HARDWARE_TESTS = "1"
$env:AUTOSHOP_AGENT_HARDWARE_CONFIG = "D:\path\hardware-config.json"
$env:AUTOSHOP_AGENT_HARDWARE_PROFILE = "bench"
go test ./... -run Hardware -v
```

当前版本默认使用 simulator 后端。真机测试启用后应显式验证硬件后端；如果硬件后端仍未实现，测试会失败。这样做是故意的：只有在后续真正实现 PLC 通讯、模式读取、监控读取等能力后，才允许这些测试通过。

## 真机测试前置条件

- PLC 与 PC 的连接方式、IP/USB/串口参数已经由人工确认。
- 测试工程和 PLC 均处于可调试状态，不连接生产设备。
- 运行/停止/下载类测试必须单独确认，并使用专门的测试程序。
- 测试失败时先保留 CLI JSON 输出和 AutoShop 输出窗口日志，再分析通讯或目标状态。
