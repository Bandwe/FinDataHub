import request from './request'

export const getShareholderStructures = (params) => {
  return request({
    url: '/shareholder_structure',
    method: 'get',
    params
  })
}

export const createShareholderStructure = (data) => {
  return request({
    url: '/shareholder_structure',
    method: 'post',
    data
  })
}

export const updateShareholderStructure = (id, data) => {
  return request({
    url: `/shareholder_structure/${id}`,
    method: 'put',
    data
  })
}

export const deleteShareholderStructure = (id) => {
  return request({
    url: `/shareholder_structure/${id}`,
    method: 'delete'
  })
}

export const exportShareholderStructure = (params) => {
  return request({
    url: '/shareholder_structure/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
