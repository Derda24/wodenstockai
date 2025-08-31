'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { Stock, StockUpdate } from '@/types/stock'

interface EditStockModalProps {
  stock: Stock
  onClose: () => void
  onSave: (stock: StockUpdate & { id: number }) => void
}

interface FormErrors {
  symbol?: string
  name?: string
  current_price?: string
  previous_close?: string
  change?: string
  change_percent?: string
  market_cap?: string
  volume?: string
  pe_ratio?: string
  dividend_yield?: string
  sector?: string
  industry?: string
  description?: string
}

export default function EditStockModal({ stock, onClose, onSave }: EditStockModalProps) {
  const [formData, setFormData] = useState<StockUpdate>({})
  const [errors, setErrors] = useState<FormErrors>({})

  useEffect(() => {
    setFormData({
      symbol: stock.symbol,
      name: stock.name,
      current_price: stock.current_price,
      previous_close: stock.previous_close,
      change: stock.change,
      change_percent: stock.change_percent,
      market_cap: stock.market_cap,
      volume: stock.volume,
      pe_ratio: stock.pe_ratio,
      dividend_yield: stock.dividend_yield,
      sector: stock.sector,
      industry: stock.industry,
      description: stock.description,
    })
  }, [stock])

  const validateForm = () => {
    const newErrors: FormErrors = {}
    
    if (formData.symbol && !formData.symbol.trim()) {
      newErrors.symbol = 'Symbol cannot be empty'
    }
    if (formData.name && !formData.name.trim()) {
      newErrors.name = 'Name cannot be empty'
    }
    if (formData.current_price !== undefined && formData.current_price <= 0) {
      newErrors.current_price = 'Price must be greater than 0'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onSave({ ...formData, id: stock.id })
    }
  }

  const handleChange = (field: keyof StockUpdate, value: string | number | undefined) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Edit Stock: {stock.symbol}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Symbol */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol
              </label>
              <input
                type="text"
                value={formData.symbol || ''}
                onChange={(e) => handleChange('symbol', e.target.value.toUpperCase())}
                className={`input ${errors.symbol ? 'border-danger-500' : ''}`}
                placeholder="AAPL"
                maxLength={10}
              />
              {errors.symbol && (
                <p className="mt-1 text-sm text-danger-600">{errors.symbol}</p>
              )}
            </div>

            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                className={`input ${errors.name ? 'border-danger-500' : ''}`}
                placeholder="Apple Inc."
              />
              {errors.name && (
                <p className="mt-1 text-sm text-danger-600">{errors.name}</p>
              )}
            </div>

            {/* Current Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Price
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.current_price || ''}
                onChange={(e) => handleChange('current_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                className={`input ${errors.current_price ? 'border-danger-500' : ''}`}
                placeholder="150.00"
              />
              {errors.current_price && (
                <p className="mt-1 text-sm text-danger-600">{errors.current_price}</p>
              )}
            </div>

            {/* Previous Close */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Previous Close
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.previous_close || ''}
                onChange={(e) => handleChange('previous_close', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="input"
                placeholder="149.50"
              />
            </div>

            {/* Sector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sector
              </label>
              <input
                type="text"
                value={formData.sector || ''}
                onChange={(e) => handleChange('sector', e.target.value)}
                className="input"
                placeholder="Technology"
              />
            </div>

            {/* Industry */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <input
                type="text"
                value={formData.industry || ''}
                onChange={(e) => handleChange('industry', e.target.value)}
                className="input"
                placeholder="Consumer Electronics"
              />
            </div>

            {/* Market Cap */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Market Cap (Billions)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.market_cap ? formData.market_cap / 1e9 : ''}
                onChange={(e) => handleChange('market_cap', e.target.value ? parseFloat(e.target.value) * 1e9 : undefined)}
                className="input"
                placeholder="2.5"
              />
            </div>

            {/* Volume */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Volume
              </label>
              <input
                type="number"
                min="0"
                value={formData.volume || ''}
                onChange={(e) => handleChange('volume', e.target.value ? parseInt(e.target.value) : undefined)}
                className="input"
                placeholder="50000000"
              />
            </div>

            {/* P/E Ratio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                P/E Ratio
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.pe_ratio || ''}
                onChange={(e) => handleChange('pe_ratio', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="input"
                placeholder="25.5"
              />
            </div>

            {/* Dividend Yield */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dividend Yield (%)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.dividend_yield || ''}
                onChange={(e) => handleChange('dividend_yield', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="input"
                placeholder="2.5"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => handleChange('description', e.target.value)}
              className="input"
              rows={3}
              placeholder="Brief description of the company..."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
