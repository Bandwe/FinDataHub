import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/shareholder_count'

export const getShareholderCounts = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createShareholderCount = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateShareholderCount = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteShareholderCount = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportShareholderCount = (params) => {
  return exportModuleRecords(endpoint, params)
}
