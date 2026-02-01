# 视觉风格统一指南

本文档定义了前端设计中保持视觉一致性的核心规范和最佳实践。

## 设计令牌系统

### 颜色系统

#### 主色调

```css
:root {
  /* Element Plus Blue - 主色调 */
  --color-primary-50: #ecf5ff;
  --color-primary-100: #d9ecff;
  --color-primary-200: #b3d8ff;
  --color-primary-300: #79bbff;
  --color-primary-400: #409EFF;
  --color-primary-500: #337ecc;
  --color-primary-600: #2667cc;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1a3a8a;
  --color-primary-900: #182b5c;
}
```

#### 语义色

```css
:root {
  /* 成功 */
  --color-success-50: #f0f9eb;
  --color-success-100: #e1f3d8;
  --color-success-200: #c3e6b5;
  --color-success-300: #a6d88f;
  --color-success-400: #67C23A;
  --color-success-500: #529e2c;
  
  /* 警告 */
  --color-warning-50: #fdf6ec;
  --color-warning-100: #faecd8;
  --color-warning-200: #f5dab1;
  --color-warning-300: #f0c787;
  --color-warning-400: #E6A23C;
  --color-warning-500: #c48a32;
  
  /* 错误 */
  --color-error-50: #fef0f0;
  --color-error-100: #fde2e2;
  --color-error-200: #f9c8c8;
  --color-error-300: #f4a8a8;
  --color-error-400: #F56C6C;
  --color-error-500: #c65454;
  
  /* 信息 */
  --color-info-50: #f4f4f5;
  --color-info-100: #e9e9eb;
  --color-info-200: #d3d3d6;
  --color-info-300: #b8b8bb;
  --color-info-400: #909399;
  --color-info-500: #737478;
}
```

#### 中性色

```css
:root {
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
}
```

### 间距系统

#### 基础间距

```css
:root {
  --space-0: 0;
  --space-px: 1px;
  --space-0-5: 2px;
  --space-1: 4px;
  --space-1-5: 6px;
  --space-2: 8px;
  --space-2-5: 10px;
  --space-3: 12px;
  --space-3-5: 14px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 28px;
  --space-8: 32px;
  --space-9: 36px;
  --space-10: 40px;
  --space-11: 44px;
  --space-12: 48px;
  --space-14: 56px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
}
```

#### 组件间距

```css
:root {
  /* 按钮内部间距 */
  --btn-padding-x: var(--space-4);
  --btn-padding-y: var(--space-2);
  
  /* 表单字段间距 */
  --form-field-margin-bottom: var(--space-4);
  --form-label-margin-bottom: var(--space-1);
  --form-input-height: 40px;
  
  /* 卡片间距 */
  --card-padding: var(--space-5);
  --card-header-padding-bottom: var(--space-4);
  --card-body-padding-top: var(--space-4);
  
  /* 表格间距 */
  --table-cell-padding-x: var(--space-4);
  --table-cell-padding-y: var(--space-3);
  
  /* 弹窗间距 */
  --dialog-padding: var(--space-6);
  --dialog-header-margin-bottom: var(--space-4);
  --dialog-body-margin-bottom: var(--space-5);
  --dialog-footer-padding-top: var(--space-5);
}
```

### 圆角系统

```css
:root {
  /* 基础圆角 */
  --radius-none: 0;
  --radius-sm: 2px;
  --radius-base: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-3xl: 24px;
  --radius-full: 9999px;
  
  /* 组件圆角 */
  --radius-btn: var(--radius-lg);
  --radius-input: var(--radius-md);
  --radius-card: var(--radius-xl);
  --radius-badge: var(--radius-full);
  --radius-dropdown: var(--radius-lg);
  --radius-tooltip: var(--radius-md);
  --radius-modal: var(--radius-2xl);
}
```

### 阴影系统

```css
:root {
  /* 基础阴影 */
  --shadow-none: none;
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-base: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-md: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  /* 悬停状态 */
  --shadow-hover: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-focus: 0 0 0 3px rgba(64, 158, 255, 0.3);
}
```

### 字体系统

```css
:root {
  /* 字体族 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
  
  /* 字号 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;
  
  /* 字重 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* 行高 */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
  
  /* 字间距 */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

## 视觉层级

### 标题层级

```css
h1, .heading-1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tighter);
  color: var(--color-gray-900);
}

h2, .heading-2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-gray-900);
}

h3, .heading-3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
  color: var(--color-gray-900);
}

h4, .heading-4 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
  color: var(--color-gray-900);
}

h5, .heading-5 {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  color: var(--color-gray-900);
}

h6, .heading-6 {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  line-height: var(--leading-normal);
  color: var(--color-gray-700);
}
```

### 正文层级

```css
.text-lead {
  font-size: var(--text-lg);
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
  color: var(--color-gray-600);
}

.text-body {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
  color: var(--color-gray-600);
}

.text-small {
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
  color: var(--color-gray-500);
}

.text-xs {
  font-size: var(--text-xs);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
  color: var(--color-gray-500);
}
```

## 组件状态样式

### 默认状态

```css
.component {
  background-color: white;
  border: 1px solid var(--color-gray-200);
  color: var(--color-gray-900);
  box-shadow: var(--shadow-sm);
}
```

### 悬停状态

```css
.component--hoverable:hover {
  border-color: var(--color-gray-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

### 激活/点击状态

```css
.component:active {
  transform: scale(0.98);
  box-shadow: var(--shadow-sm);
}
```

### 焦点状态

```css
.component:focus {
  outline: none;
  border-color: var(--color-primary-400);
  box-shadow: var(--shadow-focus);
}
```

### 禁用状态

```css
.component:disabled,
.component--disabled {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}
```

### 加载状态

```css
.component--loading {
  position: relative;
  pointer-events: none;
}

.component--loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.7);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23333'%3E%3Ccircle cx='12' cy='12' r='10' stroke-width='4' /%3E%3Cpath d='M12 2a10 10 0 0 1 10 10' stroke-width='4' stroke-linecap='round' class='spinner' /%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 24px;
}
```

## 动画效果

### 过渡时长

```css
:root {
  --transition-duration-fast: 150ms;
  --transition-duration-base: 200ms;
  --transition-duration-slow: 300ms;
  --transition-duration-slower: 500ms;
  
  --transition-timing-linear: linear;
  --transition-timing-ease: ease;
  --transition-timing-ease-in: ease-in;
  --transition-timing-ease-out: ease-out;
  --transition-timing-ease-in-out: ease-in-out;
  --transition-timing-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 常用过渡

```css
.transition-colors {
  transition: background-color, border-color, color, fill, stroke var(--transition-duration-base) var(--transition-timing-ease-in-out);
}

.transition-transform {
  transition: transform var(--transition-duration-base) var(--transition-timing-ease-in-out);
}

.transition-shadow {
  transition: box-shadow var(--transition-duration-base) var(--transition-timing-ease-in-out);
}

.transition-all {
  transition: all var(--transition-duration-base) var(--transition-timing-ease-in-out);
}
```

### 关键帧动画

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 应用类 */
.animate-fade-in {
  animation: fadeIn var(--transition-duration-slow) var(--transition-timing-ease-out) forwards;
}

.animate-slide-up {
  animation: slideUp var(--transition-duration-slow) var(--transition-timing-ease-out) forwards;
}

.animate-scale-in {
  animation: scaleIn var(--transition-duration-base) var(--transition-timing-spring) forwards;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

## 响应式设计

### 断点

```css
:root {
  --breakpoint-xs: 0;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}
```

### 容器宽度

```css
.container {
  /* 移动端 */
  width: 100%;
  max-width: 100%;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

@media (min-width: var(--breakpoint-sm)) {
  .container {
    max-width: var(--breakpoint-sm);
    padding-left: var(--space-5);
    padding-right: var(--space-5);
  }
}

@media (min-width: var(--breakpoint-md)) {
  .container {
    max-width: var(--breakpoint-md);
  }
}

@media (min-width: var(--breakpoint-lg)) {
  .container {
    max-width: var(--breakpoint-lg);
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}

@media (min-width: var(--breakpoint-xl)) {
  .container {
    max-width: var(--breakpoint-xl);
  }
}

@media (min-width: var(--breakpoint-2xl)) {
  .container {
    max-width: 1400px;
  }
}
```

## 深色模式

```css
:root {
  /* 浅色模式 */
  --bg-primary: white;
  --bg-secondary: var(--color-gray-50);
  --bg-tertiary: var(--color-gray-100);
  
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --text-tertiary: var(--color-gray-500);
  
  --border-primary: var(--color-gray-200);
  --border-secondary: var(--color-gray-100);
}

:root.dark {
  /* 深色模式 */
  --bg-primary: var(--color-gray-900);
  --bg-secondary: var(--color-gray-800);
  --bg-tertiary: var(--color-gray-700);
  
  --text-primary: white;
  --text-secondary: var(--color-gray-300);
  --text-tertiary: var(--color-gray-400);
  
  --border-primary: var(--color-gray-700);
  --border-secondary: var(--color-gray-800);
}

.component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-primary);
}
```

## 最佳实践

### 1. 使用 CSS 变量

```css
/* 推荐 */
.button {
  background-color: var(--color-primary-500);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
}

/* 不推荐 */
.button {
  background-color: #409EFF;
  padding: 8px 16px;
  border-radius: 8px;
}
```

### 2. 保持一致性

```css
/* 所有按钮使用相同的间距和圆角 */
.btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
}

/* 所有标题使用相同的字重 */
h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-semibold);
  color: var(--color-gray-900);
}
```

### 3. 响应式适配

```css
/* 移动优先 */
.card {
  padding: var(--space-4);
}

@media (min-width: var(--breakpoint-md)) {
  .card {
    padding: var(--space-6);
  }
}
```

### 4. 可访问性

```css
/* 确保对比度 */
.text {
  color: var(--text-primary);
  background-color: var(--bg-primary);
}

/* 焦点状态清晰可见 */
.button:focus {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
```
