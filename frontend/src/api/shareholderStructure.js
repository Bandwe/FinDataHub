import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/shareholder_structure'

export const getShareholderStructures = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createShareholderStructure = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateShareholderStructure = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteShareholderStructure = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportShareholderStructure = (params) => {
  return exportModuleRecords(endpoint, params)
}
