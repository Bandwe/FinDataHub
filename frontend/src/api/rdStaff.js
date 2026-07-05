import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/rd_staff'

export const getRdStaffs = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createRdStaff = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateRdStaff = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteRdStaff = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportRdStaff = (params) => {
  return exportModuleRecords(endpoint, params)
}
