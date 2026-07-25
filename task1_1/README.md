# Task1.1 配电网拓扑悬空异常检测

## 1. 项目简介

本项目面向配电网图模校验任务中的设备拓扑悬空检测问题。

针对配电网模型数据中可能存在的设备连接缺失、孤立区域、电源路径缺失等问题，基于设备模型数据、端子连接关系以及主配网电源追踪信息，构建配电网拓扑图，实现三类异常检测：

1. 非末端设备单端悬空端点检测；
2. 多设备连片悬空检测；
3. 无母线接入拓扑孤岛检测。
---

## 2. 技术路线
SQL数据
↓
CSV转换
↓
设备数据清洗
↓
拓扑关系构建
↓
设备语义解析
↓
连通区域分析
↓
异常规则检测
↓
结果输出
---

## 3. 项目结构
Task1.1_Topology_Check

├── data
│ ├── raw
│ └── processed
│
├── preprocess
│
├── detection
│
├── docs
│
├── output
│
└── README.md

---

## 4. 数据说明

主要输入数据包括：

- 配网设备模型数据
- 配网端子数据
- 主网设备及端子数据
- 馈线电源追踪数据


经过预处理后生成：

- equipment_clean.csv
- terminal_clean.csv
- edge.csv
- power_source.csv
- feeder_power_trace.csv


用于后续拓扑分析。

---

## 5. 环境要求

Python >= 3.10

主要依赖：

- pandas
- networkx
- openpyxl


安装：

```bash
pip install -r requirements.txt

---

## 6. 使用方法

数据预处理

运行：

python preprocess/preprocess.py

生成标准化数据。

电源路径分析

运行：

python preprocess/build_power_trace.py

生成：

feeder_power_trace.csv
异常检测

运行：

python detection/detect_task1_1.py

输出：

output/task1_1_result.xlsx

---

## 7. 输出结果

最终检测结果：

output/task1_1_result.xlsx

包含：

异常设备编号
设备名称
所属馈线
异常类型
问题说明

同时生成：

debug_component.csv
debug_degree.csv

用于算法验证和结果分析。
