## 1. 装饰器基础设施

- [x] 1.1 创建 decorators/ 目录结构
- [x] 1.2 实现 Constraint 基类，用于收集装饰器约束
- [x] 1.3 实现装饰器注册机制，支持约束累加
- [x] 1.4 实现约束冲突检测框架
- [x] 1.5 实现友好的约束冲突错误消息

## 2. Tree 生成器重构

- [x] 2.1 重构 Tree(n) 只保留 n 参数
- [x] 2.2 实现 @with_node_weight(generator) 装饰器
- [x] 2.3 实现 @with_edge_weight(generator) 装饰器
- [x] 2.4 实现 @with_diameter(min, max) 装饰器
- [x] 2.5 实现直径约束的构造算法（先构造主链）
- [x] 2.6 实现 @with_centroid(count) 装饰器
- [x] 2.7 实现重心约束的构造算法
- [x] 2.8 实现 @with_depth(min, max) 装饰器
- [x] 2.9 添加 Tree 约束冲突检测（如直径 > n-1）

## 3. Graph 生成器重构

- [x] 3.1 重构 Graph(n, m) 只保留 n, m 参数
- [x] 3.2 实现 @with_node_weight(generator) 装饰器
- [x] 3.3 实现 @with_edge_weight(generator) 装饰器
- [x] 3.4 实现 @directed 装饰器
- [x] 3.5 实现 @with_cycle(negative) 装饰器
- [x] 3.6 实现带环图的构造算法
- [x] 3.7 实现负环图的构造算法
- [x] 3.8 实现 @with_path(start, end) 装饰器
- [x] 3.9 实现保证通路的构造算法
- [x] 3.10 实现 @with_cut_vertex(count) 装饰器
- [x] 3.11 实现割点约束的构造算法
- [x] 3.12 实现 @with_longest_path(min, max) 装饰器
- [x] 3.13 实现 @allow_self_loops 装饰器
- [x] 3.14 实现 @allow_multi_edges 装饰器
- [x] 3.15 添加 Graph 约束冲突检测

## 4. Sequence 生成器增强

- [x] 4.1 实现 @with_relation(predicate) 装饰器
- [x] 4.2 实现关系约束的生成-验证-重试策略
- [x] 4.3 实现 @monotonic(direction) 装饰器
- [x] 4.4 实现单调序列的直接构造算法
- [x] 4.5 实现 @prefix_sum_bounded(max_val) 装饰器
- [x] 4.6 实现前缀和约束的生成策略

## 5. String 生成器（新）

- [x] 5.1 创建 generators/string.py
- [x] 5.2 实现 String(length) 基础生成器
- [x] 5.3 实现 @from_charset(chars) 装饰器
- [x] 5.4 实现 @from_template(pattern) 装饰器
- [x] 5.5 实现模板解析（* 通配符）
- [x] 5.6 实现 @must_contain(substrings) 装饰器
- [x] 5.7 实现子串约束的生成策略
- [x] 5.8 实现 @as_trie_words(count, max_depth) 装饰器
- [x] 5.9 实现 Trie 词集生成算法
- [x] 5.10 添加 String 约束冲突检测（如字符集不包含必须子串字符）

## 6. Matrix 生成器（新）

- [x] 6.1 创建 generators/matrix.py
- [x] 6.2 实现 Matrix(rows, cols, element) 基础生成器
- [x] 6.3 实现 @as_maze(path, wall) 装饰器
- [x] 6.4 实现 @with_path_between(start, end) 装饰器
- [x] 6.5 实现迷宫通路生成算法（DFS/BFS）
- [x] 6.6 实现 @with_border(symbol) 装饰器
- [x] 6.7 实现 @with_coord_constraint(predicate) 装饰器
- [x] 6.8 实现 @row_sum_max(value) 装饰器
- [x] 6.9 实现 @col_sum_max(value) 装饰器
- [x] 6.10 实现行列和约束的生成策略
- [x] 6.11 实现 @row_product_max(value) 装饰器
- [x] 6.12 实现 @col_product_max(value) 装饰器
- [x] 6.13 实现 @with_row_operator(op, max_val) 装饰器
- [x] 6.14 实现 @with_col_operator(op, max_val) 装饰器
- [x] 6.15 添加 Matrix 约束冲突检测

## 7. API 更新

- [x] 7.1 从 __init__.py 移除 Dict 导出
- [x] 7.2 添加 String 导出
- [x] 7.3 添加 Matrix 导出
- [x] 7.4 导出所有新装饰器
- [x] 7.5 更新 __all__ 列表

## 8. 测试

- [x] 8.1 测试 Tree 装饰器组合
- [x] 8.2 测试 Graph 装饰器组合
- [x] 8.3 测试 Sequence 装饰器组合
- [x] 8.4 测试 String 装饰器组合
- [x] 8.5 测试 Matrix 迷宫模式
- [x] 8.6 测试 Matrix 数值约束模式
- [x] 8.7 测试约束冲突检测错误消息
- [x] 8.8 性能测试：大规模数据约束生成
