import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const navigate = useNavigate()
  const { login, register, isLoading, error } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (isRegister) await register(email, password)
      else await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Auth failed:', err)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-2">💰 Finance Tracker</h1>
        <form onSubmit={handleSubmit} className="space-y-4 mt-8">
          <input type="email" placeholder="Email..." value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-2 border rounded-lg" />
          <input type="password" placeholder="Password..." value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-2 border rounded-lg" />
          <button type="submit" disabled={isLoading} className="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400">
            {isLoading ? 'Loading...' : isRegister ? 'Sign Up' : 'Sign In'}
          </button>
        </form>
        {error && <p className="mt-4 text-red-600 text-center text-sm">{error}</p>}
        <button onClick={() => setIsRegister(!isRegister)} className="mt-6 w-full text-indigo-600 hover:text-indigo-700 text-sm">
          {isRegister ? 'Back to Sign In' : "Don't have an account? Sign Up"}
        </button>
      </div>
    </div>
  )
}