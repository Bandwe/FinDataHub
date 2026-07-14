import request from './request'
import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/profit_rate'

export const getProfitRates = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createProfitRate = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateProfitRate = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteProfitRate = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const importProfitRate = (formData, preview = false) => {
  return request({
    url: `/profit_rate/import${preview ? '?preview=true' : ''}`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const exportProfitRate = (params) => {
  return exportModuleRecords(endpoint, params)
}
