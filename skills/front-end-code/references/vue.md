# Vue 项目约束

> 适用范围：判定为 Vue 项目时（存在 `vue` 依赖、`.vue` 单文件组件）生效。

## UI 组件库

- 统一使用 `Element Plus` 作为 UI 组件库，优先复用其内置组件，不要为已有能力另造一套。

## 组合式工具

- 轮询、防抖、节流、事件监听、剪贴板、本地存储等通用能力，优先使用 `VueUse`（`useIntervalFn`、`useDebounceFn`、`useThrottleFn`、`useEventListener` 等），不要手写 `setInterval` / 定时器管理逻辑。
- 手写这类逻辑容易漏掉组件卸载时的清理，VueUse 已处理好生命周期绑定。

## 生命周期与副作用边界

- `onMounted` 允许在同一组件内多次声明。当存在多块互不相关的初始化逻辑时，**分别用独立的 `onMounted` 声明**，保持每块逻辑的边界与独立性，不要为了“只写一个钩子”把无关逻辑塞进同一个函数体。

  ```ts
  // 推荐：各自独立，便于单独增删
  onMounted(() => {
    initChart();
  });

  onMounted(() => {
    subscribeSocket();
  });
  ```

- 每块副作用逻辑需要清理时，就近在对应的 `onUnmounted` / `onScopeDispose` 中处理，保持成对出现。
