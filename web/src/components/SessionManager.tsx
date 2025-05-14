import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Plus, Trash2, RefreshCw } from 'lucide-react'
import { api } from '@/lib/api'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

interface SessionManagerProps {
  appName: string
  userId: string
  currentSession: string
  onSessionChange: (sessionId: string) => void
  onNewSession: () => void
}

export function SessionManager({
  appName,
  userId,
  currentSession,
  onSessionChange,
  onNewSession,
}: SessionManagerProps) {
  const [sessions, setSessions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchSessions = async () => {
    if (!appName) return
    
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

  useEffect(() => {
    fetchSessions()
  }, [appName, userId])

  const createNewSession = async () => {
    try {
      const response = await api.post(`/apps/${appName}/users/${userId}/sessions`)
      await fetchSessions()
      onSessionChange(response.data.id)
    } catch (error) {
      console.error('Error creating session:', error)
    }
  }

  const deleteSession = async (sessionId: string) => {
    try {
      await api.delete(`/apps/${appName}/users/${userId}/sessions/${sessionId}`)
      await fetchSessions()
      if (currentSession === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId)
        if (remainingSessions.length > 0) {
          onSessionChange(remainingSessions[0].id)
        } else {
          onNewSession()
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={currentSession} onValueChange={onSessionChange}>
        <SelectTrigger className="w-64 bg-[#2a2a30] border-[#3a3a40] text-white hover:bg-[#33333a] transition-colors">
          <SelectValue placeholder={loading ? "Loading..." : "Select a session"} />
        </SelectTrigger>
        <SelectContent className="bg-[#2a2a30] border-[#3a3a40]">
          {sessions.map((session) => (
            <SelectItem 
              key={session.id} 
              value={session.id} 
              className="text-white hover:bg-[#33333a] focus:bg-[#33333a]"
            >
              <div className="flex items-center justify-between w-full">
                <span>{session.id.substring(0, 8)}...</span>
                <span className="text-xs text-[#a0a0a8] ml-2">
                  {new Date(session.creation_timestamp * 1000).toLocaleDateString()}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        onClick={createNewSession}
        variant="ghost"
        size="icon"
        className="text-blue-400 hover:text-blue-300 hover:bg-[#2a2a30]"
      >
        <Plus className="w-4 h-4" />
      </Button>

      <Button
        onClick={fetchSessions}
        variant="ghost"
        size="icon"
        className="text-[#a0a0a8] hover:text-white hover:bg-[#2a2a30]"
      >
        <RefreshCw className="w-4 h-4" />
      </Button>

      {currentSession && (
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-red-400 hover:text-red-300 hover:bg-[#2a2a30]"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="bg-[#1a1a1f] border-[#2a2a30]">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-white">Confirm delete</AlertDialogTitle>
              <AlertDialogDescription className="text-[#a0a0a8]">
                Are you sure you want to delete this session {currentSession.substring(0, 8)}...?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="bg-[#2a2a30] text-white border-[#3a3a40] hover:bg-[#33333a]">
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={() => deleteSession(currentSession)}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </div>
  )
}