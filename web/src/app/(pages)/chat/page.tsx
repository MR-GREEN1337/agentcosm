'use client'

import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AppSelector } from '@/components/AppSelector'
import { SessionManager } from '@/components/SessionManager'
import { EventsTab } from '@/components/tabs/EventsTab'
import { StateTab } from '@/components/tabs/StateTab'
import { ArtifactsTab } from '@/components/tabs/ArtifactsTab'
import { SessionsTab } from '@/components/tabs/SessionsTab'
import { EvalTab } from '@/components/tabs/EvalTab'
import { MessageInput } from '@/components/MessageInput'
import { useWebSocket } from '@/hooks/useWebsocket'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Folder, FileText, Database, GitBranch, TestTube } from 'lucide-react'
import InteractiveFolder from '@/components/InteractiveFolder'
import { api } from '@/lib/api'
import Link from 'next/link'
import { PlanetIcon } from '@/components/PlanetIcon'

const queryClient = new QueryClient()

export default function AgentDevUI() {
  const [selectedApp, setSelectedApp] = useState<string>('')
  const [currentSession, setCurrentSession] = useState<string>('')
  const [userId, setUserId] = useState<string>('default-user')
  const [activeTab, setActiveTab] = useState('events')
  const [sessionEvents, setSessionEvents] = useState<any[]>([])
  const [availableApps, setAvailableApps] = useState<string[]>([])

  const { sendMessage, events: wsEvents, isConnected } = useWebSocket(
    selectedApp && currentSession
      ? `${process.env.NEXT_PUBLIC_WS_URL}/run_live?app_name=${selectedApp}&user_id=${userId}&session_id=${currentSession}`
      : null
  )

  useEffect(() => {
    if (wsEvents.length > 0) {
      setSessionEvents(prev => [...prev, ...wsEvents])
    }
  }, [wsEvents])

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

  const handleSessionChange = (sessionId: string) => {
    setCurrentSession(sessionId)
    setSessionEvents([])
  }

  const handleNewSession = () => {
    const newSessionId = crypto.randomUUID()
    setCurrentSession(newSessionId)
    setSessionEvents([])
  }

  // Auto-select session when app changes
  useEffect(() => {
    if (!selectedApp) return

    const selectOrCreateSession = async () => {
      try {
        const response = await api.get(`/apps/${selectedApp}/users/${userId}/sessions`)
        const sessions = response.data

        if (sessions.length > 0) {
          // Select the most recent session (first in the list)
          setCurrentSession(sessions[0].id)
        } else {
          // Create a new session if none exist
          const newSessionResponse = await api.post(`/apps/${selectedApp}/users/${userId}/sessions`)
          setCurrentSession(newSessionResponse.data.id)
        }
      } catch (error) {
        console.error('Error handling session selection:', error)
        // Fallback: create a new session
        try {
          const newSessionResponse = await api.post(`/apps/${selectedApp}/users/${userId}/sessions`)
          setCurrentSession(newSessionResponse.data.id)
        } catch (createError) {
          console.error('Error creating new session:', createError)
        }
      }
    }

    selectOrCreateSession()
  }, [selectedApp, userId])

  // Create app items for the folder
  const appItems = availableApps.slice(0, 3).map((app, index) => (
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
        <p className="text-xs font-medium text-gray-700 truncate max-w-[60px]">{app}</p>
      </div>
    </div>
  ))

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col h-screen bg-[#0e0e10]">
        {/* Top Navigation Bar */}
        <header className="bg-[#1a1a1f] border-b border-[#2a2a30] px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-6">
                <Link href="/" className="flex items-center gap-2">
                  <PlanetIcon />
                  <h1 className="text-[1.3rem] font-normal tracking-[0.02em] text-white">agent cosm</h1>
                </Link>
              </div>
              <AppSelector value={selectedApp} onChange={setSelectedApp} />
            </div>
            {selectedApp && (
              <SessionManager
                appName={selectedApp}
                userId={userId}
                currentSession={currentSession}
                onSessionChange={handleSessionChange}
                onNewSession={handleNewSession}
              />
            )}
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {selectedApp && currentSession ? (
            <div className="flex-1 flex">
              {/* Left Sidebar with Tabs */}
              <div className="w-60 bg-[#17171b] border-r border-[#2a2a30]">
                <Tabs
                  value={activeTab}
                  onValueChange={setActiveTab}
                  orientation="vertical"
                  className="h-full"
                >
                  <TabsList className="flex flex-col w-full bg-transparent p-2 h-auto">
                    <TabsTrigger
                      value="events"
                      className="w-full justify-start text-left py-3 px-4 text-[#a0a0a8] hover:text-white data-[state=active]:bg-[#1f1f24] data-[state=active]:text-white rounded-lg mb-1"
                    >
                      <Folder className="w-4 h-4 mr-3" />
                      Events
                    </TabsTrigger>
                    <TabsTrigger
                      value="state"
                      className="w-full justify-start text-left py-3 px-4 text-[#a0a0a8] hover:text-white data-[state=active]:bg-[#1f1f24] data-[state=active]:text-white rounded-lg mb-1"
                    >
                      <FileText className="w-4 h-4 mr-3" />
                      State
                    </TabsTrigger>
                    <TabsTrigger
                      value="artifacts"
                      className="w-full justify-start text-left py-3 px-4 text-[#a0a0a8] hover:text-white data-[state=active]:bg-[#1f1f24] data-[state=active]:text-white rounded-lg mb-1"
                    >
                      <Database className="w-4 h-4 mr-3" />
                      Artifacts
                    </TabsTrigger>
                    <TabsTrigger
                      value="sessions"
                      className="w-full justify-start text-left py-3 px-4 text-[#a0a0a8] hover:text-white data-[state=active]:bg-[#1f1f24] data-[state=active]:text-white rounded-lg mb-1"
                    >
                      <GitBranch className="w-4 h-4 mr-3" />
                      Sessions
                    </TabsTrigger>
                    <TabsTrigger
                      value="eval"
                      className="w-full justify-start text-left py-3 px-4 text-[#a0a0a8] hover:text-white data-[state=active]:bg-[#1f1f24] data-[state=active]:text-white rounded-lg mb-1"
                    >
                      <TestTube className="w-4 h-4 mr-3" />
                      Eval
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col bg-[#0e0e10]">
                {activeTab === 'events' ? (
                  <>
                    <EventsTab
                      appName={selectedApp}
                      userId={userId}
                      sessionId={currentSession}
                      events={sessionEvents}
                    />
                    <MessageInput
                      onSendMessage={sendMessage}
                      disabled={!isConnected}
                    />
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
                <h2 className="text-2xl font-medium text-white mb-2">Welcome to agent cosm</h2>
                <p className="text-[#a0a0a8] text-lg max-w-md">
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