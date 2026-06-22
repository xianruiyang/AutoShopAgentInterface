# EtherCAT / EtherNet-IP / CANopen 从站类型与采集状态

## 1. 生成信息

- 更新时间：2026-06-22。
- 目标工程：`<project-dir>`。
- 固定映射目录：`<workspace-dir>`。
- 设备模板库：`<device-library-dir>`。
- 采集脚本：`<package-dir>Work\agent-generated-files\collect_ethercat_templates.py` 与 `collect_ethernet_ip_templates.py`。
- 安全策略：采集脚本只向 AutoShop 主窗口、TreeView、菜单弹窗或工具栏等已知句柄发送 Win32 消息；不使用全局键盘、全局鼠标或按屏幕坐标反查当前窗口。
- 外部资料只用于确认 ESI/EDS 的角色；AutoShop 工程内私有记录、主站记录、EIP 私有尾部和父子拓扑必须以本机 AutoShop 样本采集为准。
- 参考：[EtherCAT Technology Group：ESI 规范下载页](https://www.ethercat.org/cn/downloads/downloads_48EF1F220AF54F77AF58921401342864.htm)。
- 参考：[ODVA：EZ-EDS 工具说明](https://www.odva.org/subscriptions-services/additional-tools/request-ez-eds/)。

## 2. 状态定义

| 字段 | 含义 |
| --- | --- |
| `toolboxName` | AutoShop 工具箱设备库树中用户能看到并选择的叶子名称；JSON 最小新增时优先填写这个字段。 |
| 内部型号 | ESI/EDS 或工程文件中的 `name` / `model`，不一定等同于 AutoShop UI 的设备名称。 |
| 正式采集 | 是否已经写入 `device-library` 模板库，并通过 JSON 解析和索引校验。 |
| 当前工程样本 | 当前 `project001` 导出里是否还保留该型号实例；这只表示当前工程状态，不代表模板库状态。 |
| 记录数 | 模板中保真的设备记录数；复杂设备还可能带原始文件或父子拓扑。 |

## 3. 汇总

| 总线 | AutoShop UI 可见类型数 | CLI Catalog 条目数 | 正式采集数 | 当前工程样本数 | 备注 |
| --- | ---: | ---: | ---: | ---: | --- |
| EtherCAT | 32 | 36 | 32 | 2 | 32 个工具箱叶子型号均已采集；分支器为父子组合模板。 |
| EtherNet/IP | 4 | 4 | 4 | 4 | `EIP_Card`、`Easy`、`H5U`、`Generic_EtherNet_IP_device` 均已采集；Generic 为 AutoShop 内置通用设备，当前以 private-only 记录保真。 |
| CANopen | 15 | 17 | 15 | 1 | 右侧 Inovance CANopen 工具箱叶子已全部采集为正式 `device-library/canopen` 模板；CLI 从 `sys/eds` 可解析 17 个 EDS 条目。 |

- EtherCAT 模板索引 SHA256：`C42D5AED66CDD6BC95BA93F86498A83F18CC3CAABEF97AE9D2E6EE820F61F660`。
- EtherNet/IP 模板索引 SHA256：`7B48D7692F87C69E8D12726CE54A226668BE9B1FEB49E0183506D20136D7FB05`。
- CANopen 模板索引 SHA256：`332653E23C3CA0696BEA398209500CAC5A344669B965FCB7AD159C7ED6019427`。
- EtherNet/IP 采集发现：普通 EDS 设备在 `ethernetIP.devices` 中有 primary `records` 和私有 `privateRecords`；`Generic_EtherNet_IP_device` 是 private-only 设备，会出现在 `ethernetIP.devices`，但不会生成 primary device records。
- EtherNet/IP 开发期 reset 必须使用干净 EIP 基线并同步 `.hcpp` 里的 `EIP.dat` 条目；仅把 JSON devices 置空还不足以阻止 AutoShop 从私有尾部/工程包快照恢复旧设备。

## 4. EtherCAT 从站类型

| # | 分组 | toolboxName | 内部型号 | ProductCode | Revision | 模板路径 | 记录数 | 主站记录 | 正式采集 |
| ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | IO耦合器 | `AM600-RTU-ECTA_2.0.7.0` | `AM600-RTU-ECTA` | `10f40202` | `0x01006000` | `ethercat/templates/00100000/10f40202/01006000/AM600-RTU-ECTA/default.json` | 24233 | 52 | 是 |
| 2 | IO耦合器 | `GL10-RTU-ECTA_2.0.7.0` | `GL10-RTU-ECTA` | `10f40910` | `0x01006000` | `ethercat/templates/00100000/10f40910/01006000/GL10-RTU-ECTA/default.json` | 24233 | 52 | 是 |
| 3 | IO耦合器 | `GL20-RTU-ECT_1.3.19.0` | `GL20-RTU-ECT` | `10f41000` | `0x01006000` | `ethercat/templates/00100000/10f41000/01006000/GL20-RTU-ECT/default.json` | 72550 | 57 | 是 |
| 4 | 伺服驱动器 | `ES810N_ECAT_v1.2` | `ES810` | `1190108` | `0x00010001` | `ethercat/templates/00100000/1190108/00010001/ES810/default.json` | 1007 | 77 | 是 |
| 5 | 伺服驱动器 | `IS620N_ECAT_v2.6.8` | `IS620N` | `c0108` | `0x00010001` | `ethercat/templates/00100000/c0108/00010001/IS620N/default.json` | 1007 | 77 | 是 |
| 6 | 伺服驱动器 | `SV510N_ECAT_v1.1.3` | `SV510N` | `10d0109` | `0x00010001` | `ethercat/templates/00100000/10d0109/00010001/SV510N/default.json` | 1052 | 84 | 是 |
| 7 | 伺服驱动器 | `SV520N-Ecat_v0.1.2` | `SV520N` | `c030a` | `0x00010001` | `ethercat/templates/00100000/c030a/00010001/SV520N/default.json` | 1025 | 79 | 是 |
| 8 | 伺服驱动器 | `SV630_1Axis_03713` | `InoSV630N` | `c0112` | `0x00010000` | `ethercat/templates/00100000/c0112/00010000/InoSV630N/default.json` | 1007 | 78 | 是 |
| 9 | 伺服驱动器 | `SV660_1Axis_V0.08` | `InoSV660N` | `c010d` | `0x00010000` | `ethercat/templates/00100000/c010d/00010000/InoSV660N/default.json` | 1007 | 78 | 是 |
| 10 | 伺服驱动器 | `SV635_1Axis_03413` | `InoSV635N` | `c010e` | `0x00010000` | `ethercat/templates/00100000/c010e/00010000/InoSV635N/default.json` | 1007 | 78 | 是 |
| 11 | 伺服驱动器 | `SV680S1Axis_04002` | `InoSV680S` | `c0119` | `0x00010000` | `ethercat/templates/00100000/c0119/00010000/InoSV680S/default.json` | 1241 | 104 | 是 |
| 12 | 伺服驱动器 | `SV680_1Axis_04002` | `InoSV680N` | `c0116` | `0x00010000` | `ethercat/templates/00100000/c0116/00010000/InoSV680N/default.json` | 1241 | 104 | 是 |
| 13 | 多轴伺服驱动器 | `IS810_1Axis_V1.02` | `IS810N` | `c1308` | `0x00010000` | `ethercat/templates/00100000/c1308/00010000/IS810N/default.json` | 1699 | 85 | 是 |
| 14 | 多轴伺服驱动器 | `IS810_2Axis_V2.02` | `IS810N` | `c0308` | `0x00010000` | `ethercat/templates/00100000/c0308/00010000/IS810N/default.json` | 3343 | 124 | 是 |
| 15 | 多轴伺服驱动器 | `SV820_3Axis_V3.03` | `SV820N` | `c310b` | `0x00010000` | `ethercat/templates/00100000/c310b/00010000/SV820N/default.json` | 4987 | 163 | 是 |
| 16 | 多轴伺服驱动器 | `SV820_4Axis_V4.04` | `SV820N` | `c010b` | `0x00010000` | `ethercat/templates/00100000/c010b/00010000/SV820N/default.json` | 6631 | 202 | 是 |
| 17 | 数字IO模块 | `AM600_0808ETNE_1.4.5.0` | `AM600_0808ETNE` | `10f40302` | `0x00000000` | `ethercat/templates/00100000/10f40302/00000000/AM600_0808ETNE/default.json` | 359 | 53 | 是 |
| 18 | 数字IO模块 | `GR10_0808ETNE_1.4.5.0` | `GR10_0808ETNE` | `10f40911` | `0x00000000` | `ethercat/templates/00100000/10f40911/00000000/GR10_0808ETNE/default.json` | 359 | 67 | 是 |
| 19 | 数字IO模块 | `AM600_1616ETNE_1.4.5.0` | `AM600_1616ETNE` | `10f40303` | `0x00000000` | `ethercat/templates/00100000/10f40303/00000000/AM600_1616ETNE/default.json` | 530 | 55 | 是 |
| 20 | 数字IO模块 | `GR10_1616ETNE_1.4.5.0` | `GR10_1616ETNE` | `10f40912` | `0x00000000` | `ethercat/templates/00100000/10f40912/00000000/GR10_1616ETNE/default.json` | 530 | 83 | 是 |
| 21 | 数字IO模块 | `GR10_1616ERE_BD_1.3.0.0` | `GR10_1616ERE_BD` | `10f40919` | `0x00000000` | `ethercat/templates/00100000/10f40919/00000000/GR10_1616ERE_BD/default.json` | 656 | 99 | 是 |
| 22 | 模拟IO模块 | `GR10-4ADE_1.4.4.0` | `GR10-4ADE` | `10f40270` | `0x00000000` | `ethercat/templates/00100000/10f40270/00000000/GR10-4ADE/default.json` | 184 | 61 | 是 |
| 23 | 模拟IO模块 | `GR10-4DAE_1.4.4.0` | `GR10-4DAE` | `10f40271` | `0x00000000` | `ethercat/templates/00100000/10f40271/00000000/GR10-4DAE/default.json` | 198 | 62 | 是 |
| 24 | 模拟IO模块 | `GR10-8TCE_1.4.5.0` | `GR10-8TCE` | `10f40272` | `0x00000000` | `ethercat/templates/00100000/10f40272/00000000/GR10-8TCE/default.json` | 402 | 91 | 是 |
| 25 | 模拟IO模块 | `GR10-2WTE_1.1.0.3` | `GR10-2WTE` | `10f40925` | `0x00000000` | `ethercat/templates/00100000/10f40925/00000000/GR10-2WTE/default.json` | 652 | 78 | 是 |
| 26 | 远程脉冲定位模块 | `AM600-4PME_1.1.3.0` | `AM600-4PME` | `10f40404` | `0x00000000` | `ethercat/templates/00100000/10f40404/00000000/AM600-4PME/default.json` | 1219 | 183 | 是 |
| 27 | 远程脉冲定位模块 | `GR10-4PME_1.1.3.0` | `GR10-4PME` | `10f40913` | `0x00000000` | `ethercat/templates/00100000/10f40913/00000000/GR10-4PME/default.json` | 1219 | 183 | 是 |
| 28 | 远程脉冲定位模块 | `GR10-2PHE_1.1.3.0` | `GR10-2PHE` | `10f40923` | `0x00000000` | `ethercat/templates/00100000/10f40923/00000000/GR10-2PHE/default.json` | 849 | 119 | 是 |
| 29 | 远程脉冲计数模块 | `GR10-2HCE_1.4.5.0` | `GR10-2HCE` | `10f40914` | `0x00000000` | `ethercat/templates/00100000/10f40914/00000000/GR10-2HCE/default.json` | 1251 | 124 | 是 |
| 30 | 远程脉冲计数模块 | `AM600-2HCE_1.4.5.0` | `AM600-2HCE` | `10f40502` | `0x00000000` | `ethercat/templates/00100000/10f40502/00000000/AM600-2HCE/default.json` | 934 | 116 | 是 |
| 31 | EtherCAT Fieldbus modules | `GS20-ECT-8L 1.0.5.3` | `GS20-ECT-8L` | `10f42ee1` | `0x00000001` | `ethercat/templates/00100000/10f42ee1/00000001/GS20-ECT-8L/default.json` | 94730 | 300 | 是 |
| 32 | 分支器 | `GR10-EC-6SW(IN,X2,X3)_1.4.2.3` | `GR10-EC-6SW` | `10f40931` | `0x00010000` | `ethercat/templates/00100000/10f40931/00010000/GR10-EC-6SW/default.json` | 55 / 总 110 | 33 / 总 66 | 是 |

## 5. EtherNet/IP 设备类型

| # | 分组 | toolboxName | 内部型号 | VendorId | ProductType | ProductCode | EDS/来源 | 模板路径 | 记录数 | 正式采集 | 说明 |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- | --- |
| 1 | Inovance Devices | `EIP_Card` | `EIP_Card` | `1660` | `150` | `1` | `sys/EipEds/MD500P_EIP_V1.00.eds` | `ethernet-ip/templates/1660/150/1/1.1/EIP_Card/default.json` | 97 | 是 | 语义设备记录模板 |
| 2 | Inovance Devices | `Easy` | `Easy` | `1660` | `14` | `269` | `sys/EipEds/Easy.eds` | `ethernet-ip/templates/1660/14/269/1.1/Easy/default.json` | 53 | 是 | 语义设备记录模板 |
| 3 | Inovance Devices | `H5U` | `H5U` | `1660` | `14` | `268` | `sys/EipEds/H5U.eds` | `ethernet-ip/templates/1660/14/268/1.1/H5U/default.json` | 53 | 是 | 语义设备记录模板 |
| 4 | Other Devices | `Generic_EtherNet_IP_device` | `Generic_EtherNet_IP_device` | `` | `` | `` | `AutoShop UI built-in Generic_EtherNet_IP_device` | `ethernet-ip/templates/generic/Generic_EtherNet_IP_device/default.json` | 0 / 私有17 | 是 | private-only 模板；映射到 `ethernetIP.devices`，无 primary records |

## 6. CANopen 设备库状态

| # | 分组 | toolboxName | 模板路径 | 节点样本 | 正式采集 |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Inovance | `H5U PLC` | `canopen/templates/000003B9/000E010C/00000000/H5U_PLC/default.json` | 2 | 是 |
| 2 | Inovance | `Easy PLC` | `canopen/templates/000003B9/000E010D/00000000/Easy_PLC/default.json` | 3 | 是 |
| 3 | Inovance | `H3U PLC` | `canopen/templates/000003B9/000E0106/00000000/H3U_PLC/default.json` | 4 | 是 |
| 4 | Inovance | `MD380/MD500_V1.11` | `canopen/templates/000003B9/000B0107/0001000B/MD380_MD500_V1.11/default.json` | 5 | 是 |
| 5 | Inovance | `MD380/MD500_V1.12` | `canopen/templates/000003B9/000B0107/0001000C/MD380_MD500_V1.12/default.json` | 6 | 是 |
| 6 | Inovance | `MD810_INV_V1.2` | `canopen/templates/000003B9/000B0112/00010002/MD810_INV_V1.2/default.json` | 7 | 是 |
| 7 | Inovance | `MD810_INV_V1.5` | `canopen/templates/000003B9/000B0112/00010005/MD810_INV_V1.5/default.json` | 8 | 是 |
| 8 | Inovance | `MD810 INV_V3.0` | `canopen/templates/000003B9/000B0112/00030000/MD810_INV_V3.0/default.json` | 9 | 是 |
| 9 | Inovance | `MD810_REC_VC.2` | `canopen/templates/000003B9/000B0112/000C0002/MD810_REC_VC.2/default.json` | 10 | 是 |
| 10 | Inovance | `MD810_REC_V12.4` | `canopen/templates/000003B9/000B0112/000C0004/MD810_REC_V12.4/default.json` | 11 | 是 |
| 11 | Inovance | `MD810_REC_V13.0` | `canopen/templates/000003B9/000B0112/000D0000/MD810_REC_V13.0/default.json` | 12 | 是 |
| 12 | Inovance | `IS620_V056` | `canopen/templates/000003B9/000D0107/19203800/IS620_V056/default.json` | 13 | 是 |
| 13 | Inovance | `SV630C_V1.1` | `canopen/templates/000003B9/000D030C/00020001/SV630C_V1.1/default.json` | 14 | 是 |
| 14 | Inovance | `SV660C_V1.1` | `canopen/templates/000003B9/000D010C/00020001/SV660C_V1.1/default.json` | 15 | 是 |
| 15 | Inovance | `IS810_V1.1` | `canopen/templates/000003B9/000D0107/01920016/IS810_V1.1/default.json` | 16 | 是 |

- CANopen 模板来自 AutoShop V4.10 右侧设备树真实新增后的 `canopen.data`，通过 `ui dev-tree-read/dev-tree-click` 直接读取/操作 `SysTreeView32` 控件采样，使用 `ID_FILE_SAVE=57603` 落盘。
- 验证副本中按右侧列表新增 15 个设备后，`workspace export` 回读 16 个从站；随后用正式 `device-library/canopen` 从干净单 IS620 工程一次性新增全部右侧设备，导出回读 16 个从站。
- 参数编辑验证：对 16 个从站分别写入 `general.producerHeartbeatTimeMs=401..416`，重新导出全部逐项回读一致。
- 删除验证：从 16 个从站删除 node 2..16，重新导出回到单 node 1。
- 仍不能把 EDS 当成完整模板。公开 CANopen 资料也把 EDS 定义为电子数据表/对象字典描述，AutoShop 工程内 record 2/3/4/5、PDO/I/O 映射起始 D 和私有默认值必须以实际保存样本为准。

## 7. 当前结论

- EtherCAT 32 个 AutoShop UI 可见叶子型号已经全部正式采集到 `device-library/ethercat`。
- EtherNet/IP 4 个 AutoShop UI 可见设备已经全部正式采集到 `device-library/ethernet-ip`。
- CANopen 右侧 15 个 Inovance 工具箱设备已经全部正式采集到 `device-library/canopen`，并完成 JSON 新增、删除和 `general.producerHeartbeatTimeMs` 参数编辑回读验证。
- CLI 已接入 EtherNet/IP 外部模板库：配置 `deviceLibraryPath` 或环境变量 `AUTOSHOP_AGENT_DEVICE_LIBRARY` 后，`workspace export` 会把库模板合并进 catalog，`workspace apply` 可从库中克隆 `EIP_Card`、`Easy`、`H5U` 的完整 `records + privateRecords`，以及 `Generic_EtherNet_IP_device` 的 private-only 记录。
- `project001` 是持续调试工程，设备数量会随样本推进变化，不能作为模板覆盖数的静态依据；截至 2026-06-02 15:17，当前回读为 13 个 H5U 加 1 个 `Generic_EtherNet_IP_device`，Generic 为 `privateOnly=true/treeCode=14`，无重复 `treeCode`。
- 未完成项：未做 AutoShop 前台重开工程截图验收；本轮按用户要求没有操作前台，只完成 CLI 写入、磁盘 readback、重新导出回读和幂等 dry-run。
