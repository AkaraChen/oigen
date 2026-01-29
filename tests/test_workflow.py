"""
Tests for oigen.workflow module.
"""

from random import Random
from unittest.mock import patch

import pytest

from oigen.errors import WorkflowError
from oigen.generators import Int, Sequence
from oigen.generators.graph import Graph
from oigen.generators.tree import Tree
from oigen.workflow import (
    Workflow,
    default_formatter,
    workflow,
)


class TestDefaultFormatter:
    def test_primitive_int(self):
        assert default_formatter(42) == "42"

    def test_primitive_float(self):
        assert default_formatter(3.14) == "3.14"

    def test_primitive_str(self):
        assert default_formatter("hello") == "hello"

    def test_simple_list(self):
        assert default_formatter([1, 2, 3]) == "1 2 3"

    def test_nested_list(self):
        result = default_formatter([[1, 2], [3, 4]])
        assert result == "1 2\n3 4"

    def test_empty_list(self):
        assert default_formatter([]) == ""

    def test_dict_with_primitive_values(self):
        result = default_formatter({"a": 1, "b": 2})
        lines = result.split("\n")
        assert len(lines) == 2

    def test_dict_with_list_values(self):
        result = default_formatter({"data": [1, 2, 3]})
        assert "1 2 3" in result

    def test_tree_data(self, rng):
        tree = Tree(n=3).generate(rng)
        result = default_formatter(tree)
        assert "3" in result  # n is in output

    def test_graph_data(self, rng):
        graph = Graph(n=3, m=2).generate(rng)
        result = default_formatter(graph)
        assert "3 2" in result  # n m is in output


class TestWorkflow:
    def test_init_with_generator(self, rng):
        gen = Int(1, 10)
        wf = Workflow(gen)
        assert wf.generator is gen
        assert wf.formatter is default_formatter
        assert wf.name is None

    def test_init_with_custom_formatter(self):
        def custom_fmt(data):
            return f"VALUE: {data}"

        gen = Int(1, 10)
        wf = Workflow(gen, formatter=custom_fmt)
        assert wf.formatter is custom_fmt

    def test_init_with_name(self):
        gen = Int(1, 10)
        wf = Workflow(gen, name="my_workflow")
        assert wf.name == "my_workflow"

    def test_generate_one(self, rng):
        gen = Int(1, 10)
        wf = Workflow(gen)
        result = wf.generate_one(rng)
        assert isinstance(result, int)
        assert 1 <= result <= 10

    def test_generate_one_deterministic(self):
        gen = Int(1, 100)
        wf = Workflow(gen)

        rng1 = Random(42)
        rng2 = Random(42)

        result1 = wf.generate_one(rng1)
        result2 = wf.generate_one(rng2)
        assert result1 == result2

    def test_format(self, rng):
        gen = Int(1, 10)
        wf = Workflow(gen)
        data = wf.generate_one(rng)
        formatted = wf.format(data)
        assert formatted == str(data)

    def test_format_custom_formatter(self, rng):
        def custom_fmt(data):
            return f"num={data}"

        gen = Int(1, 10)
        wf = Workflow(gen, formatter=custom_fmt)
        data = wf.generate_one(rng)
        formatted = wf.format(data)
        assert formatted == f"num={data}"

    def test_run_creates_files(self, tmp_path, rng):
        gen = Int(1, 10)
        wf = Workflow(gen)

        with patch("oigen.workflow.console"):
            files = wf.run(tmp_path, count=3, seed=42)

        assert len(files) == 3
        for f in files:
            assert f.exists()

    def test_run_file_content(self, tmp_path):
        gen = Int(1, 10)
        wf = Workflow(gen)

        with patch("oigen.workflow.console"):
            files = wf.run(tmp_path, count=1, seed=42)

        content = files[0].read_text().strip()
        # Content should be a number between 1 and 10
        assert content.isdigit()
        assert 1 <= int(content) <= 10

    def test_run_seed_reproducibility(self, tmp_path):
        gen = Int(1, 100)
        wf = Workflow(gen)

        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"

        with patch("oigen.workflow.console"):
            files1 = wf.run(dir1, count=3, seed=42)
            files2 = wf.run(dir2, count=3, seed=42)

        for f1, f2 in zip(files1, files2):
            assert f1.read_text() == f2.read_text()

    def test_run_filename_pattern(self, tmp_path):
        gen = Int(1, 10)
        wf = Workflow(gen)

        with patch("oigen.workflow.console"):
            files = wf.run(tmp_path, count=2, filename_pattern="test_{n}.txt")

        assert files[0].name == "test_1.txt"
        assert files[1].name == "test_2.txt"

    def test_run_creates_directory(self, tmp_path):
        gen = Int(1, 10)
        wf = Workflow(gen)

        new_dir = tmp_path / "subdir" / "nested"
        assert not new_dir.exists()

        with patch("oigen.workflow.console"):
            wf.run(new_dir, count=1, seed=42)

        assert new_dir.exists()

    def test_run_invalid_directory_raises(self, tmp_path):
        gen = Int(1, 10)
        wf = Workflow(gen)

        # Create a file where directory would be
        blocker = tmp_path / "blocker"
        blocker.write_text("file")

        invalid_path = blocker / "subdir"  # Can't create dir inside file

        with patch("oigen.workflow.console"):
            with pytest.raises(WorkflowError) as exc_info:
                wf.run(invalid_path, count=1)

        assert "Cannot create output directory" in str(exc_info.value)


class TestWorkflowDecorator:
    def test_as_decorator_without_parentheses(self):
        @workflow
        def my_data():
            return Int(1, 10)

        assert isinstance(my_data, Workflow)
        assert my_data.name == "my_data"

    def test_as_decorator_with_parentheses(self):
        @workflow()
        def my_data():
            return Int(1, 10)

        assert isinstance(my_data, Workflow)
        assert my_data.name == "my_data"

    def test_as_decorator_with_options(self):
        def custom_fmt(data):
            return str(data)

        @workflow(formatter=custom_fmt, name="custom_name")
        def my_data():
            return Int(1, 10)

        assert isinstance(my_data, Workflow)
        assert my_data.formatter is custom_fmt
        assert my_data.name == "custom_name"

    def test_decorator_function_returns_non_generator_raises(self):
        with pytest.raises(WorkflowError) as exc_info:
            @workflow()
            def bad_data():
                return 42  # Not a generator

        assert "must return a generator" in str(exc_info.value)

    def test_workflow_is_functional(self, tmp_path):
        @workflow()
        def my_sequence():
            return Sequence(Int(1, 10), length=5)

        rng = Random(42)
        data = my_sequence.generate_one(rng)
        assert isinstance(data, list)
        assert len(data) == 5

        with patch("oigen.workflow.console"):
            files = my_sequence.run(tmp_path, count=1, seed=42)

        assert len(files) == 1
        assert files[0].exists()
