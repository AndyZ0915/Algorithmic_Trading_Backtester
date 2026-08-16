"""Strategy interfaces. Strategies emit desired position changes, not executions."""
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    name = "Base Strategy"
    def __init__(self, **params): self.params = params
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame: ...
    def calculate_indicators(self, data): return data.copy()
    def validate_data(self, data):
        if data is None or data.empty: raise ValueError("Strategy received no data.")
        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required - set(data.columns)
        if missing: raise ValueError(f"Missing columns: {sorted(missing)}")

class BuyAndHoldStrategy(BaseStrategy):
    name = "Buy & Hold"
    def generate_signals(self, data):
        self.validate_data(data)
        df = data.copy(); df["signal"] = 0
        if len(df): df.iloc[0, df.columns.get_loc("signal")] = 1
        return df
