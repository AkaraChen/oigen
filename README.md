# oigen

![oigen](https://socialify.git.ci/AkaraChen/oigen/image?language=1&name=1&owner=1&pattern=Brick+Wall&theme=Light)

OI/ACM test data generation framework with stress testing support.

## Installation

```bash
pdm install
```

## Usage

```python
from oigen import Workflow, Int, Sequence

@Workflow
def gen():
    n = Int(1, 100)
    arr = Sequence(Int(1, 1000), length=n)
    return f"{n}\n{arr}"

# Generate test cases
gen.run("tests/", count=10)
```

## Development

```bash
pdm install -G dev
pdm run pytest
```
