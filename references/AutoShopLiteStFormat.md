# AutoShop Lite ST 容器记录

维护或诊断 `scripts/autoshop-agent.exe` 时使用本文档。

## 已验证的容器结构

已测试的 AutoShop Lite 工程中，`MAIN.ST`、`INT_001.ST`、`SBR_001.ST` 不是纯文本文件，而是二进制容器。每个文件都以 ASCII 签名 `AutoShop` 开头。

可编辑的 ST 源码位于文件尾部，是最后一个 MFC 风格的 `CString` 文本块，后面跟随 4 个 `00` 字节。

长度头规则：

- `length < 0xFF`：1 字节长度。
- `length < 0xFFFF`：`FF` 加 2 字节小端长度。
- 更长文本：`FF FF FF` 加 4 字节小端长度。

CLI 写回 ST 时只替换这个最终文本块，并保留其余二进制内容。

## 功能块/函数 POU 样本

用户在 AutoShop 内手动创建的功能块和函数证明，FB/FC 不是普通 `.ST` 程序块：

- 功能块文件使用 `.FB` 扩展名，`folder.txt` 的 `FB` 区登记 `FILE <name>.FB`，`.hcp` 中登记 `FileType=81`、`ProgType=7`、`POUID=-1`。
- 函数文件使用 `.FC` 扩展名，`folder.txt` 的 `FC` 区登记 `FILE <name>.FC`，`.hcp` 中登记 `FileType=82`、`ProgType=8`、`POUID=-1`。
- `.FB/.FC` 文件都是两个连续的 `AutoShop` 私有容器。第一个容器的最后一个 `CLVTItem` 对象在 17 字节对象前缀后保存 POU 名称；第二个容器保存空 LiteST 代码体。
- `pou add --type fb|fc` 必须从 `.FB/.FC` 模板生成并替换内部名称，不能创建 `.ST` 后放入 `FB`/`FC` 区。

之前错误生成的 `FB_ASAI_001.ST`、`FC_ASAI_001.ST` 是孤立错误文件；AutoShop 会从可见 `folder.txt` 树中移除它们，`.hcp` 中可能留下空 `FileName` 的旧登记。

## 全局变量表样本

`全局变量/变量表/变量表.gvt` 已通过用户在 AutoShop 内手工创建变量得到样本。该文件是 AutoShop 5.03 `CLVTItem` 序列化格式，顶层保持 4 个 `CLVTItem` 对象；真实变量行位于最后一个对象的内部数组，不能把第二个变量写成新的顶层对象。

`workspace export` 会在 `变量表.gvt.json` 中导出：

- `format: "autoshop-agent-global-variable-table.v1"`
- `kind: "global-variable-table"`
- `semanticType: "global-variable-table-v5.03"`
- `variables`

`workspace apply` 会根据 `variables` 重建 `.gvt` 内部变量行数组，并复用当前工程 `.gvt` 作为模板。用户不要直接编辑 `.gvt`，也不要为变量表伪造 `contentBase64`。

已按用户样本验证的变量类型码：

- `BOOL=1`
- `INT=4`
- `DINT=16`
- `REAL=32`
- `STRUCT/系统结构/系统联合/自定义结构体=64`
- `ARRAY=128`
- `STRING/STRING<...>=2048`
- `IP=4096`
- `BYTE=8192`

显式类型扩展按记录解析，不依赖行位置：

- `STRING<...>`：MFC `CString(dataType)` + 4 字节小端 `2048`。
- `ARRAY`：MFC `CString(arrayTypeText)` + 4 字节小端 `128` + 4 字节元素类型码 + 4 字节数组长度；当前样本中 `BOOL[0..2]` 导出为 `arrayElementDataType=BOOL`、`arrayLength=3`。
- 结构体/系统结构/系统联合：MFC `CString(dataType)`，当前样本中后面不跟额外类型码；例如 `_sMC_CAMIN`、`Stru`、`Stru_1`。

未采到 POINTER 的可写样本，因此当前文档不声明 POINTER 的语义写回支持。

## 自定义结构体样本

`全局变量/结构体/*.stru` 已按用户创建的 `Stru`、`Stru_1` 样本验证。`workspace export` 会导出：

- `format: "autoshop-agent-struct-definition.v1"`
- `kind: "struct-definition"`
- `semanticType: "struct-definition-v5.03"`
- `definition.name`
- `definition.members`

成员记录支持基础类型和结构体类型。成员名字段在当前样本中带 1 个结尾 `00` 字节，写回时 CLI 会保留该结构。

新增结构体不仅要写出 `.stru` 文件，还必须登记到 `.hcp` 工程索引。CLI 已实现 AutoShop UCode 加密/解密：`workspace apply` 会同步补齐 `<file FileType=31>` 节点、更新 `MaxFileID`，并以 `kind=project-index` 回读校验。

## 功能块实例样本

`全局变量/功能块实例/功能块实例.fbi` 已按用户创建的 `TRIG.F_TRIG` 与 `TRIG.R_TRIG` 实例验证。`workspace export` 会导出：

- `format: "autoshop-agent-fb-instance-table.v1"`
- `kind: "fb-instance-table"`
- `semanticType: "fb-instance-table-v5.03"`
- `instances`

`.fbi` 文件包含两个连续 AutoShop 容器；第一个容器保存实例行，第二个容器按原样保留。写回时 CLI 只重建第一个容器的实例数组，并保留未解析尾部容器。

## 编码

工程内嵌 ST 文本默认按 GB2312/CP936 处理。

导出的 txt 默认按 UTF-8 写出。

除非某个工程已经证明使用不同编码，否则只通过 JSON 配置或 CLI 参数调整编码，不要在代码里写死特殊规则。

## 安全边界

已支持：

- 列出现有 `*.ST` 程序容器。
- 导出内嵌 ST 源码。
- 将 txt 写回既有 `*.ST` 容器。
- 将 `变量表.gvt.json` 的 `variables` 写回全局变量表。
- 将 `*.stru.json` 的 `definition.members` 写回自定义结构体定义。
- 将 `功能块实例.fbi.json` 的 `instances` 写回功能块实例表。

未支持：

- 删除或重命名 POU 节点；新增程序块/中断/FB/FC 已通过 `pou add` 支持，但 workspace 目录内直接新增 POU 文件尚未作为主流程支持。
- 编辑 `.hcp` 工程表。
- 语义化编辑硬件配置、交叉引用数据，或未采样确认的其它私有表格式。

写回默认创建备份。只有显式传入 `--no-backup` 时才跳过备份。
