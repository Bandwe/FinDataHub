import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/pe_valuation'

export const getPeValuations = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createPeValuation = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updatePeValuation = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deletePeValuation = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportPeValuation = (params) => {
  return exportModuleRecords(endpoint, params)
}
