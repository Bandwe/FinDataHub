<template>
  <div class="company-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>公司管理</span>
          <div>
            <el-button type="warning" @click="handleExport" :disabled="selectedRows.length === 0">
              <el-icon><Download /></el-icon>
              导出选中
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增公司
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="tableData" 
        v-loading="loading" 
        border 
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="代码" width="120" />
        <el-table-column prop="name" label="个股名称" width="180" />
        <el-table-column prop="business" label="主营业务" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="代码" required>
          <el-input v-model="formData.code" placeholder="请输入代码" />
        </el-form-item>
        <el-form-item label="个股名称" required>
          <el-input v-model="formData.name" placeholder="请输入个股名称" />
        </el-form-item>
        <el-form-item label="主营业务">
          <el-input v-model="formData.business" type="textarea" rows="3" placeholder="请输入主营业务" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { getCompanies, createCompany, updateCompany, deleteCompany } from '../api/company'

const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive({
  id: null,
  code: '',
  name: '',
  business: '',
  remark: ''
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getCompanies({
      page: pagination.page,
      per_page: pagination.per_page
    })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  fetchData()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleAdd = () => {
  dialogTitle.value = '新增公司'
  Object.assign(formData, {
    id: null,
    code: '',
    name: '',
    business: '',
    remark: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑公司'
  Object.assign(formData, {
    id: row.id,
    code: row.code,
    name: row.name,
    business: row.business || '',
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (formData.id) {
      await updateCompany(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createCompany(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该公司吗？相关数据也将被删除', '提示', { type: 'warning' })
    await deleteCompany(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleExport = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要导出的公司')
    return
  }
  
  // 准备导出数据
  const exportData = selectedRows.value.map(row => ({
    '代码': row.code,
    '个股名称': row.name,
    '主营业务': row.business || '',
    '备注': row.remark || ''
  }))
  
  // 创建CSV内容
  const headers = ['代码', '个股名称', '主营业务', '备注']
  const csvContent = [
    headers.join(','),
    ...exportData.map(row => 
      headers.map(h => {
        const value = row[h] || ''
        // 处理包含逗号或换行符的情况
        if (value.includes(',') || value.includes('\n') || value.includes('"')) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )
  ].join('\n')
  
  // 添加BOM以支持中文
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  
  // 下载文件
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `公司数据_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
  
  ElMessage.success(`成功导出 ${selectedRows.value.length} 条记录`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.company-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .el-button {
  margin-left: 10px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
