# 安装和配置指南

## 1. 环境要求

- Python 3.8+
- pip 20.0+
- Git

## 2. 安装步骤

### 2.1 克隆项目

```bash
git clone https://github.com/yourusername/pp_quant_trade.git
cd pp_quant_trade
```

### 2.2 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 配置说明

### 3.1 数据源配置

在 `config/data_config.yaml` 中配置数据源参数：

```yaml
data_sources:
  tushare:
    token: "your_tushare_token"
  akshare:
    timeout: 30
  baostock:
    username: "your_username"
    password: "your_password"
```

### 3.2 券商接口配置

在 `config/broker_config.yaml` 中配置券商接口参数：

```yaml
brokers:
  xtp:
    client_id: 1
    server_ip: "127.0.0.1"
    server_port: 6001
    username: "your_username"
    password: "your_password"
  eastmoney:
    account: "your_account"
    password: "your_password"
  ths:
    server: "127.0.0.1"
    port: 7708
    account: "your_account"
    password: "your_password"
  tdx:
    server: "127.0.0.1"
    port: 7709
    account: "your_account"
    password: "your_password"
```

### 3.3 策略配置

在 `config/strategy_config.yaml` 中配置策略参数：

```yaml
strategies:
  ma_cross:
    enabled: true
    short_period: 5
    long_period: 20
    position_size: 100
  breakout:
    enabled: true
    period: 20
    threshold: 0.02
    position_size: 100
  mean_reversion:
    enabled: true
    period: 20
    std_dev: 2
    position_size: 100
```

### 3.4 风险控制配置

在 `config/risk_config.yaml` 中配置风险控制参数：

```yaml
risk_control:
  max_position_size: 5000
  max_capital: 100000
  max_drawdown: 0.1
  position_limit: 1000
  volatility_limit: 0.2
  correlation_limit: 0.7
```

## 4. 使用说明

### 4.1 启动系统

```bash
python main.py
```

### 4.2 运行回测

```bash
python -m src.backtest.run_backtest --strategy ma_cross --start_date 2020-01-01 --end_date 2023-12-31
```

### 4.3 实盘交易

```bash
python -m src.trading.run_trading --strategy ma_cross --broker xtp
```

## 5. 常见问题

### 5.1 数据获取失败

- 检查网络连接
- 验证数据源配置是否正确
- 确认API密钥是否有效

### 5.2 券商接口连接失败

- 检查券商交易软件是否正常运行
- 验证账号密码是否正确
- 确认网络连接是否正常

### 5.3 策略运行异常

- 检查策略配置是否正确
- 验证数据格式是否符合要求
- 查看日志文件定位问题

## 6. 更新和维护

### 6.1 更新系统

```bash
git pull
pip install -r requirements.txt
```

### 6.2 日志管理

- 日志文件位于 `logs/` 目录
- 按日期自动分割
- 可通过 `config/log_config.yaml` 配置日志级别和格式

### 6.3 数据备份

- 定期备份 `data/` 目录下的数据文件
- 备份配置文件
- 备份日志文件 