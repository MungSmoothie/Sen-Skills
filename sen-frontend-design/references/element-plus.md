# Element Plus 参考指南

## 核心原则

### 何时使用 Element Plus

- Vue 3 项目
- 企业级中后台管理系统
- 需要丰富组件库的场景
- 对组件功能完整性要求高

### 何时不使用

- 需要极致轻量级的项目
- 追求高度自定义视觉效果
- 非中后台的管理系统

## 常用组件模式

### 表格 (Table)

```vue
<template>
  <el-table 
    :data="tableData" 
    stripe 
    border
    :header-cell-style="{ background: '#f5f7fa' }"
    @selection-change="handleSelectionChange"
  >
    <el-table-column type="selection" width="50" />
    <el-table-column prop="name" label="名称" min-width="120" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="row.status === 'active' ? 'success' : 'info'">
          {{ row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="150" fixed="right">
      <template #default="{ row }">
        <el-button type="primary" link @click="handleEdit(row)">
          编辑
        </el-button>
        <el-button type="danger" link @click="handleDelete(row)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface TableItem {
  id: number
  name: string
  status: string
}

const tableData = ref<TableItem[]>([])
const selectedRows = ref<TableItem[]>([])

const handleSelectionChange = (rows: TableItem[]) => {
  selectedRows.value = rows
}

const handleEdit = (row: TableItem) => {
  // 编辑逻辑
}

const handleDelete = (row: TableItem) => {
  // 删除逻辑
}
</script>
```

### 表单 (Form)

```vue
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    label-width="120px"
    class="sen-form"
  >
    <el-form-item label="用户名" prop="username">
      <el-input 
        v-model="formData.username" 
        placeholder="请输入用户名"
        clearable
      />
    </el-form-item>
    
    <el-form-item label="邮箱" prop="email">
      <el-input 
        v-model="formData.email" 
        placeholder="请输入邮箱"
        clearable
      />
    </el-form-item>
    
    <el-form-item label="角色" prop="role">
      <el-select 
        v-model="formData.role" 
        placeholder="请选择角色"
        clearable
      >
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="状态" prop="status">
      <el-switch 
        v-model="formData.status"
        active-text="启用"
        inactive-text="禁用"
      />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitForm(formRef)">
        提交
      </el-button>
      <el-button @click="resetForm(formRef)">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface FormData {
  username: string
  email: string
  role: string
  status: boolean
}

const formRef = ref<FormInstance>()
const formData = reactive<FormData>({
  username: '',
  email: '',
  role: '',
  status: true
})

const formRules: FormRules<FormData> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const submitForm = async (form: FormInstance | undefined) => {
  if (!form) return
  await form.validate((valid) => {
    if (valid) {
      console.log('表单数据:', formData)
    }
  })
}

const resetForm = (form: FormInstance | undefined) => {
  if (!form) return
  form.resetFields()
}
</script>

<style scoped lang="scss">
.sen-form {
  max-width: 600px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
}
</style>
```

### 弹窗 (Dialog)

```vue
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑' : '新增'"
    width="600px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="dialogFormRef"
      :model="dialogFormData"
      :rules="dialogFormRules"
      label-width="100px"
    >
      <!-- 表单项 -->
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
```

### 消息提示

```typescript
// 成功提示
ElMessage.success('操作成功')

// 错误提示
ElMessage.error('操作失败，请重试')

// 警告提示
ElMessage.warning('请确认信息是否正确')

// 信息提示
ElMessage.info('这是一条信息提示')
```

### 通知

```typescript
// 成功通知
ElNotification.success({
  title: '成功',
  message: '数据已保存',
  duration: 3000
})

// 错误通知
ElNotification.error({
  title: '错误',
  message: '保存失败，请稍后重试',
  duration: 0 // 不自动关闭
})
```

## 主题定制

### 全局主题配置

```typescript
// main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

app.use(ElementPlus, {
  size: 'default', // 默认组件尺寸
  zIndex: 3000, // 弹框初始 z-index
  message: {
    max: 3, // 最大消息数量
  }
})

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

### SCSS 变量覆盖

```scss
// styles/element-variables.scss
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #409EFF,
    ),
    'success': (
      'base': #67C23A,
    ),
    'warning': (
      'base': #E6A23C,
    ),
    'danger': (
      'base': #F56C6C,
    ),
    'info': (
      'base': #909399,
    ),
  ),
  $border-radius: (
    'base': 8px,
    'small': 4px,
    'round': 20px,
  ),
)
```

## 最佳实践

### 1. 组件尺寸统一

```vue
<template>
  <el-config-provider :size="globalSize">
    <App />
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const globalSize = ref('default')
</script>
```

### 2. 国际化

```typescript
import { createI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

const i18n = createI18n({
  locale: localStorage.getItem('locale') || 'zh-CN',
  messages: {
    'zh-CN': zhCn,
    'en': en
  }
})
```

### 3. 权限控制

```vue
<template>
  <el-button 
    v-permission="'system:user:add'"
    type="primary"
    @click="handleAdd"
  >
    新增
  </el-button>
</template>
```

### 4. 表格排序和筛选

```vue
<template>
  <el-table
    :data="tableData"
    @sort-change="handleSortChange"
  >
    <el-table-column
      prop="createTime"
      label="创建时间"
      sortable="custom"
      width="180"
    />
  </el-table>
</template>

<script setup lang="ts">
const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  // 根据 prop 和 order 进行排序
  console.log(prop, order)
}
</script>
```
