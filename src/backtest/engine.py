from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from ..strategy.base import BaseStrategy
from ..data_fetcher.base import BaseDataFetcher

class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self,
        config: Dict,
        strategy: BaseStrategy,
        data_fetcher: BaseDataFetcher
    ):
        """
        初始化回测引擎
        
        Args:
            config: 配置信息
            strategy: 交易策略
            data_fetcher: 数据获取器
        """
        self.config = config
        self.strategy = strategy
        self.data_fetcher = data_fetcher
        self.results = {}
        self.logger = logging.getLogger(__name__)
    
    def run(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        initial_capital: float = 1000000
    ) -> Dict:
        """
        运行回测
        
        Args:
            symbol: 交易品种
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            
        Returns:
            Dict: 回测结果
        """
        self.logger.info(f"开始回测 {symbol}")
        self.logger.info(f"回测区间: {start_date} 至 {end_date}")
        
        # 获取历史数据
        data = self.data_fetcher.get_daily_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if data.empty:
            self.logger.error(f"未获取到 {symbol} 的历史数据")
            return {}
        
        # 生成交易信号
        signals = self.strategy.generate_signals(data)
        
        # 初始化回测结果
        self.results = {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'positions': [],
            'trades': [],
            'equity': [],
            'returns': []
        }
        
        # 模拟交易
        current_capital = initial_capital
        position = 0
        entry_price = 0
        
        for i in range(len(data)):
            current_date = data.index[i]
            current_price = data['close'].iloc[i]
            current_signal = signals.iloc[i]
            
            # 更新持仓市值
            if position != 0:
                current_value = position * current_price
                current_capital = current_value
            
            # 执行交易
            if current_signal != 0:
                # 计算交易数量
                trade_size = self.strategy.calculate_position_size(
                    signal=current_signal,
                    price=current_price,
                    capital=current_capital
                )
                
                # 更新持仓
                if current_signal > 0:  # 买入
                    position = trade_size / current_price
                    entry_price = current_price
                else:  # 卖出
                    position = 0
                    entry_price = 0
                
                # 记录交易
                trade = {
                    'date': current_date,
                    'type': 'buy' if current_signal > 0 else 'sell',
                    'price': current_price,
                    'size': trade_size,
                    'capital': current_capital
                }
                self.results['trades'].append(trade)
            
            # 更新持仓记录
            position_record = {
                'date': current_date,
                'price': current_price,
                'position': position,
                'capital': current_capital
            }
            self.results['positions'].append(position_record)
            
            # 计算收益率
            if i > 0:
                daily_return = (current_capital - self.results['positions'][i-1]['capital']) / self.results['positions'][i-1]['capital']
                self.results['returns'].append(daily_return)
        
        # 计算回测指标
        self._calculate_metrics()
        
        self.logger.info(f"回测完成 {symbol}")
        return self.results
    
    def _calculate_metrics(self) -> None:
        """计算回测指标"""
        if not self.results['returns']:
            return
        
        returns = pd.Series(self.results['returns'])
        
        # 计算各项指标
        self.results['metrics'] = {
            'total_return': (1 + returns).prod() - 1,
            'annual_return': (1 + returns).prod() ** (252/len(returns)) - 1,
            'sharpe_ratio': np.sqrt(252) * returns.mean() / returns.std(),
            'max_drawdown': (returns.cumsum() - returns.cumsum().cummax()).min(),
            'win_rate': (returns > 0).mean(),
            'profit_factor': abs(returns[returns > 0].sum() / returns[returns < 0].sum()),
            'total_trades': len(self.results['trades']),
            'avg_trade_return': returns.mean(),
            'volatility': returns.std() * np.sqrt(252)
        }
    
    def plot_results(self) -> None:
        """绘制回测结果"""
        try:
            import matplotlib.pyplot as plt
            
            # 创建图形
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # 绘制权益曲线
            equity = [pos['capital'] for pos in self.results['positions']]
            dates = [pos['date'] for pos in self.results['positions']]
            ax1.plot(dates, equity)
            ax1.set_title('权益曲线')
            ax1.set_xlabel('日期')
            ax1.set_ylabel('权益')
            ax1.grid(True)
            
            # 绘制回撤曲线
            returns = pd.Series(self.results['returns'])
            drawdown = (returns.cumsum() - returns.cumsum().cummax())
            ax2.plot(dates, drawdown)
            ax2.set_title('回撤曲线')
            ax2.set_xlabel('日期')
            ax2.set_ylabel('回撤')
            ax2.grid(True)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            self.logger.warning("未安装matplotlib，无法绘制回测结果")
    
    def generate_report(self) -> str:
        """
        生成回测报告
        
        Returns:
            str: 回测报告
        """
        if not self.results.get('metrics'):
            return "回测结果为空"
        
        report = f"""
回测报告
========
交易品种: {self.results['symbol']}
回测区间: {self.results['start_date']} 至 {self.results['end_date']}
初始资金: {self.results['initial_capital']:,.2f}

回测指标
--------
总收益率: {self.results['metrics']['total_return']:.2%}
年化收益率: {self.results['metrics']['annual_return']:.2%}
夏普比率: {self.results['metrics']['sharpe_ratio']:.2f}
最大回撤: {self.results['metrics']['max_drawdown']:.2%}
胜率: {self.results['metrics']['win_rate']:.2%}
盈亏比: {self.results['metrics']['profit_factor']:.2f}
总交易次数: {self.results['metrics']['total_trades']}
平均交易收益: {self.results['metrics']['avg_trade_return']:.2%}
波动率: {self.results['metrics']['volatility']:.2%}
"""
        return report 