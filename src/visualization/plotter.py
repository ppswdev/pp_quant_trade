from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

class Plotter:
    """可视化工具"""
    
    def __init__(self):
        """初始化可视化工具"""
        self.logger = logging.getLogger(__name__)
        plt.style.use('seaborn')
        
    def plot_equity_curve(self, equity_curve: List[float], save_path: Optional[str] = None) -> None:
        """
        绘制权益曲线
        
        Args:
            equity_curve: 权益曲线数据
            save_path: 保存路径
        """
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(equity_curve)
            plt.title('权益曲线')
            plt.xlabel('交易日')
            plt.ylabel('权益')
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制权益曲线异常: {str(e)}")
            
    def plot_drawdown(self, equity_curve: List[float], save_path: Optional[str] = None) -> None:
        """
        绘制回撤曲线
        
        Args:
            equity_curve: 权益曲线数据
            save_path: 保存路径
        """
        try:
            # 计算回撤
            drawdown = []
            peak = equity_curve[0]
            for value in equity_curve:
                if value > peak:
                    peak = value
                drawdown.append((peak - value) / peak)
                
            plt.figure(figsize=(12, 6))
            plt.plot(drawdown)
            plt.title('回撤曲线')
            plt.xlabel('交易日')
            plt.ylabel('回撤')
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制回撤曲线异常: {str(e)}")
            
    def plot_trade_distribution(self, trades: List[Dict], save_path: Optional[str] = None) -> None:
        """
        绘制交易分布
        
        Args:
            trades: 交易记录
            save_path: 保存路径
        """
        try:
            # 计算交易收益
            profits = []
            for trade in trades:
                if trade['action'] == 'SELL':
                    profit = (trade['price'] - trade['price']) * trade['volume']
                    profits.append(profit)
                    
            plt.figure(figsize=(12, 6))
            sns.histplot(profits)
            plt.title('交易收益分布')
            plt.xlabel('收益')
            plt.ylabel('频次')
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制交易分布异常: {str(e)}")
            
    def plot_position_concentration(self, positions: Dict[str, float], save_path: Optional[str] = None) -> None:
        """
        绘制持仓集中度
        
        Args:
            positions: 持仓数据
            save_path: 保存路径
        """
        try:
            # 计算持仓比例
            total_position = sum(positions.values())
            position_ratios = {symbol: volume/total_position for symbol, volume in positions.items()}
            
            plt.figure(figsize=(12, 6))
            plt.pie(position_ratios.values(), labels=position_ratios.keys(), autopct='%1.1f%%')
            plt.title('持仓集中度')
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制持仓集中度异常: {str(e)}")
            
    def plot_risk_metrics(self, risk_metrics: Dict[str, Any], save_path: Optional[str] = None) -> None:
        """
        绘制风险指标
        
        Args:
            risk_metrics: 风险指标数据
            save_path: 保存路径
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 绘制回撤
            axes[0, 0].plot(risk_metrics['drawdown'])
            axes[0, 0].set_title('回撤曲线')
            axes[0, 0].set_xlabel('交易日')
            axes[0, 0].set_ylabel('回撤')
            
            # 绘制波动率
            axes[0, 1].plot(risk_metrics['volatility'])
            axes[0, 1].set_title('波动率')
            axes[0, 1].set_xlabel('交易日')
            axes[0, 1].set_ylabel('波动率')
            
            # 绘制夏普比率
            axes[1, 0].plot(risk_metrics['sharpe_ratio'])
            axes[1, 0].set_title('夏普比率')
            axes[1, 0].set_xlabel('交易日')
            axes[1, 0].set_ylabel('夏普比率')
            
            # 绘制索提诺比率
            axes[1, 1].plot(risk_metrics['sortino_ratio'])
            axes[1, 1].set_title('索提诺比率')
            axes[1, 1].set_xlabel('交易日')
            axes[1, 1].set_ylabel('索提诺比率')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制风险指标异常: {str(e)}")
            
    def plot_strategy_performance(self, strategy_results: Dict[str, Any], save_path: Optional[str] = None) -> None:
        """
        绘制策略表现
        
        Args:
            strategy_results: 策略结果数据
            save_path: 保存路径
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 绘制权益曲线
            axes[0, 0].plot(strategy_results['equity_curve'])
            axes[0, 0].set_title('权益曲线')
            axes[0, 0].set_xlabel('交易日')
            axes[0, 0].set_ylabel('权益')
            
            # 绘制回撤曲线
            drawdown = []
            peak = strategy_results['equity_curve'][0]
            for value in strategy_results['equity_curve']:
                if value > peak:
                    peak = value
                drawdown.append((peak - value) / peak)
            axes[0, 1].plot(drawdown)
            axes[0, 1].set_title('回撤曲线')
            axes[0, 1].set_xlabel('交易日')
            axes[0, 1].set_ylabel('回撤')
            
            # 绘制交易收益分布
            profits = []
            for trade in strategy_results['trades']:
                if trade['action'] == 'SELL':
                    profit = (trade['price'] - trade['price']) * trade['volume']
                    profits.append(profit)
            sns.histplot(profits, ax=axes[1, 0])
            axes[1, 0].set_title('交易收益分布')
            axes[1, 0].set_xlabel('收益')
            axes[1, 0].set_ylabel('频次')
            
            # 绘制月度收益热力图
            monthly_returns = self._calculate_monthly_returns(strategy_results['equity_curve'])
            sns.heatmap(monthly_returns, annot=True, fmt='.2%', ax=axes[1, 1])
            axes[1, 1].set_title('月度收益热力图')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制策略表现异常: {str(e)}")
            
    def _calculate_monthly_returns(self, equity_curve: List[float]) -> pd.DataFrame:
        """
        计算月度收益
        
        Args:
            equity_curve: 权益曲线数据
            
        Returns:
            pd.DataFrame: 月度收益数据
        """
        try:
            # 创建日期索引
            dates = pd.date_range(start='2020-01-01', periods=len(equity_curve), freq='D')
            
            # 创建DataFrame
            df = pd.DataFrame({'equity': equity_curve}, index=dates)
            
            # 计算月度收益
            monthly_returns = df['equity'].resample('M').last().pct_change()
            
            # 重塑为热力图格式
            monthly_returns = monthly_returns.groupby([monthly_returns.index.year, monthly_returns.index.month]).mean()
            monthly_returns = monthly_returns.unstack()
            
            return monthly_returns
            
        except Exception as e:
            self.logger.error(f"计算月度收益异常: {str(e)}")
            return pd.DataFrame() 