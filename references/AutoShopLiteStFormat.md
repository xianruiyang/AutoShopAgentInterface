# AutoShop Lite ST 文件格式记录

## 本地实测结论

工程 `<project-dir>` 中的 `MAIN.ST`、`INT_001.ST`、`SBR_001.ST` 不是纯文本文件，而是以 ASCII 签名 `AutoShop` 开头的二进制容器。

可编辑的 ST 源码位于文件尾部附近，是一个 MFC 序列化风格的 `CString`：

- `长度 < 0xFF`：1 字节长度头。
- `长度 < 0xFFFF`：`FF` + 2 字节小端长度。
- 更长文本：`FF FF FF` + 4 字节小端长度。
- 源码文本后面保留 4 个 `00` 结尾字节。

当前样例中：

- 空程序 `INT_001.ST` / `SBR_001.ST`：源码块偏移 `217`，长度 `0`。
- `MAIN.ST`：源码块偏移 `217`，当前源码长度 `281` 字节。

## 功能块/函数 POU 样本

用户在 AutoShop 内手动创建的功能块和函数证明，FB/FC 不是普通 `.ST` 程序块：

- 功能块文件使用 `.FB` 扩展名，`folder.txt` 的 `FB` 区登记 `FILE <name>.FB`，`.hcp` 中登记 `FileType=81`、`ProgType=7`、`POUID=-1`。
- 函数文件使用 `.FC` 扩展名，`folder.txt` 的 `FC` 区登记 `FILE <name>.FC`，`.hcp` 中登记 `FileType=82`、`ProgType=8`、`POUID=-1`。
- `.FB/.FC` 文件都是两个连续的 `AutoShop` 私有容器。第一个容器的最后一个 `CLVTItem` 对象在 17 字节对象前缀后保存 POU 名称；第二个容器保存 LiteST 代码体。第二个容器不带 `CLVTItem` 字符串，但仍可按 ST 容器的最终 `CString` 源码块读写。
- FB/FC 新增能力通过 `workspace apply` 的 JSON/文本镜像流程使用：在 `编程/功能块(FB)` 或 `编程/函数(FC)` 下新增 `*.pou.json`，CLI 会从 `.FB/.FC` 模板生成并替换内部名称，不能创建 `.ST` 后放入 `FB`/`FC` 区。

之前错误生成的 `FB_ASAI_001.ST`、`FC_ASAI_001.ST` 是孤立错误文件；AutoShop 会从可见 `folder.txt` 树中移除它们，`.hcp` 中可能留下空 `FileName` 的旧登记。

## 编码

AutoShop 内嵌源码按本工程实测应使用 GB2312/CP936 写入。导出的 txt 默认使用 UTF-8。

CLI 配置字段：

```json
{
  "projectTextEncoding": "gb2312",
  "textEncoding": "utf8"
}
```

## 安全边界

当前 CLI 修改已有 `*.ST` 容器中的最终 ST 文本块，并保留其他二进制内容。

通过 workspace JSON 语义层已支持：

- `全局变量/变量表/变量表.gvt.json` 中的 `variables`。该表来自 AutoShop 5.03 `CLVTItem` 序列化样本，顶层仍保持 4 个 `CLVTItem` 对象；真实变量行位于最后一个对象的内部数组。写回时必须由 CLI 重建内部数组，不能把变量写成新的顶层对象，也不应手工编辑 `.gvt` 或 `contentBase64`。
- 已按用户样本验证变量类型码：`BOOL=1`、`INT=4`、`DINT=16`、`REAL=32`、`STRUCT/系统结构/系统联合/自定义结构体=64`、`ARRAY=128`、`STRING/STRING<...>=2048`、`IP=4096`、`BYTE=8192`。
- 显式类型扩展按记录解析，不依赖行位置：`STRING<...>` 是 MFC `CString(dataType)` + 4 字节小端 `2048`；`ARRAY` 是 MFC `CString(arrayTypeText)` + 4 字节小端 `128` + 元素类型码 + 数组长度；结构体/系统结构/系统联合是 MFC `CString(dataType)`，当前样本后面不跟额外类型码。
- 未采到 POINTER 的可写样本，因此当前实现不声明 POINTER 的语义写回支持。
- `全局变量/结构体/*.stru.json` 中的 `definition.members`。已按 `Stru`、`Stru_1` 样本验证，成员记录支持基础类型和结构体类型；成员名字段在当前样本中带 1 个结尾 `00` 字节，写回时 CLI 会保留该结构。
- `全局变量/功能块实例/功能块实例.fbi.json` 中的 `instances`。已按 `TRIG.F_TRIG` 与 `TRIG.R_TRIG` 实例验证；`.fbi` 文件包含两个连续 AutoShop 容器，CLI 只重建第一个容器的实例数组，并保留未解析尾部容器。

未覆盖范围：

- `pou remove` 可删除 POU 源文件，并同步 `folder.txt`、`.hcp` 和 `.hcpp`；`pou rename` 仍只返回安全计划。新增程序块/中断/FB/FC 已通过 workspace `*.pou.json` + `workspace apply` 支持，`pou add` 只作为底层兼容/诊断入口保留。
- 修改 `.hcp` 项目表。
- 语义化修改硬件配置、交叉引用表，或未采样确认的其它私有表格式。
- 自动处理 AutoShop 内部未保存编辑器缓冲区。

写回默认把备份放入同工程目录下的 `.autoshop-agent-backups/<时间戳>/` 文件夹；使用 `--no-backup` 才会跳过。
