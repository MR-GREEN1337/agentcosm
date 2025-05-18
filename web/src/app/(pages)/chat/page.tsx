'use client'

import { useState, useEffect, useRef } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
import { api } from '@/lib/api'
import Link from 'next/link'
import { PlanetIcon } from '@/components/PlanetIcon'
import { ModeToggle } from '@/components/ThemeToggle'

const queryClient = new QueryClient()

export default function AgentDevUI() {
  const [selectedApp, setSelectedApp] = useState<string>('cosm') // Default to "cosm"
  const [currentSession, setCurrentSession] = useState<string>('')
  const [userId, setUserId] = useState<string>('default-user')
  const [activeTab, setActiveTab] = useState('events')
  const [sessionEvents, setSessionEvents] = useState<any[]>([])
  const processedEventsRef = useRef<Set<string>>(new Set())
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const eventsTabRef = useRef<{ scrollToBottom: () => void }>(null)

  const { sendMessage, events: sseEvents, isLoading } = useSSE(
    selectedApp && currentSession
      ? `${process.env.NEXT_PUBLIC_API_URL}/run_live?app_name=${selectedApp}&user_id=${userId}&session_id=${currentSession}&modalities=TEXT`
      : null
  )

  // Auto-scroll function
  const scrollToBottom = () => {
    if (eventsTabRef.current?.scrollToBottom) {
      eventsTabRef.current.scrollToBottom()
    }
  }

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

  // Auto-scroll when session events change
  useEffect(() => {
    if (sessionEvents.length > 0) {
      scrollToBottom()
    }
  }, [sessionEvents])

  const handleSessionChange = async (sessionId: string) => {
    setCurrentSession(sessionId)
    setSessionEvents([])
    processedEventsRef.current.clear()
    
    // Load session events
    try {
      const response = await api.get(`/apps/${selectedApp}/users/${userId}/sessions/${sessionId}`)
      if (response.data.events) {
        setSessionEvents(response.data.events)
        // Scroll to bottom after loading session events
        setTimeout(scrollToBottom, 100)
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
    
    // Scroll to bottom after adding user message
    setTimeout(scrollToBottom, 50)
    
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

  // Initialize session on component mount
  useEffect(() => {
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
        // If there's an error, create a new session anyway
        handleNewSession()
      }
    }

    initializeSession()
  }, [userId]) // Only depends on userId now, not selectedApp

  // Clear processed events when changing sessions
  useEffect(() => {
    processedEventsRef.current.clear()
  }, [currentSession])

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col h-screen bg-background overflow-hidden">
        {/* Top Navigation Bar */}
        <header className="bg-card border-b border-border px-3 sm:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 sm:gap-6">
              <Link href="/" className="flex items-center gap-2">
                <PlanetIcon />
                <h1 className="text-lg sm:text-[1.3rem] font-normal tracking-[0.02em] text-foreground hidden sm:block">agent cosm</h1>
              </Link>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <SessionManager
                appName={selectedApp}
                userId={userId}
                currentSession={currentSession}
                onSessionChange={handleSessionChange}
                onNewSession={handleNewSession}
              />
              <ModeToggle />
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
            <div className="flex-1 flex h-full">
              {/* Left Sidebar with Tabs */}
              <div className="w-14 md:w-16 bg-secondary/30 border-r border-border flex-shrink-0">
                <Tabs
                  value={activeTab}
                  onValueChange={setActiveTab}
                  orientation="vertical"
                  className="h-full"
                >
                  <TabsList className="flex flex-col w-full bg-transparent p-2 h-auto gap-2">
                    <TabsTrigger
                      value="events"
                      className="w-full justify-center p-3 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg"
                      title="Events"
                    >
                      <Folder className="w-5 h-5" />
                    </TabsTrigger>
                    <TabsTrigger
                      value="state"
                      className="w-full justify-center p-3 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg"
                      title="State"
                    >
                      <FileText className="w-5 h-5" />
                    </TabsTrigger>
                    <TabsTrigger
                      value="artifacts"
                      className="w-full justify-center p-3 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg"
                      title="Artifacts"
                    >
                      <Database className="w-5 h-5" />
                    </TabsTrigger>
                    <TabsTrigger
                      value="sessions"
                      className="w-full justify-center p-3 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg"
                      title="Sessions"
                    >
                      <GitBranch className="w-5 h-5" />
                    </TabsTrigger>
                    <TabsTrigger
                      value="eval"
                      className="w-full justify-center p-3 text-muted-foreground hover:text-foreground data-[state=active]:bg-secondary data-[state=active]:text-foreground rounded-lg"
                      title="Eval"
                    >
                      <TestTube className="w-5 h-5" />
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col bg-transparent min-h-0">
                {activeTab === 'events' ? (
                  <>
                    <div className="flex-1 overflow-hidden" ref={scrollContainerRef}>
                      <EventsTab
                        ref={eventsTabRef as any}
                        appName={selectedApp}
                        userId={userId}
                        sessionId={currentSession}
                        events={sessionEvents}
                        onResendMessage={handleResendMessage}
                        onEditMessage={handleEditMessage}
                      />
                    </div>
                    <div className="flex-shrink-0 bg-transparent">
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
        </div>
      </div>
    </QueryClientProvider>
  )
}