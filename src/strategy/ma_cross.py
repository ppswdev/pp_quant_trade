from typing import Dict, Optional
import pandas as pd
import numpy as np

from .base import BaseStrategy

class MACrossStrategy(BaseStrategy):
    """双均线策略"""
    
    def __init__(self, config: Dict):
        """
        初始化双均线策略
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.name = "ma_cross"
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_params = ['fast_period', 'slow_period']
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"缺少必需参数: {param}")
        
        if self.config['fast_period'] >= self.config['slow_period']:
            raise ValueError("快速均线周期必须小于慢速均线周期")
    
    def generate_signals(
        self,
        data: pd.DataFrame,
        factors: Optional[Dict[str, pd.Series]] = None
    ) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据，必须包含'close'字段
            factors: 因子数据，可选
            
        Returns:
            Series: 交易信号，1表示买入，-1表示卖出，0表示持有
        """
        self._check_required_fields(data, ['close'])
        
        # 计算快速和慢速均线
        fast_ma = data['close'].rolling(
            window=self.config['fast_period']
        ).mean()
        slow_ma = data['close'].rolling(
            window=self.config['slow_period']
        ).mean()
        
        # 计算金叉和死叉
        cross_up = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        cross_down = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[cross_up] = 1    # 金叉买入
        signals[cross_down] = -1  # 死叉卖出
        
        # 处理缺失值
        signals = signals.fillna(0)
        
        return signals

class EnhancedMACrossStrategy(BaseStrategy):
    """增强版双均线策略"""
    
    def __init__(self, config: Dict):
        """
        初始化增强版双均线策略
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.name = "enhanced_ma_cross"
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_params = [
            'fast_period',
            'slow_period',
            'volume_ma_period',
            'rsi_period',
            'rsi_upper',
            'rsi_lower'
        ]
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"缺少必需参数: {param}")
        
        if self.config['fast_period'] >= self.config['slow_period']:
            raise ValueError("快速均线周期必须小于慢速均线周期")
    
    def _calculate_rsi(
        self,
        prices: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            prices: 价格序列
            period: 计算周期
            
        Returns:
            Series: RSI值
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(
        self,
        data: pd.DataFrame,
        factors: Optional[Dict[str, pd.Series]] = None
    ) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据，必须包含'close'和'volume'字段
            factors: 因子数据，可选
            
        Returns:
            Series: 交易信号，1表示买入，-1表示卖出，0表示持有
        """
        self._check_required_fields(data, ['close', 'volume'])
        
        # 计算快速和慢速均线
        fast_ma = data['close'].rolling(
            window=self.config['fast_period']
        ).mean()
        slow_ma = data['close'].rolling(
            window=self.config['slow_period']
        ).mean()
        
        # 计算成交量均线
        volume_ma = data['volume'].rolling(
            window=self.config['volume_ma_period']
        ).mean()
        
        # 计算RSI
        rsi = self._calculate_rsi(
            data['close'],
            period=self.config['rsi_period']
        )
        
        # 计算金叉和死叉
        cross_up = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        cross_down = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        
        # 生成基础信号
        signals = pd.Series(0, index=data.index)
        signals[cross_up] = 1    # 金叉买入
        signals[cross_down] = -1  # 死叉卖出
        
        # 增加成交量确认
        volume_confirm = data['volume'] > volume_ma
        signals = signals * volume_confirm
        
        # 增加RSI过滤
        rsi_filter = (
            (rsi < self.config['rsi_upper']) &
            (rsi > self.config['rsi_lower'])
        )
        signals = signals * rsi_filter
        
        # 处理缺失值
        signals = signals.fillna(0)
        
        return signals 