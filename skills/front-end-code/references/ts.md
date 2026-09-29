# TypeScript / JavaScript 语言约束

> 适用范围：所有使用 TypeScript 的前端项目，以及需要新增或修改类型定义、`.ts` / `.tsx` 文件的任务。

## 类型安全

- **禁止 `any`**：不能使用 `any` 类型，必须明确定义类型。确实无法确定时，向用户确认真实类型，而不是用 `any` 兜过去。
- **全面强类型**：在整个代码库中保持完善的强类型定义，以保证类型安全。
- **类型复用**：涉及 TS 类型与表单时，优先使用项目中已有的 TS 类型，不要自己另建一套重复类型。
- **不凭空造声明**：不要凭空生成或修改 `d.ts` 类型声明文件；发现类型缺失应先询问，而不是自行补齐一个猜测的定义。

## 类型定义写法

- **接口与类型别名**：按语义恰当地选用 `interface`（可扩展的对象结构、组件 Props）与 `type`（联合类型、映射类型、函数签名）。
- **清晰的定义**：类型定义要清晰、易读，避免层层嵌套的匿名内联类型。
- **常量对象替代枚举**：使用带 `as const` 的常量对象替代 `enum`。

  ```ts
  // 推荐
  export const ORDER_STATUS = {
    PENDING: 'pending',
    PAID: 'paid',
    CANCELED: 'canceled',
  } as const;

  export type OrderStatus = (typeof ORDER_STATUS)[keyof typeof ORDER_STATUS];

  // 不推荐
  enum OrderStatus {
    Pending = 'pending',
  }
  ```

- **命名**：类型使用 PascalCase；接口使用 `I` + PascalCase（如 `IUser`）；组件 Props 接口必须以 `Props` 结尾（如 `IButtonProps`）。

## 代码质量细则

- **遍历方式**：当目的是循环访问数组、而非对数据本身做变换时，禁止使用 `forEach`，优先使用 `for` 循环。（需要映射/过滤/归约得到新数据时，`map` / `filter` / `reduce` 仍然是正确选择。）
- **`switch` 块**：`switch` 的每个 `case` 一定要用 `{}` 包裹，避免变量提升与作用域穿透。

  ```ts
  switch (status) {
    case ORDER_STATUS.PAID: {
      const label = '已支付';
      return label;
    }
    default: {
      return '';
    }
  }
  ```

- **可选链**：通过 `.` 访问对象属性或方法时，要使用可选链，如 `data?.name`、`handler?.()`。
- **深拷贝**：优先 `structuredClone`，禁止 `JSON.parse(JSON.stringify(...))`。
- **注释**：必要时使用 JSDoc 说明参数、返回值与副作用；不写与代码重复的废话注释。
