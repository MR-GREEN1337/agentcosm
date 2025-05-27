import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'

interface SessionsTabProps {
  appName: string
  userId: string
  currentSession: string
}

interface Session {
  id: string
  app_name: string
  user_id: string
  creation_timestamp: number
  state: any
  events: any[]
}

export function SessionsTab({ appName, userId, currentSession }: SessionsTabProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true)
      try {
        const response = await api.get(`/apps/${appName}/users/${userId}/sessions`)
        setSessions(response.data)
      } catch (error) {
        console.error('Error fetching sessions:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSessions()
  }, [appName, userId])

  const fetchSessionDetails = async (sessionId: string) => {
    try {
      const response = await api.get(`/apps/${appName}/users/${userId}/sessions/${sessionId}`)
      setSelectedSession(response.data)
    } catch (error) {
      console.error('Error fetching session details:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Loading sessions...</p>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      <div className="w-1/3 border-r border-gray-700">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-2">
            {sessions.map((session) => (
              <Card
                key={session.id}
                className={`bg-gray-800 border-gray-700 p-3 cursor-pointer hover:bg-gray-750 transition-colors ${
                  selectedSession?.id === session.id ? 'border-blue-500' : ''
                }`}
                onClick={() => fetchSessionDetails(session.id)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-100">
                    {session.id === currentSession ? '(Current) ' : ''}
                    {session.id.substring(0, 8)}...
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(session.creation_timestamp * 1000).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      <div className="flex-1">
        {selectedSession ? (
          <ScrollArea className="h-full">
            <div className="p-4">
              <Card className="bg-gray-800 border-gray-700 p-4 mb-4">
                <h3 className="text-lg font-medium text-gray-100 mb-2">Session Details</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-400">ID:</span>{' '}
                    <span className="text-gray-100">{selectedSession.id}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Created:</span>{' '}
                    <span className="text-gray-100">
                      {new Date(selectedSession.creation_timestamp * 1000).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Events:</span>{' '}
                    <span className="text-gray-100">{selectedSession.events?.length || 0}</span>
                  </div>
                </div>
              </Card>

              <Card className="bg-gray-800 border-gray-700 p-4">
                <h3 className="text-lg font-medium text-gray-100 mb-2">State</h3>
                <pre className="text-sm text-gray-300 overflow-x-auto">
                  {JSON.stringify(selectedSession.state, null, 2)}
                </pre>
              </Card>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Select a session to view details</p>
          </div>
        )}
      </div>
    </div>
  )
}
