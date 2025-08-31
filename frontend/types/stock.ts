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
