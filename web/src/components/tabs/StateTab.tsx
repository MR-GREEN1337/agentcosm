import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Code } from 'lucide-react'

interface StateTabProps {
  appName: string
  userId: string
  sessionId: string
}

export function StateTab({ appName, userId, sessionId }: StateTabProps) {
  const [state, setState] = useState<any>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchSession = async () => {
      if (!sessionId) return

      setLoading(true)
      try {
        const response = await api.get(`/apps/${appName}/users/${userId}/sessions/${sessionId}`)
        setState(response.data.state || {})
      } catch (error) {
        console.error('Error fetching session:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSession()
  }, [appName, userId, sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-[#a0a0a8]">Loading state...</p>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-medium text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Code className="w-5 h-5 text-white" />
            </div>
            Session State
          </h2>
          <p className="text-[#a0a0a8] mt-2">Current state of your session</p>
        </div>

        <Card className="bg-[#1a1a1f] border-[#2a2a30] p-4">
          <pre className="text-sm text-[#d0d0d8] overflow-x-auto font-mono">
            {JSON.stringify(state, null, 2)}
          </pre>
        </Card>
      </div>
    </ScrollArea>
  )
}
