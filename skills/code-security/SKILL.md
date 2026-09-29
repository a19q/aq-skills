---
name: code-security
description: 代码安全与合法性检查。默认模式：扫描代码中的安全隐患——硬编码密钥/凭据、SQL 注入、XSS、不安全配置（CORS、加密算法、权限）、敏感数据暴露——并输出具体位置、风险等级（高/中/低）、修复建议与最佳实践；只检查不改动、不安装任何依赖。仅当用户明确要求「配置 Gitleaks」时，才执行 Husky + Gitleaks 提交前敏感信息扫描的完整配置。用户提到「代码安全」「安全检查」「代码合法性检查」「扫描敏感信息/密钥」时使用默认模式，提到「配置 Gitleaks」时才进入配置模式。
license: Apache-2.0
allowed-tools: Bash, Read, Grep, Glob
---

# 代码安全

两种模式，**先判断用户要的是哪种，再动手**：

| 模式 | 触发条件 | 做什么 |
| --- | --- | --- |
| ① 代码合法性检查 | **默认**。用户提到「安全检查」「代码合法性检查」「扫一下敏感信息」等，或要求审查代码安全性 | 只扫描、只报告；不改代码、不装依赖、不改任何配置 |
| ② 配置 Gitleaks | **仅当用户明确说出**「配置 Gitleaks」「配置 gitleaks 代码安全检测」「加提交前密钥扫描」等 | 在项目中配置 Husky + Gitleaks pre-commit 钩子 |

**核心红线：用户没有明确要求配置 Gitleaks 时，绝不执行模式②**——不 `npm install`、不改 `package.json`、不创建 `.husky/`、不创建 `.gitleaks.toml`。拿不准用户是否要配置时，先问一句再动手。

## 模式①：代码合法性检查（默认）

### 扫描范围

- 用户指定了文件/目录 → 只扫指定范围
- 未指定 → 默认扫本次改动：`git diff --name-only HEAD` 与 `git status --short` 里的文件；无 git 上下文时扫当前目录

### 检查项

- API 密钥、密码或机密信息（硬编码的 token、secret、password）
- 硬编码凭据（数据库连接字符串、访问密钥等）
- 潜在的 SQL 注入漏洞（未参数化的 SQL 查询）
- XSS 漏洞（未转义的用户输入、`innerHTML` 使用等）
- 不安全的配置（CORS 配置、加密算法、权限设置等）
- 敏感数据暴露（日志中的敏感信息、错误消息泄露等）

### 扫描方式

先用 Grep 按特征定位，再 Read 上下文确认，避免只凭单行误报。常用特征（按需扩展）：

```bash
# 硬编码密钥/凭据
(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*['"][a-zA-Z0-9]{16,}
(?i)(secret|password|passwd|pwd|token|access[_-]?token)\s*[:=]\s*['"][^'"]{8,}
sk-[a-zA-Z0-9]{20,}                                        # OpenAI/Stripe 风格
AKIA[0-9A-Z]{16}                                           # AWS Access Key
-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----           # 私钥
eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+          # JWT

# 常见漏洞
innerHTML\s*=|dangerouslySetInnerHTML|v-html|document\.write    # XSS
(SELECT|INSERT|UPDATE|DELETE).*(\+\s*\w+|\$\{|f"|format\()      # 拼接式 SQL
Access-Control-Allow-Origin.*\*                                 # CORS 过宽
md5|sha1(?![0-9a-f])|DES                                        # 弱加密算法
console\.(log|info|debug|warn|error).*(?i:password|token|secret|key)  # 日志泄露
```

### 报告格式

发现问题时逐条输出，按风险从高到低排序：

1. **问题的具体位置和代码片段**（`文件路径:行号` + 代码）
2. **安全风险等级**：高（可直接利用的密钥泄露、注入）/ 中（需特定条件触发）/ 低（不规范但有缓解措施）
3. **详细的修复建议和示例代码**（给出修复后的代码，而不是只说「建议修复」）
4. **最佳实践建议**（改用环境变量、密钥管理服务、参数化查询、输出转义等）

- 没有发现问题时明确说明「未发现 XX 类问题」，不为凑数报低价值项
- **模式①只报告，不修改任何代码**；用户接着要求修复时再改
- 报告完毕后可提示一句：如需提交前自动拦截，可明确要求「配置 Gitleaks」进入模式②

## 模式②：配置 Gitleaks（仅用户明确要求时）

目标：提交前自动扫描敏感信息，防止 API Key、Token、私钥等泄露到仓库。

前置确认：项目根目录有 `package.json` 且是 git 仓库，否则停止并告知用户。

完整步骤（安装依赖、husky init、生成 `.gitleaks.toml` 模板、写 pre-commit 钩子、验证）见 [references/gitleaks-setup.md](references/gitleaks-setup.md)。

执行要点：

- 已有 pre-commit 内容（如 `npm test`）要**保留**，只追加 gitleaks 命令
- `.gitleaks.toml` 按项目类型微调 allowlist（lock 文件、dist、node_modules 等）
- 配完跑一次 `npx gitleaks protect --staged --config=.gitleaks.toml` 验证，并汇报结果
- 完成后告知用户：此后每次 `git commit` 若发现疑似密钥/私钥会被阻止并给出位置，需先处理再重试
