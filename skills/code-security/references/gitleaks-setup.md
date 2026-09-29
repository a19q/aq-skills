# Husky + Gitleaks 配置步骤

> 目标：在提交前自动扫描敏感信息，防止 API Key、Token、私钥等泄露到仓库。
> **仅在用户明确要求「配置 Gitleaks」时执行本流程**；默认模式只做代码合法性检查。

## 1. 安装开发依赖

在项目根目录执行：

```bash
npm install -D husky gitleaks
```

## 2. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录和一个默认的 `pre-commit` 钩子文件。若仓库已初始化，确保在根目录执行。

## 3. 创建 `.gitleaks.toml`

在项目根目录创建 `.gitleaks.toml`，作为 Gitleaks 配置文件，内容按下面模板生成（可根据团队需要调整）：

```toml
# Gitleaks 配置文件
title = "Gitleaks 代码安全检测配置"

# 扫描规则
[extend]
# 使用默认规则集
useDefault = true

# 自定义规则
[[rules]]
id = "generic-api-key"
description = "检测通用 API 密钥"
regex = '''(?i)(api[_-]?key|apikey|api[_-]?secret)['"]?\s*[:=]\s*['"]?[a-zA-Z0-9]{20,}'''
tags = ["key", "API"]

[[rules]]
id = "sk-prefix-key"
description = "检测 sk- 开头的密钥（OpenAI/Stripe 等）"
regex = '''sk-[a-zA-Z0-9]{20,}'''
tags = ["key", "secret", "openai", "stripe"]

[[rules]]
id = "generic-secret"
description = "检测通用密钥格式"
regex = '''(?i)(secret|password|passwd|pwd|token|access[_-]?token)['"]?\s*[:=]\s*['"]?[a-zA-Z0-9_\-]{16,}'''
tags = ["secret", "password"]

[[rules]]
id = "private-key"
description = "检测私钥"
regex = '''-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'''
tags = ["key", "private"]

[[rules]]
id = "aws-access-key"
description = "检测 AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["key", "AWS"]

[[rules]]
id = "jwt-token"
description = "检测 JWT Token"
regex = '''eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'''
tags = ["token", "JWT"]

# 白名单配置 - 排除不需要扫描的文件
[allowlist]
description = "全局白名单"

# 文件路径
paths = [
  '''yarn\.lock''',
  '''package-lock\.json''',
  '''\.git/''',
  '''node_modules/''',
  '''dist/''',
  '''build/''',
  '''out/''',
  '''\.DS_Store''',
  '''.vscode''',
]

# 排除特定的正则匹配
regexes = [
  '''example\.com''',
]

# 排除特定提交
commits = []
```

## 4. 修改 `.husky/pre-commit`

在 Husky 默认内容基础上接入 Gitleaks，**保留已有命令**（如 `npm test`）：

```sh
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# 运行单元测试（如不需要可删除）
# npm test

# 使用 Gitleaks 检测暂存区代码中的敏感信息
npx gitleaks protect --staged --config=.gitleaks.toml
```

## 5. 验证

```bash
npx gitleaks protect --staged --config=.gitleaks.toml
```

- 无输出、退出码 0 → 暂存区无敏感信息，配置生效
- 有输出 → 列出了疑似密钥/私钥的文件与位置，提交会被阻止；先处理再验证

## 提交被阻止时

之后每次 `git commit`，若扫描发现疑似密钥/私钥等信息，会阻止提交并给出具体位置。开发者需要先处理（移除密钥、改用环境变量，或确认误报后加入 allowlist）再重试提交。
