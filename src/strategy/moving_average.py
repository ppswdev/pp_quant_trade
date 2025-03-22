from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MovingAverage(BaseStrategy):
    """均线策略"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        """
        初始化均线策略
        
        Args:
            name: 策略名称
            params: 策略参数，包含：
                - short_window: 短期均线周期
                - long_window: 长期均线周期
                - position_size: 每次交易数量
        """
        super().__init__(name, params)
        self.short_window = params.get('short_window', 5)
        self.long_window = params.get('long_window', 20)
        self.position_size = params.get('position_size', 100)
        
    def initialize(self) -> None:
        """策略初始化"""
        self.logger.info(f"初始化均线策略: short_window={self.short_window}, long_window={self.long_window}")
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: K线数据
            
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        # 计算移动平均线
        data['MA_short'] = data['close'].rolling(window=self.short_window).mean()
        data['MA_long'] = data['close'].rolling(window=self.long_window).mean()
        return data
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: K线数据
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        if len(data) < self.long_window:
            return {}
            
        # 获取最新的均线值
        current_short_ma = data['MA_short'].iloc[-1]
        current_long_ma = data['MA_long'].iloc[-1]
        prev_short_ma = data['MA_short'].iloc[-2]
        prev_long_ma = data['MA_long'].iloc[-2]
        
        # 生成交易信号
        signal = {}
        
        # 金叉：短期均线上穿长期均线
        if prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma:
            signal['action'] = 'BUY'
            signal['price'] = data['close'].iloc[-1]
            signal['volume'] = self.position_size
            
        # 死叉：短期均线下穿长期均线
        elif prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma:
            signal['action'] = 'SELL'
            signal['price'] = data['close'].iloc[-1]
            signal['volume'] = self.position_size
            
        return signal
        
    def on_bar(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        处理K线数据
        
        Args:
            market_data: K线数据
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        # 计算技术指标
        data = self.calculate_indicators(market_data)
        
        # 生成交易信号
        signal = self.generate_signals(data)
        
        # 风险检查
        if signal and not self.risk_check(signal):
            return {}
            
        return signal
        
    def on_trade(self, trade: Dict) -> None:
        """
        处理成交信息
        
        Args:
            trade: 成交信息
        """
        # 更新持仓
        symbol = trade['symbol']
        volume = trade['volume']
        if trade['action'] == 'BUY':
            self.update_position(symbol, self.get_position(symbol) + volume)
        else:
            self.update_position(symbol, self.get_position(symbol) - volume)
            
        # 添加交易记录
        self.add_trade(trade)
        
    def risk_check(self, signal: Dict[str, Any]) -> bool:
        """
        风险检查
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 是否通过风险检查
        """
        # 检查持仓限制
        if signal['action'] == 'BUY':
            current_position = self.get_position(signal['symbol'])
            if current_position + signal['volume'] > self.params.get('max_position', 1000):
                self.logger.warning("超过最大持仓限制")
                return False
                
        # 检查资金限制
        if signal['action'] == 'BUY':
            required_capital = signal['price'] * signal['volume']
            if required_capital > self.params.get('max_capital', 100000):
                self.logger.warning("超过最大资金限制")
                return False
                
        return True 