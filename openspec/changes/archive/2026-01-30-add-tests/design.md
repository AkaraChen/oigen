## Context

oigen 是一个 OI/ACM 测试数据生成框架，当前代码库包含：
- 核心模块：errors, output, workflow, stress
- 生成器：Int, Double, Char, Bool, Sequence, Tree, Graph, String, Matrix
- 装饰器系统：约束注册和应用

项目已配置 pytest 和 pytest-cov 作为开发依赖，但 `tests/` 目录尚未创建，覆盖率为 0%。

## Goals / Non-Goals

**Goals:**
- 为所有公共函数和类方法编写单元测试
- 覆盖所有代码分支（if/else、异常处理、边界条件）
- 达到 ≥90% 的代码覆盖率
- 测试可重复执行（固定随机种子）
- 测试运行快速（避免 I/O 密集操作，使用 mock）

**Non-Goals:**
- 集成测试（跨模块端到端测试）
- 性能测试/基准测试
- 修改现有代码逻辑
- 100% 覆盖率（部分防御性代码难以触发）

## Decisions

### 1. 测试目录结构

采用镜像源码的扁平结构：

```
tests/
├── conftest.py              # 共享 fixtures
├── test_errors.py
├── test_output.py
├── test_workflow.py
├── test_stress.py
├── generators/
│   ├── test_primitives.py
│   ├── test_sequence.py
│   ├── test_tree.py
│   ├── test_graph.py
│   ├── test_string.py
│   └── test_matrix.py
└── decorators/
    └── test_base.py
```

**理由**：与源码结构一致，便于查找和维护。

### 2. 测试框架选择

使用 pytest + pytest-cov（已在 pyproject.toml 中配置）。

**理由**：项目已有依赖，无需额外引入。pytest 的 fixture 和参数化功能适合测试生成器的多种输入组合。

### 3. 随机性处理

所有涉及随机的测试使用固定种子：
- 通过 `conftest.py` 提供 `seeded_random` fixture
- 每个测试用例使用独立的 Random 实例

**理由**：确保测试可重复，失败时可复现。

### 4. Mock 策略

- `output.py`：Mock `rich.console.Console` 避免终端输出
- `stress.py`：Mock `subprocess.run` 避免执行真实程序
- `workflow.py`：使用临时目录（pytest `tmp_path` fixture）

**理由**：隔离外部依赖，加速测试执行。

### 5. 参数化测试

对生成器使用 `@pytest.mark.parametrize` 覆盖：
- 边界值（min=max、空集合、单元素）
- 无效输入（触发 ConstraintError）
- 典型输入

**理由**：减少重复代码，清晰展示测试用例。

### 6. 覆盖率配置

在 `pyproject.toml` 中配置：
```toml
[tool.coverage.run]
source = ["oigen"]
branch = true

[tool.coverage.report]
fail_under = 90
show_missing = true
```

**理由**：`branch = true` 确保分支覆盖，`fail_under = 90` 强制达标。

## Risks / Trade-offs

**[风险] 生成器输出具有随机性** → 使用固定种子 + 统计验证（如生成 1000 次检查分布）

**[风险] stress.py 依赖外部可执行文件** → 创建简单的测试用脚本作为 fixture，或完全 mock subprocess

**[风险] output.py 依赖终端状态** → Mock Console 的 `is_terminal` 属性

**[权衡] 测试代码量可能较大** → 接受，测试覆盖比代码简洁更重要

**[权衡] 部分防御性代码难以触发** → 标记为 `# pragma: no cover`，记录原因
