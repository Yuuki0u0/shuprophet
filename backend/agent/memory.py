"""
推理轨迹记忆 — 存储 Thought/Action/Observation 三元组
"""

import time
from typing import Optional


class ReasoningMemory:
    """Stores the full reasoning trajectory for a single prediction session."""

    def __init__(self):
        self.steps = []
        self.start_time = time.time()

    def add_step(self, thought: str, action: str,
                 action_input: dict, observation: dict):
        """Record one Thought→Action→Observation triple."""
        self.steps.append({
            "step": len(self.steps) + 1,
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "observation": observation,
            "timestamp": round(time.time() - self.start_time, 2),
        })

    def get_summary(self) -> str:
        """Compact text summary for LLM context window."""
        lines = []
        for s in self.steps:
            lines.append(f"[Step {s['step']}] {s['action']} → {_compact(s['observation'])}")
        return "\n".join(lines) if lines else "No observations yet."

    def get_tool_results(self) -> dict:
        """Return all tool observations keyed by tool name."""
        results = {}
        for s in self.steps:
            results[s["action"]] = s["observation"]
        return results

    def to_dict(self) -> dict:
        """Serialize full trajectory for API response."""
        return {
            "steps": self.steps,
            "total_steps": len(self.steps),
            "elapsed": round(time.time() - self.start_time, 2),
        }

    def __len__(self):
        return len(self.steps)


def _compact(obs: dict, max_len: int = 120) -> str:
    """Compact dict to short string for LLM context."""
    parts = []
    for k, v in obs.items():
        if k == "tool":
            continue
        s = f"{k}={v}"
        if len(s) > 40:
            s = s[:37] + "..."
        parts.append(s)
    result = ", ".join(parts)
    return result[:max_len] if len(result) > max_len else result
