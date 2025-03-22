from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MeanReversion(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        """
        初始化均值回归策略
        
        Args:
            name: 策略名称
            params: 策略参数，包含：
                - period: 计算周期
                - std_dev: 标准差倍数
                - position_size: 每次交易数量
        """
        super().__init__(name, params)
        self.period = params.get('period', 20)
        self.std_dev = params.get('std_dev', 2)
        self.position_size = params.get('position_size', 100)
        
    def initialize(self) -> None:
        """策略初始化"""
        self.logger.info(f"初始化均值回归策略: period={self.period}, std_dev={self.std_dev}")
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: K线数据
            
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        # 计算移动平均线
        data['MA'] = data['close'].rolling(window=self.period).mean()
        
        # 计算标准差
        data['STD'] = data['close'].rolling(window=self.period).std()
        
        # 计算上下轨
        data['upper_band'] = data['MA'] + self.std_dev * data['STD']
        data['lower_band'] = data['MA'] - self.std_dev * data['STD']
        
        # 计算偏离度
        data['deviation'] = (data['close'] - data['MA']) / data['STD']
        
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
            
        # 获取最新的指标值
        current_price = data['close'].iloc[-1]
        current_ma = data['MA'].iloc[-1]
        current_std = data['STD'].iloc[-1]
        current_deviation = data['deviation'].iloc[-1]
        
        # 生成交易信号
        signal = {}
        
        # 价格突破上轨，做空
        if current_price > data['upper_band'].iloc[-1]:
            signal['action'] = 'SELL'
            signal['price'] = current_price
            signal['volume'] = self.position_size
            signal['reason'] = f'价格突破上轨，偏离度: {current_deviation:.2f}'
            
        # 价格突破下轨，做多
        elif current_price < data['lower_band'].iloc[-1]:
            signal['action'] = 'BUY'
            signal['price'] = current_price
            signal['volume'] = self.position_size
            signal['reason'] = f'价格突破下轨，偏离度: {current_deviation:.2f}'
            
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
                
        # 检查趋势强度
        if 'trend_strength' in signal and signal['trend_strength'] > self.params.get('max_trend_strength', 0.8):
            self.logger.warning("趋势强度过高，不适合均值回归")
            return False
            
        return True 