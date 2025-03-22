from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

class BaseFactor(ABC):
    """因子基类"""
    
    def __init__(self, config: Dict):
        """
        初始化因子
        
        Args:
            config: 配置信息
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置信息"""
        pass
    
    @abstractmethod
    def calculate(
        self,
        data: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> pd.Series:
        """
        计算因子值
        
        Args:
            data: 输入数据
            params: 计算参数
            
        Returns:
            Series: 因子值
        """
        pass
    
    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        验证输入数据
        
        Args:
            data: 输入数据
        """
        if data is None or data.empty:
            raise ValueError("输入数据不能为空")
    
    def _validate_params(self, params: Optional[Dict]) -> None:
        """
        验证参数
        
        Args:
            params: 参数
        """
        if params is None:
            params = {}
        
        if not isinstance(params, dict):
            raise ValueError("参数必须是字典类型")
    
    def _check_required_fields(
        self,
        data: pd.DataFrame,
        required_fields: List[str]
    ) -> None:
        """
        检查必需字段
        
        Args:
            data: 输入数据
            required_fields: 必需字段列表
        """
        missing_fields = [
            field for field in required_fields
            if field not in data.columns
        ]
        
        if missing_fields:
            raise ValueError(f"缺少必需字段: {missing_fields}")
    
    def _handle_missing_values(
        self,
        series: pd.Series,
        method: str = 'ffill'
    ) -> pd.Series:
        """
        处理缺失值
        
        Args:
            series: 输入序列
            method: 处理方法，如'ffill'、'bfill'、'drop'
            
        Returns:
            Series: 处理后的序列
        """
        if method == 'ffill':
            return series.fillna(method='ffill')
        elif method == 'bfill':
            return series.fillna(method='bfill')
        elif method == 'drop':
            return series.dropna()
        else:
            raise ValueError(f"不支持的缺失值处理方法: {method}")
    
    def _standardize(
        self,
        series: pd.Series,
        method: str = 'zscore'
    ) -> pd.Series:
        """
        标准化处理
        
        Args:
            series: 输入序列
            method: 标准化方法，如'zscore'、'minmax'
            
        Returns:
            Series: 标准化后的序列
        """
        if method == 'zscore':
            return (series - series.mean()) / series.std()
        elif method == 'minmax':
            return (series - series.min()) / (series.max() - series.min())
        else:
            raise ValueError(f"不支持的标准化方法: {method}")
    
    def _winsorize(
        self,
        series: pd.Series,
        lower: float = 0.01,
        upper: float = 0.99
    ) -> pd.Series:
        """
        去极值处理
        
        Args:
            series: 输入序列
            lower: 下分位数
            upper: 上分位数
            
        Returns:
            Series: 去极值后的序列
        """
        lower_bound = series.quantile(lower)
        upper_bound = series.quantile(upper)
        
        return series.clip(lower=lower_bound, upper=upper_bound)
    
    def _neutralize(
        self,
        series: pd.Series,
        factors: pd.DataFrame
    ) -> pd.Series:
        """
        因子中性化处理
        
        Args:
            series: 输入序列
            factors: 控制因子
            
        Returns:
            Series: 中性化后的序列
        """
        from sklearn.linear_model import LinearRegression
        
        # 准备数据
        X = factors.copy()
        y = series.copy()
        
        # 处理缺失值
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # 标准化
        X = (X - X.mean()) / X.std()
        y = (y - y.mean()) / y.std()
        
        # 回归
        model = LinearRegression()
        model.fit(X, y)
        
        # 计算残差
        residuals = y - model.predict(X)
        
        return pd.Series(residuals, index=series.index) 