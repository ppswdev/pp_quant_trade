from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 配置信息
        """
        self.config = config
        self._validate_config()
        self.positions = {}  # 当前持仓
        self.trades = []     # 交易记录
        self.performance = {}  # 策略表现
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置信息"""
        pass
    
    @abstractmethod
    def generate_signals(
        self,
        data: pd.DataFrame,
        factors: Optional[Dict[str, pd.Series]] = None
    ) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据
            factors: 因子数据
            
        Returns:
            Series: 交易信号，1表示买入，-1表示卖出，0表示持有
        """
        pass
    
    def calculate_position_size(
        self,
        signal: float,
        price: float,
        capital: float
    ) -> float:
        """
        计算仓位大小
        
        Args:
            signal: 交易信号
            price: 当前价格
            capital: 可用资金
            
        Returns:
            float: 仓位大小
        """
        if signal == 0:
            return 0
        
        # 获取仓位控制参数
        position_limit = self.config.get('position_limit', 0.8)
        single_position_limit = self.config.get('single_position_limit', 0.2)
        
        # 计算最大仓位
        max_position = min(
            capital * position_limit,
            capital * single_position_limit
        )
        
        # 计算实际仓位
        position = max_position * abs(signal)
        
        return position
    
    def update_positions(
        self,
        symbol: str,
        position: float,
        price: float,
        timestamp: datetime
    ) -> None:
        """
        更新持仓信息
        
        Args:
            symbol: 交易品种
            position: 仓位大小
            price: 成交价格
            timestamp: 时间戳
        """
        if symbol not in self.positions:
            self.positions[symbol] = {
                'position': 0,
                'price': 0,
                'timestamp': None
            }
        
        # 记录交易
        trade = {
            'symbol': symbol,
            'position': position,
            'price': price,
            'timestamp': timestamp
        }
        self.trades.append(trade)
        
        # 更新持仓
        self.positions[symbol].update({
            'position': position,
            'price': price,
            'timestamp': timestamp
        })
    
    def calculate_performance(self) -> Dict:
        """
        计算策略表现
        
        Returns:
            Dict: 策略表现指标
        """
        if not self.trades:
            return {}
        
        # 计算收益率
        returns = []
        for i in range(1, len(self.trades)):
            prev_trade = self.trades[i-1]
            curr_trade = self.trades[i]
            
            if prev_trade['symbol'] == curr_trade['symbol']:
                ret = (curr_trade['price'] - prev_trade['price']) / prev_trade['price']
                returns.append(ret)
        
        returns = pd.Series(returns)
        
        # 计算各项指标
        self.performance = {
            'total_return': (1 + returns).prod() - 1,
            'annual_return': (1 + returns).prod() ** (252/len(returns)) - 1,
            'sharpe_ratio': np.sqrt(252) * returns.mean() / returns.std(),
            'max_drawdown': (returns.cumsum() - returns.cumsum().cummax()).min(),
            'win_rate': (returns > 0).mean(),
            'profit_factor': abs(returns[returns > 0].sum() / returns[returns < 0].sum())
        }
        
        return self.performance
    
    def risk_check(self) -> bool:
        """
        风险检查
        
        Returns:
            bool: 是否通过风险检查
        """
        # 检查最大回撤
        max_drawdown = self.config.get('max_drawdown', 0.2)
        if self.performance.get('max_drawdown', 0) < -max_drawdown:
            return False
        
        # 检查持仓集中度
        position_limit = self.config.get('position_limit', 0.8)
        total_position = sum(
            pos['position'] * pos['price']
            for pos in self.positions.values()
        )
        if total_position > self.config.get('initial_capital', 1000000) * position_limit:
            return False
        
        return True
    
    def stop_loss_check(
        self,
        symbol: str,
        current_price: float
    ) -> bool:
        """
        止损检查
        
        Args:
            symbol: 交易品种
            current_price: 当前价格
            
        Returns:
            bool: 是否触发止损
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['price']
        stop_loss = self.config.get('stop_loss', 0.1)
        
        return (current_price - entry_price) / entry_price < -stop_loss
    
    def take_profit_check(
        self,
        symbol: str,
        current_price: float
    ) -> bool:
        """
        止盈检查
        
        Args:
            symbol: 交易品种
            current_price: 当前价格
            
        Returns:
            bool: 是否触发止盈
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['price']
        take_profit = self.config.get('take_profit', 0.2)
        
        return (current_price - entry_price) / entry_price > take_profit 