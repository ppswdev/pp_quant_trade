from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            name: 策略名称
            params: 策略参数
        """
        self.name = name
        self.params = params
        self.positions: Dict[str, float] = {}  # 当前持仓
        self.trades: List[Dict] = []  # 交易记录
        
    @abstractmethod
    def initialize(self) -> None:
        """策略初始化"""
        pass
        
    @abstractmethod
    def on_bar(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        处理K线数据
        
        Args:
            market_data: K线数据
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        pass
        
    @abstractmethod
    def on_trade(self, trade: Dict) -> None:
        """
        处理成交信息
        
        Args:
            trade: 成交信息
        """
        pass
        
    def update_position(self, symbol: str, volume: float) -> None:
        """
        更新持仓
        
        Args:
            symbol: 股票代码
            volume: 持仓数量
        """
        self.positions[symbol] = volume
        
    def add_trade(self, trade: Dict) -> None:
        """
        添加交易记录
        
        Args:
            trade: 交易记录
        """
        self.trades.append(trade)
        
    def get_position(self, symbol: str) -> float:
        """
        获取持仓数量
        
        Args:
            symbol: 股票代码
            
        Returns:
            float: 持仓数量
        """
        return self.positions.get(symbol, 0)
        
    def get_trades(self) -> List[Dict]:
        """
        获取交易记录
        
        Returns:
            List[Dict]: 交易记录列表
        """
        return self.trades
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: K线数据
            
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        return data
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: K线数据
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        return {}
        
    def risk_check(self, signal: Dict[str, Any]) -> bool:
        """
        风险检查
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 是否通过风险检查
        """
        return True
        
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            Dict[str, Any]: 策略参数
        """
        return self.params
        
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        设置策略参数
        
        Args:
            params: 策略参数
        """
        self.params.update(params) 