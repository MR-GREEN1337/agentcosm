import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MessageSquare, Bot, User } from 'lucide-react'

interface EventsTabProps {
  appName: string
  userId: string
  sessionId: string
  events: any[]
}

export function EventsTab({ appName, userId, sessionId, events }: EventsTabProps) {
  const [sessionEvents, setSessionEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchSession = async () => {
      if (!sessionId) return
      
      setLoading(true)
      try {
        const response = await api.get(`/apps/${appName}/users/${userId}/sessions/${sessionId}`)
        setSessionEvents(response.data.events || [])
      } catch (error) {
        console.error('Error fetching session:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSession()
  }, [appName, userId, sessionId])

  const allEvents = [...sessionEvents, ...events]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-[#a0a0a8]">Loading events...</div>
      </div>
    )
  }

  if (allEvents.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <MessageSquare className="w-16 h-16 text-[#3a3a40] mx-auto mb-4" />
          <p className="text-[#a0a0a8] text-lg">No conversations yet</p>
          <p className="text-[#6a6a70] text-sm mt-2">Start typing below to begin</p>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-4">
        {allEvents.map((event, index) => (
          <Card key={event.id || index} className="bg-[#1a1a1f] border-[#2a2a30] p-4 hover:bg-[#1f1f24] transition-colors">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                {event.author === 'assistant' ? (
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-[#2a2a30] flex items-center justify-center">
                    <User className="w-4 h-4 text-[#a0a0a8]" />
                  </div>
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-baseline justify-between mb-1">
                  <span className="text-sm font-medium text-white">
                    {event.author || 'Unknown'}
                  </span>
                  <span className="text-xs text-[#6a6a70]">
                    {event.timestamp ? new Date(event.timestamp * 1000).toLocaleTimeString() : ''}
                  </span>
                </div>
                <div className="text-[#d0d0d8]">
                  {event.text && <p>{event.text}</p>}
                  {event.function_calls && event.function_calls.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-[#a0a0a8] mb-1">Function calls:</p>
                      <div className="space-y-1">
                        {event.function_calls.map((call: any, idx: number) => (
                          <div key={idx} className="text-sm bg-[#0e0e10] p-2 rounded text-blue-400 font-mono">
                            {call.name}()
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {event.function_responses && event.function_responses.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-[#a0a0a8] mb-1">Function responses:</p>
                      <div className="space-y-1">
                        {event.function_responses.map((response: any, idx: number) => (
                          <div key={idx} className="text-sm bg-[#0e0e10] p-2 rounded">
                            <span className="text-green-400 font-mono">{response.name}</span>
                            <span className="text-[#a0a0a8]">: {response.response_data}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </ScrollArea>
  )
}