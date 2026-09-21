import api from './api'

export const getRules    = ()             => api.get('/suppression')
export const createRule  = (body)         => api.post('/suppression', body)
export const toggleRule  = (id, active)   => api.patch(`/suppression/${id}/toggle`, null, { params: { active } })
export const deleteRule  = (id)           => api.delete(`/suppression/${id}`)
