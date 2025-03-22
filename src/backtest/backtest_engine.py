from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from ..strategy.base_strategy import BaseStrategy
from ..strategy.strategy_manager import StrategyManager
from ..config.strategy_config import StrategyConfig

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, 
                 strategy_manager: StrategyManager,
                 strategy_config: StrategyConfig,
                 initial_capital: float = 1000000.0,
                 commission_rate: float = 0.0003,
                 slippage: float = 0.0001):
        """
        初始化回测引擎
        
        Args:
            strategy_manager: 策略管理器
            strategy_config: 策略配置
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点率
        """
        self.strategy_manager = strategy_manager
        self.strategy_config = strategy_config
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        self.capital = initial_capital  # 当前资金
        self.positions: Dict[str, float] = {}  # 当前持仓
        self.trades: List[Dict] = []  # 交易记录
        self.equity_curve: List[float] = []  # 权益曲线
        self.logger = logging.getLogger(__name__)
        
    def run(self, 
            start_date: datetime,
            end_date: datetime,
            market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            market_data: 市场数据，格式为 {symbol: DataFrame}
            
        Returns:
            Dict[str, Any]: 回测结果
        """
        try:
            # 初始化回测
            self._initialize_backtest()
            
            # 获取启用的策略
            enabled_strategies = self.strategy_config.get_enabled_strategies()
            if not enabled_strategies:
                self.logger.error("没有启用的策略")
                return {}
                
            # 创建策略实例
            strategies = {}
            for strategy_name in enabled_strategies:
                config = self.strategy_config.get_strategy_config(strategy_name)
                strategy = self.strategy_manager.create_strategy(strategy_name, config['params'])
                if strategy:
                    strategy.initialize()
                    strategies[strategy_name] = strategy
                    
            # 按时间顺序遍历数据
            current_date = start_date
            while current_date <= end_date:
                # 更新每个策略
                for strategy_name, strategy in strategies.items():
                    # 获取策略的交易品种
                    symbols = self.strategy_config.get_strategy_symbols(strategy_name)
                    
                    # 处理每个交易品种
                    for symbol in symbols:
                        if symbol in market_data:
                            # 获取当前日期的数据
                            data = market_data[symbol][market_data[symbol].index <= current_date]
                            if not data.empty:
                                # 生成交易信号
                                signal = strategy.on_bar(data)
                                
                                # 执行交易
                                if signal:
                                    self._execute_trade(signal, current_date)
                                    
                # 更新权益曲线
                self._update_equity_curve(current_date, market_data)
                
                # 更新日期
                current_date += pd.Timedelta(days=1)
                
            # 计算回测结果
            results = self._calculate_results()
            return results
            
        except Exception as e:
            self.logger.error(f"回测运行异常: {str(e)}")
            return {}
            
    def _initialize_backtest(self) -> None:
        """初始化回测"""
        self.capital = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.equity_curve.clear()
        
    def _execute_trade(self, signal: Dict[str, Any], trade_date: datetime) -> None:
        """
        执行交易
        
        Args:
            signal: 交易信号
            trade_date: 交易日期
        """
        try:
            # 计算交易成本
            price = signal['price'] * (1 + self.slippage)
            volume = signal['volume']
            commission = price * volume * self.commission_rate
            
            # 检查资金是否足够
            if signal['action'] == 'BUY':
                required_capital = price * volume + commission
                if required_capital > self.capital:
                    self.logger.warning("资金不足，无法执行交易")
                    return
                    
            # 更新持仓
            symbol = signal['symbol']
            if signal['action'] == 'BUY':
                self.positions[symbol] = self.positions.get(symbol, 0) + volume
                self.capital -= (price * volume + commission)
            else:
                self.positions[symbol] = self.positions.get(symbol, 0) - volume
                self.capital += (price * volume - commission)
                
            # 记录交易
            trade = {
                'date': trade_date,
                'symbol': symbol,
                'action': signal['action'],
                'price': price,
                'volume': volume,
                'commission': commission,
                'capital': self.capital
            }
            self.trades.append(trade)
            
        except Exception as e:
            self.logger.error(f"执行交易异常: {str(e)}")
            
    def _update_equity_curve(self, date: datetime, market_data: Dict[str, pd.DataFrame]) -> None:
        """
        更新权益曲线
        
        Args:
            date: 当前日期
            market_data: 市场数据
        """
        try:
            # 计算持仓市值
            position_value = 0.0
            for symbol, volume in self.positions.items():
                if symbol in market_data:
                    data = market_data[symbol][market_data[symbol].index <= date]
                    if not data.empty:
                        price = data['close'].iloc[-1]
                        position_value += price * volume
                        
            # 计算总权益
            total_equity = self.capital + position_value
            self.equity_curve.append(total_equity)
            
        except Exception as e:
            self.logger.error(f"更新权益曲线异常: {str(e)}")
            
    def _calculate_results(self) -> Dict[str, Any]:
        """
        计算回测结果
        
        Returns:
            Dict[str, Any]: 回测结果
        """
        try:
            if not self.equity_curve:
                return {}
                
            # 计算收益率
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital
            
            # 计算年化收益率
            days = len(self.equity_curve)
            annual_return = (1 + total_return) ** (365 / days) - 1
            
            # 计算最大回撤
            max_drawdown = 0.0
            peak = self.equity_curve[0]
            for value in self.equity_curve:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
                
            # 计算夏普比率
            risk_free_rate = 0.02  # 假设无风险利率为2%
            excess_returns = returns - risk_free_rate/252
            sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)
            
            # 计算交易统计
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t['action'] == 'SELL' and t['price'] > t['price']])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'equity_curve': self.equity_curve,
                'trades': self.trades
            }
            
        except Exception as e:
            self.logger.error(f"计算回测结果异常: {str(e)}")
            return {} 