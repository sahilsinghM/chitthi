import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ModelInfo {
  id: string
  name: string
  display_name: string
  provider: string
  cost_per_1k_input: number
  cost_per_1k_output: number
  available: boolean
  description?: string
}

export interface ModelCost {
  model_id: string
  display_name: string
  provider: string
  cost_per_2k_tokens: number
  cost_per_1k_input: number
  cost_per_1k_output: number
}

export const api = {
  models: {
    list: async (): Promise<ModelInfo[]> => {
      const response = await axios.get(`${API_BASE}/api/models/`)
      return response.data.models
    },
    costs: async (): Promise<ModelCost[]> => {
      const response = await axios.get(`${API_BASE}/api/models/costs`)
      return response.data.costs
    },
    test: async (model?: string, provider?: string) => {
      const response = await axios.post(`${API_BASE}/api/models/test`, {
        model,
        provider
      })
      return response.data
    },
    generate: async (prompt: string, model: string, options?: {
      system_prompt?: string
      temperature?: number
      max_tokens?: number
    }) => {
      const response = await axios.post(`${API_BASE}/api/models/generate`, {
        prompt,
        model,
        ...options
      })
      return response.data
    }
  },
  drafts: {
    generate: async (model: string, context?: string, options?: {
      topic_id?: string
      system_prompt?: string
      temperature?: number
      max_tokens?: number
    }) => {
      const response = await axios.post(`${API_BASE}/api/drafts/generate`, {
        model,
        context,
        ...options
      })
      return response.data
    },
    compare: async (models: string[], prompt: string, options?: {
      system_prompt?: string
      temperature?: number
    }) => {
      const response = await axios.post(`${API_BASE}/api/drafts/compare`, {
        models,
        prompt,
        ...options
      })
      return response.data
    },
    list: async (status?: string, limit?: number) => {
      const params = new URLSearchParams()
      if (status) params.append('status', status)
      if (limit) params.append('limit', limit.toString())
      const response = await axios.get(`${API_BASE}/api/drafts/list?${params.toString()}`)
      return response.data
    },
    get: async (draftId: string) => {
      const response = await axios.get(`${API_BASE}/api/drafts/${draftId}`)
      return response.data
    },
    getVersions: async (draftId: string) => {
      const response = await axios.get(`${API_BASE}/api/drafts/${draftId}/versions`)
      return response.data
    },
    createVersion: async (draftId: string, content: string, changesSummary?: string) => {
      const response = await axios.post(`${API_BASE}/api/drafts/${draftId}/versions`, {
        content,
        changes_summary: changesSummary
      })
      return response.data
    }
  },
  topics: {
    prioritize: async (contentItems?: any[], interestWeights?: Record<string, number>, useDatabase?: boolean) => {
      const response = await axios.post(`${API_BASE}/api/topics/prioritize`, {
        content_items: contentItems,
        interest_weights: interestWeights,
        use_database: useDatabase ?? true
      })
      return response.data
    },
    list: async (limit?: number) => {
      const params = new URLSearchParams()
      if (limit) params.append('limit', limit.toString())
      const response = await axios.get(`${API_BASE}/api/topics/list?${params.toString()}`)
      return response.data
    }
  },
  analytics: {
    usage: async (provider?: string, days?: number) => {
      const params = new URLSearchParams()
      if (provider) params.append('provider', provider)
      if (days) params.append('days', days.toString())
      const response = await axios.get(`${API_BASE}/api/analytics/usage?${params.toString()}`)
      return response.data
    },
    costs: async () => {
      const response = await axios.get(`${API_BASE}/api/analytics/costs`)
      return response.data
    }
  }
}

