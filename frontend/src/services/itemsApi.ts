// Services
import { apiClient, toQuery } from './apiClient'
// Types
import type { BusinessItem, Country, ItemStatus } from '../types/item'

export interface ItemsQuery {
  country?: Country
  status?: ItemStatus
  search?: string
}

export const getItems = (query: ItemsQuery = {}): Promise<BusinessItem[]> =>
  apiClient.get<BusinessItem[]>(`/api/items${toQuery({ ...query })}`)
