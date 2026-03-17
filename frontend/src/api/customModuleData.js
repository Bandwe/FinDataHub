import request from './request'

// 获取自定义模块数据列表
export const getCustomModuleData = (moduleCode, params) => {
  return request({
    url: `/custom-module-data/${moduleCode}`,
    method: 'get',
    params
  })
}

// 创建自定义模块数据
export const createCustomModuleData = (moduleCode, data) => {
  return request({
    url: `/custom-module-data/${moduleCode}`,
    method: 'post',
    data
  })
}

// 更新自定义模块数据
export const updateCustomModuleData = (moduleCode, recordId, data) => {
  return request({
    url: `/custom-module-data/${moduleCode}/${recordId}`,
    method: 'put',
    data
  })
}

// 删除自定义模块数据
export const deleteCustomModuleData = (moduleCode, recordId) => {
  return request({
    url: `/custom-module-data/${moduleCode}/${recordId}`,
    method: 'delete'
  })
}

// 导出自定义模块数据
export const exportCustomModuleData = (moduleCode) => {
  return request({
    url: `/custom-module-data/${moduleCode}/export`,
    method: 'get',
    responseType: 'blob'
  })
}

// 导入自定义模块数据
export const importCustomModuleData = (moduleCode, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/custom-module-data/${moduleCode}/import`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 对比自定义模块数据
export const compareCustomModuleData = (moduleCode, data) => {
  return request({
    url: `/custom-module-data/${moduleCode}/compare`,
    method: 'post',
    data
  })
}