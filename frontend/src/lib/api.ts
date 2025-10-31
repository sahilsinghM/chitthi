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
    }
  }
}

