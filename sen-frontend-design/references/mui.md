# MUI (Material UI) 参考指南

## 核心原则

### 何时使用 MUI

- React 项目需要 Material Design 风格
- 企业级应用需要成熟的组件库
- 需要强大的主题定制能力
- 需要良好的无障碍支持

### 何时不使用

- 项目要求极简或扁平化设计
- 需要快速加载的轻量级应用
- 设计风格不符合 Material Design

## 安装和配置

### 安装依赖

```bash
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
```

### 主题配置

```tsx
// src/theme/index.ts
import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    primary: {
      main: '#409EFF', // Element Plus 蓝色
      light: '#79bbff',
      dark: '#337ecc',
      contrastText: '#fff',
    },
    secondary: {
      main: '#67C23A', // 成功绿
      light: '#95d475',
      dark: '#4cae2c',
      contrastText: '#fff',
    },
    error: {
      main: '#F56C6C',
    },
    warning: {
      main: '#E6A23C',
    },
    info: {
      main: '#909399',
    },
    success: {
      main: '#67C23A',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    button: {
      textTransform: 'none', // 取消全大写
    },
  },
  shape: {
    borderRadius: 8, // 自定义圆角
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          transition: 'all 0.2s ease-in-out',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small',
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          backgroundColor: '#f5f7fa',
          fontWeight: 600,
        },
      },
    },
  },
})
```

## 常用组件模式

### Button 按钮

```tsx
import { Button, LoadingButton } from '@mui/material'
import { Save as SaveIcon, Delete as DeleteIcon } from '@mui/icons-material'

// 主要按钮
<Button variant="contained" color="primary">
  主要操作
</Button>

// 次要按钮
<Button variant="outlined" color="primary">
  次要操作
</Button>

// 文本按钮
<Button variant="text" color="primary">
  文本按钮
</Button>

// 图标按钮
<Button 
  variant="outlined" 
  startIcon={<SaveIcon />}
  onClick={handleSave}
>
  保存
</Button>

// 加载状态按钮
<LoadingButton
  loading={loading}
  variant="contained"
  onClick={handleSubmit}
>
  提交
</LoadingButton>

// 按钮尺寸
<Button size="small">小按钮</Button>
<Button size="medium">中按钮</Button>
<Button size="large">大按钮</Button>

// 按钮颜色
<Button color="primary">主要</Button>
<Button color="secondary">次要</Button>
<Button color="success">成功</Button>
<Button color="error">错误</Button>
<Button color="warning">警告</Button>
```

### Card 卡片

```tsx
import { Card, CardContent, CardActions, CardHeader, CardMedia } from '@mui/material'
import { MoreVert as MoreVertIcon } from '@mui/icons-material'

// 基础卡片
<Card sx={{ maxWidth: 345 }}>
  <CardHeader
    action={
      <IconButton aria-label="settings">
        <MoreVertIcon />
      </IconButton>
    }
    title="卡片标题"
    subheader="副标题"
  />
  <CardMedia
    component="img"
    height="140"
    image="/static/images/cards/contemplative-reptile.jpg"
    alt="图片描述"
  />
  <CardContent>
    <Typography variant="body2" color="text.secondary">
      这里是卡片的正文内容，可以是多行文本。
    </Typography>
  </CardContent>
  <CardActions>
    <Button size="small">取消</Button>
    <Button size="small" variant="contained">确认</Button>
  </CardActions>
</Card>

// 操作卡片
<Card>
  <CardContent>
    <Typography variant="h6" component="div">
      数据统计
    </Typography>
    <Typography variant="body2" color="text.secondary">
      总用户数: 1,234
    </Typography>
  </CardContent>
</Card>
```

### Dialog 弹窗

```tsx
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, DialogContentText } from '@mui/material'

interface DeleteDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  content: string
}

export function DeleteDialog({ open, onClose, onConfirm, title, content }: DeleteDialogProps) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{content}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={onConfirm} color="error" variant="contained">
          删除
        </Button>
      </DialogActions>
    </Dialog>
  )
}
```

### DataGrid 表格

```tsx
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid'
import { Chip, IconButton } from '@mui/material'
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'

interface User {
  id: number
  name: string
  email: string
  status: 'active' | 'inactive'
}

const columns: GridColDef<User>[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'name', headerName: '名称', width: 150 },
  { field: 'email', headerName: '邮箱', width: 200 },
  {
    field: 'status',
    headerName: '状态',
    width: 120,
    renderCell: (params: GridRenderCellParams<User>) => (
      <Chip
        label={params.value}
        color={params.value === 'active' ? 'success' : 'default'}
        size="small"
      />
    ),
  },
  {
    field: 'actions',
    headerName: '操作',
    width: 150,
    sortable: false,
    renderCell: (params: GridRenderCellParams<User>) => (
      <>
        <IconButton size="small" color="primary" onClick={() => handleEdit(params.row)}>
          <EditIcon />
        </IconButton>
        <IconButton size="small" color="error" onClick={() => handleDelete(params.row)}>
          <DeleteIcon />
        </IconButton>
      </>
    ),
  },
]

<DataGrid
  rows={users}
  columns={columns}
  pageSizeOptions={[10, 25, 50]}
  checkboxSelection
  disableRowSelectionOnClick
  sx={{ border: 0 }}
/>
```

### Form 表单

```tsx
import { TextField, FormControl, InputLabel, Select, MenuItem, FormHelperText } from '@mui/material'
import { useForm, Controller } from 'react-hook-form'

interface FormData {
  username: string
  email: string
  role: string
}

export function UserForm() {
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      username: '',
      email: '',
      role: '',
    },
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="username"
        control={control}
        rules={{ required: '请输入用户名' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="用户名"
            fullWidth
            margin="normal"
            error={!!errors.username}
            helperText={errors.username?.message}
          />
        )}
      />
      
      <Controller
        name="email"
        control={control}
        rules={{ 
          required: '请输入邮箱',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: '请输入有效的邮箱地址'
          }
        }}
        render={({ field }) => (
          <TextField
            {...field}
            label="邮箱"
            fullWidth
            margin="normal"
            error={!!errors.email}
            helperText={errors.email?.message}
          />
        )}
      />
      
      <FormControl fullWidth margin="normal" error={!!errors.role}>
        <InputLabel>角色</InputLabel>
        <Controller
          name="role"
          control={control}
          rules={{ required: '请选择角色' }}
          render={({ field }) => (
            <Select {...field} label="角色">
              <MenuItem value="admin">管理员</MenuItem>
              <MenuItem value="user">普通用户</MenuItem>
            </Select>
          )}
        />
        <FormHelperText>{errors.role?.message}</FormHelperText>
      </FormControl>
      
      <Button type="submit" variant="contained" sx={{ mt: 2 }}>
        提交
      </Button>
    </form>
  )
}
```

### Snackbar 消息

```tsx
import { Snackbar, Alert, AlertColor } from '@mui/material'

interface ToastProps {
  open: boolean
  message: string
  severity: AlertColor
  onClose: () => void
}

export function Toast({ open, message, severity, onClose }: ToastProps) {
  return (
    <Snackbar open={open} autoHideDuration={3000} onClose={onClose}>
      <Alert onClose={onClose} severity={severity} sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  )
}
```

### Menu 菜单

```tsx
import { Menu, MenuItem, IconButton, ListItemIcon, ListItemText } from '@mui/material'
import { Person as PersonIcon, Settings as SettingsIcon, Logout as LogoutIcon } from '@mui/icons-material'

export function UserMenu() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  
  const handleClose = () => {
    setAnchorEl(null)
  }
  
  return (
    <>
      <IconButton onClick={handleClick}>
        <PersonIcon />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        onClick={handleClose}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
          <ListItemText>个人资料</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => navigate('/settings')}>
          <ListItemIcon><SettingsIcon fontSize="small" /></ListItemIcon>
          <ListItemText>设置</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <ListItemIcon><LogoutIcon fontSize="small" color="error" /></ListItemIcon>
          <ListItemText>退出登录</ListItemText>
        </MenuItem>
      </Menu>
    </>
  )
}
```

## 最佳实践

### 1. 自定义主题组件

```tsx
// src/components/SenButton/index.tsx
import { Button, ButtonProps } from '@mui/material'
import { styled } from '@mui/material/styles'

const SenButton = styled(Button)<ButtonProps>(({ theme }) => ({
  textTransform: 'none',
  borderRadius: theme.shape.borderRadius * 1.5,
  padding: '10px 20px',
  transition: theme.transitions.create(['transform', 'box-shadow'], {
    duration: theme.transitions.duration.short,
  }),
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
  '&:active': {
    transform: 'scale(0.98)',
  },
}))

export default SenButton
```

### 2. 响应式布局

```tsx
import { useTheme, useMediaQuery, Box, Grid } from '@mui/material'

export function ResponsiveLayout() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'))
  
  return (
    <Box>
      {isMobile ? (
        <Stack spacing={2}>{/* 移动端布局 */}</Stack>
      ) : (
        <Grid container spacing={3}>
          {/* 桌面端布局 */}
        </Grid>
      )}
    </Box>
  )
}
```

### 3. 深色模式

```tsx
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { useMemo, useState } from 'react'

export function App({ children }) {
  const [mode, setMode] = useState<'light' | 'dark'>('light')
  
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // 浅色模式
              }
            : {
                // 深色模式
              }),
        },
      }),
    [mode]
  )
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  )
}
```

### 4. 动画效果

```tsx
import { Fade, Grow, Slide, Collapse } from '@mui/material'

<Fade in={visible} timeout={300}>
  <div>淡入效果</div>
</Fade>

<Grow in={visible} timeout={300}>
  <div>放大效果</div>
</Grow>

<Slide direction="up" in={visible} timeout={300}>
  <div>滑入效果</div>
</Slide>

<Collapse in={visible} timeout={300}>
  <div>折叠效果</div>
</Collapse>
```
