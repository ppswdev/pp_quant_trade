from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import time
import threading
from queue import Queue

from ..strategy.base import BaseStrategy
from ..data_fetcher.base import BaseDataFetcher

class SimulatedTradingEngine:
    """模拟交易引擎"""
    
    def __init__(
        self,
        config: Dict,
        strategy: BaseStrategy,
        data_fetcher: BaseDataFetcher
    ):
        """
        初始化模拟交易引擎
        
        Args:
            config: 配置信息
            strategy: 交易策略
            data_fetcher: 数据获取器
        """
        self.config = config
        self.strategy = strategy
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)
        
        # 初始化交易状态
        self.positions = {}
        self.capital = self.config.get('initial_capital', 1000000)
        self.trades = []
        self.is_running = False
        self.data_queue = Queue()
        self.order_queue = Queue()
        
        # 初始化风控参数
        self.risk_params = {
            'position_limit': self.config.get('position_limit', 0.8),
            'single_position_limit': self.config.get('single_position_limit', 0.2),
            'stop_loss': self.config.get('stop_loss', 0.1),
            'take_profit': self.config.get('take_profit', 0.2),
            'max_drawdown': self.config.get('max_drawdown', 0.2)
        }
    
    def start(self, symbols: List[str]) -> None:
        """
        启动模拟交易
        
        Args:
            symbols: 交易品种列表
        """
        self.logger.info("启动模拟交易")
        self.is_running = True
        
        # 创建数据获取线程
        data_thread = threading.Thread(
            target=self._data_fetcher_loop,
            args=(symbols,)
        )
        data_thread.daemon = True
        data_thread.start()
        
        # 创建交易执行线程
        trading_thread = threading.Thread(
            target=self._trading_loop
        )
        trading_thread.daemon = True
        trading_thread.start()
        
        # 创建风控监控线程
        risk_thread = threading.Thread(
            target=self._risk_monitor_loop
        )
        risk_thread.daemon = True
        risk_thread.start()
    
    def stop(self) -> None:
        """停止模拟交易"""
        self.logger.info("停止模拟交易")
        self.is_running = False
    
    def _data_fetcher_loop(self, symbols: List[str]) -> None:
        """
        数据获取循环
        
        Args:
            symbols: 交易品种列表
        """
        while self.is_running:
            try:
                for symbol in symbols:
                    # 获取实时数据
                    data = self.data_fetcher.get_realtime_data(symbol)
                    if not data.empty:
                        self.data_queue.put({
                            'symbol': symbol,
                            'data': data
                        })
                
                # 等待下一个周期
                time.sleep(self.config.get('update_interval', 1))
                
            except Exception as e:
                self.logger.error(f"数据获取错误: {str(e)}")
                time.sleep(5)  # 发生错误时等待较长时间
    
    def _trading_loop(self) -> None:
        """交易执行循环"""
        while self.is_running:
            try:
                # 获取最新数据
                if not self.data_queue.empty():
                    market_data = self.data_queue.get()
                    symbol = market_data['symbol']
                    data = market_data['data']
                    
                    # 生成交易信号
                    signals = self.strategy.generate_signals(data)
                    
                    # 执行交易
                    for i in range(len(signals)):
                        signal = signals.iloc[i]
                        if signal != 0:
                            # 计算交易数量
                            price = data['close'].iloc[i]
                            trade_size = self.strategy.calculate_position_size(
                                signal=signal,
                                price=price,
                                capital=self.capital
                            )
                            
                            # 创建订单
                            order = {
                                'symbol': symbol,
                                'type': 'buy' if signal > 0 else 'sell',
                                'price': price,
                                'size': trade_size,
                                'timestamp': data.index[i]
                            }
                            
                            # 发送订单
                            self.order_queue.put(order)
                
                time.sleep(0.1)  # 避免CPU占用过高
                
            except Exception as e:
                self.logger.error(f"交易执行错误: {str(e)}")
                time.sleep(5)
    
    def _risk_monitor_loop(self) -> None:
        """风控监控循环"""
        while self.is_running:
            try:
                # 检查持仓风险
                for symbol, position in self.positions.items():
                    # 获取最新价格
                    data = self.data_fetcher.get_realtime_data(symbol)
                    if data.empty:
                        continue
                    
                    current_price = data['close'].iloc[-1]
                    entry_price = position['price']
                    
                    # 检查止损
                    if self.strategy.stop_loss_check(symbol, current_price):
                        self.logger.warning(f"{symbol} 触发止损")
                        self._close_position(symbol, current_price)
                    
                    # 检查止盈
                    if self.strategy.take_profit_check(symbol, current_price):
                        self.logger.warning(f"{symbol} 触发止盈")
                        self._close_position(symbol, current_price)
                
                # 检查整体风险
                if not self.strategy.risk_check():
                    self.logger.warning("触发整体风控")
                    self._close_all_positions()
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"风控监控错误: {str(e)}")
                time.sleep(5)
    
    def _execute_order(self, order: Dict) -> None:
        """
        执行订单
        
        Args:
            order: 订单信息
        """
        try:
            symbol = order['symbol']
            order_type = order['type']
            price = order['price']
            size = order['size']
            
            # 计算交易成本
            commission = size * price * self.config.get('commission_rate', 0.0003)
            slippage = size * price * self.config.get('slippage', 0.0001)
            total_cost = commission + slippage
            
            # 检查资金是否足够
            if order_type == 'buy' and total_cost > self.capital:
                self.logger.warning(f"资金不足，无法执行买入订单: {order}")
                return
            
            # 更新持仓
            if order_type == 'buy':
                if symbol not in self.positions:
                    self.positions[symbol] = {
                        'position': 0,
                        'price': 0,
                        'timestamp': None
                    }
                
                self.positions[symbol].update({
                    'position': size / price,
                    'price': price,
                    'timestamp': order['timestamp']
                })
                
                self.capital -= total_cost
                
            else:  # sell
                if symbol in self.positions:
                    self.capital += size - total_cost
                    del self.positions[symbol]
            
            # 记录交易
            trade = {
                'timestamp': order['timestamp'],
                'symbol': symbol,
                'type': order_type,
                'price': price,
                'size': size,
                'commission': commission,
                'slippage': slippage,
                'capital': self.capital
            }
            self.trades.append(trade)
            
            self.logger.info(f"执行订单: {trade}")
            
        except Exception as e:
            self.logger.error(f"订单执行错误: {str(e)}")
    
    def _close_position(self, symbol: str, price: float) -> None:
        """
        平仓
        
        Args:
            symbol: 交易品种
            price: 平仓价格
        """
        if symbol in self.positions:
            position = self.positions[symbol]
            size = position['position'] * price
            
            order = {
                'symbol': symbol,
                'type': 'sell',
                'price': price,
                'size': size,
                'timestamp': datetime.now()
            }
            
            self._execute_order(order)
    
    def _close_all_positions(self) -> None:
        """平掉所有持仓"""
        for symbol in list(self.positions.keys()):
            data = self.data_fetcher.get_realtime_data(symbol)
            if not data.empty:
                self._close_position(symbol, data['close'].iloc[-1])
    
    def get_performance(self) -> Dict:
        """
        获取策略表现
        
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
                ret = (curr_trade['capital'] - prev_trade['capital']) / prev_trade['capital']
                returns.append(ret)
        
        returns = pd.Series(returns)
        
        # 计算各项指标
        performance = {
            'total_return': (1 + returns).prod() - 1,
            'annual_return': (1 + returns).prod() ** (252/len(returns)) - 1,
            'sharpe_ratio': np.sqrt(252) * returns.mean() / returns.std(),
            'max_drawdown': (returns.cumsum() - returns.cumsum().cummax()).min(),
            'win_rate': (returns > 0).mean(),
            'profit_factor': abs(returns[returns > 0].sum() / returns[returns < 0].sum()),
            'total_trades': len(self.trades),
            'avg_trade_return': returns.mean(),
            'volatility': returns.std() * np.sqrt(252),
            'current_capital': self.capital,
            'positions': self.positions
        }
        
        return performance 