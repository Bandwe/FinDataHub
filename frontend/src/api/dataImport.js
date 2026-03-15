import request from './request'

// 上传并预览数据
export const previewImportData = (formData) => {
  return request({
    url: '/data_import/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 执行导入
export const executeImportData = (formData) => {
  return request({
    url: '/data_import/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 下载导入模板
export const downloadTemplate = () => {
  return request({
    url: '/data_import/template',
    method: 'get',
    responseType: 'blob'
  })
}
