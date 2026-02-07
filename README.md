<div align="center">

# 🌊 FlowSight - 数据流动，洞察可见

**一站式开源数据中台：从采集、处理到可视化标注的全链路解决方案**

[![](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![](https://img.shields.io/github/stars/LOMI1015/flowsight?color=yellow&style=for-the-badge&logo=github)](https://github.com/LOMI1015/flowsight/stargazers)
[![](https://img.shields.io/github/forks/LOMI1015/flowsight?color=lightblue&style=for-the-badge&logo=github)](https://github.com/LOMI1015/flowsight/network/members)
[![](https://img.shields.io/badge/Made%20with-Python%2BVue3-red?style=for-the-badge&logo=python)](https://www.python.org/)
[![](https://img.shields.io/badge/Deploy-Docker-blue?style=for-the-badge&logo=docker)](https://www.docker.com/)

**🌊 数据流** | **👁️ 可视化** | **⚡ 实时标注** | **📊 洞察力**

</div>

---

## 🚀 项目简介

FlowSight 是一个现代化的开源数据中台，旨在简化从原始数据采集到最终可视化洞察的全过程。我们提供一套完整的工具链，帮助开发者、数据分析师和企业快速构建数据驱动的应用。

### 🎯 核心特性

- **一体化工作流**：数据采集 → 处理 → 存储 → 标注 → 可视化，端到端无缝衔接
- **实时协作看板**：支持多人在线协同的数据标注与可视化看板
- **模块化架构**：基于微服务思想设计，易于扩展和定制
- **云原生部署**：Docker & Kubernetes 友好，轻松部署到任何云环境
- **开发者友好**：完善的API文档，丰富的SDK支持

---

## 🛠️ 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **后端** | [FastAPI](https://fastapi.tiangolo.com/) | 高性能 ASGI 框架，自带交互式API文档 |
| **数据库** | [PostgreSQL](https://www.postgresql.org/) | 强大的关系型数据库，支持JSONB |
| **缓存/队列** | [Redis](https://redis.io/) | 高性能键值存储与任务队列 |
| **对象存储** | [MinIO](https://min.io/) | S3兼容的对象存储，可自托管 |
| **前端** | [Vue 3](https://vuejs.org/) + [TypeScript](https://www.typescriptlang.org/) | 现代化前端框架，类型安全 |
| **UI组件** | [Ant Design Vue](https://www.antdv.com/) | 企业级UI设计语言与组件库 |
| **图表库** | [ECharts](https://echarts.apache.org/) | 强大的数据可视化图表库 |
| **部署** | [Docker](https://www.docker.com/) + [Nginx](https://nginx.org/) | 容器化部署与反向代理 |

---