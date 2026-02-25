"""推理提示词模板"""

REACT_PROMPT = """Based on the current observation, decide your next action.

## Data Profile So Far
{memory_summary}

## Current Observation
{observation}

## Instructions
Think step by step:
1. What have I learned so far?
2. What information am I still missing?
3. Which tool should I call next, and why?

Respond in this exact JSON format:
{{"thought": "your reasoning here", "action": "tool_name", "action_input": {{}}, "should_stop": false}}

If you have enough information to make a forecast, set should_stop to true.
If calling a forecaster tool, include "steps" in action_input.
"""

TOOL_SELECTION_PROMPT = """Given the data profile below, select the most relevant tools to run.

Data Profile:
- Trend: {trend}
- Volatility: {volatility}
- Stationarity: {stationarity}
- Seasonality: {seasonality}

Available tools: {tool_list}

Return a JSON list of tool names to run, ordered by priority:
{{"tools": ["tool1", "tool2", ...]}}
"""
