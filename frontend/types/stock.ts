export interface Stock {
  id: number
  symbol: string
  name: string
  current_price: number
  previous_close?: number
  change?: number
  change_percent?: number
  market_cap?: number
  volume?: number
  pe_ratio?: number
  dividend_yield?: number
  sector?: string
  industry?: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface StockCreate {
  symbol: string
  name: string
  current_price: number
  previous_close?: number
  change?: number
  change_percent?: number
  market_cap?: number
  volume?: number
  pe_ratio?: number
  dividend_yield?: number
  sector?: string
  industry?: string
  description?: string
}

export interface StockUpdate {
  symbol?: string
  name?: string
  current_price?: number
  previous_close?: number
  change?: number
  change_percent?: number
  market_cap?: number
  volume?: number
  pe_ratio?: number
  dividend_yield?: number
  sector?: string
  industry?: string
  description?: string
}

export interface StockItem {
  id: string
  name: string
  category: string
  current_stock: number
  min_stock: number
  unit: string
  package_size: number
  package_unit: string
  cost_per_unit: number
  is_ready_made: boolean
  usage_per_order: number
  usage_per_day: number
  usage_type: string
  can_edit: boolean
  edit_reason: string
  edit_message: string
}

export interface StockResponse {
  stock_data: StockItem[]
  total_items: number
}
