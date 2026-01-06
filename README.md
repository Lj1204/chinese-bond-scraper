# 中国债券信息获取与文本处理工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于获取中国货币网债券信息并进行文本处理的Python工具包。

## 功能特性

### 1. 债券数据获取
- 从中国货币网API获取债券信息
- 支持多种债券类型筛选
- 按年份过滤债券
- 自动分页获取完整数据
- 数据保存为CSV格式

### 2. 智能正则匹配
- 预定义常见金融文本模式
- 支持自定义正则表达式
- 自动格式化日期、证券代码等
- 灵活的匹配结果处理

## 安装

### 环境要求
- Python 3.8+
- pip 20.0+

### 安装依赖
```bash
pip install -r requirements.txt