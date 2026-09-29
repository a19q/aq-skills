---
name: front-end-code
description: 编写、修改或评审前端代码（Web / 桌面端 / 移动端 H5）时必须遵循的开发约束与背景知识。覆盖协作流程、命名规范、组件与文件结构、测试策略、样式还原，以及 TypeScript、React、Vue、Electron 与纯 UI 阶段 mock 数据的专项规则。
---

# 前端开发约束

本技能是**背景知识**，不是可执行命令。它描述「写前端代码时必须遵守什么」，不描述「执行什么步骤」。

**标准指令（在整个前端任务期间持续生效）**：本文件只是索引。任何时候要动手写或改前端代码，先按下表判断当前需要哪些参考文件并读取；只读与当前技术栈、当前任务阶段相关的，不要一次性全部读取。任务中途切换到新的技术栈或新阶段时，按表补读对应文件。

## 通用规则（适用于所有前端项目）

| 参考文件 | 包含内容 | 何时加载 |
| --- | --- | --- |
| [references/general.md](references/general.md) | 与技术栈无关的通用约束，共五节：①协作与开发流程（确认优先、任务拆分、何时先出设计方案、`yarn`、SOLID/DRY）；②命名规范速查表；③组件与文件结构（复用、文件夹 + index、具名导出、禁止桶导出、500 行拆分、深拷贝、副作用模块边界）；④测试规范；⑤样式与 UI 还原（原子样式优先、`cn` 拼接类名、弹窗高度） | **任何前端任务开始前必读**；其中具体小节可随任务类型对照（命名看第二节、结构看第三节、测试看第四节、样式看第五节） |

## 专项规则（按技术栈与任务阶段）

| 参考文件 | 包含内容 | 何时加载 |
| --- | --- | --- |
| [references/ts.md](references/ts.md) | TypeScript 语言层约束：禁止 `any`、类型复用、`interface` 与 `type` 的取舍、以 `as const` 常量对象替代 `enum`、遍历方式、`switch` 的 `{}`、可选链等代码质量细则 | 项目使用 TypeScript，或需要新增/修改类型定义、`.ts` / `.tsx` 文件时加载。绝大多数前端任务都适用 |
| [references/react.md](references/react.md) | React 生态约束：`react-router` 统一入口、Zustand 配合 `useShallow`、React Compiler 下的性能优化取舍、组件内 state → function → useEffect 顺序、Ant Design 静态方法禁忌 | 判定项目为 React 项目（存在 `react` 依赖、`.tsx` 组件、React 路由配置）时加载 |
| [references/vue.md](references/vue.md) | Vue 生态约束：Element Plus 组件库、VueUse 优先用于轮询 / 防抖等能力、`onMounted` 等生命周期的边界与独立性 | 判定项目为 Vue 项目（存在 `vue` 依赖、`.vue` 单文件组件）时加载 |
| [references/electron.md](references/electron.md) | Electron 主进程模块系统背景知识：单 bundle 下的模块缓存机制、副作用为何不会重复执行、哪三种情况才会真正重复、如何验证 | 项目为 Electron 应用，且需要改动主进程模块、跨模块共享单例（窗口池、`ipcMain` 注册）或排查「副作用被执行多次」疑虑时加载 |
| [references/ui-dev-hardcode.md](references/ui-dev-hardcode.md) | 纯 UI 阶段（接口尚未接入）的 hardcode / mock 数据规则：数据就地定义、不复刻服务端职责、不造配合逻辑的假数据、写操作无副作用、跨页传值方式 | 任务处于「先做 UI、接口后续接」阶段，或需要写占位数据、还原静态页面时加载 |

## 最低要求

即使不加载任何参考文件，以下三条始终生效：

1. 不确定的技术细节先问，不要猜测补齐 API 或类型声明。
2. 不使用 `any`；不使用 `JSON.parse(JSON.stringify(...))` 做深拷贝。
3. 新增测试前先征得用户同意。
