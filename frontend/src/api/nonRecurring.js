import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/non_recurring'

export const getNonRecurrings = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createNonRecurring = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateNonRecurring = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteNonRecurring = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportNonRecurring = (params) => {
  return exportModuleRecords(endpoint, params)
}
