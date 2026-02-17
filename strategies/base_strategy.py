"""
Base strategy class - Template Method design pattern.
FIX: _validate_params() no longer called in __init__ to avoid attribute ordering bug.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self, name: str, **params):
        """
        Initialize the strategy.

        Args:
            name: Strategy name
            **params: Strategy-specific parameters
        """
        self.name = name
        self.params = params
        # NOTE: Do NOT call _validate_params() here.
        # Child classes set their attributes AFTER super().__init__(),
        # so validation must be called by the child after setting attributes.

    def _validate_params(self):
        """Override in child classes to validate parameters."""
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        pass

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicators. Override in child classes."""
        return data.copy()

    def get_parameters(self) -> Dict[str, Any]:
        """Return strategy parameters."""
        return self.params.copy()

    def __str__(self) -> str:
        params_str = ', '.join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.name}({params_str})"

    def __repr__(self) -> str:
        return self.__str__()


class BuyAndHoldStrategy(BaseStrategy):
    """Buy and hold benchmark strategy."""

    def __init__(self):
        super().__init__(name="Buy and Hold")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['signal'] = 0
        df.loc[df.index[0], 'signal'] = 1
        return df