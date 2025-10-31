'use client'

import { CostDashboard } from '@/components/CostDashboard'

export default function AnalyticsPage() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Analytics Dashboard</h1>
        <p className="text-muted-foreground mb-8">
          Cost tracking and usage statistics
        </p>
        <CostDashboard />
      </div>
    </main>
  )
}

