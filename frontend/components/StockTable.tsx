'use client'

import { useState } from 'react'
import { Edit, Trash2, TrendingUp, TrendingDown } from 'lucide-react'
import { Stock } from '@/types/stock'
import EditStockModal from './EditStockModal'

interface StockTableProps {
  stocks: Stock[]
  onRefresh: () => void
}

export default function StockTable({ stocks, onRefresh }: StockTableProps) {
  const [editingStock, setEditingStock] = useState<Stock | null>(null)

  const handleDelete = async (stockId: number) => {
    if (confirm('Are you sure you want to delete this stock?')) {
      try {
        const response = await fetch(`/api/stocks/${stockId}`, {
          method: 'DELETE',
        })
        
        if (response.ok) {
          onRefresh()
        }
      } catch (error) {
        console.error('Error deleting stock:', error)
      }
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value)
  }

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  if (stocks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No stocks found</h3>
        <p className="text-gray-600">Get started by adding your first stock to the portfolio.</p>
      </div>
    )
  }

  return (
    <>
      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Price</th>
              <th>Change</th>
              <th>Market Cap</th>
              <th>Volume</th>
              <th>Sector</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.id} className="hover:bg-gray-50">
                <td>
                  <div className="font-semibold text-gray-900">{stock.symbol}</div>
                </td>
                <td>
                  <div className="text-sm text-gray-900">{stock.name}</div>
                  {stock.industry && (
                    <div className="text-xs text-gray-500">{stock.industry}</div>
                  )}
                </td>
                <td>
                  <div className="font-semibold text-gray-900">
                    {formatCurrency(stock.current_price)}
                  </div>
                </td>
                <td>
                  {stock.change !== undefined && stock.change_percent !== undefined && (
                    <div className={`flex items-center gap-1 ${
                      stock.change >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {stock.change >= 0 ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      <span className="font-medium">
                        {formatCurrency(Math.abs(stock.change))}
                      </span>
                      <span className="text-sm">
                        ({formatPercentage(stock.change_percent)})
                      </span>
                    </div>
                  )}
                </td>
                <td>
                  {stock.market_cap ? (
                    <span className="text-sm text-gray-900">
                      ${(stock.market_cap / 1e9).toFixed(2)}B
                    </span>
                  ) : (
                    <span className="text-sm text-gray-400">-</span>
                  )}
                </td>
                <td>
                  {stock.volume ? (
                    <span className="text-sm text-gray-900">
                      {formatNumber(stock.volume)}
                    </span>
                  ) : (
                    <span className="text-sm text-gray-400">-</span>
                  )}
                </td>
                <td>
                  <span className="text-sm text-gray-600">{stock.sector || '-'}</span>
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setEditingStock(stock)}
                      className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                      title="Edit stock"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(stock.id)}
                      className="p-1 text-gray-400 hover:text-danger-600 transition-colors"
                      title="Delete stock"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingStock && (
        <EditStockModal
          stock={editingStock}
          onClose={() => setEditingStock(null)}
          onSave={async (updatedStock) => {
            try {
              const response = await fetch(`/api/stocks/${updatedStock.id}`, {
                method: 'PUT',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedStock),
              })
              
              if (response.ok) {
                onRefresh()
                setEditingStock(null)
              }
            } catch (error) {
              console.error('Error updating stock:', error)
            }
          }}
        />
      )}
    </>
  )
}
