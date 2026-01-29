## Why

第一轮设计中的数据生成器约束不够丰富，无法满足 OI/ACM 出题中常见的特殊数据需求（如带特定重心的树、带负环的图、满足行列和约束的矩阵等）。需要大幅增强各类生成器的约束能力，并新增矩阵生成器和字符串生成器。

## What Changes

- **BREAKING** 移除原 `Dict` 生成器，替换为 `String` 字符串生成器（模板串、子串、字典树）
- 增强 `Tree` 生成器：支持点权/边权/双权输出，支持重心、深度、直径等结构约束
- 增强 `Graph` 生成器：支持点权/边权/双权输出，支持环检测（负/非负）、起终通路、割点、最长路径等约束
- 新增 `Matrix` 生成器：迷宫矩阵（通路/障碍/符号/坐标约束）和数值矩阵（行列和/积/算子上限）
- 增强 `Sequence` 生成器：支持元素间自定义算子关系约束

## Capabilities

### New Capabilities

- `string-generation`: 字符串算法数据生成，包括模板串生成、子串约束、字典树（Trie）结构生成
- `matrix-generation`: 矩阵数据生成，包括迷宫矩阵（通路/障碍/自定义符号/坐标约束）和数值矩阵（行列总和/乘积/自定义算子上限）

### Modified Capabilities

- `data-generation`:
  - 移除 `Dict` 生成器
  - 增强 `Tree`：点权树、边权树、点权与边权树；重心约束、最小深度、最大深度、直径约束
  - 增强 `Graph`：点权图、边权图、点权与边权图；环约束（负环/非负环）、起点到终点通路、割点约束、最长路径约束
  - 增强 `Sequence`：元素间自定义算子关系约束（如相邻元素差值、前缀和单调性等）

## Impact

- **API 变更**: `Dict` 被移除，使用 `String` 替代（**BREAKING**）
- **新增模块**: `generators/string.py`, `generators/matrix.py`
- **修改模块**: `generators/tree.py`, `generators/graph.py`, `generators/sequence.py`
- **依赖**: 可能需要图算法库支持复杂约束验证
- **文档**: 需更新 API 文档说明新约束参数
