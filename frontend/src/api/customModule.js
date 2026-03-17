import request from './request'

// 获取所有启用的自定义模块
export const getCustomModules = () => {
  return request({
    url: '/custom-modules',
    method: 'get'
  })
}

// 获取所有模块（包括禁用的）- 用于管理
export const getAllModules = () => {
  return request({
    url: '/custom-modules/all',
    method: 'get'
  })
}

// 获取单个模块详情
export const getCustomModule = (moduleId) => {
  return request({
    url: `/custom-modules/${moduleId}`,
    method: 'get'
  })
}

// 创建自定义模块
export const createCustomModule = (data) => {
  return request({
    url: '/custom-modules',
    method: 'post',
    data
  })
}

// 更新自定义模块
export const updateCustomModule = (moduleId, data) => {
  return request({
    url: `/custom-modules/${moduleId}`,
    method: 'put',
    data
  })
}

// 删除自定义模块
export const deleteCustomModule = (moduleId) => {
  return request({
    url: `/custom-modules/${moduleId}`,
    method: 'delete'
  })
}

// ============ 关键词管理 ============

// 获取模块的所有关键词
export const getModuleKeywords = (moduleId) => {
  return request({
    url: `/custom-modules/${moduleId}/keywords`,
    method: 'get'
  })
}

// 为模块添加关键词
export const createModuleKeyword = (moduleId, data) => {
  return request({
    url: `/custom-modules/${moduleId}/keywords`,
    method: 'post',
    data
  })
}

// 更新关键词
export const updateModuleKeyword = (moduleId, keywordId, data) => {
  return request({
    url: `/custom-modules/${moduleId}/keywords/${keywordId}`,
    method: 'put',
    data
  })
}

// 删除关键词
export const deleteModuleKeyword = (moduleId, keywordId) => {
  return request({
    url: `/custom-modules/${moduleId}/keywords/${keywordId}`,
    method: 'delete'
  })
}

// 批量更新关键词
export const batchUpdateKeywords = (moduleId, keywords) => {
  return request({
    url: `/custom-modules/${moduleId}/keywords/batch`,
    method: 'post',
    data: { keywords }
  })
}