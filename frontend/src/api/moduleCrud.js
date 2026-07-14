import request from './request'

export const listModuleRecords = (endpoint, params) => {
  return request({
    url: endpoint,
    method: 'get',
    params
  })
}

export const createModuleRecord = (endpoint, data) => {
  return request({
    url: endpoint,
    method: 'post',
    data
  })
}

export const updateModuleRecord = (endpoint, id, data) => {
  return request({
    url: `${endpoint}/${id}`,
    method: 'put',
    data
  })
}

export const deleteModuleRecord = (endpoint, id) => {
  return request({
    url: `${endpoint}/${id}`,
    method: 'delete'
  })
}

export const exportModuleRecords = (endpoint, params) => {
  return request({
    url: `${endpoint}/export`,
    method: 'get',
    params,
    responseType: 'blob'
  })
}
