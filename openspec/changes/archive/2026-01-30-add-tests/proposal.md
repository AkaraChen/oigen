## Why

项目 oigen 是一个功能完整的 OI/ACM 竞赛测试数据生成框架，包含多种生成器、工作流系统和压力测试功能，但目前没有任何单元测试。缺乏测试覆盖会导致重构困难、bug 难以发现、代码质量无法保证。需要为所有函数和逻辑分支编写单元测试，达到至少 90% 的覆盖率。

## What Changes

- 创建完整的测试套件，覆盖所有模块的所有函数
- 测试所有代码分支和边界情况
- 配置 pytest-cov 以跟踪覆盖率
- 确保测试可重复（固定随机种子）
- 目标覆盖率：≥90%

需要测试的模块：
- `oigen/errors.py` - 异常类
- `oigen/output.py` - 终端输出工具（Console 类）
- `oigen/workflow.py` - 数据生成工作流
- `oigen/stress.py` - 压力测试系统
- `oigen/generators/` - 所有生成器（Int, Double, Char, Bool, Sequence, Tree, Graph, String, Matrix）
- `oigen/decorators/base.py` - 约束装饰器系统

## Capabilities

### New Capabilities

- `unit-testing`: 单元测试框架和测试套件，覆盖所有生成器、工作流、压力测试和装饰器系统的验证逻辑、生成逻辑和边界情况

### Modified Capabilities

（无现有 spec 需要修改）

## Impact

- 新增 `tests/` 目录结构
- 可能需要更新 `pyproject.toml` 配置 pytest
- 不影响现有代码功能
- 提升代码可维护性和重构信心
