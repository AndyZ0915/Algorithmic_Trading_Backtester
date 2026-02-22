"""Base class for trading strategies."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStrategy(ABC):
    """All strategies inherit from this."""
    
    def __init__(self, name, **params):
        self.name = name
        self.params = params
    
    def _validate_params(self):
        """Override this to add parameter validation."""
        pass
    
    @abstractmethod
    def generate_signals(self, data):
        """
        Main method - returns data with 'signal' column added.
        1 = buy, -1 = sell, 0 = hold
        """
        pass
    
    def calculate_indicators(self, data):
        """Optional: calculate indicators before generating signals."""
        return data.copy()
    
    def get_parameters(self):
        return self.params.copy()
    
    def __str__(self):
        params_str = ', '.join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.name}({params_str})"
    
    def __repr__(self):
        return self.__str__()


class BuyAndHoldStrategy(BaseStrategy):
    """Simple buy-and-hold benchmark."""
    
    def __init__(self):
        super().__init__(name="Buy and Hold")
    
    def generate_signals(self, data):
        df = data.copy()
        df['signal'] = 0
        df.loc[df.index[0], 'signal'] = 1  # buy on day 1
        return df
