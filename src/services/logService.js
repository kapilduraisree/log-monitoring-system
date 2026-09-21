import api from './api'

export const getLogs           = (params) => api.get('/logs', { params })
export const getLog            = (id)     => api.get(`/logs/${id}`)
export const deleteLog         = (id)     => api.delete(`/logs/${id}`)
export const getStats          = ()       => api.get('/logs/stats')
export const getHourly         = ()       => api.get('/logs/hourly')
export const getTopIPs         = (limit)  => api.get('/logs/top-ips', { params: { limit } })
export const getAttackCats     = ()       => api.get('/logs/attack-categories')
// Feature 9: Threat Timeline
export const getTimeline       = (ip)     => api.get('/logs/timeline', { params: ip ? { ip } : {} })
