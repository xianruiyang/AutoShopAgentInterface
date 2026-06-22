# EtherCAT / EtherNet-IP / CANopen 从站类型与采集状态

## 1. 生成信息

- 更新时间：2026-06-01。
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
| CANopen | 14 | 17 | 0 | 1 | 右侧截图可见 14 个 Inovance CANopen 工具箱叶子；CLI 从 `sys/eds` 可解析 17 个 EDS 条目。正式 `device-library/canopen` 模板尚未采集入库；当前工程样本为 IS620/`canopen.data`，临时验证模板未纳入正式库。 |

- EtherCAT 模板索引 SHA256：`C42D5AED66CDD6BC95BA93F86498A83F18CC3CAABEF97AE9D2E6EE820F61F660`。
- EtherNet/IP 模板索引 SHA256：`7B48D7692F87C69E8D12726CE54A226668BE9B1FEB49E0183506D20136D7FB05`。
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

| # | 分组 | toolboxName | 正式采集 | 当前状态 |
| ---: | --- | --- | --- | --- |
| 1 | Inovance | `H5U PLC` | 否 | 仅 EDS/catalog 可见，未采集 AutoShop 保存后的真实 `canopen.data` 模板。 |
| 2 | Inovance | `Easy PLC` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 3 | Inovance | `H3U PLC` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 4 | Inovance | `MD380/MD500_V...` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 5 | Inovance | `MD810_INV_V1.2` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 6 | Inovance | `MD810_INV_V1.5` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 7 | Inovance | `MD810_INV_V3.0` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 8 | Inovance | `MD810_REC_V2...` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 9 | Inovance | `MD810_REC_V12...` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 10 | Inovance | `MD810_REC_V13...` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 11 | Inovance | `IS620_V056` | 否 | 当前工程样本存在，可作为当前工程模板新增/删除；尚未采集入正式 `device-library/canopen`。 |
| 12 | Inovance | `SV630C_V1.1` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 13 | Inovance | `SV660C_V1.1` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |
| 14 | Inovance | `IS810_V1.1` | 否 | 仅 EDS/catalog 可见，未采集真实模板。 |

- 本轮已新增 CANopen 外部模板库机制：当 `deviceLibraryPath/canopen/index.json` 提供 AutoShop 实际保存的 `canopen.data` 模板时，`workspace apply` 可通过 `toolboxName` / `catalogKey` 新增右侧设备库中的对应设备，并继续支持删除和既有参数编辑。
- 不能把 EDS 当成完整模板。公开 CANopen 资料也把 EDS 定义为电子数据表/对象字典描述，AutoShop 工程内 record 2/3/4/5、PDO/I/O 映射起始 D 和私有默认值必须以实际保存样本为准。
- 右侧设备自动采样尝试记录：双击右侧设备树只选中未新增；选中后点击总线触发 AutoShop 弹窗“遇到不适当的参数。”，因此当前 CLI/Win32 路径未能可靠批量采集 14 个右侧真实模板。

## 7. 当前结论

- EtherCAT 32 个 AutoShop UI 可见叶子型号已经全部正式采集到 `device-library/ethercat`。
- EtherNet/IP 4 个 AutoShop UI 可见设备已经全部正式采集到 `device-library/ethernet-ip`。
- CANopen 已支持当前工程模板和外部 `device-library/canopen` 真实模板两种新增路径；正式模板库尚无 14 个右侧设备的真实模板，不能宣称全部设备已离线内置。
- CLI 已接入 EtherNet/IP 外部模板库：配置 `deviceLibraryPath` 或环境变量 `AUTOSHOP_AGENT_DEVICE_LIBRARY` 后，`workspace export` 会把库模板合并进 catalog，`workspace apply` 可从库中克隆 `EIP_Card`、`Easy`、`H5U` 的完整 `records + privateRecords`，以及 `Generic_EtherNet_IP_device` 的 private-only 记录。
- `project001` 是持续调试工程，设备数量会随样本推进变化，不能作为模板覆盖数的静态依据；截至 2026-06-02 15:17，当前回读为 13 个 H5U 加 1 个 `Generic_EtherNet_IP_device`，Generic 为 `privateOnly=true/treeCode=14`，无重复 `treeCode`。
- 未完成项：未做 AutoShop 前台重开工程截图验收；本轮按用户要求没有操作前台，只完成 CLI 写入、磁盘 readback、重新导出回读和幂等 dry-run。
