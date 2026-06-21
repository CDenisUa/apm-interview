// Types

export type Country = 'AT' | 'DE' | 'US' | 'UA'
export type ItemStatus = 'active' | 'inactive' | 'pending'

export interface BusinessItem {
  id: string
  name: string
  country: Country
  status: ItemStatus
  revenue: number
  owner: string
  updatedAt: string
}
