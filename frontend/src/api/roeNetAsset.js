import request from './request'

export const getRoeNetAssets = (params) => {
  return request({
    url: '/roe_net_asset',
    method: 'get',
    params
  })
}

export const createRoeNetAsset = (data) => {
  return request({
    url: '/roe_net_asset',
    method: 'post',
    data
  })
}

export const updateRoeNetAsset = (id, data) => {
  return request({
    url: `/roe_net_asset/${id}`,
    method: 'put',
    data
  })
}

export const deleteRoeNetAsset = (id) => {
  return request({
    url: `/roe_net_asset/${id}`,
    method: 'delete'
  })
}

export const exportRoeNetAsset = (params) => {
  return request({
    url: '/roe_net_asset/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
