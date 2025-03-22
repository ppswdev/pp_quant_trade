from typing import Dict, Type, Optional, Any
import importlib
import os
import logging
from .base_strategy import BaseStrategy

class StrategyManager:
    """策略管理器"""
    
    def __init__(self):
        """初始化策略管理器"""
        self.strategies: Dict[str, Type[BaseStrategy]] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_strategy(self, strategy_name: str, strategy_class: Type[BaseStrategy]) -> None:
        """
        加载策略
        
        Args:
            strategy_name: 策略名称
            strategy_class: 策略类
        """
        self.strategies[strategy_name] = strategy_class
        self.logger.info(f"加载策略: {strategy_name}")
        
    def load_strategy_from_file(self, strategy_file: str) -> None:
        """
        从文件加载策略
        
        Args:
            strategy_file: 策略文件路径
        """
        try:
            # 获取策略文件名（不含扩展名）
            strategy_name = os.path.splitext(os.path.basename(strategy_file))[0]
            
            # 动态导入策略模块
            spec = importlib.util.spec_from_file_location(strategy_name, strategy_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取策略类
            strategy_class = getattr(module, strategy_name.capitalize())
            
            # 加载策略
            self.load_strategy(strategy_name, strategy_class)
            
        except Exception as e:
            self.logger.error(f"加载策略文件失败: {str(e)}")
            
    def load_strategies_from_directory(self, strategy_dir: str) -> None:
        """
        从目录加载所有策略
        
        Args:
            strategy_dir: 策略目录路径
        """
        try:
            # 遍历目录下的所有Python文件
            for file in os.listdir(strategy_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    strategy_file = os.path.join(strategy_dir, file)
                    self.load_strategy_from_file(strategy_file)
                    
        except Exception as e:
            self.logger.error(f"加载策略目录失败: {str(e)}")
            
    def create_strategy(self, strategy_name: str, params: Dict[str, Any]) -> Optional[BaseStrategy]:
        """
        创建策略实例
        
        Args:
            strategy_name: 策略名称
            params: 策略参数
            
        Returns:
            Optional[BaseStrategy]: 策略实例，如果策略不存在则返回None
        """
        try:
            strategy_class = self.strategies.get(strategy_name)
            if not strategy_class:
                self.logger.error(f"策略不存在: {strategy_name}")
                return None
                
            return strategy_class(strategy_name, params)
            
        except Exception as e:
            self.logger.error(f"创建策略实例失败: {str(e)}")
            return None
            
    def get_strategy_names(self) -> list:
        """
        获取所有策略名称
        
        Returns:
            list: 策略名称列表
        """
        return list(self.strategies.keys())
        
    def get_strategy_class(self, strategy_name: str) -> Optional[Type[BaseStrategy]]:
        """
        获取策略类
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            Optional[Type[BaseStrategy]]: 策略类，如果策略不存在则返回None
        """
        return self.strategies.get(strategy_name)
        
    def remove_strategy(self, strategy_name: str) -> None:
        """
        移除策略
        
        Args:
            strategy_name: 策略名称
        """
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            self.logger.info(f"移除策略: {strategy_name}")
            
    def clear_strategies(self) -> None:
        """清空所有策略"""
        self.strategies.clear()
        self.logger.info("清空所有策略") 