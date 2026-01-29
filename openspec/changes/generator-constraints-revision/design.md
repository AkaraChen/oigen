## Context

oigen 第一轮设计完成了基础框架，但生成器的约束能力较弱。OI/ACM 出题中经常需要生成满足特定性质的数据（如直径为 D 的树、带负环的图、满足行列和约束的矩阵）。本次修订旨在大幅增强约束表达能力。

核心设计理念：**装饰器优先，参数最小化**。

## Goals / Non-Goals

**Goals:**
- 生成器 class 只保留最基础的通用参数
- 所有特殊约束通过装饰器注入和组合
- 装饰器可自由叠加，形成 pipeline
- 保持声明式、可读性强的 API

**Non-Goals:**
- 不实现完整的图论算法库
- 不保证所有约束组合都能在多项式时间内生成
- 不支持交互式约束调整

## Decisions

### 1. 装饰器注入约束模式

**Decision:** 生成器只有最基本参数，所有约束通过装饰器叠加。

```python
@with_diameter(5, 8)        # 直径约束
@with_centroid(count=1)     # 重心约束
@with_edge_weight(Int(1, 100))
def my_tree():
    return Tree(n=10)       # Tree 只需要 n
```

**Rationale:**
- class 参数少 → 学习成本低
- 装饰器组合 → 灵活性高
- 声明式 → 可读性好

### 2. 统一的生成器基础参数

**Decision:** 每种生成器只保留最核心参数：

| 生成器 | 核心参数 |
|--------|----------|
| `Tree` | `n`（节点数） |
| `Graph` | `n`, `m`（节点数、边数） |
| `Sequence` | `element`, `length` |
| `Matrix` | `rows`, `cols` |
| `String` | `length` |

其他一切通过装饰器：

```python
# Tree 装饰器
@with_node_weight(generator)   # 点权
@with_edge_weight(generator)   # 边权
@with_diameter(min, max)       # 直径
@with_centroid(count)          # 重心
@with_depth(min, max)          # 深度

# Graph 装饰器
@with_node_weight(generator)
@with_edge_weight(generator)
@with_cycle(negative=False)    # 带环（可指定负环）
@with_path(start, end)         # 保证通路
@with_cut_vertex(count)        # 割点
@directed                      # 有向图

# Matrix 装饰器
@as_maze(path='.', wall='#')   # 迷宫模式
@with_path_between(start, end) # 保证迷宫通路
@with_border(symbol)           # 边界约束
@row_sum_max(value)            # 行和上限
@col_sum_max(value)            # 列和上限
@with_operator(op, max_val)    # 自定义算子上限

# Sequence 装饰器
@with_relation(lambda a, b: condition)  # 相邻元素关系
@monotonic(direction='increasing')      # 单调性
@prefix_sum_bounded(max_val)            # 前缀和约束

# String 装饰器
@from_template(pattern)         # 模板匹配
@must_contain(substrings)       # 必须包含子串
@as_trie_words(count, max_depth) # Trie 词集
@from_charset(chars)            # 字符集
```

### 3. 装饰器组合语义

**Decision:** 装饰器从下往上执行，约束累加。

```python
@with_diameter(5)
@with_centroid(1)
@with_edge_weight(Int(1, 10))
def tree_data():
    return Tree(n=10)
```

等价于：先生成 n=10 的树 → 注入边权 → 约束重心 → 约束直径。

内部实现时，约束在生成前收集，统一规划生成策略。

### 4. 约束冲突检测

**Decision:** 装饰器注册时检查兼容性，冲突时立即报错。

```python
@with_diameter(20)  # 直径 20
def bad_tree():
    return Tree(n=10)  # 只有 10 个节点

# ❌ 错误：直径不能超过 n-1
```

### 5. Matrix 统一模型

**Decision:** Matrix 只有一个类，通过装饰器切换模式。

```python
# 迷宫矩阵
@as_maze(path='.', wall='#')
@with_path_between((0, 0), (9, 9))
def maze():
    return Matrix(rows=10, cols=10)

# 数值矩阵
@row_sum_max(100)
@col_sum_max(100)
def numeric():
    return Matrix(rows=5, cols=5, element=Int(1, 20))
```

**Rationale:** 一个 Matrix class，装饰器决定其行为，避免类爆炸。

### 6. String 统一模型

**Decision:** String 只有一个类，通过装饰器定义生成规则。

```python
# 随机字符串
@from_charset("abc")
def random_str():
    return String(length=100)

# 模板字符串
@from_template("ab*cd*ef")  # * 是通配
@from_charset("abcdef")
def template_str():
    return String(length=20)

# Trie 词集
@as_trie_words(count=10, max_depth=5)
@from_charset("az")
def trie_words():
    return String()  # 返回词集而非单个字符串
```

### 7. 生成策略

**Decision:** 收集所有装饰器约束后，选择最优生成策略。

策略选择逻辑：
1. 如果有专用构造算法（如指定直径的树），使用构造法
2. 否则使用生成-验证-重试，设置最大重试次数
3. 超过重试次数报错，提示约束可能过严

## Risks / Trade-offs

**[Risk]** 装饰器顺序可能让用户困惑 → 文档明确说明从下往上执行

**[Risk]** 太多装饰器影响 IDE 补全 → 按类型分组，提供良好的 docstring

**[Trade-off]** Lambda 约束无法序列化 → 接受限制，用户保存代码

**[Trade-off]** 某些约束组合效率低 → 文档说明性能特性

## Open Questions

1. 是否提供装饰器预设组合（如 `@bamboo_tree` = `@with_diameter(n-1)`）？
2. 装饰器是否支持运行时动态参数（如 `@with_diameter(lambda n: n//2)`）？
