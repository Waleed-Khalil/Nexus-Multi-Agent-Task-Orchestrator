"""Tests for agent tools — these run without an API key."""

import json

from app.tools.research import web_search, summarize_document, fact_check, TOOL_DISPATCH as R_DISPATCH
from app.tools.codegen import validate_python, generate_tests, explain_code, TOOL_DISPATCH as C_DISPATCH
from app.tools.data_analysis import (
    compute_statistics,
    detect_outliers,
    suggest_visualization,
    TOOL_DISPATCH as D_DISPATCH,
)


class TestResearchTools:
    def test_web_search(self):
        result = json.loads(web_search("LangGraph tutorial"))
        assert result["tool"] == "web_search"
        assert len(result["results"]) > 0

    def test_summarize_short_text(self):
        assert summarize_document("short") == "short"

    def test_summarize_long_text(self):
        long_text = "a" * 1000
        result = summarize_document(long_text, max_length=100)
        assert len(result) < 1000
        assert result.endswith("[truncated]")

    def test_fact_check(self):
        result = json.loads(fact_check("The sky is blue"))
        assert result["verdict"] == "plausible"

    def test_dispatch_keys(self):
        assert set(R_DISPATCH.keys()) == {"web_search", "summarize_document", "fact_check"}

    def test_dispatch_calls(self):
        result = R_DISPATCH["web_search"]({"query": "test"})
        assert "web_search" in result


class TestCodeGenTools:
    def test_validate_valid_python(self):
        result = json.loads(validate_python("x = 1 + 2"))
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_invalid_python(self):
        result = json.loads(validate_python("def foo("))
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_generate_tests(self):
        result = json.loads(generate_tests("def add(a, b): return a + b", "python"))
        assert result["language"] == "python"

    def test_explain_code(self):
        result = json.loads(explain_code("x = 1\ny = 2\nz = x + y"))
        assert result["total_lines"] == 3

    def test_dispatch_keys(self):
        assert set(C_DISPATCH.keys()) == {"validate_python", "generate_tests", "explain_code"}


class TestDataAnalysisTools:
    def test_compute_statistics(self):
        result = json.loads(compute_statistics([1, 2, 3, 4, 5]))
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["min"] == 1
        assert result["max"] == 5

    def test_compute_statistics_empty(self):
        result = json.loads(compute_statistics([]))
        assert "error" in result

    def test_detect_outliers(self):
        values = [1, 2, 2, 2, 2, 2, 100]
        result = json.loads(detect_outliers(values, threshold=2.0))
        assert len(result["outliers"]) > 0
        assert result["outliers"][0]["value"] == 100

    def test_detect_outliers_few_points(self):
        result = json.loads(detect_outliers([1, 2]))
        assert result["outliers"] == []

    def test_detect_outliers_no_variance(self):
        result = json.loads(detect_outliers([5, 5, 5, 5]))
        assert result["outliers"] == []

    def test_suggest_visualization(self):
        result = json.loads(suggest_visualization("sales by region"))
        assert len(result["suggestions"]) == 3

    def test_dispatch_keys(self):
        assert set(D_DISPATCH.keys()) == {
            "compute_statistics",
            "detect_outliers",
            "suggest_visualization",
        }
