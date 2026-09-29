# Electron 项目约束与模块系统背景知识

> 适用范围：Electron 应用，且需要改动主进程模块、跨模块共享单例（窗口池、`ipcMain` 注册等），或排查“副作用是否被执行多次”的疑虑时加载。

## 结论先说

Electron 主进程经 `vite-plugin-electron` 打成**一个 bundle**，运行在 Node 的模块系统里，因此：

**同一模块被多处 import，模块体只求值一次，副作用只发生一次。** 可以放心在多个文件中导入同一模块的单例，不会产生新的副作用。

## 为什么

- **CJS（`require`）**：有 `require.cache`，按**已解析的绝对路径**做 key。第一次 `require('./meeting-notice')` 执行模块体并缓存，第二次直接返回缓存。
- **ESM**：有 module record 注册表，同一模块 spec 同样只求值一次。

两处 `import { checkAndCleanup } from "./meeting-notice"` 解析到的是同一路径，命中同一份缓存，所以 `checkAndCleanup` 也是同一个函数引用。

## 什么情况下才会「副作用重复」

必须满足「**模块被当成两个不同的模块**」，常见三种：

1. **解析路径不同**：一处用 `./meeting-notice`、另一处用绝对路径或带不同后缀。`require.cache` 按路径做 key，会被当成两个模块各执行一次。
2. **打进两个独立 bundle**：例如 main 和某个 worker 各自打包了一份。主进程为单 bundle 时不存在此问题。
3. **CJS / ESM 双重引用**：同一文件既被 `require` 又被 `import`，在模块系统边界上可能各算一份。主进程统一打包时不存在。

只要项目内引用路径写法一致、主进程单 bundle，就不用担心「多 import 一次 → 单例池多一份、池窗口数量翻倍、`ipcMain.handle` 重复注册报错」。

## 实践建议

- 需要在另一个模块（如 `protocol.ts`）读取某模块导出的单例（如 `noticePool`）时，直接 `import` 即可，这只是多一个地方读取已存在的单例，**不会**产生新的副作用。
- 保持同一模块在项目内的**引用路径写法统一**（都用相对路径且后缀写法一致），这是避免副作用重复的关键前提。
- 独立的功能模块应作为副作用模块在导入时自行生效，而不是导出一个 `init()` 让每个导入方手动调用——后者反而更容易被重复触发。

## 如何验证

在目标模块（如 `meeting-notice.ts`）顶层加一行：

```ts
console.log('meeting-notice module evaluated');
```

运行后，无论被 import 几次，这条日志只会打印一次。
