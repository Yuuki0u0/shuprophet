# 提示词模板
from .system import SYSTEM_PROMPT
from .react import REACT_PROMPT, TOOL_SELECTION_PROMPT
from .critic import CRITIC_PROMPT

__all__ = [
    "SYSTEM_PROMPT",
    "REACT_PROMPT",
    "TOOL_SELECTION_PROMPT",
    "CRITIC_PROMPT",
]
