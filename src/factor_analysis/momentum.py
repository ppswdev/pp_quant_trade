from typing import Dict, Optional
import pandas as pd
import numpy as np

from .base import BaseFactor

class MomentumFactor(BaseFactor):
    """动量因子"""
    
    def __init__(self, config: Dict):
        """
        初始化动量因子
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.name = "momentum"
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_params = ['lookback_period', 'skip_recent']
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"缺少必需参数: {param}")
    
    def calculate(
        self,
        data: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> pd.Series:
        """
        计算动量因子值
        
        Args:
            data: 输入数据，必须包含'close'字段
            params: 计算参数，可选
            
        Returns:
            Series: 动量因子值
        """
        self._validate_data(data)
        self._validate_params(params)
        self._check_required_fields(data, ['close'])
        
        # 使用配置参数或传入参数
        lookback = params.get('lookback_period', self.config['lookback_period'])
        skip = params.get('skip_recent', self.config['skip_recent'])
        
        # 计算收益率
        returns = data['close'].pct_change()
        
        # 计算动量
        momentum = returns.rolling(window=lookback).mean()
        
        # 跳过最近N天
        if skip > 0:
            momentum = momentum.shift(skip)
        
        # 处理缺失值
        momentum = self._handle_missing_values(momentum)
        
        # 去极值
        momentum = self._winsorize(momentum)
        
        # 标准化
        momentum = self._standardize(momentum)
        
        return momentum

class PriceMomentumFactor(BaseFactor):
    """价格动量因子"""
    
    def __init__(self, config: Dict):
        """
        初始化价格动量因子
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.name = "price_momentum"
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_params = ['lookback_period']
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"缺少必需参数: {param}")
    
    def calculate(
        self,
        data: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> pd.Series:
        """
        计算价格动量因子值
        
        Args:
            data: 输入数据，必须包含'close'字段
            params: 计算参数，可选
            
        Returns:
            Series: 价格动量因子值
        """
        self._validate_data(data)
        self._validate_params(params)
        self._check_required_fields(data, ['close'])
        
        # 使用配置参数或传入参数
        lookback = params.get('lookback_period', self.config['lookback_period'])
        
        # 计算价格动量
        momentum = data['close'] / data['close'].shift(lookback) - 1
        
        # 处理缺失值
        momentum = self._handle_missing_values(momentum)
        
        # 去极值
        momentum = self._winsorize(momentum)
        
        # 标准化
        momentum = self._standardize(momentum)
        
        return momentum

class VolumeMomentumFactor(BaseFactor):
    """成交量动量因子"""
    
    def __init__(self, config: Dict):
        """
        初始化成交量动量因子
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.name = "volume_momentum"
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_params = ['lookback_period']
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"缺少必需参数: {param}")
    
    def calculate(
        self,
        data: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> pd.Series:
        """
        计算成交量动量因子值
        
        Args:
            data: 输入数据，必须包含'volume'字段
            params: 计算参数，可选
            
        Returns:
            Series: 成交量动量因子值
        """
        self._validate_data(data)
        self._validate_params(params)
        self._check_required_fields(data, ['volume'])
        
        # 使用配置参数或传入参数
        lookback = params.get('lookback_period', self.config['lookback_period'])
        
        # 计算成交量动量
        momentum = data['volume'] / data['volume'].shift(lookback) - 1
        
        # 处理缺失值
        momentum = self._handle_missing_values(momentum)
        
        # 去极值
        momentum = self._winsorize(momentum)
        
        # 标准化
        momentum = self._standardize(momentum)
        
        return momentum 