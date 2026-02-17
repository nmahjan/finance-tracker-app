import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { accountsAPI, transactionsAPI } from '../services/api'
import { Account, Transaction } from '../types'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // For now, just load transactions (accounts route not set up yet)
      const txnRes = await transactionsAPI.list()
      setTransactions(txnRes.data)
      // TODO: Add accounts endpoint once Plaid integration is complete
      setAccounts([])
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">💰 Finance Tracker</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-lg text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h3 className="text-sm font-medium text-gray-500">Total Balance</h3>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h3 className="text-sm font-medium text-gray-500">Connected Accounts</h3>
                <p className="text-3xl font-bold text-gray-900 mt-2">{accounts.length}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h3 className="text-sm font-medium text-gray-500">Recent Transactions</h3>
                <p className="text-3xl font-bold text-gray-900 mt-2">{transactions.length}</p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Bank Accounts</h2>
              {accounts.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">No accounts connected yet</p>
                  <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm">
                    Link Bank Account
                  </button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Bank Name</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Account Type</th>
                        <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {accounts.map((account) => (
                        <tr key={account.id} className="border-t hover:bg-gray-50 transition">
                          <td className="px-4 py-3 text-sm text-gray-900 font-medium">{account.bank_name}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{account.account_type}</td>
                          <td className="px-4 py-3 text-sm font-semibold text-gray-900 text-right">
                            ${account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
