# 时序分析工具库
from .statistical import STATISTICAL_TOOLS
from .spectral import SPECTRAL_TOOLS
from .decomposition import DECOMPOSITION_TOOLS
from .forecasters import FORECASTER_TOOLS
from .validators import VALIDATOR_TOOLS

ALL_TOOLS = {
    **STATISTICAL_TOOLS,
    **SPECTRAL_TOOLS,
    **DECOMPOSITION_TOOLS,
    **FORECASTER_TOOLS,
    **VALIDATOR_TOOLS,
}

__all__ = [
    "ALL_TOOLS",
    "STATISTICAL_TOOLS",
    "SPECTRAL_TOOLS",
    "DECOMPOSITION_TOOLS",
    "FORECASTER_TOOLS",
    "VALIDATOR_TOOLS",
]
