import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/roe_net_asset'

export const getRoeNetAssets = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createRoeNetAsset = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateRoeNetAsset = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteRoeNetAsset = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportRoeNetAsset = (params) => {
  return exportModuleRecords(endpoint, params)
}
