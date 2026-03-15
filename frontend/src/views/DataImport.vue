<template>
  <div class="data-import-container">
    <el-card class="import-card">
      <template #header>
        <div class="card-header">
          <span>数据导入中心</span>
          <el-button type="primary" @click="handleDownloadTemplate">
            <el-icon><Download /></el-icon>
            下载导入模板
          </el-button>
        </div>
      </template>

      <el-steps :active="activeStep" finish-status="success" class="import-steps">
        <el-step title="上传文件" description="选择Excel文件" />
        <el-step title="数据预览" description="检查数据内容" />
        <el-step title="执行导入" description="导入到数据库" />
      </el-steps>

      <!-- 步骤1: 上传文件 -->
      <div v-if="activeStep === 0" class="step-content">
        <el-alert
          title="导入说明"
          type="info"
          description="支持单Sheet或多Sheet Excel文件。多Sheet文件会自动识别各模块数据，单Sheet文件需要选择对应模块类型。"
          show-icon
          :closable="false"
          class="import-info"
        />

        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          action=""
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".xlsx,.xls"
          :limit="1"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx, .xls 格式文件，文件大小不超过16MB
            </div>
          </template>
        </el-upload>

        <el-form v-if="isSingleSheet" label-width="120px" class="module-select">
          <el-form-item label="数据模块">
            <el-select v-model="selectedModule" placeholder="请选择数据模块">
              <el-option
                v-for="(label, value) in moduleOptions"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button type="primary" :disabled="!uploadFile" @click="handlePreview">
            <el-icon><View /></el-icon>
            预览数据
          </el-button>
          <el-button type="success" :disabled="!uploadFile" @click="handleDirectImport">
            <el-icon><Upload /></el-icon>
            直接导入
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 数据预览 -->
      <div v-if="activeStep === 1" class="step-content">
        <el-alert
          v-if="previewSummary"
          :title="`共识别 ${previewSummary.total_modules} 个模块，${previewSummary.total_records} 条记录`"
          type="success"
          show-icon
          :closable="false"
          class="preview-summary"
        />

        <el-collapse v-model="activeCollapse" class="preview-collapse">
          <el-collapse-item
            v-for="(moduleData, moduleName) in previewDataList"
            :key="moduleName"
            :title="`${moduleLabels[moduleName]} (${moduleData.success_count} 条)`"
            :name="moduleName"
          >
            <el-table
              :data="moduleData.preview_data?.slice(0, 10)"
              border
              stripe
              size="small"
              class="preview-table"
            >
              <el-table-column prop="row" label="行号" width="70" />
              <el-table-column prop="code" label="代码" width="100" />
              <el-table-column prop="name" label="个股名称" width="150" />
              <el-table-column label="数据内容">
                <template #default="{ row }">
                  <el-descriptions :column="2" size="small" border>
                    <el-descriptions-item
                      v-for="(value, key) in row.data"
                      :key="key"
                      :label="key"
                    >
                      {{ formatValue(value) }}
                    </el-descriptions-item>
                  </el-descriptions>
                </template>
              </el-table-column>
            </el-table>

            <el-alert
              v-if="moduleData.error_count > 0"
              :title="`${moduleData.error_count} 条错误`"
              type="error"
              show-icon
              class="error-alert"
            >
              <template #default>
                <ul class="error-list">
                  <li v-for="(error, idx) in moduleData.errors.slice(0, 5)" :key="idx">
                    {{ error }}
                  </li>
                  <li v-if="moduleData.errors.length > 5">
                    ...还有 {{ moduleData.errors.length - 5 }} 条错误
                  </li>
                </ul>
              </template>
            </el-alert>
          </el-collapse-item>
        </el-collapse>

        <div class="step-actions">
          <el-button @click="activeStep = 0">上一步</el-button>
          <el-button type="primary" @click="executeImport">
            <el-icon><Upload /></el-icon>
            执行导入
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入结果 -->
      <div v-if="activeStep === 2" class="step-content">
        <el-result
          :icon="importResult.success ? 'success' : 'error'"
          :title="importResult.success ? '导入成功' : '导入失败'"
          :sub-title="importResult.message"
        >
          <template #extra>
            <div v-if="importResult.details" class="result-details">
              <el-descriptions title="导入详情" :column="2" border>
                <el-descriptions-item
                  v-for="(detail, moduleName) in importResult.details"
                  :key="moduleName"
                  :label="moduleLabels[moduleName]"
                >
                  <el-tag type="success">成功: {{ detail.success }}</el-tag>
                  <el-tag v-if="detail.error > 0" type="danger" style="margin-left: 8px;">
                    失败: {{ detail.error }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <el-alert
                v-if="importResult.errors && importResult.errors.length > 0"
                title="错误信息"
                type="error"
                show-icon
                class="error-list-alert"
              >
                <ul class="error-list">
                  <li v-for="(error, idx) in importResult.errors.slice(0, 10)" :key="idx">
                    {{ error }}
                  </li>
                </ul>
              </el-alert>
            </div>

            <div class="result-actions">
              <el-button @click="resetImport">重新导入</el-button>
              <el-button type="primary" @click="goToDataPage">查看数据</el-button>
            </div>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled, View, Upload } from '@element-plus/icons-vue'
import { previewImportData, executeImportData, downloadTemplate } from '../api/dataImport'

const activeStep = ref(0)
const uploadRef = ref(null)
const uploadFile = ref(null)
const isSingleSheet = ref(false)
const selectedModule = ref('')
const activeCollapse = ref([])

const previewDataList = ref({})
const previewSummary = ref(null)
const importResult = ref({})

const moduleOptions = {
  profit_rate: '毛利率与净利率',
  non_recurring: '扣非净利润增长',
  roe_net_asset: 'ROE与净资产',
  pe_valuation: 'PE估值',
  shareholder_structure: '股东结构',
  shareholder_count: '股东户数',
  rd_expense: '研发投入',
  rd_staff: '研发人员'
}

const moduleLabels = {
  profit_rate: '毛利率与净利率',
  non_recurring: '扣非净利润增长',
  roe_net_asset: 'ROE与净资产',
  pe_valuation: 'PE估值',
  shareholder_structure: '股东结构',
  shareholder_count: '股东户数',
  rd_expense: '研发投入',
  rd_staff: '研发人员'
}

const handleFileChange = (file) => {
  uploadFile.value = file.raw
  // 这里可以检测是否为单Sheet
  isSingleSheet.value = false // 简化处理，让后端自动检测
}

const handleFileRemove = () => {
  uploadFile.value = null
  isSingleSheet.value = false
  selectedModule.value = ''
}

const handleDownloadTemplate = async () => {
  try {
    const blob = await downloadTemplate()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '数据导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const handlePreview = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }

  const formData = new FormData()
  formData.append('file', uploadFile.value)
  if (selectedModule.value) {
    formData.append('module', selectedModule.value)
  }

  try {
    const responseData = await previewImportData(formData)
    
    previewDataList.value = responseData.preview || {}
    previewSummary.value = responseData.summary || {}
    activeCollapse.value = Object.keys(previewDataList.value)
    activeStep.value = 1

    ElMessage.success('预览成功')
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error(error.message || '预览失败')
  }
}

const handleDirectImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }

  try {
    await ElMessage.confirm(
      '确定要直接导入吗？建议先预览数据确认无误后再导入。',
      '直接导入确认',
      {
        confirmButtonText: '确定导入',
        cancelButtonText: '先预览',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  await executeImportInternal()
}

const executeImport = async () => {
  await executeImportInternal()
}

const executeImportInternal = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('文件已丢失，请重新上传')
    return
  }

  const formData = new FormData()
  formData.append('file', uploadFile.value)
  if (selectedModule.value) {
    formData.append('module', selectedModule.value)
  }

  try {
    const responseData = await executeImportData(formData)
    
    importResult.value = {
      success: true,
      message: `成功导入 ${responseData.total_success} 条记录`,
      details: responseData.details,
      errors: responseData.errors
    }
    activeStep.value = 2

    ElMessage.success('导入成功')
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      success: false,
      message: error.message || '导入失败'
    }
    activeStep.value = 2
    ElMessage.error('导入失败')
  }
}

const resetImport = () => {
  activeStep.value = 0
  uploadFile.value = null
  selectedModule.value = ''
  previewDataList.value = {}
  previewSummary.value = null
  importResult.value = {}
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const goToDataPage = () => {
  window.location.href = '/profit-rate'
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') return value.toFixed(2)
  return value
}
</script>

<style scoped>
.data-import-container {
  padding: 20px;
}

.import-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-steps {
  margin: 30px 0;
}

.step-content {
  margin-top: 30px;
}

.import-info {
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
}

.module-select {
  margin-top: 20px;
}

.step-actions {
  margin-top: 30px;
  text-align: center;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.preview-summary {
  margin-bottom: 20px;
}

.preview-collapse {
  margin-bottom: 20px;
}

.preview-table {
  margin-bottom: 10px;
}

.error-alert {
  margin-top: 10px;
}

.error-list {
  margin: 0;
  padding-left: 20px;
  font-size: 12px;
}

.error-list li {
  margin: 5px 0;
  color: #f56c6c;
}

.result-details {
  text-align: left;
  margin: 20px 0;
}

.error-list-alert {
  margin-top: 20px;
}

.result-actions {
  margin-top: 30px;
}
</style>
