# 安装和配置指南

## 一、系统要求

### 1. 硬件要求
- 电脑：Windows 10/11、MacOS或Linux系统
- 内存：至少4GB
- 硬盘：至少10GB可用空间
- 网络：稳定的互联网连接

### 2. 软件要求
- Python 3.8或更高版本
- pip（Python包管理器）
- Git（用于下载系统）

## 二、安装步骤

### 1. 安装Python
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8或更高版本
3. 运行安装程序
4. 重要：安装时请勾选"Add Python to PATH"选项
5. 完成安装

### 2. 下载系统
1. 打开命令行（终端）
2. 进入您想安装系统的目录
3. 运行以下命令：
```bash
git clone https://github.com/ppswdev/pp_quant_trade.git
cd pp_quant_trade
```

### 3. 安装系统依赖
1. 创建虚拟环境（推荐）：
```bash
# Windows系统：
python -m venv venv
venv\Scripts\activate

# Mac/Linux系统：
python -m venv venv
source venv/bin/activate
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 三、配置系统

### 1. 配置数据源
1. 打开 `config/data_config.yaml` 文件
2. 选择您要使用的数据源（如Tushare）
3. 填入您的账号信息（如Tushare的token）
4. 保存文件

### 2. 配置券商接口
1. 打开 `config/broker_config.yaml` 文件
2. 选择您要使用的券商（如XTP）
3. 填入您的券商账号信息
4. 保存文件

### 3. 配置交易策略
1. 打开 `config/strategy_config.yaml` 文件
2. 选择您要使用的策略
3. 调整策略参数
4. 保存文件

### 4. 配置风险控制
1. 打开 `config/risk_config.yaml` 文件
2. 设置风险控制参数
3. 保存文件

## 四、验证安装

### 1. 运行测试
```bash
python -m pytest tests/
```

### 2. 运行示例
```bash
# 运行回测示例
python -m src.backtest.run_backtest --strategy ma_cross --start_date 2020-01-01 --end_date 2023-12-31
```

## 五、常见问题

### 1. 安装问题
- 如果提示"python不是内部或外部命令"，请检查Python是否正确安装并添加到PATH
- 如果安装依赖包时出错，请检查网络连接
- 如果提示权限错误，请使用管理员权限运行命令

### 2. 配置问题
- 确保配置文件中的账号信息正确
- 检查文件路径是否正确
- 确保配置文件格式正确（YAML格式）

### 3. 运行问题
- 确保Python环境已激活（命令提示符前有(venv)）
- 检查日志文件了解详细错误信息
- 确保所有依赖包都已正确安装

## 六、获取帮助

- 查看详细文档：`docs/` 目录
- 提交问题：在GitHub上创建Issue
- 加入讨论：项目Discussions页面

## 七、安全提示

- 请妥善保管您的账号信息
- 不要将包含账号信息的配置文件上传到GitHub
- 定期更新系统和依赖包
- 实盘交易前请充分测试
- 建议先使用小资金测试 