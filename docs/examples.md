# 示例文档

## 1. 数据获取示例

### 1.1 使用Tushare获取数据

```python
from src.data.data_fetcher import TushareDataFetcher

# 创建数据获取器
fetcher = TushareDataFetcher(token='your_tushare_token')

# 获取历史数据
data = fetcher.get_historical_data(
    symbol='000001.SZ',
    start_date='2020-01-01',
    end_date='2023-12-31',
    frequency='1d'
)

# 获取实时数据
realtime_data = fetcher.get_realtime_data(symbol='000001.SZ')
```

### 1.2 使用AkShare获取数据

```python
from src.data.data_fetcher import AkShareDataFetcher

# 创建数据获取器
fetcher = AkShareDataFetcher()

# 获取历史数据
data = fetcher.get_historical_data(
    symbol='000001',
    start_date='2020-01-01',
    end_date='2023-12-31',
    frequency='1d'
)
```

## 2. 因子分析示例

### 2.1 计算技术指标

```python
from src.factor.factor_analyzer import FactorAnalyzer

# 创建因子分析器
analyzer = FactorAnalyzer()

# 计算技术指标
indicators = analyzer.calculate_technical_indicators(data)

# 计算基本面因子
factors = analyzer.calculate_fundamental_factors(data)
```

## 3. 策略开发示例

### 3.1 均线交叉策略

```python
from src.strategy.ma_cross import MACrossStrategy

# 创建策略实例
strategy = MACrossStrategy(
    short_period=5,
    long_period=20,
    position_size=100
)

# 计算指标
indicators = strategy.calculate_indicators(data)

# 生成信号
signals = strategy.generate_signals(data)

# 处理K线数据
signals = strategy.on_bar(data)

# 处理交易结果
strategy.on_trade(trade)

# 风险检查
is_safe = strategy.risk_check()
```

### 3.2 突破策略

```python
from src.strategy.breakout import BreakoutStrategy

# 创建策略实例
strategy = BreakoutStrategy(
    period=20,
    threshold=0.02,
    position_size=100
)

# 计算指标
indicators = strategy.calculate_indicators(data)

# 生成信号
signals = strategy.generate_signals(data)
```

### 3.3 均值回归策略

```python
from src.strategy.mean_reversion import MeanReversionStrategy

# 创建策略实例
strategy = MeanReversionStrategy(
    period=20,
    std_dev=2,
    position_size=100
)

# 计算指标
indicators = strategy.calculate_indicators(data)

# 生成信号
signals = strategy.generate_signals(data)
```

## 4. 回测示例

### 4.1 运行回测

```python
from src.backtest.backtest_engine import BacktestEngine
from src.strategy.strategy_manager import StrategyManager

# 创建策略管理器
strategy_manager = StrategyManager()
strategy_manager.add_strategy('ma_cross', MACrossStrategy(params))

# 创建回测引擎
engine = BacktestEngine(
    strategy_manager=strategy_manager,
    initial_capital=100000,
    commission_rate=0.0003,
    slippage=0.0001
)

# 运行回测
results = engine.run(
    start_date='2020-01-01',
    end_date='2023-12-31',
    market_data=market_data
)
```

### 4.2 分析回测结果

```python
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.visualization.plotter import Plotter

# 创建性能分析器
analyzer = PerformanceAnalyzer()
performance = analyzer.analyze(results)

# 创建可视化工具
plotter = Plotter()
plotter.plot_strategy_performance(results)
```

## 5. 实盘交易示例

### 5.1 使用XTP接口

```python
from src.trading.trading_engine import TradingEngine
from src.brokers.broker_factory import BrokerFactory

# 创建券商接口
broker = BrokerFactory.create_broker('xtp', config)

# 创建交易引擎
engine = TradingEngine(
    strategy_manager=strategy_manager,
    broker=broker,
    risk_manager=risk_manager
)

# 启动交易
engine.start()
```

### 5.2 使用通达信接口

```python
from src.brokers.tdx_broker import TDXBroker

# 创建券商接口
broker = TDXBroker(
    server='127.0.0.1',
    port=7709,
    account='your_account',
    password='your_password'
)

# 连接交易接口
broker.connect()

# 获取账户信息
account_info = broker.get_account_info()

# 获取持仓信息
positions = broker.get_positions()

# 下单
order_id = broker.place_order(order)

# 撤单
success = broker.cancel_order(order_id)
```

## 6. 风险管理示例

### 6.1 配置风险参数

```python
from src.risk.risk_manager import RiskManager

# 创建风险管理器
risk_manager = RiskManager({
    'max_position_size': 5000,
    'max_capital': 100000,
    'max_drawdown': 0.1,
    'position_limit': 1000,
    'volatility_limit': 0.2,
    'correlation_limit': 0.7
})

# 检查交易风险
is_safe = risk_manager.check_risk(strategy, signal)

# 更新风险指标
risk_manager.update_risk_metrics(trade)

# 获取风险指标
risk_metrics = risk_manager.get_risk_metrics()
```

## 7. 日志记录示例

### 7.1 配置日志

```python
from src.utils.logger import Logger

# 创建日志系统
logger = Logger(
    log_dir='logs',
    log_level=logging.INFO,
    log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 记录交易信息
logger.log_trade(trade)

# 记录持仓信息
logger.log_position(position)

# 记录风险指标
logger.log_risk(risk_metrics)

# 记录策略信号
logger.log_strategy(strategy_name, signal)

# 记录性能指标
logger.log_performance(performance)

# 记录错误信息
logger.log_error(error, context)
```

## 8. 完整示例

### 8.1 运行完整的量化交易系统

```python
import logging
from src.data.data_fetcher import TushareDataFetcher
from src.factor.factor_analyzer import FactorAnalyzer
from src.strategy.ma_cross import MACrossStrategy
from src.strategy.strategy_manager import StrategyManager
from src.backtest.backtest_engine import BacktestEngine
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.visualization.plotter import Plotter
from src.risk.risk_manager import RiskManager
from src.utils.logger import Logger

# 配置日志
logger = Logger()
logger.info("启动量化交易系统")

# 创建数据获取器
fetcher = TushareDataFetcher(token='your_tushare_token')

# 获取历史数据
data = fetcher.get_historical_data(
    symbol='000001.SZ',
    start_date='2020-01-01',
    end_date='2023-12-31',
    frequency='1d'
)

# 创建因子分析器
analyzer = FactorAnalyzer()
indicators = analyzer.calculate_technical_indicators(data)

# 创建策略管理器
strategy_manager = StrategyManager()
strategy_manager.add_strategy('ma_cross', MACrossStrategy(
    short_period=5,
    long_period=20,
    position_size=100
))

# 创建回测引擎
engine = BacktestEngine(
    strategy_manager=strategy_manager,
    initial_capital=100000,
    commission_rate=0.0003,
    slippage=0.0001
)

# 运行回测
results = engine.run(
    start_date='2020-01-01',
    end_date='2023-12-31',
    market_data=data
)

# 分析回测结果
performance_analyzer = PerformanceAnalyzer()
performance = performance_analyzer.analyze(results)

# 可视化结果
plotter = Plotter()
plotter.plot_strategy_performance(results)

# 记录结果
logger.log_performance(performance)
logger.info("量化交易系统运行完成")
``` 