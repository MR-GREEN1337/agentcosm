import { useState, useRef, useCallback, memo, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Inbox, Settings, FolderOpen, Trash2, User, LogOut, Moon, Sun } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'

interface ChatSession {
  id: string
  title?: string
  creation_timestamp: number
  last_message?: string
  last_message_timestamp?: number
}

interface ChatSidebarProps {
  isOpen: boolean
  onClose: () => void
  appName: string
  userId: string
  currentSession: string
  onSessionChange: (sessionId: string) => void
  onNewSession: () => void
  onThemeToggle: () => void
  theme: 'light' | 'dark'
}

// Memoized session item component for better performance
const SessionItem = memo(({ 
  session, 
  isActive, 
  onClick,
  onDelete
}: { 
  session: ChatSession
  isActive: boolean
  onClick: () => void
  onDelete: (e: React.MouseEvent) => void
}) => {
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric'
    })
  }
  
  const sessionTitle = session.title || `Chat ${formatDate(session.creation_timestamp)}`
  const lastMessage = session.last_message || 'New conversation'
  
  return (
    <div 
      className={`relative group rounded-lg p-3 mb-1 cursor-pointer transition-colors ${
        isActive 
          ? 'bg-primary/10 hover:bg-primary/15' 
          : 'hover:bg-muted/50'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
          <FolderOpen className="w-4 h-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium truncate">{sessionTitle}</p>
            <span className="text-xs text-muted-foreground ml-1">
              {formatDate(session.creation_timestamp)}
            </span>
          </div>
          <p className="text-xs text-muted-foreground truncate mt-0.5">{lastMessage}</p>
        </div>
      </div>
      
      {/* Delete button - only visible on hover */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive"
          onClick={onDelete}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
});

SessionItem.displayName = 'SessionItem';

// Main Sidebar Component
export function ChatSidebar({
  isOpen,
  onClose,
  appName,
  userId,
  currentSession,
  onSessionChange,
  onNewSession,
  onThemeToggle,
  theme
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chats' | 'settings'>('chats')
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  
  // Fetch sessions
  const fetchSessions = useCallback(async () => {
    if (!appName || !userId) return
    
    setLoading(true)
    try {
      const response = await api.get(`/apps/${appName}/users/${userId}/sessions`)
      
      // Process sessions and add titles based on first message or date
      const processedSessions = await Promise.all(response.data.map(async (session: any) => {
        try {
          // Fetch first few messages to generate a title
          const sessionDetails = await api.get(
            `/apps/${appName}/users/${userId}/sessions/${session.id}`
          )
          
          let title = ''
          let lastMessage = ''
          let lastMessageTimestamp = session.creation_timestamp
          
          // Extract messages if available
          if (sessionDetails.data.events && sessionDetails.data.events.length > 0) {
            // Find first user message for title
            const firstUserMessage = sessionDetails.data.events.find(
              (e: any) => e.author === 'user' || e.content?.role === 'user'
            )
            
            if (firstUserMessage) {
              const text = firstUserMessage.text || firstUserMessage.content?.parts?.[0]?.text || ''
              // Create short title from first message
              title = text.length > 30 ? `${text.substring(0, 27)}...` : text
            }
            
            // Get last message for preview
            const lastEventWithText = [...sessionDetails.data.events].reverse().find(
              (e: any) => {
                const text = e.text || e.content?.parts?.[0]?.text
                return text && text.trim().length > 0
              }
            )
            
            if (lastEventWithText) {
              const text = lastEventWithText.text || lastEventWithText.content?.parts?.[0]?.text || ''
              lastMessage = text.length > 40 ? `${text.substring(0, 37)}...` : text
              lastMessageTimestamp = lastEventWithText.timestamp || lastEventWithText.creation_timestamp
            }
          }
          
          return {
            ...session,
            title,
            last_message: lastMessage,
            last_message_timestamp: lastMessageTimestamp
          }
        } catch (error) {
          console.error(`Error fetching details for session ${session.id}:`, error)
          return session
        }
      }))
      
      // Sort by most recent
      processedSessions.sort((a, b) => {
        const timeA = a.last_message_timestamp || a.creation_timestamp
        const timeB = b.last_message_timestamp || b.creation_timestamp
        return timeB - timeA
      })
      
      setSessions(processedSessions)
    } catch (error) {
      console.error('Error fetching sessions:', error)
    } finally {
      setLoading(false)
    }
  }, [appName, userId])
  
  // Delete session handler
  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!window.confirm('Are you sure you want to delete this chat?')) {
      return
    }
    
    try {
      await api.delete(`/apps/${appName}/users/${userId}/sessions/${sessionId}`)
      
      // If the current session was deleted, switch to the first available session or create a new one
      if (sessionId === currentSession) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId)
        if (remainingSessions.length > 0) {
          onSessionChange(remainingSessions[0].id)
        } else {
          onNewSession()
        }
      }
      
      // Update the sessions list
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }
  
  // Effect to load sessions when sidebar opens
  useEffect(() => {
    if (isOpen) {
      fetchSessions()
    }
  }, [isOpen, fetchSessions])
  
  // Reset scroll position when changing tabs
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = 0
    }
  }, [activeTab])

  const sidebarVariants = {
    hidden: { x: '-100%', opacity: 0.5 },
    visible: { x: 0, opacity: 1, transition: { duration: 0.2, ease: "easeOut" } }
  }
  
  const tabVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.3 } }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 dark:bg-black/50 z-30 lg:hidden"
            onClick={onClose}
          />
          
          {/* Sidebar */}
          <motion.div
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={sidebarVariants}
            className="fixed left-0 top-0 bottom-0 z-40 w-[280px] sm:w-[320px] bg-background border-r border-border"
            style={{ willChange: 'transform' }}
          >
            {/* Sidebar header */}
            <div className="h-14 px-4 border-b border-border flex items-center justify-between">
              <h2 className="text-lg font-semibold">Agent Cosm</h2>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={onClose}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </Button>
            </div>
            
            {/* Sidebar tabs */}
            <div className="flex border-b border-border">
              <button
                className={`flex-1 p-3 text-sm font-medium transition-colors ${
                  activeTab === 'chats'
                    ? 'bg-primary/10 text-primary border-b-2 border-primary'
                    : 'hover:bg-muted/50 text-muted-foreground'
                }`}
                onClick={() => setActiveTab('chats')}
              >
                <div className="flex items-center justify-center gap-2">
                  <Inbox className="w-4 h-4" />
                  <span>Chats</span>
                </div>
              </button>
              <button
                className={`flex-1 p-3 text-sm font-medium transition-colors ${
                  activeTab === 'settings'
                    ? 'bg-primary/10 text-primary border-b-2 border-primary'
                    : 'hover:bg-muted/50 text-muted-foreground'
                }`}
                onClick={() => setActiveTab('settings')}
              >
                <div className="flex items-center justify-center gap-2">
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </div>
              </button>
            </div>
            
            {/* Sidebar content */}
            <div className="h-[calc(100vh-8.5rem)]">
              <AnimatePresence mode="wait">
                {activeTab === 'chats' ? (
                  <motion.div
                    key="chats-tab"
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    variants={tabVariants}
                    className="h-full flex flex-col"
                  >
                    {/* New chat button */}
                    <div className="p-3 border-b border-border">
                      <Button
                        variant="default"
                        size="sm"
                        className="w-full"
                        onClick={() => {
                          onNewSession()
                          onClose()
                        }}
                      >
                        <span className="text-sm font-medium">New Chat</span>
                      </Button>
                    </div>
                    
                    {/* Sessions list */}
                    <ScrollArea className="flex-1 p-3">
                      <div ref={scrollAreaRef} className="space-y-1">
                        {loading ? (
                          <div className="py-8 flex items-center justify-center">
                            <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                          </div>
                        ) : sessions.length > 0 ? (
                          sessions.map((session) => (
                            <SessionItem
                              key={session.id}
                              session={session}
                              isActive={session.id === currentSession}
                              onClick={() => {
                                onSessionChange(session.id)
                                onClose()
                              }}
                              onDelete={(e) => handleDeleteSession(session.id, e)}
                            />
                          ))
                        ) : (
                          <div className="py-8 text-center text-muted-foreground">
                            <p>No chat sessions yet</p>
                          </div>
                        )}
                      </div>
                    </ScrollArea>
                  </motion.div>
                ) : (
                  <motion.div
                    key="settings-tab"
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    variants={tabVariants}
                    className="h-full"
                  >
                    <ScrollArea className="h-full p-3">
                      <div ref={scrollAreaRef}>
                        <div className="space-y-6">
                          {/* Profile section */}
                          <div className="space-y-3">
                            <h3 className="text-sm font-medium text-muted-foreground">Profile</h3>
                            <div className="flex items-center p-3 rounded-lg bg-muted/50">
                              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                                <User className="w-5 h-5 text-primary" />
                              </div>
                              <div className="ml-3">
                                <p className="text-sm font-medium">{userId}</p>
                                <p className="text-xs text-muted-foreground">Free Plan</p>
                              </div>
                            </div>
                          </div>
                          
                          {/* Appearance */}
                          <div className="space-y-3">
                            <h3 className="text-sm font-medium text-muted-foreground">Appearance</h3>
                            <button
                              className="flex items-center justify-between w-full p-3 rounded-lg hover:bg-muted/50 transition-colors"
                              onClick={onThemeToggle}
                            >
                              <div className="flex items-center">
                                {theme === 'dark' ? (
                                  <Moon className="w-4 h-4 mr-3" />
                                ) : (
                                  <Sun className="w-4 h-4 mr-3" />
                                )}
                                <span className="text-sm">Theme</span>
                              </div>
                              <Badge variant="outline">
                                {theme === 'dark' ? 'Dark' : 'Light'}
                              </Badge>
                            </button>
                          </div>
                          
                          {/* About */}
                          <div className="space-y-3">
                            <h3 className="text-sm font-medium text-muted-foreground">About</h3>
                            <div className="p-3 rounded-lg bg-muted/50 text-sm">
                              <p>Agent Cosm v1.0.0</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                © 2025 Cosm AI. All rights reserved.
                              </p>
                            </div>
                          </div>
                          
                          {/* Log out button */}
                          <div className="pt-4">
                            <Button
                              variant="outline"
                              className="w-full flex items-center justify-center gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
                            >
                              <LogOut className="w-4 h-4" />
                              <span>Log Out</span>
                            </Button>
                          </div>
                        </div>
                      </div>
                    </ScrollArea>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}