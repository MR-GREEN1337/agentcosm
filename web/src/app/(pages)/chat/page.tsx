'use client'

import { useState, useEffect, useRef } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AppSelector } from '@/components/AppSelector'
import { SessionManager } from '@/components/SessionManager'
import { EventsTab } from '@/components/tabs/EventsTab'
import { StateTab } from '@/components/tabs/StateTab'
import { ArtifactsTab } from '@/components/tabs/ArtifactsTab'
import { SessionsTab } from '@/components/tabs/SessionsTab'
import { EvalTab } from '@/components/tabs/EvalTab'
import { MessageInput } from '@/components/MessageInput'
import { useSSE } from '@/hooks/use-sse'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Folder, FileText, Database, GitBranch, TestTube } from 'lucide-react'
import InteractiveFolder from '@/components/InteractiveFolder'
import { api } from '@/lib/api'
import Link from 'next/link'
import { PlanetIcon } from '@/components/PlanetIcon'
import { ModeToggle } from '@/components/ThemeToggle'

const queryClient = new QueryClient()

export default function AgentDevUI() {
  const [selectedApp, setSelectedApp] = useState<string>('')
  const [currentSession, setCurrentSession] = useState<string>('')
  const [userId, setUserId] = useState<string>('default-user')
  const [activeTab, setActiveTab] = useState('events')
  const [sessionEvents, setSessionEvents] = useState<any[]>([])
  const [availableApps, setAvailableApps] = useState<string[]>([])
  const processedEventsRef = useRef<Set<string>>(new Set())

  const { sendMessage, events: sseEvents, isLoading } = useSSE(
    selectedApp && currentSession
      ? `${process.env.NEXT_PUBLIC_API_URL}/run_live?app_name=${selectedApp}&user_id=${userId}&session_id=${currentSession}&modalities=TEXT`
      : null
  )

  // Process SSE events
  useEffect(() => {
    if (sseEvents.length === 0) return
    
    // Get the latest event
    const latestEvent = sseEvents[sseEvents.length - 1]
    
    // Only process events with text content
    const text = latestEvent.content?.parts?.[0]?.text
    if (!text) return
    
    setSessionEvents(prev => {
      // If this is a streaming event, update the last message
      if (latestEvent.isStreaming || latestEvent.partial) {
        const lastIndex = prev.length - 1
        if (lastIndex >= 0 && prev[lastIndex].author === latestEvent.author) {
          // Update the last message with the new streaming content
          const updated = [...prev]
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: text,
            isStreaming: true
          }
          return updated
        }
      }
      
      // This is a new message or the final version
      const eventToAdd = {
        id: latestEvent.id || `event-${Date.now()}-${Math.random()}`,
        author: latestEvent.author || 'assistant',
        text: text,
        timestamp: latestEvent.timestamp || Date.now() / 1000,
        isStreaming: latestEvent.isStreaming || false,
        function_calls: latestEvent.actions?.function_calls,
        function_responses: latestEvent.function_responses
      }
      
      // If we were streaming and this is the final message, replace the last one
      if (!latestEvent.partial && !latestEvent.isStreaming) {
        const lastIndex = prev.length - 1
        if (lastIndex >= 0 && 
            prev[lastIndex].author === eventToAdd.author && 
            prev[lastIndex].isStreaming) {
          // Replace the streaming message with the final one
          const updated = [...prev]
          updated[lastIndex] = {
            ...eventToAdd,
            isStreaming: false
          }
          return updated
        }
      }
      
      // Check if this exact text already exists from the same author
      const exists = prev.some(e => 
        e.author === eventToAdd.author && 
        e.text === eventToAdd.text &&
        !e.isStreaming
      )
      
      if (exists) {
        console.log('Skipping duplicate in state:', eventToAdd.text)
        return prev
      }
      
      return [...prev, eventToAdd]
    })
  }, [sseEvents])

  // Fetch available apps
  useEffect(() => {
    const fetchApps = async () => {
      try {
        const response = await api.get('/list-apps')
        setAvailableApps(response.data)
      } catch (error) {
        console.error('Error fetching apps:', error)
      }
    }
    fetchApps()
  }, [])

  const handleSessionChange = async (sessionId: string) => {
    setCurrentSession(sessionId)
    setSessionEvents([])
    processedEventsRef.current.clear()
    
    // Load session events
    try {
      const response = await api.get(`/apps/${selectedApp}/users/${userId}/sessions/${sessionId}`)
      if (response.data.events) {
        setSessionEvents(response.data.events)
      }
    } catch (error) {
      console.error('Error loading session events:', error)
    }
  }

  const handleNewSession = () => {
    const newSessionId = crypto.randomUUID()
    setCurrentSession(newSessionId)
    setSessionEvents([])
    processedEventsRef.current.clear()
  }

  const handleResendMessage = async (text: string) => {
    // Create a new message with the resent text
    const message = {
      content: {
        parts: [{ text }],
        role: "user"
      }
    }
    await handleSendMessage(message)
  }

  const handleSendMessage = async (message: any) => {
    // Add user message to events immediately
    const userMessage = {
      id: `user-${Date.now()}`,
      author: 'user',
      text: message.content.parts?.[0]?.text || '',
      timestamp: Date.now() / 1000,
      isStreaming: false
    }
    
    setSessionEvents(prev => [...prev, userMessage])
    
    // Send through SSE
    await sendMessage(message)
  }

  const handleEditMessage = async (messageId: string, newText: string) => {
    // Find the message and update it
    setSessionEvents(prev => 
      prev.map(event => 
        event.id === messageId 
          ? { ...event, text: newText }
          : event
      )
    )
    
    // Optionally resend the edited message
    await handleResendMessage(newText)
  }

  // Auto-select or create session when app changes
  useEffect(() => {
    if (!selectedApp) return

    const initializeSession = async () => {
      try {
        const response = await api.get(`/apps/${selectedApp}/users/${userId}/sessions`)
        const sessions = response.data

        if (sessions.length > 0) {
          await handleSessionChange(sessions[0].id)
        } else {
          const newSessionResponse = await api.post(`/apps/${selectedApp}/users/${userId}/sessions`)
          await handleSessionChange(newSessionResponse.data.id)
        }
      } catch (error) {
        console.error('Error initializing session:', error)
      }
    }

    initializeSession()
  }, [selectedApp, userId])

  // Clear processed events when changing sessions
  useEffect(() => {
    processedEventsRef.current.clear()
  }, [currentSession])

  const appItems = availableApps.slice(0, 3).map((app) => (
    <div
      key={app}
      className="flex items-center justify-center h-full cursor-pointer hover:bg-white/10 transition-colors rounded-lg"
      onClick={(e) => {
        e.stopPropagation()
        setSelectedApp(app)
      }}
    >
      <div className="text-center p-2">
        <div className="w-8 h-8 mx-auto mb-2 rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <FileText className="w-4 h-4 text-white" />
        </div>
        <p className="text-xs font-medium text-foreground truncate max-w-[60px]">{app}</p>
      </div>
    </div>
  ))

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col h-screen bg-background overflow-hidden">
        {/* Top Navigation Bar */}
        <header className="bg-card border-b border-border px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="flex items-center gap-2">
                <PlanetIcon />
                <h1 className="text-[1.3rem] font-normal tracking-[0.02em] text-foreground">agent cosm</h1>
              </Link>
              <AppSelector value={selectedApp} onChange={setSelectedApp} />
            </div>
            <div className="flex items-center gap-4">
              {selectedApp && (
                <SessionManager
                  appName={selectedApp}
                  userId={userId}
                  currentSession={currentSession}
                  onSessionChange={handleSessionChange}
                  onNewSession={handleNewSession}
                />
              )}
              <ModeToggle />
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {selectedApp && currentSession ? (
            <div className="flex-1 flex h-full">
              {/* Left Sidebar with Tabs */}
              <div className="w-60 bg-secondary/30 border-r border-border flex-shrink-0">
                <Tabs
                  value={activeTab}
                  onValueChange={setActiveTab}
                  orientation="vertical"
                  className="h-full"
                >
                  <TabsList className="flex flex-col w-full bg-transparent p-2 h-auto">
                    <TabsTrigger
                      value="events"
                      className="w-full justify-start text-left py-3 px-4 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg mb-1"
                    >
                      <Folder className="w-4 h-4 mr-3" />
                      Events
                    </TabsTrigger>
                    <TabsTrigger
                      value="state"
                      className="w-full justify-start text-left py-3 px-4 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg mb-1"
                    >
                      <FileText className="w-4 h-4 mr-3" />
                      State
                    </TabsTrigger>
                    <TabsTrigger
                      value="artifacts"
                      className="w-full justify-start text-left py-3 px-4 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg mb-1"
                    >
                      <Database className="w-4 h-4 mr-3" />
                      Artifacts
                    </TabsTrigger>
                    <TabsTrigger
                      value="sessions"
                      className="w-full justify-start text-left py-3 px-4 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg mb-1"
                    >
                      <GitBranch className="w-4 h-4 mr-3" />
                      Sessions
                    </TabsTrigger>
                    <TabsTrigger
                      value="eval"
                      className="w-full justify-start text-left py-3 px-4 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg mb-1"
                    >
                      <TestTube className="w-4 h-4 mr-3" />
                      Eval
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col bg-background min-h-0">
                {activeTab === 'events' ? (
                  <>
                    <div className="flex-1 overflow-hidden">
                      <EventsTab
                        appName={selectedApp}
                        userId={userId}
                        sessionId={currentSession}
                        events={sessionEvents}
                        onResendMessage={handleResendMessage}
                        onEditMessage={handleEditMessage}
                      />
                    </div>
                    <div className="flex-shrink-0">
                      <MessageInput
                        onSendMessage={handleSendMessage}
                        disabled={false}
                      />
                    </div>
                  </>
                ) : (
                  <div className="flex-1 overflow-hidden">
                    {activeTab === 'state' && (
                      <StateTab
                        appName={selectedApp}
                        userId={userId}
                        sessionId={currentSession}
                      />
                    )}
                    {activeTab === 'artifacts' && (
                      <ArtifactsTab
                        appName={selectedApp}
                        userId={userId}
                        sessionId={currentSession}
                      />
                    )}
                    {activeTab === 'sessions' && (
                      <SessionsTab
                        appName={selectedApp}
                        userId={userId}
                        currentSession={currentSession}
                      />
                    )}
                    {activeTab === 'eval' && (
                      <EvalTab
                        appName={selectedApp}
                        userId={userId}
                      />
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center flex flex-col items-center">
                <div className="pb-20">
                  <InteractiveFolder
                    color="#3b82f6"
                    scale={2}
                    items={appItems}
                  />
                </div>
                <h2 className="text-2xl font-medium text-foreground mb-2">Welcome to agent cosm</h2>
                <p className="text-muted-foreground text-lg max-w-md">
                  {!selectedApp
                    ? 'Select an app from the folder to get started'
                    : 'Loading session...'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </QueryClientProvider>
  )
}