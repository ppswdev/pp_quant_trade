from typing import Dict, Any
import json
import os
import logging

class StrategyConfig:
    """策略配置管理"""
    
    def __init__(self, config_file: str = 'strategy_config.json'):
        """
        初始化策略配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.load_config()
        
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"加载策略配置: {self.config_file}")
            else:
                self.logger.warning(f"配置文件不存在: {self.config_file}")
                self.create_default_config()
                
        except Exception as e:
            self.logger.error(f"加载策略配置失败: {str(e)}")
            self.create_default_config()
            
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"保存策略配置: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"保存策略配置失败: {str(e)}")
            
    def create_default_config(self) -> None:
        """创建默认配置"""
        self.config = {
            'moving_average': {
                'enabled': True,
                'params': {
                    'short_window': 5,
                    'long_window': 20,
                    'position_size': 100,
                    'max_position': 1000,
                    'max_capital': 100000
                },
                'symbols': ['000001.SZ', '600000.SH']
            },
            'breakout': {
                'enabled': False,
                'params': {
                    'period': 20,
                    'threshold': 0.02,
                    'position_size': 100,
                    'max_position': 1000,
                    'max_capital': 100000
                },
                'symbols': []
            },
            'mean_reversion': {
                'enabled': False,
                'params': {
                    'period': 20,
                    'std_dev': 2,
                    'position_size': 100,
                    'max_position': 1000,
                    'max_capital': 100000
                },
                'symbols': []
            }
        }
        self.save_config()
        
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        获取策略配置
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            Dict[str, Any]: 策略配置
        """
        return self.config.get(strategy_name, {})
        
    def update_strategy_config(self, strategy_name: str, config: Dict[str, Any]) -> None:
        """
        更新策略配置
        
        Args:
            strategy_name: 策略名称
            config: 策略配置
        """
        self.config[strategy_name] = config
        self.save_config()
        
    def enable_strategy(self, strategy_name: str) -> None:
        """
        启用策略
        
        Args:
            strategy_name: 策略名称
        """
        if strategy_name in self.config:
            self.config[strategy_name]['enabled'] = True
            self.save_config()
            
    def disable_strategy(self, strategy_name: str) -> None:
        """
        禁用策略
        
        Args:
            strategy_name: 策略名称
        """
        if strategy_name in self.config:
            self.config[strategy_name]['enabled'] = False
            self.save_config()
            
    def get_enabled_strategies(self) -> list:
        """
        获取启用的策略列表
        
        Returns:
            list: 启用的策略名称列表
        """
        return [name for name, config in self.config.items() if config.get('enabled', False)]
        
    def add_symbol(self, strategy_name: str, symbol: str) -> None:
        """
        添加交易品种
        
        Args:
            strategy_name: 策略名称
            symbol: 股票代码
        """
        if strategy_name in self.config:
            if 'symbols' not in self.config[strategy_name]:
                self.config[strategy_name]['symbols'] = []
            if symbol not in self.config[strategy_name]['symbols']:
                self.config[strategy_name]['symbols'].append(symbol)
                self.save_config()
                
    def remove_symbol(self, strategy_name: str, symbol: str) -> None:
        """
        移除交易品种
        
        Args:
            strategy_name: 策略名称
            symbol: 股票代码
        """
        if strategy_name in self.config and 'symbols' in self.config[strategy_name]:
            if symbol in self.config[strategy_name]['symbols']:
                self.config[strategy_name]['symbols'].remove(symbol)
                self.save_config()
                
    def get_strategy_symbols(self, strategy_name: str) -> list:
        """
        获取策略的交易品种列表
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            list: 股票代码列表
        """
        return self.config.get(strategy_name, {}).get('symbols', []) 