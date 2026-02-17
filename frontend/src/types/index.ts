export interface User {
  id: string
  email: string
  name?: string
  created_at?: string
}

export interface Account {
  id: string
  user_id: string
  bank_name: string
  account_number: string
  account_type: string
  balance: number
  is_active: boolean
  created_at: string
}

export interface Transaction {
  id: string
  account_id: string
  amount: number
  date: string
  description: string
  category: string
  type: 'debit' | 'credit'
}

export interface Budget {
  id: string
  user_id: string
  name: string
  limit: number
  spent: number
  category: string
  created_at: string
}

export interface Bill {
  id: string
  user_id: string
  name: string
  amount: number
  due_date: string
  status: 'pending' | 'paid' | 'overdue'
  created_at: string
}

export interface AuthResponse {
  access_token: string
  user: User
}
