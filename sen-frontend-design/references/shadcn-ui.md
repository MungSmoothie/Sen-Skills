# shadcn/ui 参考指南

## 核心原则

### 何时使用 shadcn/ui

- React 项目（Next.js, Vite, Remix）
- 需要高度定制化的 UI
- 追求 Tailwind CSS 的灵活性
- 现代化的 SaaS 产品

### 何时不使用

- 不使用 React 的项目
- 需要完整封装组件库的场景
- 项目时间紧张，需要快速开发

## 安装和配置

### 初始化

```bash
npx shadcn-ui@latest init
```

### 添加组件

```bash
# 添加单个组件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
npx shadcn-ui@latest add table
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add toast

# 添加所有常用组件
npx shadcn-ui@latest add button card dialog form table input select toast dropdown-menu avatar badge alert
```

## 常用组件模式

### Button 变体

```tsx
import { Button } from '@/components/ui/button'

// 主要按钮 - 用于主要操作
<Button variant="default">主要按钮</Button>

// 次要按钮 - 用于次要操作
<Button variant="secondary">次要按钮</Button>

// 幽灵按钮 - 用于背景色区域
<Button variant="ghost">幽灵按钮</Button>

// 链接按钮
<Button variant="link">链接按钮</Button>

// 轮廓按钮
<Button variant="outline">轮廓按钮</Button>

// 破坏性操作
<Button variant="destructive">删除</Button>

// 尺寸
<Button size="sm">小按钮</Button>
<Button size="default">默认尺寸</Button>
<Button size="lg">大按钮</Button>
<Button size="icon"><PlusIcon /></Button>
```

### Card 组件

```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

// 基础卡片
<Card className="w-[350px]">
  <CardHeader>
    <CardTitle>卡片标题</CardTitle>
    <CardDescription>卡片描述信息，用于补充说明</CardDescription>
  </CardHeader>
  <CardContent>
    <p>卡片内容区域</p>
  </CardContent>
  <CardFooter className="flex justify-between">
    <Button variant="outline">取消</Button>
    <Button>确认</Button>
  </CardFooter>
</Card>

// 带表单的卡片
<Card>
  <CardHeader>
    <CardTitle>登录</CardTitle>
    <CardDescription>请输入您的账号信息</CardDescription>
  </CardHeader>
  <CardContent>
    <form onSubmit={handleSubmit}>
      {/* 表单字段 */}
    </form>
  </CardContent>
</Card>
```

### Dialog 弹窗

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">打开弹窗</Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[425px]">
    <DialogHeader>
      <DialogTitle>编辑资料</DialogTitle>
      <DialogDescription>
        对您的个人资料进行修改。完成后点击保存。
      </DialogDescription>
    </DialogHeader>
    <div className="grid gap-4 py-4">
      {/* 表单内容 */}
    </div>
    <DialogFooter>
      <Button type="submit">保存更改</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Form 表单

```tsx
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'

const formSchema = z.object({
  username: z.string().min(2, {
    message: '用户名至少2个字符',
  }),
  email: z.string().email({
    message: '请输入有效的邮箱地址',
  }),
})

export function UserForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      email: '',
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>用户名</FormLabel>
              <FormControl>
                <Input placeholder="请输入用户名" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>邮箱</FormLabel>
              <FormControl>
                <Input placeholder="请输入邮箱" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">提交</Button>
      </form>
    </Form>
  )
}
```

### Table 表格

```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const columns = [
  {
    accessorKey: 'name',
    header: '名称',
    cell: ({ row }) => <div className="font-medium">{row.getValue('name')}</div>,
  },
  {
    accessorKey: 'status',
    header: '状态',
    cell: ({ row }) => {
      const status = row.getValue('status')
      return (
        <Badge variant={status === 'active' ? 'default' : 'secondary'}>
          {status}
        </Badge>
      )
    },
  },
]

<Table>
  <TableHeader>
    <TableRow>
      <TableHead className="w-[100px]">ID</TableHead>
      <TableHead>名称</TableHead>
      <TableHead>状态</TableHead>
      <TableHead className="text-right">操作</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {table.getRowModel().rows?.map((row) => (
      <TableRow key={row.id}>
        <TableCell>{row.original.id}</TableCell>
        <TableCell>{row.getValue('name')}</TableCell>
        <TableCell>
          <Badge variant={row.original.status === 'active' ? 'default' : 'secondary'}>
            {row.getValue('status')}
          </Badge>
        </TableCell>
        <TableCell className="text-right">
          <Button variant="ghost" size="sm">编辑</Button>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Toast 通知

```tsx
import { useToast } from '@/components/ui/use-toast'

const { toast } = useToast()

// 成功提示
toast({
  title: '操作成功',
  description: '数据已保存',
  variant: 'default',
  duration: 3000,
})

// 错误提示
toast({
  title: '操作失败',
  description: '请稍后重试',
  variant: 'destructive',
  duration: 5000,
})
```

### Dropdown Menu

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">菜单</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent className="w-56">
    <DropdownMenuLabel>我的账户</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>个人资料</DropdownMenuItem>
    <DropdownMenuItem>设置</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-red-600">
      退出登录
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## 工具函数

### cn (classNames 工具)

```tsx
import { cn } from '@/lib/utils'

// 基本用法
<div className={cn('base-class', condition && 'conditional-class')} />

// 条件类名
<div className={cn(
  'flex items-center p-4',
  isActive && 'bg-blue-500',
  isDisabled && 'opacity-50'
)} />

// 响应式
<div className={cn(
  'text-sm',
  'md:text-base',
  'lg:text-lg'
)} />
```

## 自定义主题

### 修改全局 CSS 变量

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}
```

## 最佳实践

### 1. 组件封装

```tsx
// components/ui/button.tsx 基础上封装
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface SenButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'ghost' | 'link' | 'outline' | 'destructive'
  size?: 'sm' | 'default' | 'lg' | 'icon'
  loading?: boolean
}

export function SenButton({ 
  className, 
  variant = 'default', 
  size = 'default',
  loading = false,
  children,
  disabled,
  ...props 
}: SenButtonProps) {
  return (
    <Button
      variant={variant}
      size={size}
      className={cn(
        'transition-all duration-200',
        loading && 'cursor-wait',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <LoadingSpinner className="h-4 w-4 animate-spin" />
          加载中...
        </span>
      ) : (
        children
      )}
    </Button>
  )
}
```

### 2. 动画过渡

```tsx
import { motion } from 'framer-motion'

// 使用 Framer Motion 配合 shadcn/ui
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -10 }}
  transition={{ duration: 0.2 }}
>
  <Card>{/* 内容 */}</Card>
</motion.div>
```

### 3. 响应式设计

```tsx
// 使用 Tailwind 响应式类名
<div className="
  grid grid-cols-1 gap-4
  md:grid-cols-2 gap-6
  lg:grid-cols-3 gap-8
  xl:grid-cols-4 gap-8
">
  {/* 内容 */}
</div>
```

### 4. 深色模式

```tsx
// 使用 next-themes 实现深色模式
import { useTheme } from 'next-themes'

const { theme, setTheme } = useTheme()

<Button
  variant="ghost"
  onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
>
  {theme === 'dark' ? '🌞' : '🌙'}
</Button>
```
