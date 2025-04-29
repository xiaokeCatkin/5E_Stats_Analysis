# CS:GO 数据分析系统

## 简要介绍
本项目是一个5E竞技平台CS2比赛数据分析工具，能够：
- 通过API获取玩家比赛数据
- 批量处理多个玩家的战绩数据
- 使用大模型(GPT/Gemini等)进行专业分析
- 生成严厉版/鼓励版两种风格的分析报告
- 提供可视化Web界面和API服务

主要功能模块：
- 数据获取：从5E平台的CS2 API获取比赛详情和玩家数据（5E战绩查询开源地址：https://github.com/loveboyme/5E_Play_CS-GO）
- 数据分析：使用AI模型进行专业分析
- 可视化界面：提供Web界面，支持玩家数据查询和分析报告生成
- 报告生成：输出Excel/CSV格式的完整报告
- 批量处理：支持同时处理多个玩家的数据

## 快速开始

### 前置要求
- Python 3.8+
- 安装依赖：`pip install -r requirements.txt`
- 有效的OpenAI API密钥(配置在.env文件中)

### 填好env文件
在文件夹内复制.env.example 为 .env，填入你的openai api key。

此处模型默认使用gemini-2.5-pro-exp-03-25

环境变量目前包括：

OPENAI_API_KEY - OpenAI API密钥
OPENAI_BASE_URL - OpenAI API基础URL（可选）

### 启动Web服务
1. 启动API服务：
```bash
python api/api_server.py
```
2. 打开 web_interface.html 使用可视化界面

## 功能特性

### 数据获取
- 支持5E平台CS2比赛数据API获取
- 支持批量获取多个玩家战绩数据
- 支持自定义时间范围和比赛类型筛选

### 数据分析
- 提供两种分析风格模板：严厉版/鼓励版
- 支持自定义分析模板
- 支持多种大模型选择(GPT/Gemini/Claude等)

### 报告生成
- 自动生成Markdown格式分析报告
- 支持Excel/CSV格式数据导出
- 自动保存分析结果到result目录

## 项目结构
CS_stats_Ana/
├── api/                  # API服务代码
│   └── api_server.py     # Flask API服务
├── Get_Stats/            # 数据获取模块
│   └── main_script.py    # 主数据获取脚本
├── templates/            # 分析模板
│   ├── template_default.txt # 模板的模板
│   ├── template_amuse.txt # 乐子人(好哥们儿)模板
│   ├── template_rage.txt # 严厉版模板
│   └── template_yasashii.txt # 鼓励版模板
├── result/               # 分析结果保存目录
├── web_interface.html    # Web界面
├── llm_analysis.py       # 大模型分析主程序
├── batch_fetch_stats.py  # 批量获取脚本
└── requirements.txt      # 依赖列表



## 贡献指南

### 如何贡献
1. Fork本项目
2. 创建新分支 (`git checkout -b feature/your-feature`)
3. 提交修改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

### 开发规范
- 使用PEP8代码风格
- 为新增功能编写单元测试
- 更新相关文档(包括README)
- 保持提交信息清晰明确

### 问题反馈
如发现任何问题，请在GitHub提交Issue，包括：
- 问题描述
- 重现步骤
- 预期行为
- 实际行为
- 相关截图(如有)


