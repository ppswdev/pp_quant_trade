from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from itertools import product
from ..strategy.strategy_manager import StrategyManager
from ..strategy.base_strategy import BaseStrategy
from ..backtest.backtest_engine import BacktestEngine
from ..config.strategy_config import StrategyConfig

class StrategyOptimizer:
    """策略优化器"""
    
    def __init__(self,
                 strategy_manager: StrategyManager,
                 strategy_config: StrategyConfig,
                 backtest_engine: BacktestEngine):
        """
        初始化策略优化器
        
        Args:
            strategy_manager: 策略管理器
            strategy_config: 策略配置
            backtest_engine: 回测引擎
        """
        self.strategy_manager = strategy_manager
        self.strategy_config = strategy_config
        self.backtest_engine = backtest_engine
        self.logger = logging.getLogger(__name__)
        
    def optimize(self,
                strategy_name: str,
                param_grid: Dict[str, List[Any]],
                start_date: datetime,
                end_date: datetime,
                market_data: Dict[str, pd.DataFrame],
                target_metric: str = 'sharpe_ratio') -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        优化策略参数
        
        Args:
            strategy_name: 策略名称
            param_grid: 参数网格，格式为 {param_name: [param_values]}
            start_date: 开始日期
            end_date: 结束日期
            market_data: 市场数据
            target_metric: 优化目标指标，可选值：
                - sharpe_ratio: 夏普比率
                - total_return: 总收益率
                - max_drawdown: 最大回撤
                - win_rate: 胜率
                
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: (最优参数, 优化结果)
        """
        try:
            # 获取策略配置
            config = self.strategy_config.get_strategy_config(strategy_name)
            if not config:
                self.logger.error(f"策略配置不存在: {strategy_name}")
                return {}, {}
                
            # 生成参数组合
            param_combinations = self._generate_param_combinations(param_grid)
            
            # 存储优化结果
            results = []
            
            # 遍历参数组合
            for params in param_combinations:
                # 更新策略配置
                config['params'].update(params)
                self.strategy_config.update_strategy_config(strategy_name, config)
                
                # 运行回测
                backtest_results = self.backtest_engine.run(
                    start_date=start_date,
                    end_date=end_date,
                    market_data=market_data
                )
                
                if backtest_results:
                    # 记录结果
                    result = {
                        'params': params,
                        'results': backtest_results
                    }
                    results.append(result)
                    
            if not results:
                self.logger.error("没有找到有效的参数组合")
                return {}, {}
                
            # 选择最优参数
            best_result = self._select_best_result(results, target_metric)
            return best_result['params'], best_result['results']
            
        except Exception as e:
            self.logger.error(f"策略优化异常: {str(e)}")
            return {}, {}
            
    def _generate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        生成参数组合
        
        Args:
            param_grid: 参数网格
            
        Returns:
            List[Dict[str, Any]]: 参数组合列表
        """
        try:
            # 获取参数名称和值列表
            param_names = list(param_grid.keys())
            param_values = list(param_grid.values())
            
            # 生成笛卡尔积
            combinations = list(product(*param_values))
            
            # 转换为字典列表
            param_combinations = []
            for combo in combinations:
                params = dict(zip(param_names, combo))
                param_combinations.append(params)
                
            return param_combinations
            
        except Exception as e:
            self.logger.error(f"生成参数组合异常: {str(e)}")
            return []
            
    def _select_best_result(self, results: List[Dict[str, Any]], target_metric: str) -> Dict[str, Any]:
        """
        选择最优结果
        
        Args:
            results: 优化结果列表
            target_metric: 优化目标指标
            
        Returns:
            Dict[str, Any]: 最优结果
        """
        try:
            # 根据目标指标排序
            if target_metric in ['sharpe_ratio', 'total_return', 'win_rate']:
                sorted_results = sorted(results, 
                                     key=lambda x: x['results'][target_metric],
                                     reverse=True)
            else:
                sorted_results = sorted(results,
                                     key=lambda x: x['results'][target_metric])
                
            return sorted_results[0]
            
        except Exception as e:
            self.logger.error(f"选择最优结果异常: {str(e)}")
            return {}
            
    def optimize_with_cross_validation(self,
                                     strategy_name: str,
                                     param_grid: Dict[str, List[Any]],
                                     market_data: Dict[str, pd.DataFrame],
                                     n_splits: int = 5,
                                     target_metric: str = 'sharpe_ratio') -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        使用交叉验证优化策略参数
        
        Args:
            strategy_name: 策略名称
            param_grid: 参数网格
            market_data: 市场数据
            n_splits: 交叉验证折数
            target_metric: 优化目标指标
            
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: (最优参数, 优化结果)
        """
        try:
            # 获取数据时间范围
            dates = sorted(list(market_data[list(market_data.keys())[0]].index))
            split_size = len(dates) // n_splits
            
            # 存储每个参数组合的交叉验证结果
            cv_results = []
            
            # 生成参数组合
            param_combinations = self._generate_param_combinations(param_grid)
            
            # 遍历参数组合
            for params in param_combinations:
                cv_scores = []
                
                # 交叉验证
                for i in range(n_splits):
                    # 划分训练集和验证集
                    start_idx = i * split_size
                    end_idx = (i + 1) * split_size
                    
                    train_dates = dates[:start_idx] + dates[end_idx:]
                    val_dates = dates[start_idx:end_idx]
                    
                    # 准备训练数据
                    train_data = self._prepare_data(market_data, train_dates)
                    val_data = self._prepare_data(market_data, val_dates)
                    
                    # 运行回测
                    train_results = self.backtest_engine.run(
                        start_date=train_dates[0],
                        end_date=train_dates[-1],
                        market_data=train_data
                    )
                    
                    val_results = self.backtest_engine.run(
                        start_date=val_dates[0],
                        end_date=val_dates[-1],
                        market_data=val_data
                    )
                    
                    if train_results and val_results:
                        # 计算综合得分
                        score = self._calculate_cv_score(
                            train_results,
                            val_results,
                            target_metric
                        )
                        cv_scores.append(score)
                        
                if cv_scores:
                    # 计算平均得分
                    mean_score = np.mean(cv_scores)
                    std_score = np.std(cv_scores)
                    
                    cv_results.append({
                        'params': params,
                        'mean_score': mean_score,
                        'std_score': std_score,
                        'cv_scores': cv_scores
                    })
                    
            if not cv_results:
                self.logger.error("没有找到有效的参数组合")
                return {}, {}
                
            # 选择最优参数
            best_result = max(cv_results, key=lambda x: x['mean_score'])
            
            # 使用最优参数运行完整回测
            config = self.strategy_config.get_strategy_config(strategy_name)
            config['params'].update(best_result['params'])
            self.strategy_config.update_strategy_config(strategy_name, config)
            
            final_results = self.backtest_engine.run(
                start_date=dates[0],
                end_date=dates[-1],
                market_data=market_data
            )
            
            return best_result['params'], final_results
            
        except Exception as e:
            self.logger.error(f"交叉验证优化异常: {str(e)}")
            return {}, {}
            
    def _prepare_data(self, market_data: Dict[str, pd.DataFrame], dates: List[datetime]) -> Dict[str, pd.DataFrame]:
        """
        准备数据
        
        Args:
            market_data: 市场数据
            dates: 日期列表
            
        Returns:
            Dict[str, pd.DataFrame]: 处理后的数据
        """
        prepared_data = {}
        for symbol, data in market_data.items():
            prepared_data[symbol] = data[data.index.isin(dates)]
        return prepared_data
        
    def _calculate_cv_score(self,
                          train_results: Dict[str, Any],
                          val_results: Dict[str, Any],
                          target_metric: str) -> float:
        """
        计算交叉验证得分
        
        Args:
            train_results: 训练集结果
            val_results: 验证集结果
            
        Returns:
            float: 综合得分
        """
        # 计算训练集和验证集的得分
        train_score = train_results[target_metric]
        val_score = val_results[target_metric]
        
        # 计算综合得分（可以调整权重）
        return 0.7 * train_score + 0.3 * val_score 