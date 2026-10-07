# glab 命令清单

## 环境探测

```bash
git remote -v
which glab
glab auth status          # 应显示 Logged in to <HOST> as <USERNAME>
```

## 分支创建与推送

```bash
git checkout -b <BRANCH>
git push -u origin <BRANCH>
```

## 提交代码

```bash
git add .
git commit -m "简短提交信息"
```

## 解析项目信息

```bash
# 从 git remote 提取 NAMESPACE/REPO
export REMOTE=$(git remote -v | head -1 | awk '{print $2}' | sed 's/.*:\(.*\).git$/\1/')
export NS_REPO=$(echo $REMOTE | sed 's/[^/]*\///')  # 如 my-team/my-project
export NAMESPACE=$(echo $NS_REPO | cut -d/ -f1)
export REPO=$(echo $NS_REPO | cut -d/ -f2)

# 获取项目 ID（用于 API）
PROJECT_ID=$(glab api "projects/${NAMESPACE}%2F${REPO}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

## 查询里程碑

```bash
# 全部里程碑
glab api "projects/${NAMESPACE}%2F${REPO}/milestones?state=all&per_page=100"

# 取最新激活里程碑（按截止日期降序，第二个 pipe 取 ID）
LATEST_MILESTONE_ID=$(glab api "projects/${NAMESPACE}%2F${REPO}/milestones?state=active&per_page=100" \
  | python3 -c "import sys,json; ms=json.load(sys.stdin); print(max(ms, key=lambda x: x.get('due_date', '') or '')['id'] if ms else '')")

# 取最新激活里程碑名称
LATEST_MILESTONE_TITLE=$(glab api "projects/${NAMESPACE}%2F${REPO}/milestones?state=active&per_page=100" \
  | python3 -c "import sys,json; ms=json.load(sys.stdin); print(max(ms, key=lambda x: x.get('due_date', '') or '')['title'] if ms else '')")
```

## 创建里程碑（不存在时）

用户指定了里程碑但不存在时创建：

```bash
glab api --method POST "projects/${NAMESPACE}%2F${REPO}/milestones" \
  -f "title=1.0.0" \
  -f "state=active"
```

## 查询用户

```bash
glab api "users?username=<USERNAME>"
# 取当前登录用户（默认取认证用户作为本人）
```

## 远端预检（正式场景执行前，只读）

```bash
# 当前所在分支
git branch --show-current

# 远端是否已有同名分支（有输出即存在）
git ls-remote --heads origin <BRANCH>

# 该分支是否已有打开的 MR
glab mr list -R "${NS_REPO}" -s <BRANCH> --state opened
```

命中任一项即**停止并汇报**，不改分支、不推送、不建 MR，等用户指示。

## 创建 Issue

```bash
glab issue create -R "${NS_REPO}" \
  -t "<TITLE>" -d "" --no-editor -y
```

Issue 创建后，从输出中提取 IID（如 `#123`），关掉 `-` 用 `--no-editor`。

## 创建 MR

```bash
glab mr create -R "${NS_REPO}" \
  -s <BRANCH> -b <BASE_BRANCH> \
  --title "<TITLE>" \
  -F <BODY_FILE> --no-editor -y
```

- `-s` = source branch（当前分支）
- `-b` = target base branch（如 `main`）
- `-F` = body 文件路径（临时文件，多行内容用此方式）
- body 文件包含 `Close #<ISSUE_ID>`

## 设为 Draft / WIP

```bash
# 创建后通过 API 设为 draft（glab 本身不支持 --draft 标志时）
MR_IID=$(glab mr list -R "${NS_REPO}" -s <BRANCH> --state opened \
  | python3 -c "import sys; print(sys.stdin.read().strip().split()[1])")

glab api --method PUT "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  -f "wip_event=wip"        # 设为 WIP（GitLab 旧版本）
# 或使用 WIP 标题前缀
# glab api --method PUT "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
#   -f "title=WIP: <TITLE>"
```

## 补设 assignee / milestone / 审批数

```bash
# 获取 MR IID
MR_IID=$(glab mr list -R "${NS_REPO}" -s <BRANCH> --state opened \
  | python3 -c "import sys; print(sys.stdin.read().strip().split()[1])")

# 设置 assignee（用户 ID）
glab api --method PUT "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  -f "assignee_id=<USER_ID>"

# 设置 milestone
glab api --method PUT "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  -f "milestone_id=<MILESTONE_ID>"

# 设置审批规则
glab api --method POST "projects/${PROJECT_ID}/merge_requests/${MR_IID}/approval_rules" \
  -f "name=Minimum required approvals" \
  -f "approvals_required=<APPROVALS>" \
  -f "rule_type=any_approver"
```

## 补设 label（用户确认后）

用户确认要绑定标签时执行；未确认不主动设。

```bash
# 查项目已有标签（确认标签名存在）
glab api "projects/${PROJECT_ID}/labels?per_page=100"

# 给 MR 加标签（逗号分隔多个）
glab api --method PUT "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  -f "add_labels=<LABEL>"

# 给 Issue 加标签
glab api --method PUT "projects/${PROJECT_ID}/issues/<ISSUE_IID>" \
  -f "add_labels=<LABEL>"
```

## 安全字段检查（命中即终止，不 commit/push/MR）

```bash
# 检查当前分支暂存区
git diff --cached -G'(cscKeyPassword|token)' --name-only
# 检查当前分支全部修改
git diff -G'(cscKeyPassword|token)' --name-only

# 检查整个仓库是否有文件包含敏感字（避免误提交）
git grep -n -i 'cscKeyPassword' -- ':!*.log*' ':!node_modules/'
# 命中任一即终止并警告
```

## 注意事项

- `glab mr create` 不支持直接传 `--milestone`，必须通过 API 补设
- `glab issue create` 的 `-d` 参数传空字符串 `""` 表示空 body
- 命名空间中的 `/` 在 API URL 中必须转义为 `%2F`
- `glab` 的 `-F` 参数同时支持 MR 创建和 Issue 创建
- 所有 `glab api` 命令的 `-f` 参数支持多次传值