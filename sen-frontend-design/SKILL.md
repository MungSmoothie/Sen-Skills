---
name: "sen-frontend-design"
description: "基于 Element Plus, shadcn/ui, MUI 和 Untitled UI 的个性化前端设计技能。专注于组件开发、视觉风格统一、动画交互效果和个人设计偏好的应用。使用场景包括：创建 Vue 3/React 组件、构建响应式 UI、实现微交互动画、维护设计一致性。"
---

# Sen 前端设计技能

## 快速开始

### 核心原则

1. **优先使用**: Element Plus (Vue 3) > shadcn/ui (React) > MUI > Untitled UI
2. **视觉统一**: 保持设计语言一致性
3. **动画优先**: 适当的微交互提升用户体验

### 组件选择流程

```
用户需求 → 确定框架 → 匹配组件 → 应用视觉风格 → 添加动画
```

## 框架使用指南

### Element Plus (首选 - Vue 3)

- 用于 Vue 3 项目
- 企业级中后台应用
- 参考 [element-plus.md](references/element-plus.md)

### shadcn/ui (React 项目)

- 用于 React 项目
- 追求极致定制化
- 参考 [shadcn-ui.md](references/shadcn-ui.md)

### MUI (Material UI)

- 需要 Material Design 风格时
- React 生态系统
- 参考 [mui.md](references/mui.md)

### Untitled UI

- 现代、简洁的视觉风格
- 适合 SaaS 产品
- 参考 [untitled-ui.md](references/untitled-ui.md)

## 视觉风格规范

### 设计令牌

详情见 [visual-guidelines.md](references/visual-guidelines.md)

#### 颜色系统
- 主色调: #409EFF (Element Plus Blue)
- 成功: #67C23A
- 警告: #E6A23C
- 危险: #F56C6C
- 信息: #909399

#### 圆角规范
- 小: 4px (按钮、标签)
- 中: 8px (卡片、弹窗)
- 大: 12px-16px (大型卡片)

#### 间距系统
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 动画与交互

### 基础动画

```css
/* 淡入淡出 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 滑入滑出 */
.slide-up-enter-active {
  transition: all 0.3s ease-out;
}
.slide-up-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* 缩放 */
.scale-enter-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.scale-leave-active {
  transition: all 0.2s ease;
}
.scale-enter-from, .scale-leave-to {
  transform: scale(0.9);
  opacity: 0;
}
```

### 交互反馈

- **悬停效果**: 轻微的阴影加深和位移
- **点击效果**: 缩放反馈 (scale-0.95)
- **加载状态**: 骨架屏优先于 loading spinner
- **成功反馈**: 绿色 toast + 短暂震动
- **错误反馈**: 红色 toast + 表单高亮

## 组件开发规范

### 目录结构

```
src/
├── components/
│   ├── common/          # 通用组件
│   │   ├── Button/
│   │   ├── Card/
│   │   └── Modal/
│   ├── business/        # 业务组件
│   └── index.ts         # 统一导出
```

### 组件模板

#### Vue 3 (Element Plus)

```vue
<template>
  <el-card class="sen-card" :class="{ 'sen-card--hoverable': hoverable }">
    <template #header>
      <div class="sen-card__header">
        <span>{{ title }}</span>
        <el-button v-if="showAction" type="primary" link @click="handleAction">
          {{ actionText }}
        </el-button>
      </div>
    </template>
    <slot />
  </el-card>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Props {
  title: string
  hoverable?: boolean
  showAction?: boolean
  actionText?: string
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  showAction: false,
  actionText: 'More'
})

const emit = defineEmits<{
  action: []
}>()

const handleAction = () => {
  emit('action')
}
</script>

<style scoped lang="scss">
.sen-card {
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &--hoverable:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}
</style>
```

#### React (shadcn/ui)

```tsx
import { cn } from '@/lib/utils'

interface SenCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  hoverable?: boolean
}

export function SenCard({ 
  className, 
  title, 
  hoverable = false,
  children,
  ...props 
}: SenCardProps) {
  return (
    <div 
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        hoverable && 'transition-all duration-300 hover:shadow-md hover:-translate-y-1',
        className
      )}
      {...props}
    >
      {title && (
        <div className="flex flex-col space-y-1.5 p-6">
          <h3 className="text-lg font-semibold leading-none tracking-tight">{title}</h3>
        </div>
      )}
      <div className="p-6 pt-0">
        {children}
      </div>
    </div>
  )
}
```

## 响应式设计

### 断点系统

```scss
$breakpoints: (
  xs: 0,
  sm: 640px,
  md: 768px,
  lg: 1024px,
  xl: 1280px,
  2xl: 1536px
)
```

### 移动优先策略

- 默认编写移动端样式
- 使用 `@media (min-width: ...)` 添加响应式断点
- 优先保证移动端体验

## 无障碍设计

### 原则

- **键盘导航**: 所有交互可通过键盘完成
- **焦点可见**: 焦点状态清晰可见
- **语义化**: 正确的 HTML 标签和 ARIA 属性
- **对比度**: 文本对比度 ≥ 4.5:1

### 示例

```vue
<!-- 按钮无障碍 -->
<el-button 
  aria-label="提交表单" 
  aria-describedby="form-description"
>
  提交
</el-button>

<!-- 表单标签 -->
<el-form-item label="邮箱" label-for="email-input">
  <el-input id="email-input" aria-describedby="email-hint" />
  <span id="email-hint" class="el-form-item__error">
    请输入有效的邮箱地址
  </span>
</el-form-item>
```

## 性能优化

### 组件懒加载

```typescript
// Vue 3
import { defineAsyncComponent } from 'vue'

export const LazyModal = defineAsyncComponent(() => 
  import('@/components/common/Modal/index.vue')
)

// React
const HeavyChart = lazy(() => import('@/components/common/Chart'))
```

### 样式优化

- 使用 CSS 变量实现主题切换
- 避免深层嵌套选择器
- 使用 CSS Containment 优化渲染

## 质量检查清单

创建或修改组件后，检查以下项目：

- [ ] 组件有完整的 TypeScript 类型定义
- [ ] 使用设计令牌（颜色、间距、圆角）
- [ ] 包含必要的动画过渡效果
- [ ] 支持键盘导航
- [ ] 通过 Lighthouse 性能检查
- [ ] 响应式布局正常
- [ ] 深色模式兼容（如适用）

## 常用资源

### 颜色工具
- [Tailwind CSS Colors](https://tailwindcss.com/docs/customizing-colors)
- [CSS Gradient Generator](https://cssgradient.io/)

### 动画库
- [Animate.css](https://animate.style/)
- [Motion One](https://motion.dev/)
- [Vue Transitions](https://vuejs.org/guide/built-ins/transition.html)

### 图标库
- [Element Plus Icons](https://element-plus.org/zh-CN/component/icon.html)
- [Lucide Icons](https://lucide.dev/)
- [Heroicons](https://heroicons.com/)
