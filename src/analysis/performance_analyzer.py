from typing import Dict, List, Any
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        """初始化性能分析器"""
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析回测结果
        
        Args:
            backtest_results: 回测结果
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            if not backtest_results:
                return {}
                
            # 计算基础指标
            basic_metrics = self._calculate_basic_metrics(backtest_results)
            
            # 计算风险指标
            risk_metrics = self._calculate_risk_metrics(backtest_results)
            
            # 计算交易指标
            trade_metrics = self._calculate_trade_metrics(backtest_results)
            
            # 计算资金指标
            capital_metrics = self._calculate_capital_metrics(backtest_results)
            
            return {
                'basic_metrics': basic_metrics,
                'risk_metrics': risk_metrics,
                'trade_metrics': trade_metrics,
                'capital_metrics': capital_metrics
            }
            
        except Exception as e:
            self.logger.error(f"性能分析异常: {str(e)}")
            return {}
            
    def _calculate_basic_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        计算基础指标
        
        Args:
            results: 回测结果
            
        Returns:
            Dict[str, float]: 基础指标
        """
        try:
            # 计算收益率
            returns = np.diff(results['equity_curve']) / results['equity_curve'][:-1]
            total_return = results['total_return']
            annual_return = results['annual_return']
            
            # 计算波动率
            volatility = np.std(returns) * np.sqrt(252)
            
            # 计算夏普比率
            sharpe_ratio = results['sharpe_ratio']
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            }
            
        except Exception as e:
            self.logger.error(f"计算基础指标异常: {str(e)}")
            return {}
            
    def _calculate_risk_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        计算风险指标
        
        Args:
            results: 回测结果
            
        Returns:
            Dict[str, float]: 风险指标
        """
        try:
            # 计算最大回撤
            max_drawdown = results['max_drawdown']
            
            # 计算回撤持续时间
            drawdown_duration = self._calculate_drawdown_duration(results['equity_curve'])
            
            # 计算下行风险
            downside_risk = self._calculate_downside_risk(results['equity_curve'])
            
            # 计算索提诺比率
            sortino_ratio = self._calculate_sortino_ratio(results['equity_curve'])
            
            return {
                'max_drawdown': max_drawdown,
                'drawdown_duration': drawdown_duration,
                'downside_risk': downside_risk,
                'sortino_ratio': sortino_ratio
            }
            
        except Exception as e:
            self.logger.error(f"计算风险指标异常: {str(e)}")
            return {}
            
    def _calculate_trade_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        计算交易指标
        
        Args:
            results: 回测结果
            
        Returns:
            Dict[str, float]: 交易指标
        """
        try:
            trades = results['trades']
            
            # 计算交易统计
            total_trades = results['total_trades']
            win_rate = results['win_rate']
            
            # 计算平均收益
            profits = []
            for trade in trades:
                if trade['action'] == 'SELL':
                    profit = (trade['price'] - trade['price']) * trade['volume']
                    profits.append(profit)
                    
            avg_profit = np.mean(profits) if profits else 0
            
            # 计算盈亏比
            winning_trades = [p for p in profits if p > 0]
            losing_trades = [p for p in profits if p < 0]
            
            profit_factor = (abs(sum(winning_trades)) / abs(sum(losing_trades))) if losing_trades else float('inf')
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'profit_factor': profit_factor
            }
            
        except Exception as e:
            self.logger.error(f"计算交易指标异常: {str(e)}")
            return {}
            
    def _calculate_capital_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        计算资金指标
        
        Args:
            results: 回测结果
            
        Returns:
            Dict[str, float]: 资金指标
        """
        try:
            equity_curve = results['equity_curve']
            
            # 计算资金利用率
            capital_utilization = self._calculate_capital_utilization(results['trades'])
            
            # 计算资金周转率
            turnover_rate = self._calculate_turnover_rate(results['trades'])
            
            # 计算资金曲线
            capital_curve = self._calculate_capital_curve(results['trades'])
            
            return {
                'capital_utilization': capital_utilization,
                'turnover_rate': turnover_rate,
                'capital_curve': capital_curve
            }
            
        except Exception as e:
            self.logger.error(f"计算资金指标异常: {str(e)}")
            return {}
            
    def _calculate_drawdown_duration(self, equity_curve: List[float]) -> int:
        """
        计算回撤持续时间
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            int: 最大回撤持续时间（天）
        """
        try:
            max_duration = 0
            current_duration = 0
            peak = equity_curve[0]
            
            for value in equity_curve:
                if value > peak:
                    peak = value
                    current_duration = 0
                else:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
                    
            return max_duration
            
        except Exception as e:
            self.logger.error(f"计算回撤持续时间异常: {str(e)}")
            return 0
            
    def _calculate_downside_risk(self, equity_curve: List[float]) -> float:
        """
        计算下行风险
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            float: 下行风险
        """
        try:
            returns = np.diff(equity_curve) / equity_curve[:-1]
            downside_returns = returns[returns < 0]
            return np.sqrt(np.mean(downside_returns ** 2)) * np.sqrt(252)
            
        except Exception as e:
            self.logger.error(f"计算下行风险异常: {str(e)}")
            return 0.0
            
    def _calculate_sortino_ratio(self, equity_curve: List[float]) -> float:
        """
        计算索提诺比率
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            float: 索提诺比率
        """
        try:
            returns = np.diff(equity_curve) / equity_curve[:-1]
            downside_risk = self._calculate_downside_risk(equity_curve)
            excess_returns = returns - 0.02/252  # 假设无风险利率为2%
            return np.sqrt(252) * np.mean(excess_returns) / downside_risk if downside_risk > 0 else 0
            
        except Exception as e:
            self.logger.error(f"计算索提诺比率异常: {str(e)}")
            return 0.0
            
    def _calculate_capital_utilization(self, trades: List[Dict]) -> float:
        """
        计算资金利用率
        
        Args:
            trades: 交易记录
            
        Returns:
            float: 资金利用率
        """
        try:
            total_capital = sum(trade['capital'] for trade in trades)
            avg_capital = total_capital / len(trades) if trades else 0
            return avg_capital / trades[0]['capital'] if trades else 0
            
        except Exception as e:
            self.logger.error(f"计算资金利用率异常: {str(e)}")
            return 0.0
            
    def _calculate_turnover_rate(self, trades: List[Dict]) -> float:
        """
        计算资金周转率
        
        Args:
            trades: 交易记录
            
        Returns:
            float: 资金周转率
        """
        try:
            total_volume = sum(trade['volume'] for trade in trades)
            total_capital = trades[0]['capital'] if trades else 0
            return total_volume / total_capital if total_capital > 0 else 0
            
        except Exception as e:
            self.logger.error(f"计算资金周转率异常: {str(e)}")
            return 0.0
            
    def _calculate_capital_curve(self, trades: List[Dict]) -> List[float]:
        """
        计算资金曲线
        
        Args:
            trades: 交易记录
            
        Returns:
            List[float]: 资金曲线
        """
        try:
            return [trade['capital'] for trade in trades]
            
        except Exception as e:
            self.logger.error(f"计算资金曲线异常: {str(e)}")
            return []
            
    def plot_results(self, results: Dict[str, Any], save_path: str = None) -> None:
        """
        绘制分析结果
        
        Args:
            results: 分析结果
            save_path: 保存路径
        """
        try:
            # 创建子图
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 绘制权益曲线
            equity_curve = results['equity_curve']
            axes[0, 0].plot(equity_curve)
            axes[0, 0].set_title('权益曲线')
            axes[0, 0].set_xlabel('交易日')
            axes[0, 0].set_ylabel('权益')
            
            # 绘制回撤曲线
            drawdown = self._calculate_drawdown(equity_curve)
            axes[0, 1].plot(drawdown)
            axes[0, 1].set_title('回撤曲线')
            axes[0, 1].set_xlabel('交易日')
            axes[0, 1].set_ylabel('回撤')
            
            # 绘制资金曲线
            capital_curve = results['capital_metrics']['capital_curve']
            axes[1, 0].plot(capital_curve)
            axes[1, 0].set_title('资金曲线')
            axes[1, 0].set_xlabel('交易日')
            axes[1, 0].set_ylabel('资金')
            
            # 绘制交易分布
            profits = []
            for trade in results['trades']:
                if trade['action'] == 'SELL':
                    profit = (trade['price'] - trade['price']) * trade['volume']
                    profits.append(profit)
                    
            sns.histplot(profits, ax=axes[1, 1])
            axes[1, 1].set_title('交易收益分布')
            axes[1, 1].set_xlabel('收益')
            axes[1, 1].set_ylabel('频次')
            
            # 调整布局
            plt.tight_layout()
            
            # 保存或显示
            if save_path:
                plt.savefig(save_path)
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制分析结果异常: {str(e)}")
            
    def _calculate_drawdown(self, equity_curve: List[float]) -> List[float]:
        """
        计算回撤曲线
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            List[float]: 回撤曲线
        """
        try:
            drawdown = []
            peak = equity_curve[0]
            
            for value in equity_curve:
                if value > peak:
                    peak = value
                drawdown.append((peak - value) / peak)
                
            return drawdown
            
        except Exception as e:
            self.logger.error(f"计算回撤曲线异常: {str(e)}")
            return [] 