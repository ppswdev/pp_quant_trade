# 使用指南

## 1. 系统架构

### 1.1 核心模块

- 数据获取模块：负责从不同数据源获取市场数据
- 因子分析模块：计算技术指标和因子
- 策略引擎模块：实现交易策略逻辑
- 回测引擎模块：进行策略回测
- 券商接口模块：对接不同券商交易接口
- 性能分析模块：分析策略表现
- 风险管理模块：控制交易风险
- 可视化工具：绘制分析图表
- 日志系统：记录系统运行日志

### 1.2 数据流

1. 数据获取 → 数据清洗 → 因子计算
2. 策略信号生成 → 风险控制 → 交易执行
3. 交易记录 → 性能分析 → 可视化展示

## 2. 策略开发

### 2.1 创建新策略

1. 在 `src/strategy/` 目录下创建新的策略文件
2. 继承 `BaseStrategy` 类
3. 实现必要的方法：
   - `calculate_indicators`: 计算技术指标
   - `generate_signals`: 生成交易信号
   - `on_bar`: 处理K线数据
   - `on_trade`: 处理交易结果
   - `risk_check`: 风险检查

### 2.2 策略示例

```python
from src.strategy.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def calculate_indicators(self, data):
        # 计算技术指标
        pass
        
    def generate_signals(self, data):
        # 生成交易信号
        pass
        
    def on_bar(self, data):
        # 处理K线数据
        pass
        
    def on_trade(self, trade):
        # 处理交易结果
        pass
        
    def risk_check(self):
        # 风险检查
        pass
```

## 3. 回测系统

### 3.1 运行回测

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

### 3.2 分析回测结果

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

## 4. 实盘交易

### 4.1 启动交易系统

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

### 4.2 监控交易状态

```python
# 获取账户信息
account_info = broker.get_account_info()

# 获取持仓信息
positions = broker.get_positions()

# 获取订单状态
orders = broker.get_orders()
```

## 5. 风险管理

### 5.1 配置风险参数

```python
from src.risk.risk_manager import RiskManager

risk_config = {
    'max_position_size': 5000,
    'max_capital': 100000,
    'max_drawdown': 0.1,
    'position_limit': 1000,
    'volatility_limit': 0.2,
    'correlation_limit': 0.7
}

risk_manager = RiskManager(risk_config)
```

### 5.2 风险监控

```python
# 获取风险指标
risk_metrics = risk_manager.get_risk_metrics()

# 检查交易风险
is_safe = risk_manager.check_risk(strategy, signal)

# 更新风险指标
risk_manager.update_risk_metrics(trade)
```

## 6. 日志管理

### 6.1 配置日志

```python
from src.utils.logger import Logger

logger = Logger(
    log_dir='logs',
    log_level=logging.INFO,
    log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 6.2 记录日志

```python
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

## 7. 最佳实践

### 7.1 策略开发

1. 使用模块化设计
2. 实现完整的风险控制
3. 添加详细的日志记录
4. 进行充分的回测验证
5. 使用配置文件管理参数

### 7.2 实盘交易

1. 先进行模拟交易
2. 从小资金开始
3. 实时监控风险
4. 定期检查系统状态
5. 做好数据备份

### 7.3 系统维护

1. 定期更新依赖包
2. 检查日志文件
3. 清理临时文件
4. 备份重要数据
5. 监控系统资源 