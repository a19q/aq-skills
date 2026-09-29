# React 项目约束

> 适用范围：判定为 React 项目时（存在 `react` 依赖、`.tsx` 组件、React 路由配置）生效。


## 基础语法规范
1. ts类型规范，显性声明类型，如 `useState<boolean>(false)`

## 路由

- 新版 `react-router` 已把 `react-router-dom` 合并进 `react-router`，统一从 `react-router` 引入并做路由管理，不要再依赖 `react-router-dom`。

## 状态管理

- 使用 Zustand 且一次读取多个状态时，用 `useShallow` 做浅比较获取，避免不必要的 re-render。

  ```tsx
  const { user, token } = useAuthStore(
    useShallow((s) => ({ user: s.user, token: s.token }))
  );
  ```

## 性能优化

- 项目若启用了 React Compiler，无需手动使用 `memo`、`useCallback`、`useMemo`，编译器会自动处理；不要为“优化”而添加这些包装。
- 未启用 React Compiler 时，仅在确有渲染开销证据时才手动优化。

## 组件代码结构

- React 组件内部必须遵循严格顺序：**state（状态定义） → function（函数定义） → useEffect（副作用处理）**。

  ```tsx
  export const UserPanel = ({ userId }: IUserPanelProps) => {
    // 1. state
    const [loading, setLoading] = useState(false);

    // 2. function
    const handleRefresh = () => { /* ... */ };

    // 3. useEffect
    useEffect(() => { /* ... */ }, [userId]);

    return null;
  };
  ```

- 组件统一 `export const` 具名导出，不使用 `function` 声明 + `export default`。
- 组件 Props 接口以 `Props` 结尾，如 `IUserPanelProps`。

## Ant Design

- **严格禁止**在组件中使用 `import { message } from "antd"` 这类静态方法，必须改为通过 `App.useApp()` 获取实例：

  ```tsx
  const { message, modal, notification } = App.useApp();
  ```

  静态方法拿不到 `ConfigProvider` 的主题与 context，会导致样式和国际化不一致。
