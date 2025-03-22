from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from ..strategy.base_strategy import BaseStrategy

class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化风险管理器
        
        Args:
            config: 风险配置，包含：
                - max_position_size: 最大持仓数量
                - max_capital: 最大资金使用
                - max_drawdown: 最大回撤限制
                - position_limit: 单个品种持仓限制
                - volatility_limit: 波动率限制
                - correlation_limit: 相关性限制
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化风险指标
        self.positions: Dict[str, float] = {}  # 当前持仓
        self.capital: float = 0.0  # 当前资金
        self.equity_curve: List[float] = []  # 权益曲线
        self.trade_history: List[Dict] = []  # 交易历史
        
    def check_risk(self, strategy: BaseStrategy, signal: Dict[str, Any]) -> bool:
        """
        检查交易风险
        
        Args:
            strategy: 策略实例
            signal: 交易信号
            
        Returns:
            bool: 是否通过风险检查
        """
        try:
            # 检查持仓限制
            if not self._check_position_limit(signal):
                return False
                
            # 检查资金限制
            if not self._check_capital_limit(signal):
                return False
                
            # 检查回撤限制
            if not self._check_drawdown_limit():
                return False
                
            # 检查波动率限制
            if not self._check_volatility_limit(strategy):
                return False
                
            # 检查相关性限制
            if not self._check_correlation_limit(strategy):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"风险检查异常: {str(e)}")
            return False
            
    def update_risk_metrics(self, trade: Dict[str, Any]) -> None:
        """
        更新风险指标
        
        Args:
            trade: 交易信息
        """
        try:
            # 更新持仓
            symbol = trade['symbol']
            volume = trade['volume']
            if trade['action'] == 'BUY':
                self.positions[symbol] = self.positions.get(symbol, 0) + volume
            else:
                self.positions[symbol] = self.positions.get(symbol, 0) - volume
                
            # 更新资金
            self.capital = trade['capital']
            
            # 更新权益曲线
            self.equity_curve.append(self.capital)
            
            # 更新交易历史
            self.trade_history.append(trade)
            
        except Exception as e:
            self.logger.error(f"更新风险指标异常: {str(e)}")
            
    def _check_position_limit(self, signal: Dict[str, Any]) -> bool:
        """
        检查持仓限制
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 是否通过持仓限制检查
        """
        try:
            symbol = signal['symbol']
            volume = signal['volume']
            
            # 检查单个品种持仓限制
            current_position = self.positions.get(symbol, 0)
            if signal['action'] == 'BUY':
                if current_position + volume > self.config.get('position_limit', 1000):
                    self.logger.warning(f"超过单个品种持仓限制: {symbol}")
                    return False
            else:
                if current_position - volume < 0:
                    self.logger.warning(f"持仓不足: {symbol}")
                    return False
                    
            # 检查总持仓限制
            total_position = sum(self.positions.values())
            if signal['action'] == 'BUY':
                if total_position + volume > self.config.get('max_position_size', 5000):
                    self.logger.warning("超过总持仓限制")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"检查持仓限制异常: {str(e)}")
            return False
            
    def _check_capital_limit(self, signal: Dict[str, Any]) -> bool:
        """
        检查资金限制
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 是否通过资金限制检查
        """
        try:
            if signal['action'] == 'BUY':
                required_capital = signal['price'] * signal['volume']
                if required_capital > self.config.get('max_capital', 100000):
                    self.logger.warning("超过资金使用限制")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"检查资金限制异常: {str(e)}")
            return False
            
    def _check_drawdown_limit(self) -> bool:
        """
        检查回撤限制
        
        Returns:
            bool: 是否通过回撤限制检查
        """
        try:
            if not self.equity_curve:
                return True
                
            # 计算当前回撤
            current_equity = self.equity_curve[-1]
            max_equity = max(self.equity_curve)
            current_drawdown = (max_equity - current_equity) / max_equity
            
            # 检查是否超过最大回撤限制
            if current_drawdown > self.config.get('max_drawdown', 0.1):
                self.logger.warning(f"超过最大回撤限制: {current_drawdown:.2%}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"检查回撤限制异常: {str(e)}")
            return False
            
    def _check_volatility_limit(self, strategy: BaseStrategy) -> bool:
        """
        检查波动率限制
        
        Args:
            strategy: 策略实例
            
        Returns:
            bool: 是否通过波动率限制检查
        """
        try:
            # 获取策略的波动率
            volatility = strategy.get_volatility()
            
            # 检查是否超过波动率限制
            if volatility > self.config.get('volatility_limit', 0.2):
                self.logger.warning(f"超过波动率限制: {volatility:.2%}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"检查波动率限制异常: {str(e)}")
            return False
            
    def _check_correlation_limit(self, strategy: BaseStrategy) -> bool:
        """
        检查相关性限制
        
        Args:
            strategy: 策略实例
            
        Returns:
            bool: 是否通过相关性限制检查
        """
        try:
            # 获取策略的相关性
            correlation = strategy.get_correlation()
            
            # 检查是否超过相关性限制
            if abs(correlation) > self.config.get('correlation_limit', 0.7):
                self.logger.warning(f"超过相关性限制: {correlation:.2f}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"检查相关性限制异常: {str(e)}")
            return False
            
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        获取风险指标
        
        Returns:
            Dict[str, Any]: 风险指标
        """
        try:
            # 计算当前回撤
            current_equity = self.equity_curve[-1] if self.equity_curve else 0
            max_equity = max(self.equity_curve) if self.equity_curve else 0
            current_drawdown = (max_equity - current_equity) / max_equity if max_equity > 0 else 0
            
            # 计算持仓集中度
            total_position = sum(self.positions.values())
            position_concentration = {}
            for symbol, volume in self.positions.items():
                if total_position > 0:
                    position_concentration[symbol] = volume / total_position
                    
            # 计算资金利用率
            capital_utilization = sum(self.positions.values()) / self.config.get('max_position_size', 5000)
            
            return {
                'current_drawdown': current_drawdown,
                'position_concentration': position_concentration,
                'capital_utilization': capital_utilization,
                'total_position': total_position,
                'current_capital': self.capital
            }
            
        except Exception as e:
            self.logger.error(f"获取风险指标异常: {str(e)}")
            return {}
            
    def reset(self) -> None:
        """重置风险指标"""
        self.positions.clear()
        self.capital = 0.0
        self.equity_curve.clear()
        self.trade_history.clear() 