# 架构文档模板（ARCHITECTURE.md）

生成 `ARCHITECTURE.md` 时按以下 11 节结构填写。全部使用**简体中文**；节标题保留中英对照，便于 agent 与工具识别。占位符 `[...]` 全部替换为实际内容；某节确实不适用时保留标题并写「暂无」+ 一句原因，**不要删除整节**。

---

# Architecture Overview（架构总览）

本文档是随代码库演进持续更新的「活文档」（living document），目标是让 agent 与新成员第一天就能快速、全面地理解代码库架构，实现高效导航与有效贡献。代码库演进时同步更新本文档。

## 1. 项目结构（Project Structure）

> 填写要点：按架构分层或功能域组织目录树；每一行用 `#` 注释说明该目录/文件的职责；突出关注点分离。以下为示例结构，按实际项目裁剪替换，保留「目录 → 一句话职责」的注释风格。

```
[项目根目录]/
├── backend/              # 服务端代码与 API
│   ├── src/              # 服务端主源码
│   │   ├── api/          # API 端点与控制器
│   │   ├── client/       # 业务逻辑与服务实现
│   │   ├── models/       # 数据库模型/模式
│   │   └── utils/        # 服务端工具函数
│   ├── config/           # 服务端配置文件
│   ├── tests/            # 服务端单元与集成测试
│   └── Dockerfile        # 服务端部署 Dockerfile
├── frontend/             # 客户端 UI 代码
│   ├── src/              # 前端主源码
│   │   ├── components/   # 可复用 UI 组件
│   │   ├── pages/        # 应用页面/视图
│   │   ├── assets/       # 图片、字体等静态资源
│   │   ├── services/     # 前端 API 交互服务
│   │   └── store/        # 状态管理（如 Redux、Vuex、Context API）
│   ├── public/           # 公开静态资源（如 index.html）
│   ├── tests/            # 前端单元与 E2E 测试
│   └── package.json      # 前端依赖与脚本
├── common/               # 前后端共享代码、类型与工具
│   ├── types/            # 共享 TypeScript/接口定义
│   └── utils/            # 通用工具函数
├── docs/                 # 项目文档（API 文档、上手指南等）
├── scripts/              # 自动化脚本（部署、数据填充等）
├── .github/              # GitHub Actions 或其他 CI/CD 配置
├── .gitignore            # Git 忽略规则
├── README.md             # 项目概览与快速上手
└── ARCHITECTURE.md       # 本文档
```

## 2. 高层系统图（High-Level System Diagram）

> 填写要点：给出简单的块图（如 C4 Model Level 1 系统上下文图）或清晰的文字描述；聚焦数据如何流动、服务间如何通信、关键架构边界在哪。交互复杂时可补 Mermaid 图。

```
[用户] <--> [前端应用] <--> [后端服务 1] <--> [数据库 1]
                               |
                               +--> [后端服务 2] <--> [外部 API]
```

## 3. 核心组件（Core Components）

> 填写要点：列出并简要描述系统的主要组件；每个组件写清首要职责与使用的关键技术。前端、每个重要后端服务各一小节，结构如下。

### 3.1. 前端（Frontend）

- 名称：[如 Web 应用、移动端应用]
- 描述：[首要用途、关键功能，用户或其他系统如何与之交互]
- 技术栈：[如 React、Next.js、Vue.js、Swift/Kotlin、HTML/CSS/JS]
- 部署：[如 Vercel、Netlify、S3/CloudFront]

### 3.2. 后端服务（Backend Services）

#### 3.2.1. [服务名 1]

- 名称：[如用户管理服务、数据处理 API]
- 描述：[用途，如「处理用户认证与个人资料管理」]
- 技术栈：[如 Node.js (Express)、Python (Django/Flask)、Java (Spring Boot)、Go]
- 部署：[如 AWS EC2、Kubernetes、Serverless (Lambda/Cloud Functions)]

（每个重要后端服务重复以上结构，按需增加 3.2.2、3.2.3……）

## 4. 数据存储（Data Stores）

> 填写要点：列出并描述使用的数据库与其他持久化存储；只列关键表/集合名，无需完整 schema。

### 4.1. [数据存储类型 1]

- 名称：[如主用户数据库、分析数据仓库]
- 类型：[如 PostgreSQL、MongoDB、Redis、S3、Firestore]
- 用途：[存储什么数据、为什么]
- 关键表/集合：[如 users、products、orders]

### 4.2. [数据存储类型 2]

- 名称：[如缓存、消息队列]
- 类型：[如 Redis、Kafka、RabbitMQ]
- 用途：[如「缓存高频访问数据」或「服务间通信」]

## 5. 外部集成 / API（External Integrations / APIs）

> 填写要点：列出系统交互的第三方服务或外部 API；每个服务写清用途与集成方式。

- [服务名 1，如 Stripe、SendGrid、Google Maps API]
  - 用途：[如「支付处理」]
  - 集成方式：[如 REST API、SDK]

## 6. 部署与基础设施（Deployment & Infrastructure）

- 云服务商：[如 AWS、GCP、Azure、自托管/本地部署]
- 关键服务：[如 EC2、Lambda、S3、RDS、Kubernetes、Cloud Functions]
- CI/CD 流水线：[如 GitHub Actions、GitLab CI、Jenkins、CircleCI]
- 监控与日志：[如 Prometheus、Grafana、CloudWatch、ELK Stack]

## 7. 安全考量（Security Considerations）

> 填写要点：突出关键安全面、认证机制、数据加密实践。

- 认证：[如 OAuth2、JWT、API Keys]
- 授权：[如 RBAC、ACL]
- 数据加密：[如传输层 TLS、静态数据 AES-256]
- 关键安全工具/实践：[如 WAF、定期安全审计]

## 8. 开发与测试环境（Development & Testing Environment）

- 本地搭建：[链接 CONTRIBUTING.md 或简述关键步骤]
- 测试框架：[如 Jest、Pytest、JUnit]
- 代码质量工具：[如 ESLint、Black、SonarQube]

## 9. 未来规划 / 路线图（Future Considerations / Roadmap）

> 填写要点：简述已知的架构债、计划的重大变更、可能影响架构的未来特性。无法确认时基于代码证据给出建议，每条标注「建议」。

- [如「从单体迁移到微服务」]
- [如「引入事件驱动架构实现实时更新」]

## 10. 项目标识（Project Identification）

- 项目名称：[项目名]
- 仓库地址：[Repository URL]
- 主要联系人/团队：[负责人/团队名]
- 最后更新日期：[YYYY-MM-DD]

## 11. 术语表 / 缩略语（Glossary / Acronyms）

> 填写要点：定义项目专有术语与缩略语；通用技术名词不收。

- [缩略语]：[完整定义]
- [术语]：[解释]
