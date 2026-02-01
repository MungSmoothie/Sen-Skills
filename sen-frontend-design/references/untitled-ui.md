# Untitled UI 参考指南

## 核心原则

### 何时使用 Untitled UI

- 现代 SaaS 产品和 Web 应用
- 追求简洁、扁平的设计风格
- 需要高度可定制化
- 适合初创公司和数字产品

### 设计特点

- 简洁的线条和几何形状
- 适度的圆角（通常 6-12px）
- 中性色调为主
- 注重留白和呼吸感
- 微妙的阴影和层次

## 设计令牌

### 颜色系统

```css
:root {
  /* 主色调 - 蓝色 */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;
  
  /* 中性色 */
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
  
  /* 语义色 */
  --color-success-500: #22c55e;
  --color-warning-500: #f59e0b;
  --color-error-500: #ef4444;
  --color-info-500: #3b82f6;
}
```

### 间距系统

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
}
```

### 圆角系统

```css
:root {
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;
}
```

### 阴影系统

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
```

## 组件模式

### Button 按钮

```css
/* Untitled UI Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.25rem;
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  outline: none;
}

.btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Primary */
.btn--primary {
  background-color: var(--color-gray-900);
  color: white;
}

.btn--primary:hover {
  background-color: var(--color-gray-800);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn--primary:active {
  transform: translateY(0);
}

/* Secondary */
.btn--secondary {
  background-color: white;
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-200);
}

.btn--secondary:hover {
  background-color: var(--color-gray-50);
  border-color: var(--color-gray-300);
}

/* Ghost */
.btn--ghost {
  background-color: transparent;
  color: var(--color-gray-600);
}

.btn--ghost:hover {
  background-color: var(--color-gray-100);
  color: var(--color-gray-900);
}

/* Sizes */
.btn--sm {
  padding: var(--space-1) var(--space-3);
  font-size: 0.813rem;
}

.btn--lg {
  padding: var(--space-3) var(--space-6);
  font-size: 0.938rem;
}
```

### Card 卡片

```css
.card {
  background-color: white;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.card--hoverable:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-gray-300);
  transform: translateY(-2px);
}

.card__header {
  padding: var(--space-5) var(--space-5) 0;
}

.card__title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0 0 var(--space-1) 0;
}

.card__description {
  font-size: 0.875rem;
  color: var(--color-gray-500);
  margin: 0;
}

.card__body {
  padding: var(--space-4) var(--space-5);
}

.card__footer {
  padding: 0 var(--space-5) var(--space-5);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
}
```

### Input 输入框

```css
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: var(--color-gray-900);
  background-color: white;
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  outline: none;
}

.input::placeholder {
  color: var(--color-gray-400);
}

.input:hover {
  border-color: var(--color-gray-400);
}

.input:focus {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.input--error {
  border-color: var(--color-error-500);
}

.input--error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input__label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700);
  margin-bottom: var(--space-1);
}

.input__helper {
  font-size: 0.813rem;
  color: var(--color-gray-500);
  margin-top: var(--space-1);
}

.input__error {
  color: var(--color-error-500);
}
```

### Badge 徽章

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px var(--space-2);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  border-radius: var(--radius-full);
}

.badge--default {
  background-color: var(--color-gray-100);
  color: var(--color-gray-600);
}

.badge--primary {
  background-color: var(--color-primary-100);
  color: var(--color-primary-700);
}

.badge--success {
  background-color: #dcfce7;
  color: #166534;
}

.badge--warning {
  background-color: #fef3c7;
  color: #92400e;
}

.badge--error {
  background-color: #fee2e2;
  color: #991b1b;
}
```

### Avatar 头像

```css
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background-color: var(--color-gray-100);
  color: var(--color-gray-600);
  font-weight: 500;
  overflow: hidden;
}

.avatar--sm {
  width: 32px;
  height: 32px;
  font-size: 0.75rem;
}

.avatar--md {
  width: 40px;
  height: 40px;
  font-size: 0.875rem;
}

.avatar--lg {
  width: 48px;
  height: 48px;
  font-size: 1rem;
}

.avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### Dropdown 下拉菜单

```css
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown__menu {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 50;
  min-width: 200px;
  padding: var(--space-1);
  margin-top: var(--space-1);
  background-color: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 0.2s ease;
}

.dropdown__menu--open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown__item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: 0.875rem;
  color: var(--color-gray-700);
  background: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.dropdown__item:hover {
  background-color: var(--color-gray-100);
}

.dropdown__divider {
  height: 1px;
  margin: var(--space-1) 0;
  background-color: var(--color-gray-200);
}
```

## 动画效果

### 基础动画

```css
/* 淡入淡出 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* 滑入 */
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

/* 缩放 */
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

/* 应用动画 */
.animate-fade-in {
  animation: fadeIn 0.3s ease forwards;
}

.animate-slide-up {
  animation: slideUp 0.3s ease forwards;
}

.animate-scale-in {
  animation: scaleIn 0.2s ease forwards;
}
```

### 过渡类

```css
.transition-base {
  transition: all 0.2s ease;
}

.transition-fast {
  transition: all 0.15s ease;
}

.transition-slow {
  transition: all 0.3s ease;
}

/* 悬停效果 */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.hover-scale:hover {
  transform: scale(1.02);
}

/* 点击效果 */
.active-scale:active {
  transform: scale(0.98);
}
```

## 响应式设计

### 断点

```css
/* 移动优先断点 */
@media (min-width: 640px) {
  /* sm */
}

@media (min-width: 768px) {
  /* md */
}

@media (min-width: 1024px) {
  /* lg */
}

@media (min-width: 1280px) {
  /* xl */
}

@media (min-width: 1536px) {
  /* 2xl */
}
```

### 容器

```css
.container {
  width: 100%;
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

@media (min-width: 640px) {
  .container {
    padding-left: var(--space-5);
    padding-right: var(--space-5);
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}
```

## 最佳实践

### 1. 保持一致性

```css
/* 统一使用 CSS 变量 */
.element {
  color: var(--color-gray-900);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}
```

### 2. 适度的留白

```css
.section {
  padding: var(--space-16) 0;
}

@media (min-width: 768px) {
  .section {
    padding: var(--space-20) 0;
  }
}

/* 元素间距 */
.element + .element {
  margin-top: var(--space-4);
}
```

### 3. 清晰的视觉层级

```css
.heading-xl {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
  color: var(--color-gray-900);
}

.heading-lg {
  font-size: 1.875rem;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.025em;
  color: var(--color-gray-900);
}

.heading-md {
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-gray-900);
}

.body-text {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-gray-600);
}

.caption {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-gray-500);
}
```

### 4. 交互反馈

```css
/* 加载状态 */
.loading {
  position: relative;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.7);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

/* 禁用状态 */
.disabled {
  opacity: 0.5;
  pointer-events: none;
}
```

## 常用资源

### 图标库
- [Heroicons](https://heroicons.com/) - 免费的 SVG 图标库
- [Phosphor Icons](https://phosphoricons.com/) - 现代化图标库
- [Lucide](https://lucide.dev/) - 轻量级图标库

### 工具
- [CSS Variables Generator](https://components.ai/tailwind-css-variable-generator) - 生成 CSS 变量
- [Box Shadow Generator](https://www.cssmatic.com/box-shadow) - 阴影效果生成
- [Border Radius Generator](https://www.cssmatic.com/border-radius-generator) - 圆角生成
