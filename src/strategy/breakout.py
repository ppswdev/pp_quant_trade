from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class Breakout(BaseStrategy):
    """突破策略"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        """
        初始化突破策略
        
        Args:
            name: 策略名称
            params: 策略参数，包含：
                - period: 计算周期
                - threshold: 突破阈值
                - position_size: 每次交易数量
        """
        super().__init__(name, params)
        self.period = params.get('period', 20)
        self.threshold = params.get('threshold', 0.02)
        self.position_size = params.get('position_size', 100)
        
    def initialize(self) -> None:
        """策略初始化"""
        self.logger.info(f"初始化突破策略: period={self.period}, threshold={self.threshold}")
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: K线数据
            
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        # 计算最高价和最低价
        data['high_max'] = data['high'].rolling(window=self.period).max()
        data['low_min'] = data['low'].rolling(window=self.period).min()
        
        # 计算突破信号
        data['breakout_up'] = data['close'] > data['high_max'].shift(1)
        data['breakout_down'] = data['close'] < data['low_min'].shift(1)
        
        return data
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: K线数据
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        if len(data) < self.period:
            return {}
            
        # 获取最新的突破信号
        current_breakout_up = data['breakout_up'].iloc[-1]
        current_breakout_down = data['breakout_down'].iloc[-1]
        
        # 生成交易信号
        signal = {}
        
        # 向上突破
        if current_breakout_up:
            signal['action'] = 'BUY'
            signal['price'] = data['close'].iloc[-1]
            signal['volume'] = self.position_size
            signal['reason'] = '向上突破'
            
        # 向下突破
        elif current_breakout_down:
            signal['action'] = 'SELL'
            signal['price'] = data['close'].iloc[-1]
            signal['volume'] = self.position_size
            signal['reason'] = '向下突破'
            
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
                
        # 检查波动率
        if 'volatility' in signal and signal['volatility'] > self.params.get('max_volatility', 0.1):
            self.logger.warning("波动率过高")
            return False
            
        return True 