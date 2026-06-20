# AutoShop Agent CLI 指令文档

适用版本：`autoshop-agent.exe v0.8.131`。

本文是当前 CLI 的使用文档，只记录已经存在的指令、推荐工作流、JSON 映射和能力边界，不记录开发计划。正常工程内容编辑统一走 `workspace export` / `workspace apply`，不要为变量、结构体、FB/FC、模块参数等再绕开 workspace 增加零散编辑指令。

## 1. 首选工作流

### 1.1 固定工程映射目录

在 `D:\program\PLC` 当前工作区，固定使用：

```text
D:\program\PLC\AutoShopAgentInterfaceWork\current-export
```

临时验证目录只放在：

```text
D:\program\PLC\AutoShopAgentInterfaceWork\archive
```

不要在 `D:\program\PLC` 根目录继续生成 `project001-*` 目录，也不要把 workspace、smoke、临时导出放进 `D:\program\PLC\AutoShopAgentInterface` skill 文件夹。

### 1.2 导出、修改、预检查、应用

```powershell
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui close-project --project D:\program\PLC\project001 --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace export --project D:\program\PLC\project001 --out D:\program\PLC\AutoShopAgentInterfaceWork\current-export --force
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --dry-run --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe workspace apply --project D:\program\PLC\project001 --in D:\program\PLC\AutoShopAgentInterfaceWork\current-export --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui restore-project --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

如果目标工程当前已在 AutoShop 打开，常规编辑流程必须先用 `ui windows --format json` 确认主窗口 `title` 中的工程路径就是目标工程，再用 `ui close-project` 记录并关闭工程，完成正式 `workspace apply` 后再用 `ui restore-project` 恢复工程和窗口。若 AutoShop 未打开目标工程则跳过关闭/恢复；若打开的是其他工程，不要关闭。`--allow-open-project` 只作为用户明确要求跳过关闭/恢复流程时的例外，不作为默认写回路径。

`workspace apply` 写入后会立刻从工程文件回读并校验 SHA。JSON 输出中的 `verified=true` 和 `readBackSha256` 表示该项已经实际写回到磁盘工程文件。写回 POU、结构体、配置节点等会同步 `.hcp` 工程索引和 `.hcpp` 工程包成员快照，输出中的 `kind=project-index` / `kind=project-package` 表示索引和工程包也被更新。

### 1.3 AutoShop UI 刷新边界

外部写回后，AutoShop 已打开窗口不一定立即刷新。ST/普通树节点可用 `--refresh`、`ui refresh` 或 `ui refresh-path` 关闭并重开窗口。变量表、模块配置、运动轴等工程级缓存经常需要关闭工程再重新打开工程才能在 AutoShop 里看到磁盘更新。

工程级刷新拆成两步：

```powershell
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui close-project --project D:\program\PLC\project001 --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
D:\program\PLC\AutoShopAgentInterface\scripts\autoshop-agent.exe ui restore-project --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json
```

`ui restore-project` 会优先在记录的同一个 AutoShop 进程中通过“打开工程”对话框恢复工程；只有原进程不存在时才退回到按工程文件启动 AutoShop。该流程默认通过指定窗口句柄发送 Win32 消息：`close-project` 通过 `WM_COMMAND` 关闭工程，`restore-project` 通过 `WM_COMMAND` 打开工程对话框、`WM_SETTEXT` 写入工程路径并确认；优先匹配菜单文本，AutoShop 使用自绘菜单导致 `GetMenu` 不可用时，会回退到从 AutoShop V4.10 资源确认的命令号 `32860`（关闭工程）和 `32859`（打开工程）。`ui close-project`、`ui restore-project`、`ui refresh-project`、`ui open`、`ui open-path`、`ui refresh`、`ui refresh-path`、`ui focus`、`ui close`、`ui tree`、`ui output`、`ui compile`、`ui compile-all`、`ui run`、`ui stop`、`ui download`、`ui upload`、`ui monitor` 和 `ui screenshot` 默认启用后台窗口保护：保存 `WINDOWPLACEMENT` 和操作前前台窗口，把 AutoShop 主窗口完全移动到当前虚拟屏幕右下角外侧执行，完成后恢复原窗口位置、最大化/最小化状态；如果 AutoShop 在过程中抢到前台，CLI 会先尝试把前台还给原用户窗口；若 Windows 前台限制导致恢复失败且 AutoShop 仍占前台，会把 AutoShop 最小化作为兜底，保证用户前台窗口不被 AutoShop 长时间打断。所有 UI 操作仍不使用全局键盘、全局鼠标或剪贴板。

这些 UI 命令仍可能让 AutoShop 自己弹出模态对话框；`ui close-project` / `ui refresh-project` 对“工程已修改，是否保存?”提示默认选择保存，也可用 `--save-prompt discard` 不保存关闭、`--save-prompt cancel` 取消关闭、`--save-prompt fail` 保持失败并交给人工处理。其他非自动处理的工程错误或普通确认对话框仍会导致命令失败并报告需要人工处理。`ui screenshot` 使用 Win32 `PrintWindow`，默认同样强制离屏截图；`--restore-offscreen` 仅作为兼容参数保留，`--offscreen-visible 0` 表示完全离屏。

## 2. 通用格式和参数

```text
autoshop-agent.exe <command> [subcommand] [flags]
```

常用通用参数：

| 参数 | 说明 |
| --- | --- |
| `--config <path>` | JSON 配置路径，优先级高于 `AUTOSHOP_AGENT_CONFIG`。 |
| `--project <dir|file>` | 工程目录或工程文件。 |
| `--project-text-encoding <encoding>` | 覆盖工程 ST 文本编码；当前 `project001` 默认 `gb2312`。 |
| `--profile <name>` | 配置文件中的连接配置名。 |
| `--backend simulator|hardware` | 后端。默认 `simulator`；`hardware` 当前会拒绝执行。 |
| `--format text|json|ndjson` | 输出格式。自动化调用优先用 `json`。 |
| `--dry-run` | 只解析和验证，不写文件，不影响 AutoShop 或 PLC。 |
| `--allow-open-project` | 例外开关；目标工程在 AutoShop 打开时仍允许文件写回。常规流程应先用 `ui windows` 确认当前打开的是目标工程，再 `ui close-project`，写回后 `ui restore-project`。 |
| `--no-backup` | 不生成备份；默认会把被覆盖的工程文件备份到同工程目录下的 `.autoshop-agent-backups/<时间戳>/` 文件夹。 |
| `--force` | 允许覆盖已有导出或忽略导出后工程源文件变化等保护。 |
| `--refresh` | 写回后尝试刷新相关 AutoShop 窗口。 |
| `--yes` | 对模拟目标命令进行非交互确认。 |
| `--timeout` / `--timeout-ms` | 超时时间；不同命令使用字符串或毫秒参数。 |

默认配置路径：

```text
%APPDATA%\AutoShopAgentInterface\config.json
```

## 3. Workspace 映射文件

导出的 workspace 按 AutoShop 工程树排布。普通文件编辑只改 workspace 里的 `.st.txt` 或 JSON，再统一 `workspace apply`。

| AutoShop 树节点 | workspace 文件 | 编辑方式 |
| --- | --- | --- |
| 编程/程序块 | `编程/程序块/*.st.txt` | 编辑既有程序块 ST 正文。 |
| 编程/程序块 | `编程/程序块/*.pou.json` | 新增程序块、子程序或中断；`type=program|subprogram|interrupt`。 |
| 编程/程序块 | `编程/程序块/_interrupt-triggers.json` | 编辑既有中断程序触发源；写回 AutoShop 4.10 `.hcp` 中断 `POUID`/`Timer=0` 并同步 `.hcpp`。 |
| 编程/功能块(FB) | `编程/功能块(FB)/*.pou.json` | 新增 FB；`type=fb`，会创建 `.FB` 并注册 `FileType=81`、`ProgType=7`。 |
| 编程/函数(FC) | `编程/函数(FC)/*.pou.json` | 新增 FC；`type=fc`，会创建 `.FC` 并注册 `FileType=82`、`ProgType=8`。 |
| 全局变量/变量表 | `全局变量/变量表/变量表.gvt.json` | 编辑 `variables` 数组；不要手工改 `.gvt`。 |
| 全局变量/结构体 | `全局变量/结构体/*.stru.json` | 编辑 `definition.members`；新增符合格式的 JSON 可创建结构体。 |
| 全局变量/功能块实例 | `全局变量/功能块实例/功能块实例.fbi.json` | 编辑 `instances`。 |
| 配置/输入滤波 | `配置/输入滤波/_node.config.json` | 优先改 `inputFilter.parameters`。 |
| 配置/模块配置 | `配置/模块配置/_node.config.json` | 优先改 `moduleConfig.modules` 和每槽位 `moduleParameters`。 |
| 配置/运动控制轴 | `配置/运动控制轴/_node.config.json` | 优先改 `motionAxis.axes[].parameters`。 |
| 配置/轴组设置 | `配置/轴组设置/_node.config.json` | 优先改 `axisGroup.groups[].parameters`。 |
| 配置/电子凸轮 | `配置/电子凸轮/_node.config.json` | 优先改 `electronicCam.cams`、`parameters.masterRange/slaveRange` 和已验证的 18 字节点表 `points`。 |
| 配置/CAN(CANLink) | `配置/CAN(CANLink)/_node.config.json` | 优先改 `canLink.portConfig.parameters.protocol/stationNumber/baudRateKbps`；AutoShop 4.10 H5U 样本中的 `CANLink.prg` 会导出为 `canLink.programConfig`，当前支持既有 IS/SV 从站 D/M、发送配置和接收许可表写回，`syncView` 为只读派生视图；协议为 `CANOpen` 时会附加只读 `canOpen.catalog`。 |
| 配置/EtherCAT | `配置/EtherCAT/_node.config.json` | 改 `ethercat.parameters` 和 `ethercat.slaves`；新增从站优先写 AutoShop 工具箱叶子名称 `toolboxName`，`catalogKey` 仅用于高级诊断。 |
| 配置/EtherNet/IP | `配置/EtherNet/IP/_node.config.json` | 改 `ethernetIP.devices`、标签、连接和 I/O 数据集；新增设备可只写 `internalName` / `deviceName` / `toolboxName`，`catalogKey` 仅用于高级诊断。 |
| 其他配置节点 | `配置/<节点名>/_node.config.json` | 语义字段不存在时才改 `files[].contentHex` 或 `files[].contentBase64`。 |

Windows 保留设备名会使用安全目录名，例如 AutoShop 树里的 `配置/COM0` 在 workspace 中是 `配置/COM0_/_node.config.json`，JSON 内 `treePath` 仍保留原始树路径。

## 4. 语义 JSON 字段

### 4.1 POU 定义

新增 `*.pou.json` 使用：

```json
{
  "format": "autoshop-agent-pou-definition.v1",
  "kind": "pou-definition",
  "name": "JSON_FB_001",
  "type": "fb",
  "language": "litest",
  "encoding": "utf8",
  "sourceRelative": "JSON_FB_001.FB",
  "text": "VAR\n    t1 : BOOL := OFF;\nEND_VAR\n"
}
```

`workspace apply` 会创建对应 `.ST`、`.FB` 或 `.FC` 容器，维护 `folder.txt`，并同步 `.hcp` 工程索引和 `.hcpp` 工程包。`pou add` 是底层兼容/诊断入口，不是推荐新增流程。

### 4.1.1 中断触发设置

既有中断程序的触发源位于 `编程/程序块/_interrupt-triggers.json`，每个 `interrupts[]` 对应 `.hcp` 中一个 `ProgType=2` 的中断 POU。优先编辑 `trigger`：

- `type=external`：`input` 为 `X0|X1|X2|X3`，`edge` 为 `falling|rising|both`。
- `type=timed`：`channel` 为 `1..4`，`periodMs=1..1000`；AutoShop 4.10 样本编码为 `POUID=0x02CCPPPP`。
- `type=comparison`：`compareIndex` 为 `1..16`。
- `type=raw`：直接写 `rawCode` 或 `trigger.code`，用于未知或有歧义的 AutoShop 指针值。

`workspace apply` 会重建加密 `.hcp` 中对应 `<POUID>`，同时保持 `<Timer>0</Timer>`，回读校验，并同步 `.hcpp` 工程包。AutoShop 4.10 实测外部中断编码为 `0x01II00EE`（`EE=01` 上升、`02` 下降、`03` 双沿），比较中断编码为 `0xNNFFFF`；旧 CLI 写入的 legacy `Timer` 码会在导出时迁移成 POUID。

### 4.2 全局变量表

`变量表.gvt.json` 使用：

```json
{
  "format": "autoshop-agent-global-variable-table.v1",
  "kind": "global-variable-table",
  "variables": [
    {
      "name": "stubid",
      "dataType": "BOOL",
      "initialValue": "OFF",
      "powerRetain": "保持",
      "networkAccess": "私有",
      "comment": ""
    }
  ]
}
```

支持已验证类型：`BOOL`、`BYTE`、`INT`、`DINT`、`REAL`、`ARRAY`、`IP`、`STRING` / `STRING<...>`、自定义结构体、以 `_s` / `_u` 开头的系统结构/联合类型。`powerRetain` 对应“掉电保持”，使用 `保持|不保持`；`networkAccess` 对应“网络公开”，使用 `私有|公有|输入|输出`。

### 4.3 结构体和 FB 实例

结构体 JSON 的关键字段是 `definition.members`，可创建和修改自定义结构体成员。新增结构体时，`sourceRelative` 指向新的 `.stru` 文件，`workspace apply` 会注册 `.hcp` 中 `FileType=31`。

功能块实例 JSON 的关键字段是 `instances`。编辑后由 `workspace apply` 重建 `.fbi`。

### 4.4 输入滤波

`inputFilter.parameters` 当前已确认字段：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `normalX0ToX7Ms` | 普通输入滤波 `X0-X7`，单位 `ms`。 |
| `highSpeedX0ToX3_100ns` | 高速输入滤波 `X0-X3`，单位 `100ns`。 |
| `highSpeedX4ToX7Us` | 高速输入滤波 `X4-X7`，单位 `us`。 |

### 4.5 模块配置

`moduleConfig.modules` 是槽位数组。常用字段：

| 字段 | 说明 |
| --- | --- |
| `slot` | 机槽号。 |
| `model` | 模块型号，例如 `GL10(AM600)-4DA`。已知 GL10 样本可只填型号生成默认参数。 |
| `identity` / `moduleTypeCode` / `instance` | AutoShop 私有模块标识。 |
| `ioSignals` | 已有 X/Y 地址映射；可改地址，数量必须与该模块参数中地址字段一致。 |
| `moduleParameters` | 模块内部页面参数。4DA/4AD 是 4 个通道页；8TC/4TC/4PT 是通道组页数组。 |
| `parametersHex` | 未完全拆解时的保真兜底字节。 |

已按样本映射的模块包括 `GL10(AM600)-1600END`、`GL10(AM600)-3200END`、`GL10(AM600)-0032ETN`、`GL10(AM600)-4DA`、`GL10(AM600)-4AD`、`GL10(AM600)-8TC`、`GL10(AM600)-4TC`、`GL10(AM600)-4PT`。已确认字段可以语义编辑；未知私有位域保留 `rawCode` 或 `parametersHex`。

### 4.6 EtherCAT

`ethercat.parameters` 当前只承诺写回常规设置：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `cycleTimeUs` | 分布式时钟循环时间，单位 `us`。 |
| `syncOffsetPercent` | 同步偏移，单位 `%`。 |
| `autoRestartSlave` | 自动重启从站。 |
| `aliasEnabled` | 别名模式使能。 |

`ethercat.records` 里的 `parameter_0x...` 是主站私有记录视图；状态页里的循环时间、执行时间、丢帧次数等是在线任务监控值，不作为离线工程配置写回。

`ethercat.slaves` 是顶层从站数组。每个从站对象包含：

| 字段 | 含义 |
| --- | --- |
| `key` | 本次导出的稳定键；删除从站时从数组移除对应对象。 |
| `templateKey` | 新增从站时使用的模板键，指向当前工程中已有从站的 `key`。 |
| `toolboxName` | 新增从站时首选填写的 AutoShop 工具箱叶子名称，例如 `SV820_3Axis_V3.03`、`GL10-RTU-ECTA_2.0.7.0`。CLI 会用它映射到内部 ESI 型号、ProductCode、Revision 和模板。 |
| `catalogKey` | 高级诊断字段，来自 `ethercat.catalog.devices[].key` 或 `aliases[]`；正常 JSON 不应要求用户手写它。 |
| `allowGeneratedFromCatalog` | 默认 `false`。没有同型号模板时，CLI 会拒绝新增以保证 AutoShop UI 参数保真；显式设为 `true` 才允许按 ESI 生成基础从站段。若 catalog 标记 `requiresTemplateForCatalogGeneration=true`，即使显式允许也会拒绝基础生成，必须先在 AutoShop 创建样本、使用 `templateKey` 或提供完整 `segmentBase64`。 |
| `allowIdentityOverride` | 默认 `false`。仅用于高级诊断；设为 `true` 才允许绕过 ESI 身份校验写入不匹配的 `deviceName` / `productCode` 等字段。正常工程不要使用。 |
| `name` / `deviceVersion` / `productCode` / `protocol` | 从 `0x20000121` 等通用记录解析出的设备身份信息；`deviceName` 是 AutoShop 查找 ESI XML 的关键字段，只允许 ESI 型号名或数字副本后缀，例如 `SV820N`、`SV820N_1`。 |
| `parameters` | 已确认的通用从站字段，优先编辑这里。 |
| `records` | 从站段内完整私有记录，包含 PDO、对象字典、设备参数等型号专属内容；未命名字段可在这里按 `value` 修改。 |
| `disconnectOutput` | EtherCAT 数字量输出从站的断线/错误状态输出语义。`mode` 对应 AutoShop 私有记录 `0x50200001` 并镜像到 CoE `0x6206:1`，可写 `hold` 或 `setValue`；`channels[].level` 对应 AutoShop 页面私有记录 `0x50200002` 并镜像到 CoE `0x6207:n` 位掩码，可写 `low` 或 `high`。`modeRawHex`、`masks[].rawHex` 仅作诊断。 |
| `pages` | 从站页面化语义索引，所有 EtherCAT 从站都会按 identity、topology、sync/DC、ESI SyncManager、RxPDO、TxPDO、CoE Object Dictionary、AutoShop objectDictionary/deviceParameter/private records 等页面分组导出；`editable:true` 字段可直接改 `value`。 |
| `segmentBase64` | 完整从站段原始模板；用于精确克隆和保真回写。 |

常用 `slaves[].parameters`：

| 字段 | 含义 |
| --- | --- |
| `autoIncrementAddress` | 自动增量地址，常见为 `-物理序号`。 |
| `physicalAddress` / `positionIndex` | 从站物理序号。 |
| `stationIndex` | AutoShop 从站树/站号索引；新增克隆从站未显式填写时会按当前最大值加 1。 |
| `syncMode` | 同步模式字符串，例如 `DC-Synchron`、`SM-Synchron`。 |
| `expertSettingsEnabled` | 从站页面“使能专家设置”。 |
| `cycleTimeAUs` / `cycleTimeBUs` / `cycleTimeCUs` | 从站通用周期字段。 |
| `deviceName` / `deviceVersion` / `productCode` / `protocol` / `internalPort` | 设备身份和内部端口字段。 |

`ethercat.catalog` 从 AutoShop 安装目录的 `xml/*.xml` 解析 ESI 设备库。每个设备会列出 `toolboxName`、`key`、`aliases`、内部型号 `name`、ProductCode、Revision、同步管理器、Rx/Tx PDO、CoE 对象字典 `objectDictionary`、DC 模式、`templateAvailable` 和必要时的 `requiresTemplateForCatalogGeneration`。`objectDictionary` 来自 ESI `Profile/Dictionary/Objects`，包含对象 Index、SubIndex、名称、类型、bitSize、访问权限、PDO 映射和默认值，用作所有 EtherCAT 型号的统一语义来源。`toolboxName` 是正常 JSON 应写的 AutoShop 工具箱名称；内部型号 `name` 只用于 AutoShop 查找 XML 和诊断。没有设备名或 ProductCode 的 ESI 父占位项不会导出为可新增型号。如果 `templateAvailable=true`，说明当前工程已有同型号从站，新增时会优先克隆完整私有 `segmentBase64` 模板，并同时复制/重排对应主站记录和 `SYS_ETHERCAT.ecgvt` 系统变量行；如果为 `false`，默认会拒绝用该设备新增，以避免把 ESI 基础实例误认为完整 AutoShop UI 参数保真。

`slaves[].pages` 是 EtherCAT 从站的统一语义编辑入口。`identity`、`topology`、`sync` 页直接同步 `slaves[].parameters` 和对应通用记录；`syncManagers`、`rxPdos`、`txPdos`、`objectDictionary`、`dcModes` 页来自 ESI catalog，默认只读，用于确认厂商语义；`disconnectOutput` 页来自 AutoShop 私有 UI 记录 `0x50200001`、CoE InitCmd `0x6206:1` 和 ESI `0x6207` 对象，`disconnectOutput.mode`、`disconnectOutput.channels.N.level` 可直接改 `value`；`slaveGeneralRecords`、`pdoOrSyncRecords`、`deviceParameterRecords`、`objectDictionaryRecords`、`privateRecords` 页来自 AutoShop 实际保存的从站段记录，`editable:true` 时可改 `value`，apply 会按原 record 长度和类型写回。这样未提前命名的厂家私有字段不会退化成不可发现的二进制块，而是至少按协议类别和 record 身份暴露；已经确认的字段仍优先编辑 `parameters`、`disconnectOutput` 或其它专门语义字段。

AutoShop 常规页中的“写入站点别名”输入框当前不作为 workspace JSON 字段承诺：现有样本显示它是 UI-only/在线写入候选，尚未确认存在稳定工程持久化记录。`physicalAddress`、`positionIndex`、`autoIncrementAddress` 等拓扑字段可通过 JSON 写回并回读 backing records，但不要把它们等同为“写入站点别名”的 UI 输入框。

断线输出 JSON 示例：

```json
{
  "key": "slave_000_GR10_0808ETNE",
  "disconnectOutput": {
    "mode": "setValue",
    "channels": [
      { "channel": 0, "level": "low", "subIndex": 1, "bit": 0 },
      { "channel": 3, "level": "high", "subIndex": 1, "bit": 3 }
    ]
  }
}
```

`disconnectOutput.mode` 的语义值为 `hold` 或 `setValue`。写回时 CLI 会同步 AutoShop 页面实际使用的私有记录 `0x50200001`，并在工程已存储 `0x6206:1` InitCmd 时同步该 CoE 数据；若只有 AutoShop 私有模式记录而缺少 `0x6206:1`，仍优先更新私有记录以匹配页面显示。`disconnectOutput.channels[].level` 写回到 AutoShop 页面实际使用的私有记录 `0x50200002`；如果工程原本已存储 `0x6207:n` InitCmd，则同步更新对应 CoE 位掩码。根据 AutoShop 手动样本，页面级电平修改不会新建缺失的 `0x6207` InitCmd，因此 CLI 也不会为 `channels[].level` 自动创建缺失的 `0x6207` 记录组，以避免 AutoShop 打开后页面显示与工程私有记录不一致。

修改既有从站时，保留数组顺序并改对应对象的 `parameters` 或 `records[].value`。删除从站时，直接删除对应 `slaves[]` 对象。新增同型号从站时，在数组末尾追加最小对象：

```json
{
  "key": "slave_010_GR10_4ADE_CLONE",
  "templateKey": "slave_004_GR10-4ADE",
  "name": "GR10-4ADE-CLONE"
}
```

使用 `templateKey` 新增从站时，CLI 会克隆完整私有从站段，并自动重写 AutoShop 拓扑字段：`autoIncrementAddress`、`physicalAddress`、`positionIndex`、`stationIndex`、`slaveTreeIndex`，同时重写段内 `_IQ/_Q` 等站号引用；这些字段只有在用户显式改成不同于模板值时才会按用户值保留。`name` / `parameters.deviceName` 不要填任意显示名，必须保持 AutoShop/ESI 可识别的型号名或数字副本后缀，例如 `GL20-RTU-ECT`、`GL20-RTU-ECT_3`；随意写 `JSON_xxx` 这类名称会被 `workspace apply` 拒绝，避免 AutoShop 打开工程时报找不到 XML。

新增设备库型号时优先使用 `toolboxName`：

```json
{
  "key": "slave_011_SV520N",
  "toolboxName": "SV520N-Ecat_v0.1.2",
  "parameters": {
    "expertSettingsEnabled": true
  }
}
```

当 `toolboxName` 命中 `templateAvailable=true` 时，新增对象可以只填 `key`、`toolboxName` 和需要覆盖的 `parameters`；`deviceName` 未填写时会自动生成 AutoShop 可识别的数字副本名，例如已有 `SV820N` 和 `SV820N_1` 时新增为 `SV820N_2`。`deviceVersion`、`productCode`、`protocol`、`internalPort` 会从 catalog/模板默认补齐。如果需要 100% 保留某型号厂商私有页面的全部底层字段，仍应优先让 `toolboxName` 命中 `templateAvailable=true` 的同型号模板，或显式复制带 `segmentBase64` 的从站对象。写回会同步 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`、`SYS_ETHERCAT.ecgvt`、`.hcp` 和 `.hcpp`，并保留运动轴、轴组尾部记录以及 AutoShop 追加在最后一个从站后的私有尾部记录，不会在新增从站时把这些尾部记录插到新从站前面。
确实只需要基础 ESI 实例时，可以额外设置 `"allowGeneratedFromCatalog": true`；该模式只承诺写入身份、同步、PDO 元数据和通用参数，不承诺覆盖厂家私有配置页隐藏字段，也不保证 AutoShop 工程树会把该基础实例识别为可见从站。像 `SV820_3Axis_V3.03` 这种 ESI 中带模块定义的多轴伺服会导出 `requiresTemplateForCatalogGeneration=true`，CLI 会拒绝基础生成，因为手动样本包含大量 AutoShop 私有模块记录和主站记录；需要界面可见且可完整编辑时，必须使用 AutoShop 手动创建过的同型号模板、`templateKey` 或完整 `segmentBase64`。

如果某个 EtherCAT 型号的厂商页面存在 AutoShop 私有字段，而 ESI 中没有可命名信息，导出会把它放入对应的 `deviceParameterRecords`、`objectDictionaryRecords` 或 `privateRecords` 页面；这类字段仍可通过 `pages[].fields[].value` 或 `records[].value` 写回，但 CLI 不会伪造未确认的中文 UI 名称。

导出 `配置/EtherCAT`、`配置/运动控制轴`、`配置/轴组设置` 时，CLI 优先使用 AutoShop 当前主文件 `EtherCat.dat` / `EtherCat.tmp` 生成语义 JSON；只有两个主文件都无法读取或解析时才回退 `EtherCat.datBAK`。这是为了避免 AutoShop 手动保存后留下的旧 BAK 被误认为当前工程状态；应用时仍会同步写回三个镜像文件。

### 4.7 运动控制轴

运动轴位于 `motionAxis.axes`。当前支持修改既有轴参数，也支持在数组末尾追加默认运动轴；工程没有运动轴时会导出空数组，可直接从 0 开始追加。写回会同步 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`；删除或中间插入轴会被 `workspace apply` 拒绝。优先编辑每个轴的 `parameters`，`uiRecords` / `compilerRecords` 只用于底层诊断或未命名字段回写。

常用字段：

| 字段 | 含义 |
| --- | --- |
| `virtualAxisMode` | 基本设置“虚轴模式”；按手动保存样本同步可见 UI 记录 `0x80000111` 和编译记录 `0x1900xx06`。 |
| `autoMappingEnabled` | 基本设置“自动映射”。 |
| `outputDevice` | 基本设置“输出设备”；写 `未分配` 可清除绑定，写 EtherCAT 从站名、`deviceVersion`、`productCode`、`key` 或 `index:N` 会按该从站已选 PDO 生成运动轴绑定 UI/编译记录，例如 `IS620N`。 |
| `encoderMode` | `增量模式|绝对模式`。写回时同步可见 UI 记录、`encoderModeEffective` 和 `encoderModeLinkedFlag`。 |
| `axisMotionMode` | `线性模式|旋转模式`。 |
| `softwareLimitEnabled` | 软件限位使能。 |
| `ignoreLimitAfterErrorStop` | 由 `encoderMode` / `axisMotionMode` 改动时按 AutoShop 样本联动归一化：增量或旋转为 `true`，绝对+线性为 `false`。 |
| `reverseDirection` | 单位换算页“反向”；同步可见复选框位和联动标志。 |
| `gearDeviceEnabled` | 单位换算页“使用变速装置”。 |
| `pulsesPerRevolution` | 十进制数；AutoShop 里的 `16#1000000` 对应 JSON `16777216`。 |
| `homeOriginSignal` / `homeZSignal` / `homePositiveLimit` / `homeNegativeLimit` | `未分配|使用|不使用`。正负限位不能同时为 `使用`。 |
| `homeReturnDirection` / `homeInputDetectionDirection` | `未分配|正向|负向`。 |
| `homeMethodNumber` | 对已由样本确认的下拉项组合自动同步；未知组合不猜测。 |

AutoShop 手动保存可能保留旧的 `encoderModeLegacy` compilerRecord。语义 `apply` 不强行改这个旧编译记录，除非用户明确编辑底层 `compilerRecords`。

新增轴时，在 `motionAxis.axes` 末尾追加一个最小对象即可；轴号、记录组和底层默认记录按数组位置自动生成。示例：

```json
{
  "name": "Axis_2",
  "parameters": {
    "axisName": "Axis_2"
  }
}
```

### 4.8 轴组设置

轴组设置位于 `axisGroup.groups`。当前支持修改既有轴组，也支持在数组末尾追加默认轴组；工程没有轴组时会导出空数组，可直接从 0 开始追加。写回会同步 `EtherCat.dat`、`EtherCat.tmp`、`EtherCat.datBAK`；删除或中间插入轴组会被 `workspace apply` 拒绝。优先编辑每个轴组的 `parameters`，`records` 只作为底层诊断视图。

常用字段：

| 字段 | 含义 |
| --- | --- |
| `groupNumber` | 轴组号；AutoShop UI 中为只读，JSON 写回时会同步底层镜像记录。 |
| `groupName` | 轴组名称，例如 `GroupAxes_0`。 |
| `xAxis` / `yAxis` / `zAxis` / `auxiliaryAxis` | 基本设置中的 X/Y/Z/辅助轴，值可填 `availableAxes` 中的轴名或 `未分配`。 |
| `maxSpeed` | 参数设置“最大速度”，单位 `Unit/s`。 |
| `maxAcceleration` | 参数设置“最大加速度”，单位 `Unit/s^2`。 |
| `stopMode` | 插补参数“停止方式”；当前样本确认值为 `立即停止`。 |

`axisGroup.availableAxes` 会列出当前工程可选运动轴名称。`未分配` 在底层可能保存为空字符串或 GB2312 的“未分配”，导出统一显示为 `未分配`，应用未变化时不会改动原始字节。

新增轴组时，在 `axisGroup.groups` 末尾追加对象；`groupNumber` 和 `groupName` 会按数组位置和名称自动归一化。示例：

```json
{
  "name": "GroupAxes_2",
  "parameters": {
    "groupName": "GroupAxes_2",
    "xAxis": "Axis_0",
    "yAxis": "Axis_1",
    "zAxis": "Axis_2",
    "auxiliaryAxis": "未分配",
    "maxSpeed": 3000,
    "maxAcceleration": 500
  }
}
```

如果一次同时修改 `配置/运动控制轴/_node.config.json` 和 `配置/轴组设置/_node.config.json`，`workspace apply` 会对同一个 `EtherCat.dat` 串行叠加语义改动，不需要分两次应用。

### 4.9 电子凸轮

`electronicCam` 位于 `配置/电子凸轮/_node.config.json`，由 AutoShop 工程文件 `Ecam.tr` 导出。当前已经通过 AutoShop 实际界面验证的格式是 TLV 记录加尾部 CRC32：头部记录保存凸轮数量、选中索引和格式标记；每个凸轮使用 `0x7100 + index*0x0100` 记录组保存序号、点数、表格 payload、名称、索引、保留字段、主轴范围和从轴范围。`workspace apply` 会重建 `Ecam.tr`，重算 CRC32，同步 `.hcp` 中 `FileType=55` / `FileName=Ecam.tr` 的工程树注册，并同步 `.hcpp` 工程包。

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `camCount` | 电子凸轮数量，正常由 `cams.length` 自动得到。 |
| `header.selectedIndex` / `header.formatMarker` | AutoShop 头部状态；常规编辑不需要修改。 |
| `cams[].name` | 工程树下的凸轮显示名，例如 `Cam_A`；当前只允许 ASCII 名称，避免未验证的编码写坏工程树。 |
| `cams[].parameters.pointCount` | AutoShop 点表行数，对应底层记录 `0x7102`；正常由 `points.length` 自动同步，显式填写时必须与 `points` 数量一致。 |
| `cams[].parameters.masterRange` | 页面曲线和表格的主轴范围；未显式填写时由 `points` 最后一行 `M-Pos` 自动得到。 |
| `cams[].parameters.slaveRange` | 页面曲线和表格的从轴范围；未显式填写时由 `points` 最后一行 `S-Pos` 自动得到。 |
| `cams[].points` | 已验证的 AutoShop 点表，每行 18 字节：`M-Pos`、`S-Pos`、`PU Speed` 为 float32，类型码位于行尾。第 1 行必须是 `0/0/0/NA`，后续已验证写回类型为 `Line` 或 `Spline`，最多 1500 行。 |
| `cams[].records` | 底层 TLV 诊断记录，包含记录 ID、偏移、长度、值和 SHA；不作为常规编辑入口。 |

新增电子凸轮时，在 `cams` 末尾追加对象即可；缺省 `ordinal`、`camIndex`、`parameters.pointCount`、`reserved`、点表和底层记录会按 AutoShop 样本规则自动补齐。删除电子凸轮时从 `cams` 数组移除对象，CLI 会重新顺序生成 `ordinal/camIndex` 和记录组。中间插入也会按数组顺序重建，但建议常规新增只追加到末尾，便于和 AutoShop 工程树行为一致。

示例：

```json
{
  "electronicCam": {
    "cams": [
      {
        "name": "Cam_A",
        "parameters": {
          "masterRange": 720,
          "slaveRange": 180
        },
        "points": [
          { "row": 1, "mPos": 0, "sPos": 0, "puSpeed": 0, "type": "NA" },
          { "row": 2, "mPos": 120, "sPos": 20, "puSpeed": 0, "type": "Spline" },
          { "row": 3, "mPos": 240, "sPos": 70, "puSpeed": 0, "type": "Line" },
          { "row": 4, "mPos": 360, "sPos": 120, "puSpeed": 0, "type": "Spline" },
          { "row": 5, "mPos": 540, "sPos": 165, "puSpeed": 0, "type": "Spline" },
          { "row": 6, "mPos": 720, "sPos": 180, "puSpeed": 0, "type": "Spline" }
        ]
      }
    ]
  }
}
```

当前开放的是已验证的 18 字节点表多点写回：首行 `NA`，后续 `Line` 或 `Spline`，`M-Pos` 必须非递减；如果显式填写 `masterRange/slaveRange`，必须和最后一个点的 `mPos/sPos` 一致。`NA` 只用于首行或空/无效点，不作为后续点的普通可选插补类型；非 ASCII 凸轮名以及未知保留位仍未开放，这些字段必须先通过 AutoShop 手动样本和 UI 回显验证后再进入语义 JSON。未验证字段仍可在 `records` 中诊断定位，但不要用 raw 字节猜测写回生产工程。

### 4.10 CAN(CANLink)

`canLink` 位于 `配置/CAN(CANLink)/_node.config.json`。根配置来自 `PortConfig.cfg`，系统变量仍保留 `_SYS_CAN.svt` 文件级入口；AutoShop 4.10 H5U CANLink3.0 样本确认 `CANLink.prg` 可单独存在并保存站点配置，导出为 `canLink.programConfig`。

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `canLink.portConfig.parameters.protocol` | 协议类型，取值 `CANLink` 或 `CANOpen`；底层 `PortConfig.cfg` 偏移 `0xCF`，`0=CANLink`、`1=CANopen`。 |
| `canLink.portConfig.parameters.stationNumber` | 通讯参数/站号，范围 `1..63`；底层偏移 `0xD5`。 |
| `canLink.portConfig.parameters.baudRateKbps` | 通讯参数/波特率，单位 Kbps，支持 `20/50/100/125/250/500/800/1000`；底层 `0xD7` 起 `uint16le`。 |
| `canLink.portConfig.parameters.stationSource` / `baudRateSource` | 当前样本显示为 `background`，但对应拨码控件在 H5U-A16 上禁用，导出只读；未采样到可写设备前写成其它值会被拒绝。 |
| `canLink.rightClickConfig` | 记录右键“添加CAN配置”产生的 `CANLink.data`、`CANLink.prg` 是否存在。AutoShop 4.10 H5U 样本确认 `CANLink.prg` 可单文件存在，`CANLink.data` 缺失不代表配置不存在；缺失文件不会伪造。 |
| `canLink.programConfig` | 从 `CANLink.prg` 解析出的 CANLink3.0 KLC record 视图，包含 header、CRC16/MODBUS 校验、网络记录、从站记录、发送配置、接收许可表、只读同步视图和原始 records。 |
| `canLink.programConfig.network.masterStationNumber` | 主站号；当前样本 record 0 解析，正常与根口站号一致。 |
| `canLink.programConfig.network.baudRateKbps` | CANLink3.0 网络波特率，当前样本 record 0 解析为 `500`。 |
| `canLink.programConfig.network.heartbeatMs` | 网络心跳周期，当前样本 record 0 解析为 `500` ms。 |
| `canLink.programConfig.slaves[].stationNumber` | 既有从站号；当前版本只允许保持原值，不支持从 JSON 新增/删除/改站号。 |
| `canLink.programConfig.slaves[].type` / `typeCode` | 从站类型；当前已采样 `typeCode=5` 为 `IS/SV(伺服)`。 |
| `canLink.programConfig.slaves[].statusRegister` | CANLink3.0 主窗口“状态码寄存器(D)”，例如 `D1001`。当前已支持对既有从站写回。 |
| `canLink.programConfig.slaves[].startStopElement` | CANLink3.0 主窗口“从站启停元件(M)”，例如 `M1001`。当前已支持对既有从站写回。 |
| `canLink.programConfig.sendConfigurations[]` | CANLink3.0 “发送配置”页条目。当前按真实样本支持既有条目修改：`time-ms`、`event-ms`、`event-m` 三类触发的站号、D/H 寄存器、功能码、寄存器数量、周期或触发 M。 |
| `canLink.programConfig.receiveConfigurations[]` | CANLink3.0 “接收配置”许可表。当前支持修改既有条目的接收站和最多 8 个 `allowedSenderStations`。 |
| `canLink.programConfig.syncView[]` | AutoShop “同步写”页的派生视图，底层来自 `sendConfigurations[]`；该字段只读，直接修改会被拒绝。实际同步写触发元件仍有未完全采样的 UI 约束。 |
| `canLink.programConfig.records[]` | KLC record 原始视图，未知 record 保留 `dataHex`，不丢失不猜测。 |

可直接改 `parameters`，也可在未改 `parameters` 时修改 `portConfig.protocol`、`portConfig.station.number`、`portConfig.baudRate.kbps` 这些嵌套字段。`workspace apply` 会写回 `PortConfig.cfg`，并同步 `.hcpp` 工程包成员快照。

`programConfig` 写回只承诺当前已采样验证的既有从站 `statusRegister`/`startStopElement`、既有 `sendConfigurations[]` 条目和既有 `receiveConfigurations[]` 条目。写回时 CLI 会在 `CANLink.prg` 内改对应字段、重算尾部 `CRC16/MODBUS`，并同步 `.hcpp`。如果 `programConfig.parseError` 存在且没有语义编辑，apply 保持 no-op；如果用户在不可解析样本上做语义编辑，会拒绝。

示例：在导出的 JSON 中保留对应对象，只修改既有条目，不新建对象：

```json
{
  "canLink": {
    "programConfig": {
      "slaves": [
        {
          "stationNumber": 1,
          "statusRegister": "D1002",
          "startStopElement": "M1003"
        }
      ],
      "sendConfigurations": [
        {
          "entryIndex": 0,
          "triggerMode": "time-ms",
          "senderStation": 1,
          "senderRegister": "H200",
          "receiverStation": 63,
          "receiverRegister": "D120",
          "registerCount": 1,
          "intervalMs": 200
        }
      ],
      "receiveConfigurations": [
        {
          "entryIndex": 0,
          "receiverStation": 63,
          "allowedSenderStations": [1]
        }
      ]
    }
  }
}
```

当前未完成的边界：CANLink3.0 从站新增/删除、发送/接收配置新增删除、站号迁移、真实同步写触发元件完整语义，都必须继续按真实 AutoShop 样本反解后再开放；不能用猜测 JSON 生成生产工程。

### 4.10.1 CANopen catalog

当 `canLink.portConfig.parameters.protocol` 为 `CANOpen` 时，同一个 `配置/CAN(CANLink)/_node.config.json` 会附加只读 `canOpen` 诊断对象。

| 字段 | 含义 |
| --- | --- |
| `canOpen.portConfig` | `canLink.portConfig` 的只读镜像。需要修改协议、站号或波特率时，改 `canLink.portConfig.parameters`；只改 `canOpen.portConfig` 会被拒绝。 |
| `canOpen.catalog.autoShopRoot` / `edsDirectory` | AutoShop 安装根和 `sys/eds` 目录，用于诊断 EDS 来源。 |
| `canOpen.catalog.devices[]` | 从 AutoShop EDS 文件解析出的 CANopen 设备列表，包含 `vendorNumber/productNumber/revisionNumber/productName/sourceRelative`、支持波特率、RxPDO/TxPDO 数量和对象字典摘要。 |
| `canOpen.catalog.devices[].rxPdos[]` / `txPdos[]` | EDS 中 `0x1600..0x17FF`、`0x1A00..0x1BFF` 的 PDO mapping 对象摘要。 |
| `canOpen.catalog.devices[].objectDictionary[]` | EDS 里的对象字典条目，保留 `index/subIndex/objectType/dataType/accessType/defaultValue/pdoMapping` 等诊断字段。 |
| `canOpen.jsonCreateSupported` | 当前固定为 `false`。无 AutoShop 保存过的 CANopen 主站/从站样本时，不允许从 EDS 直接生成真实工程配置。 |

`canOpen.catalog` 只解决 EDS 目录可见性和对象字典核对，不代表 CANopen 主站、从站、PDO、SDO 或 I/O Mapping 已经能写回。当前 `workspace apply` 会明确拒绝直接添加 `canOpen.slaves`，也不会根据 catalog 伪造 `CANopen` 配置文件。后续必须先用 AutoShop 保存真实 CANopen 从站样本，再按文件差异开放主站参数、PDO、SDO 和 I/O Mapping 的语义 JSON。

### 4.11 EtherNet/IP

`ethernetIP` 当前映射：

| 字段 | AutoShop 页面含义 |
| --- | --- |
| `devices` | 工程树 `配置/EtherNet/IP` 下的设备/从站，例如 `EIP_Card`、`H5U`、`Easy`。 |
| `producerTags` | 生产者标签。 |
| `serverMessageTags` | 顶层 EtherNet/IP 服务/服务器标签，不等同于 H5U 从站窗口里的“服务消息标签”页。 |
| `adapter.connections` | EtherNet/IP Adapter 连接，包含 O->T/T->O 实例 ID 和大小。 |
| `adapter.connections[].outputDatasets` | 输出数据集。 |
| `adapter.connections[].inputDatasets` | 输入数据集。 |
| `devices[].general` | 选中从站的“通用”页视图，包含 IP、电子匹配和 Identity。 |
| `devices[].info` | 选中从站的“信息”页视图，包含设备名、模板键和 Identity。 |
| `devices[].status` | 选中从站的“状态”页视图；这是运行态只读信息，离线 JSON 中只标记不可编辑。 |
| `devices[].pages` | 从站页面/底层记录的完整字段索引。简单设备会额外导出 `standardConnection` 语义页；其余字段按 primary records、private general、private connection blocks、private datasets、private extra 分组。 |
| `devices[].producerTags` / `devices[].serverMessageTags` / `devices[].adapter` | 顶层生产者标签、顶层服务/服务器标签和 Adapter I/O 数据集的设备页别名。顶层字段仍是导出 JSON 的规范位置；最小 JSON 可在顶层缺省时只写这些别名。 |
| `devices[].serviceMessageTags` | H5U 等从站窗口 `服务消息标签` 页，包含标签名、目标标签、数据类型、元素数量、连接类型、设置类型、触发类型和触发条件。 |
| `availableDataTypes` | 服务消息标签等通用 EtherNet/IP 标签类型参考。 |
| `availableAdapterDataTypes` | Adapter I/O 数据集的 AutoShop UI 实际可选类型。 |
| `catalog` | 从 AutoShop `sys/EipEds/*.eds` 和 `deviceLibraryPath` 指向的设备模板库合并出的 EtherNet/IP 设备库。 |

Adapter 的 `outputDatasets[].dataType` 和 `inputDatasets[].dataType` 只能使用 `INT`、`DINT`、`REAL`。这是 AutoShop 当前 Adapter I/O 数据集下拉的实际限制；虽然 EtherNet/IP 标签层还存在 `BOOL`、`BYTE`、`STRING` 等通用类型，但这些不能作为 Adapter I/O 数据集类型写入。`workspace apply` 会拒绝不在 `availableAdapterDataTypes` 中的类型。

`ethernetIP.devices` 的编辑规则与 EtherCAT 顶层从站一致：修改既有设备时改对应对象的顶层字段、`parameters`、`records[].value` 或 `privateRecords[].value`；删除设备时从数组移除，写成空数组 `[]` 会清空 EtherNet/IP 从站设备表；新增同型号/同结构设备时追加带 `templateKey` 的对象；从设备库新增时可只写 `internalName`、`deviceName` 或 `toolboxName`，值写 AutoShop 工具箱或模板库里的设备名称。`catalogKey` 来自 `ethernetIP.catalog.devices[].key`，仅作为高级诊断字段。如果同型号 `templateAvailable=true`，apply 会优先克隆完整工程模板；当前工程没有同型号模板但 `deviceLibraryPath` 指向的模板库存在模板时，会从模板库克隆完整 `records` 和/或私有 `0x20` 工程树记录；然后从 catalog 默认补齐 `vendorId`、`productType`、`productCode`、`majorRevision`、`minorRevision` 等身份字段。仍没有模板时默认拒绝，避免把 EDS 基础 identity 记录误认为完整 AutoShop UI 参数保真。确实只需要基础 EDS 设备记录时，显式设置 `"allowGeneratedFromCatalog": true`。

`devices[].pages` 是完整字段索引和兜底编辑入口，不替代语义字段。每个字段包含 `value`、`originalValue`、`editable`、`source`、`recordKey`、`field`、`dataHex` 和推荐 `editPath`。apply 只有在 `value` 与 `originalValue` 不同，或显式写 `apply:true` 时才会写回该字段，因此导出 JSON 原样应用不会用页面旧值覆盖 `general`、`connections` 等语义编辑。`editable:false` 的字段表示该底层记录由更高层语义字段、实例规划或 AutoShop 运行态管理；例如 H5U 结构化连接块和数据集应编辑 `devices[].connections`、`devices[].tagConnections` 或 `devices[].ioMappings`，直接改对应 page 字段会被拒绝并返回推荐路径。`EIP_Card`、`Easy` 和其它单 primary connection 简单设备会导出 `standardConnection` 页，字段包括 `enabled`、`rpiMs`、O->T/T->O assembly、大小、`outputConnectionType`、`inputConnectionType`、`outputConnectionPriority`、`inputConnectionPriority`、`electronicKeying`；连接类型和优先级均使用与 H5U 相同的语义文本，apply 自动转回 primary record 编码。

`deviceLibraryPath` 可指向模板库根目录或 `ethernet-ip/index.json` 所在目录；当前正式库在 `D:\program\PLC\AutoShopAgentInterfaceWork\device-library`。未显式配置时，CLI 会从当前工程目录和发布 exe 目录向上查找 `AutoShopAgentInterfaceWork\device-library`，因此常规工程可直接用最小 JSON 新增。`EIP_Card`、`Easy`、`H5U` 已有 `records + privateRecords` 模板，可用最小 JSON 新增并在 apply 后回读补全；`Generic_EtherNet_IP_device` 已作为 private-only 模板接入，可通过 `internalName` / `deviceName` / `toolboxName` 新增、删除和保真回读，但没有 primary device records，字段级编辑以 `privateRecords` 中已识别的值为准。

EtherNet/IP 设备导出会包含 `instance` 诊断视图，记录 AutoShop 已分配的 `primaryGroup`、`privateGroup`、`deviceIndex`、private `typeCode/treeCode/primaryLink` 和 `_IPn_*` 变量名。修改既有设备时，CLI 会保留这些实例状态，只同步用户显式修改的 IP、identity、RPI、I/O size、assembly instance、显示名等字段；不会按 JSON 数组下标重算 `deviceIndex`、private `typeCode/treeCode` 或变量名。新增设备时，CLI 会从当前工程模板或正式模板库克隆 `records/privateRecords`，再按缺失字段补齐实例状态；private-only 设备没有 primary records，未显式提供 `instance.typeCode` / `instance.treeCode` 时会按当前工程已规划的 primary/private 占用情况分配未占用值，避免和既有设备树节点冲突。正常使用时不建议手工改 `instance`、`records` 和 `privateRecords` 里的联动字段；若 JSON 中只填写 `internalName` / `deviceName` / `toolboxName` 和必要参数，`workspace apply` 后再 `workspace export` 会回读补全完整 `records`、`privateRecords` 与 `instance`。

同一 `toolboxName` 连续新增多个 EtherNet/IP 设备时，`toolboxName` 必须继续保持 AutoShop 工具箱叶子名称，例如都写 `H5U`；CLI 会自动把 AutoShop 工程树显示名写成 `H5U`、`H5U_1`、`H5U_2` 等实例名。不要把第二个设备的 `toolboxName` 写成 `H5U_1`，否则会导致设备库匹配失败。

`workspace apply` 还会同步 `SYS_EIP.eIPgvt`：系统变量名优先来自 `privateRecords` / `instance` 中真实保存的 `_IPn_*` 引用；CLI 会保留既有系统变量行，只在新增设备需要的变量缺失时追加补齐，不会因为当前设备列表变短就重建或删除历史 `_IPn_*` 行。Adapter 连接里的 `outputDatasets[].variableName` / `inputDatasets[].variableName` 也会按数据集类型自动补齐成系统变量，避免 AutoShop 编译时报 I/O 映射变量无效。这样更贴近 AutoShop 的保存行为，也可以避免用户手工改错 `_IPn_*` 或 `_Connection*` 变量导致 AutoShop 工程树或 I/O 映射漂移。如果导出的 JSON 没有语义变化，apply 不会为了“规范化”私有字节而重写 `EIP.dat`；但会继续检查 `EIP.datBAK` 这类镜像文件，若镜像仍是旧内容，会把镜像同步到当前 `EIP.dat` 字节，避免只看主文件读回正确、重开工程却仍受旧镜像影响。除此之外，`workspace export -> workspace apply --dry-run` 应保持无实际变更。

常用 `devices[]` 字段：

| 字段 | 含义 |
| --- | --- |
| `key` | 本次导出的稳定键；`templateKey` 引用它。 |
| `internalName` / `deviceName` / `toolboxName` | 新增设备时可只填写其中一个名称，例如 `H5U`、`Easy`、`EIP_Card`、`Generic_EtherNet_IP_device`；三者同时出现时必须解析到同一个模板。 |
| `name` / `catalogKey` | 根据 Vendor/Product/Revision 推断的设备名和身份键；`catalogKey` 仅作为高级诊断字段。 |
| `allowGeneratedFromCatalog` | 默认 `false`。没有当前工程模板和外部语义模板时，CLI 会拒绝新增以保证 AutoShop UI 参数保真；显式设为 `true` 才允许按 EDS 生成基础设备记录。 |
| `ipAddress` | 设备 IP。 |
| `vendorId` / `productType` / `productCode` / `majorRevision` / `minorRevision` | EDS/CIP 身份字段。 |
| `electronicKeying` | 通用页“电子匹配”，取值 `compatible-module`、`exact-match`、`disable-keying`；中文别名 `兼容模块`、`精确匹配`、`禁止匹配` 也可写入。 |
| `general` / `info` / `status` | 从站编辑页视图。`general` 和顶层 IP/Identity/电子匹配互通；只改 `general.ipAddress`、`general.electronicKeying` 或 identity 字段也会写回底层 records/privateRecords。`info` 为只读诊断回退，不作为写入优先字段；`status.editable=false` 表示状态页没有离线可写字段。 |
| `parameters` | 已确认设备字段，优先编辑这里。 |
| `instance` | AutoShop 实例状态诊断视图；普通编辑不要手工改，apply 会为新增设备自动补齐。 |
| `connections` | 设备从站侧普通 I/O 连接。H5U 等设备在 `EIP.dat` 中会为每个连接占用一个 primary group，但导出 JSON 会折叠在同一个从站对象下。 |
| `tagConnections` | 设备从站侧标签连接，例如 H5U 消费者标签连接。 |
| `producerTags` / `serverMessageTags` / `adapter` | 顶层生产者标签、顶层服务/服务器标签和 Adapter 数据集的设备页别名。导出的顶层字段存在时顶层字段优先；最小 JSON 可省略顶层字段，只写这些别名。顶层服务/服务器标签显式写 `dataType` 时优先于旧导出的 `dataTypeCode`，避免只改类型名时被旧编码覆盖。 |
| `serviceMessageTags` | H5U 等从站窗口 `服务消息标签` 页的语义编辑入口。不要用 `serverMessageTags` 修改该页。 |
| `ioMappings` | 页面别名式 I/O 映射入口；用于直接对应 H5U 等从站窗口里的 `EtherNet/IP I/O映射` 页。也可直接改 `adapter.connections[].outputDatasets/inputDatasets` 或 `connections[].outputDatasets/inputDatasets`。 |
| `records` | 设备完整 AutoShop 私有记录视图，用于型号专属字段保真和兜底编辑。 |
| `privateRecords` | AutoShop 工程树使用的私有 `0x20` 记录；导出用于保真和诊断，普通新增优先通过模板库补全。 |

`devices[].connections[]` 可编辑 `name`、`connectionPath`、`rpiMs`、`timeoutMultiplier`、`triggerType`、`transportType`、`connectionType`、`outputConnectionType`、`inputConnectionType`、`connectionPriority`、`outputConnectionPriority`、`inputConnectionPriority`、`outputFixedVariable`、`inputFixedVariable`、`outputTransferFormat`、`inputTransferFormat`、`outputInhibitTimeMs`、`inputInhibitTimeMs`、`proxyConfigSizeBytes`、`targetConfigSizeBytes`、`outputAssemblyInstance`、`inputAssemblyInstance`、`configurationAssemblyInstance`、`outputSizeBytes`、`inputSizeBytes`、`inputVariable`、`outputVariable`、`inputDatasets`、`outputDatasets`。`connectionType` 是连接类型简写，会同时设置 O->T 和 T->O 两侧连接类型；`outputConnectionType` / `inputConnectionType` 可分别覆盖输出方向和输入方向，取值为 `null`、`multicast`、`point-to-point`，中文 `组播`、`点对点` 也可写入，缺省时优先沿用导出 JSON 中的 privateRecords 原值，否则按 `point-to-point` 补齐。`connectionPriority` 是优先级简写，会同时设置 O->T 和 T->O 两侧优先级；`outputConnectionPriority` / `inputConnectionPriority` 可分别覆盖输出方向和输入方向，取值为 `low`、`high`、`Scheduled`、`urgent`，缺省时优先沿用导出 JSON 中的 privateRecords 原值，否则按 `Scheduled` 补齐。`transportType` 取值 `exclusive-owner`、`input-only`、`listen-only`；`triggerType` 当前支持 AutoShop 已验证的 `cyclic`；固定/变量字段取值 `fixed`、`variable`；传输格式取值 `pure-data`、`heartbeat`、`run-idle-32bit`，中文 `纯数据`、`心跳`、`32bit运行/空闲` 也可写入。`timeoutMultiplier` 使用 UI 显示值 `4/8/16/32/64/128/256/512`；旧版导出的 `1/2` 会兼容归一为实际默认 `16`。缺省时 CLI 按 AutoShop H5U 规则补齐：连接名 `Connection1/2/...`，RPI 50ms，超时倍增 16，触发类型循环，传输类型 `exclusive-owner`，配置 Assembly 从 100 开始每个普通连接递增 2，输入 Assembly 为配置 Assembly + 1，输出 Assembly 为 `0xFFFFFFFF`，大小默认 100 byte，连接路径自动生成 `20 04 2C <config> 2C <input>`，输出格式 `run-idle-32bit`，输入格式 `pure-data`，数据集默认生成 `INT` 数组变量。

H5U 等结构化从站的 I/O 映射页变量名可以通过 `devices[].ioMappings[].variableName` 修改；apply 会同步首个 `inputDatasets/outputDatasets` 变量、连接派生字段 `inputVariable/outputVariable`、`privateRecords` 中的 AutoShop 私有记录以及 `SYS_EIP.eIPgvt`。单数据项连接的 `inputSizeBytes/outputSizeBytes` 是大小主语义，写回时会同步首个数据项和 `ioMappings` 的 bit length，避免旧导出映射位长覆盖连接页面大小。如果只改 `connections[].inputDatasets/outputDatasets` 而旧导出 `ioMappings` 未改，apply 会自动让 `ioMappings` 跟随数据集；如果同一个字段在数据集和 `ioMappings` 两边都被改成不同值，会直接报冲突，生产 JSON 应避免对同一字段双写。

当已有标签连接占用 primary group 时，最小 JSON 追加普通连接会自动跳过已占用 group/deviceIndex，避免把新普通连接和已有标签连接写到同一个底层 primary group。

H5U 普通连接、标签连接以及简单设备 `standardConnection` 的连接类型/优先级都会同步到对应 primary group 的主记录。primary 记录 `0x0014/0x0015` 分别是 O->T/T->O 连接类型，底层值 `0x2000=multicast`、`0x4000=point-to-point`、`0=null`；`0x0016/0x0017` 分别是 O->T/T->O 优先级，底层值 `0x0000=low`、`0x0400=high`、`0x0800=Scheduled`、`0x0C00=urgent`。AutoShop 编辑窗口会优先反映这些 primary 字段，因此 JSON 写回会统一修正 primary/private 两侧，避免只改 private 后 UI 无变化。

`devices[].tagConnections[]` 可编辑 `name`、`tag`、`rpiMs`、`timeoutMultiplier`、`triggerType`、`transportType`、`connectionType`、`outputConnectionType`、`inputConnectionType`、`connectionPriority`、`outputConnectionPriority`、`inputConnectionPriority`、`outputFixedVariable`、`inputFixedVariable`、`outputTransferFormat`、`inputTransferFormat`、`outputInhibitTimeMs`、`inputInhibitTimeMs`。连接类型、优先级、固定/变量、传输格式字段含义与普通连接相同。缺省时 CLI 补齐名称 `消费者标签1/2/...`、标签 `tag0/tag1/...`、RPI 50ms、超时倍增 16，并按 AutoShop 的“连接标签/只输入/心跳输出/纯数据输入”结构写入 private 连接块，即 `transportType=input-only`、`outputTransferFormat=heartbeat`、`inputTransferFormat=pure-data`。标签连接不会生成 I/O 数据集系统变量。

`devices[].serviceMessageTags[]` 可编辑 H5U 从站 `服务消息标签` 页：`name`、`targetTag`、`instanceId`、`elementCount`、`dataType`、`dataTypeCode`、`connectionType`、`settingType`、`triggerType`、`triggerCondition`、`variableName`。缺省时 CLI 按 AutoShop 新增行规则补齐：名称 `服务者标签1/2/...`、目标标签 `tag0/tag1/...`、实例 ID 从 `10` 开始、元素数量 `1`、数据类型 `INT`、连接类型 `class3`、设置类型 `originator-read`、触发类型 `cyclic`、触发条件 `50`，变量名按 `_IP<primaryGroup>_<index>` 生成。`connectionType` 支持 `class3`、`ucmm`；`settingType` 支持 `originator-read`、`originator-write`；`triggerType` 支持 `cyclic`、`application-trigger`。写回时 CLI 会同步 H5U 私有服务标签块 `0x0F9C00/0x0F9Dxx/0x0F9Exx`、primary `0x0200xx` 服务标签记录和 `SYS_EIP.eIPgvt` 缺失变量。`serverMessageTags` 仍保留为顶层标签，不能用于修改 H5U 从站这个页面。

示例：为 H5U 保留/生成 3 个普通连接和 2 个标签连接：

```json
{
  "internalName": "H5U",
  "connections": [{}, {}, {}],
  "tagConnections": [{}, {}]
}
```

示例：用当前工程的 H5U 模板克隆一个 Easy：

```json
{
  "key": "device_002_Easy",
  "templateKey": "device_001_H5U",
  "name": "Easy",
  "ipAddress": "192.168.1.4",
  "productCode": 269,
  "parameters": {
    "ipAddress": "192.168.1.4",
    "productCode": 269
  }
}
```

示例：直接用 AutoShop 工具箱名称新增 Easy：

```json
{
  "key": "device_002_Easy",
  "toolboxName": "Easy",
  "ipAddress": "192.168.1.77",
  "parameters": {
    "outputSizeBytes": 120,
    "inputSizeBytes": 124,
    "rpiMs": 50
  }
}
```

示例：只写内部名称新增 H5U，让 apply 自动补齐记录和变量：

```json
{
  "internalName": "H5U",
  "ipAddress": "192.168.1.77",
  "parameters": {
    "rpiMs": 50
  }
}
```

`workspace apply` 会重建 `EIP.dat`，并同步 `EIP.datBAK`；原文件带有效尾部 CRC32 时会重算校验。EtherNet/IP 设备新增/删除会同步 `devices[].records` 主记录、`devices[].privateRecords` 私有 `0x20..0x27` 工程树记录和 `SYS_EIP.eIPgvt` 系统变量表；`Generic_EtherNet_IP_device` 属于 private-only 设备，可通过 `internalName` / `deviceName` / `toolboxName` 从设备库新增，但不会生成 primary device records，其 private `typeCode/treeCode` 会按当前工程占用情况自动选择未冲突值。`EIP.data` 仍作为真实成员文件保留在 `files` 中。

EtherNet/IP private group 的低 4 位写在 24-bit record id 的高 4 位中，高位写在 kind 字节 `0x20..0x27` 中；因此 group 16 开始会使用 kind `0x21`，当前 CLI 支持 private groups `0..127`。

## 5. 完整指令索引

### 5.1 config

```powershell
autoshop-agent.exe config init [--config path] [--project dir] [--autoshop-exe path] [--device-library path] [--force]
autoshop-agent.exe config show [--config path] [--format json]
autoshop-agent.exe config validate [--config path]
autoshop-agent.exe config get <key> [--config path]
autoshop-agent.exe config set <key> <value> [--config path]
autoshop-agent.exe config profile add <name> --transport ethernet --ip <ip> [--port <port>]
autoshop-agent.exe config profile add <name> --transport usb
autoshop-agent.exe config profile list
autoshop-agent.exe config profile remove <name>
```

### 5.2 workspace

```powershell
autoshop-agent.exe workspace export --project <dir> --out <workspace-dir> [--force] [--format json]
autoshop-agent.exe workspace apply --project <dir> --in <workspace-dir> [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
```

### 5.3 project 和 project node

```powershell
autoshop-agent.exe project info --project <dir|hcp|hcpp|updown> [--format json]
autoshop-agent.exe project tree --project <dir> [--format json]
autoshop-agent.exe project check --project <dir> [--strict] [--format json]
autoshop-agent.exe project backup --project <dir> --out <zip|dir> [--format json]
autoshop-agent.exe project archive pack --project <dir> --out <zip> [--format json]
autoshop-agent.exe project archive unpack --in <zip> --out <dir> [--format json]
autoshop-agent.exe project compare --left <project> --right <project|target> [--detail] [--format json]
autoshop-agent.exe project node list --project <dir> [--category program|config|monitor|report|trace|variable|all] [--format json]
autoshop-agent.exe project node info --project <dir> --name <node> [--format json]
autoshop-agent.exe project node export --project <dir> --name <node> --out <path> [--as auto|binary|json|zip] [--format json]
autoshop-agent.exe project node import --project <dir> --name <node> --in <path> [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
autoshop-agent.exe project node refresh --project <dir> --name <node> [--format json]
```

`project node` 是节点级诊断/兼容入口。能用 workspace JSON 表达的内容，优先走 `workspace export/apply`。

### 5.4 pou

```powershell
autoshop-agent.exe pou list --project <dir> [--format json]
autoshop-agent.exe pou show --project <dir> --name MAIN [--format json]
autoshop-agent.exe pou export --project <dir> --name MAIN --out MAIN.st.txt [--format json]
autoshop-agent.exe pou export-all --project <dir> --out <dir> [--format json]
autoshop-agent.exe pou import --project <dir> --name MAIN --in MAIN.st.txt [--dry-run] [--allow-open-project] [--refresh] [--format json]
autoshop-agent.exe pou add --project <dir> --name SBR_002 --type program|subprogram|interrupt|fb|fc [--language litest] [--text <litest>] [--dry-run] [--allow-open-project] [--no-backup] [--format json]
autoshop-agent.exe pou rename --project <dir> --from OLD --to NEW [--format json]
autoshop-agent.exe pou remove --project <dir> --name SBR_002 [--dry-run] [--allow-open-project] [--no-backup] [--format json]
```

`pou add` 会创建 POU 源文件，并同步 `folder.txt`、`.hcp` 和 `.hcpp`；JSON 输出中的 `hcppUpdated=true` 表示工程包已补齐新成员。`pou remove` 会删除 POU 源文件，并同步 `folder.txt`、`.hcp` 和 `.hcpp`；若 `.hcp` 中存在 `FileName` 为空但 `Caption`/`Alias` 匹配的损坏 POU 登记，也会按索引清理模式删除该隐藏残留并同步 `.hcpp`。默认禁止在目标工程已由 AutoShop 打开时写入，必须先关闭工程或显式传 `--allow-open-project`。`pou rename` 当前仍只返回安全计划，不实际改工程。新增 POU 的推荐方式仍是在 workspace 中新增 `*.pou.json` 后 `workspace apply`。

### 5.5 st

```powershell
autoshop-agent.exe st format --in source.st --out source.formatted.st
autoshop-agent.exe st lint --in source.st [--target h5u|easy] [--firmware <version>] [--format json]
autoshop-agent.exe st parse --in source.st [--format json]
autoshop-agent.exe st symbols --in source.st [--format json]
autoshop-agent.exe st refs --in source.st --symbol <name> [--format json]
autoshop-agent.exe st scaffold mb-master --out example.st
autoshop-agent.exe st scaffold fb-call --name <FB> --out call.st
autoshop-agent.exe st instruction search <keyword> [--format json]
autoshop-agent.exe st instruction show <name> [--format json]
```

### 5.6 var 和 var table

```powershell
autoshop-agent.exe var list --project <dir> [--scope global|local|system] [--format json]
autoshop-agent.exe var export --project <dir> --out vars.csv|vars.json [--format json]
autoshop-agent.exe var import --project <dir> --in vars.csv|vars.json [--merge|--replace] [--format json]
autoshop-agent.exe var bind --project <dir> --name <var> --device D100 [--format json]
autoshop-agent.exe var validate --project <dir> [--format json]
autoshop-agent.exe var system list --project <dir> [--group ethernet|com|can|ecat|motion|info] [--format json]
autoshop-agent.exe var system show --project <dir> --name _SYS_COM [--format json]
autoshop-agent.exe var system export --project <dir> --name _SYS_COM --out _SYS_COM.svt [--format json]
autoshop-agent.exe var system import --project <dir> --name _SYS_COM --in _SYS_COM.svt [--dry-run] [--allow-open-project] [--refresh] [--format json]
autoshop-agent.exe var system refresh --project <dir> --name _SYS_COM [--format json]
autoshop-agent.exe var table list --project <dir> [--category system|global|internal|all] [--all] [--format json]
autoshop-agent.exe var table info --project <dir> --name variable|device|struct|fb-instance|_SYS_COM [--format json]
autoshop-agent.exe var table export --project <dir> --name variable --out 变量表.gvt [--as binary|json|hex|base64] [--format json]
autoshop-agent.exe var table import --project <dir> --name variable --in 变量表.gvt [--dry-run] [--allow-open-project] [--no-backup] [--force] [--refresh] [--format json]
autoshop-agent.exe var table refresh --project <dir> --name variable [--format json]
```

变量内容编辑不要用 `var table import` 直接替换私有二进制；优先改 workspace 中的 `variables`、`definition.members`、`instances`。

### 5.7 build

```powershell
autoshop-agent.exe build check --project <dir> [--format json]
autoshop-agent.exe build diagnostics --project <dir> [--format json]
autoshop-agent.exe build compile --project <dir> [--clean] [--backend simulator] [--format json]
autoshop-agent.exe build down --project <dir> --out <file.down> [--include-source] [--retain keep|init] [--backend simulator] [--format json]
autoshop-agent.exe build updown --project <dir> --out <file.updown> [--include-source] [--retain keep|init] [--backend simulator] [--format json]
```

当前 `compile/down/updown` 是 simulator 后端产物，不等同于 AutoShop 官方私有编译器生成的可下载文件。

### 5.8 target / online / monitor

```powershell
autoshop-agent.exe target scan [--transport ethernet|usb|index:N|<visible-text>] [--backend simulator|hardware] [--timeout-ms 15000] [--format json]
autoshop-agent.exe target transports --backend hardware [--timeout-ms 15000] [--format json]
autoshop-agent.exe target connect --profile <name> [--backend simulator] [--format json]
autoshop-agent.exe target connect --backend hardware [--profile <name>] [--transport ethernet|usb|index:N|<visible-text>] [--ip <plc-ip>] [--test=true|false] [--timeout-ms 15000] [--format json]
autoshop-agent.exe target info --profile <name> [--format json]
autoshop-agent.exe target login --profile <name> [--password <value>] [--format json]
autoshop-agent.exe target logout --profile <name> [--format json]
autoshop-agent.exe target run --profile <name> [--yes] [--format json]
autoshop-agent.exe target stop --profile <name> [--yes] [--format json]
autoshop-agent.exe target mode --profile <name> [--format json]
autoshop-agent.exe target download --profile <name> --project <dir> [--yes] [--format json]
autoshop-agent.exe target upload --profile <name> --out <dir|updown> [--format json]
autoshop-agent.exe target download-file --profile <name> --in <down|updown> [--yes] [--format json]
autoshop-agent.exe target upload-updown --profile <name> --out <file.updown> [--format json]
autoshop-agent.exe online enter --profile <name> --project <dir> [--format json]
autoshop-agent.exe online status --profile <name> [--format json]
autoshop-agent.exe online patch --profile <name> --project <dir> --in <patch-file> [--yes] [--format json]
autoshop-agent.exe online commit --profile <name> [--yes] [--format json]
autoshop-agent.exe online exit --profile <name> [--format json]
autoshop-agent.exe online compare --profile <name> --project <dir> [--format json]
autoshop-agent.exe monitor read --profile <name> --device D100 [--format json]
autoshop-agent.exe monitor write --profile <name> --device D100 --value 123 [--yes] [--format json]
autoshop-agent.exe monitor watch --profile <name> --items D100,M0,TEST --interval 100ms --out samples.ndjson
autoshop-agent.exe monitor memory save --profile <name> --project <dir> --out snapshot.json [--format json]
autoshop-agent.exe monitor memory load --profile <name> --project <dir> --in snapshot.json [--yes] [--format json]
autoshop-agent.exe monitor recipe save --profile <name> --project <dir> --out recipe.json [--format json]
autoshop-agent.exe monitor recipe apply --profile <name> --project <dir> --in recipe.json [--yes] [--format json]
```

`target transports --backend hardware` 只读取 AutoShop `通讯设置` 下拉框的全部通讯类型，返回 `transports[].index/text/selected`，不点击搜索或测试。`target scan --backend hardware` 和 `target connect --backend hardware` 会复用 AutoShop 官方 UI 的 `工具 -> 通讯设置` 流程，并在后台窗口保护中执行：`scan` 选择通讯类型后点击搜索并返回 AutoShop 搜索列表数量；`connect` 选择通讯类型、必要时写入设备 IP、读回校验 `appliedIp`，默认点击 `测试`，AutoShop 返回已连通后点击 `确定`。`--transport` 可使用 `ethernet`、`usb`、`index:N`，也可直接传 AutoShop 下拉框中的可见文字；如果传 `--test=false`，CLI 只写入并确认通讯设置，不声明已连通。除这几个硬件入口外，本节其他 `target`、`online`、`monitor` 命令仍只操作本地模拟状态，不运行、不停止、不下载、不上传真实 PLC；真实 RUN/STOP/下载/上载/监控按钮仍使用 `ui run`、`ui stop`、`ui download`、`ui upload`、`ui monitor`。

### 5.9 trace / diagnose

```powershell
autoshop-agent.exe trace list --project <dir> [--format json]
autoshop-agent.exe trace add --project <dir> --name <trace> --items D100,D200,TEST [--format json]
autoshop-agent.exe trace start --profile <name> --name <trace> [--format json]
autoshop-agent.exe trace stop --profile <name> --name <trace> [--format json]
autoshop-agent.exe trace export --project <dir> --name <trace> --out trace.csv [--format json]
autoshop-agent.exe trace remove --project <dir> --name <trace> [--format json]
autoshop-agent.exe diagnose target --profile <name> [--format json]
autoshop-agent.exe diagnose logs --profile <name> --out logs.json [--format json]
autoshop-agent.exe diagnose error-code <code> [--domain program|modbus|ethercat|motion|system] [--format json]
autoshop-agent.exe diagnose project --project <dir> [--format json]
autoshop-agent.exe diagnose bundle --project <dir> [--profile <name>] --out support.zip [--format json]
```

`trace` 当前是本地侧车定义和导出，不启动真实 PLC 采样。

### 5.10 comm / motion

```powershell
autoshop-agent.exe comm serial show --project <dir> [--format json]
autoshop-agent.exe comm serial set --project <dir> --port COM1 --baud 9600 --data-bits 8 --parity none --stop-bits 1 [--format json]
autoshop-agent.exe comm modbus-rtu master add --project <dir> --name <name> --port COM1 --addr <id> [--format json]
autoshop-agent.exe comm modbus-tcp master add --project <dir> --name <name> --ip <ip> --port 502 [--format json]
autoshop-agent.exe comm ethernet show --project <dir> [--format json]
autoshop-agent.exe comm ethernet set-ip --profile <name> --ip <ip> --mask <mask> --gateway <gateway> [--yes] [--format json]
autoshop-agent.exe comm can show --project <dir> [--format json]
autoshop-agent.exe comm canopen import-eds --project <dir> --in <file.eds> [--format json]
autoshop-agent.exe comm ethercat import-xml --project <dir> --in <file.xml> [--format json]
autoshop-agent.exe comm ethercat scan --profile <name> [--format json]
autoshop-agent.exe comm ethercat status --profile <name> [--format json]
autoshop-agent.exe motion axis list --project <dir> [--format json]
autoshop-agent.exe motion axis add --project <dir> --name Axis1 --type ethercat|pulse [--format json]
autoshop-agent.exe motion axis set --project <dir> --name Axis1 --param <key=value> [--format json]
autoshop-agent.exe motion axis status --profile <name> --name Axis1 [--format json]
autoshop-agent.exe motion group list --project <dir> [--format json]
autoshop-agent.exe motion group add --project <dir> --name Group1 --axes Axis1,Axis2 [--format json]
autoshop-agent.exe motion cam import --project <dir> --name Cam1 --in cam.csv [--format json]
autoshop-agent.exe motion cam export --project <dir> --name Cam1 --out cam.csv [--format json]
autoshop-agent.exe motion hsc list --project <dir> [--format json]
autoshop-agent.exe motion hsc add --project <dir> --name Counter1 --mode linear|rotary [--format json]
```

这些组当前是 simulator / 本地侧车能力。真实工程配置优先通过 workspace 中的配置 JSON 修改。

### 5.11 ui

```powershell
autoshop-agent.exe ui windows [--format json]
autoshop-agent.exe ui tree [--format json]
autoshop-agent.exe ui refresh --program MAIN [--format json]
autoshop-agent.exe ui refresh-path --path "全局变量/变量表" [--title 变量表] [--format json]
autoshop-agent.exe ui close-project --project <dir> [--project-file <hcp|hcpp>] [--autoshop-exe <path>] [--state project-state.json] [--timeout-ms 20000] [--save-prompt save|discard|cancel|fail] [--dry-run] [--format json]
autoshop-agent.exe ui restore-project [--project <dir>] [--state project-state.json] [--project-file <hcp|hcpp>] [--autoshop-exe <path>] [--timeout-ms 20000] [--dry-run] [--format json]
autoshop-agent.exe ui refresh-project --project <dir> [--save-prompt save|discard|cancel|fail] [--dry-run] [--format json]
autoshop-agent.exe ui close --program MAIN [--format json]
autoshop-agent.exe ui close --title H5U [--format json]
autoshop-agent.exe ui open --program MAIN [--format json]
autoshop-agent.exe ui open-path --path "系统变量表/_SYS_COM" [--title _SYS_COM] [--format json]
autoshop-agent.exe ui open-path --path "配置/CAN(CANLink)/CANlink配置" --top-title "CANLink3.0" [--format json]
autoshop-agent.exe ui focus --program MAIN [--format json]
autoshop-agent.exe ui compile [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui compile-all [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui run [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui stop [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui download [--yes] [--run-after] [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui upload [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui monitor [--timeout-ms 15000] [--lines errors|all] [--tail 200] [--dismiss-dialog=true] [--format json]
autoshop-agent.exe ui output [--pane compile|communication|transfer|search|visible|all] [--lines errors|all] [--tail 0] [--format json]
autoshop-agent.exe ui screenshot --out autoshop.png [--format json]
autoshop-agent.exe ui screenshot --title 变量表 --out var-table.png [--format json]
autoshop-agent.exe ui screenshot --program MAIN --out main-editor.png [--client] [--format json]
autoshop-agent.exe ui screenshot --title 变量表 --out var-table.png [--offscreen-visible 0] [--format json]
autoshop-agent.exe ui screenshot --hwnd 0x1234 --out window.png [--allow-minimized] [--format json]
autoshop-agent.exe ui dev-audit-pages --pid <pid> --path "配置/EtherCAT/GR10_0808ETNE" --preset ethercat --out <dir> [--format json]
autoshop-agent.exe ui dev-audit-pages --pid <pid> --path "配置/EtherCAT/GS20-ECT-8L" --pages "common=110,28;process=110,76;startup=110,126;slot=110,174;io=110,224;info=110,272;status=110,320" --out <dir> [--format json]
autoshop-agent.exe ui dev-clicks --hwnd 0x1234 --clicks "row=45,42" [--double] [--post] [--format json]
autoshop-agent.exe ui dev-key --hwnd 0x1234 --keys "down,enter" [--format json]
autoshop-agent.exe ui dev-h5u-tag-connection --row <n> [--inspect-only] [--input-connection-type multicast|point-to-point] [--out <dir>] [--timeout-ms 15000] [--format json]
```

后台窗口保护会用 `SM_XVIRTUALSCREEN/SM_YVIRTUALSCREEN/SM_CXVIRTUALSCREEN/SM_CYVIRTUALSCREEN` 读取当前虚拟屏幕边界，按右下角外侧计算临时位置，因此兼容不同分辨率、缩放布局和带负坐标的多显示器。`--offscreen-visible` 大于 0 时会在屏幕边缘保留对应像素用于诊断；默认 `0` 表示完全离屏。操作结束后使用启动前保存的 `WINDOWPLACEMENT` 恢复 AutoShop 的原恢复矩形；若原来是最小化，使用不激活窗口的最小化状态恢复，避免用户从任务栏重新打开时窗口留在屏幕外；如果 AutoShop 截图期间抢到前台，会同样使用最小化兜底保护用户前台窗口。

`ui open-path --title` 用于打开工程树中的 MDI 子窗口；`ui open-path --top-title` 用于打开 CANLink、CANopen、H5U 参数等同进程顶层配置窗口，JSON 会返回该顶层窗口的 `handle`，后续可传给 `ui dev-inspect-window --hwnd` 或 `ui screenshot --hwnd` 采样。`ui compile` 对应 AutoShop 的 `Ctrl+F7` 编译按钮，`ui compile-all` 对应 `F7` 全部编译，`ui run` 对应 `F5` 运行，`ui stop` 对应 `F6` 停止，`ui download` 对应 `F8` 下载，`ui upload` 对应 `F9` 上载，`ui monitor` 对应 `F3` 监控。它们在后台窗口保护内通过 AutoShop 主窗口句柄发送 `WM_COMMAND`，不会使用全局键盘、全局鼠标或剪贴板。JSON 返回包含 `commandId`、`shortcut`、`output`、`outputChanged` 和 `dialogs`；其中 `output` 来自下方“信息输出窗口”的 ListBox，`dialogs` 会采集本次命令新弹出的 AutoShop 模态提示文本和按钮。`--lines errors` 是默认值，只返回错误行；需要完整读取编译过程、时间戳和普通状态行时使用 `--lines all`。`--tail` 限制过滤后返回的末尾行数，`0` 表示全部；JSON 中 `output.count` 是控件总行数，`output.returnedCount` 是本次实际返回行数。`--dismiss-dialog=true` 会读取并自动确认 AutoShop 的连接状态类 `确定` 弹窗；`ui monitor` / `ui run` / `ui stop` 会优先处理这类弹窗，避免循环调用时堆积大量模态窗口。`ui download --yes` 会确认 AutoShop 的下载设置和下载过程提示，并返回 `confirmedDialogs`；如果遇到下载后是否运行 PLC 的提示，默认选择不运行，只有显式 `--run-after` 才会同意运行。`ui upload` 只触发并采集上载弹窗/输出，不自动确认可能改写当前 AutoShop 会话的上载流程。若需要人工保留弹窗可设为 `false`。

`ui output` 单独读取下方“信息输出窗口”，`--pane compile` 读取“编译”，`communication` 读取“通讯”，`transfer` 读取“转换”，`search` 读取“查找结果”，`visible` 读取当前可见页，`all` 返回全部输出页。默认 `--lines errors` 适合自动化只取报错；完整输出使用 `--lines all --tail 0`。AutoShop 的输出 ListBox 是 owner-draw 控件，CLI 会从 item data 指针读取 AutoShop 进程内字符串并按工程文本编码解码；当前 `project001` 默认按 `gb2312` 处理。

`ui focus` 只通过 `MDIClient` 的 `WM_MDIACTIVATE` 激活子窗口；`ui open` / `ui refresh` / `ui close` / `ui close-project` / `ui restore-project` 默认使用指定窗口或控件句柄消息，并统一在离屏后台保护中执行。`ui close --title` 可关闭任意已打开的 MDI 参数页，适合批量手动验证时“打开、截图、关闭”以避免 AutoShop 子窗口数量上限影响后续打开。`ui restore-project --project <dir>` 在没有历史 state 文件时会构造临时恢复状态并通过同一套离屏打开流程打开指定工程；若传入 `--state` 则仍严格读取该 state。`ui close-project` / `ui refresh-project` 遇到“工程已修改，是否保存?”时默认保存关闭；可用 `--save-prompt discard` 不保存关闭，`cancel` 取消关闭，`fail` 保持失败。若 AutoShop 弹出其他工程错误或普通确认对话框，CLI 会失败并要求人工处理。

`ui dev-h5u-tag-connection` 是开发期采样命令，只用于研究 AutoShop H5U 普通连接/标签连接编辑子对话框，不进入生产编辑流程。正式内容修改仍必须优先改 workspace JSON 并执行 `workspace apply`。该开发命令同样复用后台窗口保护，并在打开“编辑连接”对话框、组合框下拉窗口等关联顶层窗口时立即移动到离屏位置，避免子框短暂出现在用户当前桌面。传入 `--out` 时会离屏保存编辑子框、内容子窗口和输入连接类型下拉框截图，并在 JSON 输出中附带子控件枚举结果。传入 `--inspect-only` 时只打开、截图、枚举并确认关闭子框，不修改下拉字段。

`ui dev-audit-pages` 是开发期页面截图审查命令，只用于验证/采样，不进入生产编辑流程。命令会离屏打开指定工程树路径，按 `--preset` 或 `--pages name=x,y;...` 点击左侧页面导航并截图；截图文件名包含页序号，例如 `SV820N_1-01-common.png`，即使中文页面名被文件名清洗为 `window` 也不会覆盖同一从站的其它页面。正式内容修改仍必须通过 workspace JSON 完成。

### 5.12 doc

```powershell
autoshop-agent.exe doc sources [--format json]
autoshop-agent.exe doc outline [--manual programming|instruction|user|autoshop|all] [--format json]
autoshop-agent.exe doc search <keyword> [--manual programming|instruction|user|autoshop|all] [--format json]
autoshop-agent.exe doc command-set [--out AutoShopCliCommands.md] [--format json]
```

`doc command-set` 输出的内容与本文件同源，用于重新生成指令文档。

## 6. 兼容别名

旧入口仍可用，但新流程应优先使用完整命令：

```powershell
autoshop-agent.exe list --project <dir> [--json]
autoshop-agent.exe export --project <dir> --program MAIN --out MAIN.st.txt
autoshop-agent.exe import --project <dir> --program MAIN --in MAIN.st.txt [--allow-open-project] [--refresh]
autoshop-agent.exe refresh --program MAIN
autoshop-agent.exe windows [--json]
```

## 7. 验收建议

文件层编辑的最小验收顺序：

1. `workspace apply --dry-run --format json`，确认没有格式错误、冲突或只读字段修改。
2. 如果 `ui windows --format json` 显示 AutoShop 当前打开的就是目标工程，先执行 `ui close-project --project <dir> --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json`；若打开的是其他工程，不要关闭。
3. 正式 `workspace apply --format json`，检查每个变更项的 `verified=true`。
4. 如第 2 步关闭过工程，执行 `ui restore-project --state D:\program\PLC\AutoShopAgentInterfaceWork\current-project-state.json --format json` 恢复工程和窗口。
5. 重新 `workspace export --force` 到固定目录，读取 JSON 确认语义字段已回读为预期值。

当前没有 PLC 真机后端。所有真机相关指令只能作为接口占位和离线测试入口使用。



