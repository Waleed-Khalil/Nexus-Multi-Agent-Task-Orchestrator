"""Tools available to the DataAnalysisAgent."""

from __future__ import annotations

import json
import math


def compute_statistics(values: list[float]) -> str:
    """Compute basic descriptive statistics for a list of numbers.

    Args:
        values: List of numeric values.

    Returns:
        JSON string with statistics.
    """
    if not values:
        return json.dumps({"tool": "compute_statistics", "error": "Empty dataset"})

    n = len(values)
    mean = sum(values) / n
    sorted_v = sorted(values)
    median = (
        sorted_v[n // 2]
        if n % 2
        else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    )
    variance = sum((x - mean) ** 2 for x in values) / n
    stddev = math.sqrt(variance)

    return json.dumps(
        {
            "tool": "compute_statistics",
            "count": n,
            "mean": round(mean, 4),
            "median": round(median, 4),
            "stddev": round(stddev, 4),
            "min": min(values),
            "max": max(values),
        }
    )


def detect_outliers(values: list[float], threshold: float = 2.0) -> str:
    """Detect outliers using z-score method.

    Args:
        values: List of numeric values.
        threshold: Z-score threshold for outlier detection.

    Returns:
        JSON string with outlier indices and values.
    """
    if len(values) < 3:
        return json.dumps({"tool": "detect_outliers", "outliers": [], "note": "Too few data points"})

    n = len(values)
    mean = sum(values) / n
    stddev = math.sqrt(sum((x - mean) ** 2 for x in values) / n)

    if stddev == 0:
        return json.dumps({"tool": "detect_outliers", "outliers": [], "note": "No variance"})

    outliers = [
        {"index": i, "value": v, "z_score": round(abs(v - mean) / stddev, 2)}
        for i, v in enumerate(values)
        if abs(v - mean) / stddev > threshold
    ]

    return json.dumps({"tool": "detect_outliers", "outliers": outliers, "threshold": threshold})


def suggest_visualization(data_description: str, analysis_type: str = "exploratory") -> str:
    """Suggest appropriate visualization types for a dataset.

    Args:
        data_description: Natural language description of the data.
        analysis_type: Type of analysis being performed.

    Returns:
        JSON string with visualization suggestions.
    """
    return json.dumps(
        {
            "tool": "suggest_visualization",
            "data_description": data_description,
            "suggestions": [
                {"type": "bar_chart", "reason": "Good for comparing categories"},
                {"type": "line_chart", "reason": "Good for trends over time"},
                {"type": "scatter_plot", "reason": "Good for showing correlations"},
            ],
        }
    )


DATA_ANALYSIS_TOOLS = [
    {
        "name": "compute_statistics",
        "description": "Compute descriptive statistics (mean, median, stddev, etc.) for a list of numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numeric values",
                }
            },
            "required": ["values"],
        },
    },
    {
        "name": "detect_outliers",
        "description": "Detect outliers in a dataset using z-score method",
        "input_schema": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numeric values",
                },
                "threshold": {
                    "type": "number",
                    "description": "Z-score threshold",
                    "default": 2.0,
                },
            },
            "required": ["values"],
        },
    },
    {
        "name": "suggest_visualization",
        "description": "Suggest appropriate chart types for data",
        "input_schema": {
            "type": "object",
            "properties": {
                "data_description": {"type": "string", "description": "Description of the data"},
                "analysis_type": {"type": "string", "description": "Type of analysis", "default": "exploratory"},
            },
            "required": ["data_description"],
        },
    },
]

TOOL_DISPATCH = {
    "compute_statistics": lambda args: compute_statistics(args["values"]),
    "detect_outliers": lambda args: detect_outliers(args["values"], args.get("threshold", 2.0)),
    "suggest_visualization": lambda args: suggest_visualization(
        args["data_description"], args.get("analysis_type", "exploratory")
    ),
}
