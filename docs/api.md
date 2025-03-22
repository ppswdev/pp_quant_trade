# API文档

## 1. 数据获取模块

### 1.1 BaseDataFetcher

```python
class BaseDataFetcher:
    """数据获取基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据获取器
        
        Args:
            config: 配置参数
        """
        
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: str, 
                          end_date: str, 
                          frequency: str = '1d') -> pd.DataFrame:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            pd.DataFrame: 历史数据
        """
        
    def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            Dict[str, Any]: 实时数据
        """
```

### 1.2 TushareDataFetcher

```python
class TushareDataFetcher(BaseDataFetcher):
    """Tushare数据获取器"""
    
    def __init__(self, token: str):
        """
        初始化Tushare数据获取器
        
        Args:
            token: Tushare API Token
        """
```

## 2. 因子分析模块

### 2.1 FactorAnalyzer

```python
class FactorAnalyzer:
    """因子分析器"""
    
    def __init__(self):
        """初始化因子分析器"""
        
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 市场数据
            
        Returns:
            pd.DataFrame: 技术指标
        """
        
    def calculate_fundamental_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算基本面因子
        
        Args:
            data: 市场数据
            
        Returns:
            pd.DataFrame: 基本面因子
        """
```

## 3. 策略引擎模块

### 3.1 BaseStrategy

```python
class BaseStrategy:
    """策略基类"""
    
    def __init__(self):
        """初始化策略"""
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 市场数据
            
        Returns:
            pd.DataFrame: 技术指标
        """
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        生成交易信号
        
        Args:
            data: 市场数据
            
        Returns:
            List[Dict[str, Any]]: 交易信号
        """
        
    def on_bar(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        处理K线数据
        
        Args:
            data: K线数据
            
        Returns:
            List[Dict[str, Any]]: 交易信号
        """
        
    def on_trade(self, trade: Dict[str, Any]) -> None:
        """
        处理交易结果
        
        Args:
            trade: 交易信息
        """
        
    def risk_check(self) -> bool:
        """
        风险检查
        
        Returns:
            bool: 是否通过风险检查
        """
```

## 4. 回测引擎模块

### 4.1 BacktestEngine

```python
class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, 
                 strategy_manager: StrategyManager,
                 initial_capital: float = 100000,
                 commission_rate: float = 0.0003,
                 slippage: float = 0.0001):
        """
        初始化回测引擎
        
        Args:
            strategy_manager: 策略管理器
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
        """
        
    def run(self, 
            start_date: str, 
            end_date: str, 
            market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            market_data: 市场数据
            
        Returns:
            Dict[str, Any]: 回测结果
        """
```

## 5. 券商接口模块

### 5.1 BaseBroker

```python
class BaseBroker:
    """券商接口基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化券商接口
        
        Args:
            config: 配置参数
        """
        
    def connect(self) -> bool:
        """
        连接交易接口
        
        Returns:
            bool: 是否连接成功
        """
        
    def disconnect(self) -> None:
        """断开连接"""
        
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户信息
        
        Returns:
            Dict[str, Any]: 账户信息
        """
        
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        获取持仓信息
        
        Returns:
            List[Dict[str, Any]]: 持仓信息
        """
        
    def place_order(self, order: Dict[str, Any]) -> str:
        """
        下单
        
        Args:
            order: 订单信息
            
        Returns:
            str: 订单ID
        """
        
    def cancel_order(self, order_id: str) -> bool:
        """
        撤单
        
        Args:
            order_id: 订单ID
            
        Returns:
            bool: 是否撤单成功
        """
```

## 6. 性能分析模块

### 6.1 PerformanceAnalyzer

```python
class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        """初始化性能分析器"""
        
    def analyze(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析回测结果
        
        Args:
            backtest_results: 回测结果
            
        Returns:
            Dict[str, Any]: 分析结果
        """
```

## 7. 风险管理模块

### 7.1 RiskManager

```python
class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化风险管理器
        
        Args:
            config: 配置参数
        """
        
    def check_risk(self, strategy: BaseStrategy, signal: Dict[str, Any]) -> bool:
        """
        检查交易风险
        
        Args:
            strategy: 策略实例
            signal: 交易信号
            
        Returns:
            bool: 是否通过风险检查
        """
        
    def update_risk_metrics(self, trade: Dict[str, Any]) -> None:
        """
        更新风险指标
        
        Args:
            trade: 交易信息
        """
```

## 8. 可视化工具

### 8.1 Plotter

```python
class Plotter:
    """可视化工具"""
    
    def __init__(self):
        """初始化可视化工具"""
        
    def plot_equity_curve(self, equity_curve: List[float], save_path: Optional[str] = None) -> None:
        """
        绘制权益曲线
        
        Args:
            equity_curve: 权益曲线数据
            save_path: 保存路径
        """
        
    def plot_drawdown(self, equity_curve: List[float], save_path: Optional[str] = None) -> None:
        """
        绘制回撤曲线
        
        Args:
            equity_curve: 权益曲线数据
            save_path: 保存路径
        """
        
    def plot_trade_distribution(self, trades: List[Dict], save_path: Optional[str] = None) -> None:
        """
        绘制交易分布
        
        Args:
            trades: 交易记录
            save_path: 保存路径
        """
```

## 9. 日志系统

### 9.1 Logger

```python
class Logger:
    """日志系统"""
    
    def __init__(self, 
                 log_dir: str = 'logs',
                 log_level: int = logging.INFO,
                 log_format: Optional[str] = None):
        """
        初始化日志系统
        
        Args:
            log_dir: 日志目录
            log_level: 日志级别
            log_format: 日志格式
        """
        
    def log_trade(self, trade: dict) -> None:
        """
        记录交易信息
        
        Args:
            trade: 交易信息
        """
        
    def log_position(self, position: dict) -> None:
        """
        记录持仓信息
        
        Args:
            position: 持仓信息
        """
        
    def log_risk(self, risk_metrics: dict) -> None:
        """
        记录风险指标
        
        Args:
            risk_metrics: 风险指标
        """
```
