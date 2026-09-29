# glab 审查命令清单

## 环境与项目信息

与 pr-creation 技能的 references/glab-api.md 相同：

```bash
git remote -v
which glab
glab auth status

# 从 git remote 提取 NAMESPACE/REPO
export REMOTE=$(git remote -v | head -1 | awk '{print $2}' | sed 's/.*:\(.*\).git$/\1/')
export NS_REPO=$(echo $REMOTE | sed 's/[^/]*\///')  # 如 my-team/my-project
export NAMESPACE=$(echo $NS_REPO | cut -d/ -f1)
export REPO=$(echo $NS_REPO | cut -d/ -f2)

# 获取项目 ID（用于 API）
PROJECT_ID=$(glab api "projects/${NAMESPACE}%2F${REPO}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

## 定位当前分支的 MR

```bash
export BRANCH=$(git branch --show-current)

# 获取 MR IID
MR_IID=$(glab mr list -R "${NS_REPO}" -s ${BRANCH} --state opened \
  | python3 -c "import sys; print(sys.stdin.read().strip().split()[1])")
```

当前分支没有开启的 MR 时停止并告知用户（可提示用 pr-creation 技能先建 MR）。

## MR 详情与 diff

```bash
# MR 详情 JSON：target_branch、milestone、assignee、description、diff_refs 都在这里
glab api "projects/${PROJECT_ID}/merge_requests/${MR_IID}"

# 审查用 diff（仅相对 base 分支的变更）
glab mr diff ${MR_IID} -R "${NS_REPO}"

# diff_refs（inline comment 必需）
glab api "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['diff_refs']; print(d['base_sha'], d['start_sha'], d['head_sha'])"
```

## 合法性检查相关查询

```bash
# approve rule（看 approvals_required 是否 ≥ 1）
glab api "projects/${PROJECT_ID}/merge_requests/${MR_IID}/approval_rules"

# base 分支对应的 PR（pmx link 规则用）：目标不是 main 时，查 base 分支自己的 MR 描述
glab api "projects/${PROJECT_ID}/merge_requests?source_branch=<BASE_BRANCH>&state=opened"

# pmx 检查：对上一步取到的 description（或目标是 main 时的当前 MR description）
# 要求同时包含 "pmx link" 和 "pmx" 两个全匹配子串，不区分大小写
echo "<DESCRIPTION>" | grep -qi 'pmx link' && echo "<DESCRIPTION>" | grep -qi 'pmx'
```

## 提交 inline comment（discussions API）

```bash
# 先取 diff_refs
read BASE_SHA START_SHA HEAD_SHA < <(glab api "projects/${PROJECT_ID}/merge_requests/${MR_IID}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['diff_refs']; print(d['base_sha'], d['start_sha'], d['head_sha'])")

# 在新增代码的某一行发 inline comment
glab api --method POST "projects/${PROJECT_ID}/merge_requests/${MR_IID}/discussions" \
  -f "body=$(cat ~/Downloads/comment.md)" \
  -f "position[base_sha]=${BASE_SHA}" \
  -f "position[start_sha]=${START_SHA}" \
  -f "position[head_sha]=${HEAD_SHA}" \
  -f "position[position_type]=text" \
  -f "position[new_path]=<FILE_PATH>" \
  -f "position[new_line]=<LINE>"

# 评论删除/修改的旧代码行时改用：
#   -f "position[old_path]=<FILE_PATH>" -f "position[old_line]=<LINE>"
```

## 注意事项

- 命名空间中的 `/` 在 API URL 中必须转义为 `%2F`
- `position` 三要素（base_sha/start_sha/head_sha）缺失或 sha 过期时 API 会报 400，需重新拉取 diff_refs
- 多行 body 用临时文件 + `$(cat <file>)` 传值，不要在命令行里塞多行字符串
- `glab api` 的 `-f` 参数支持多次传值
