'use client';

import { useState, useEffect, useRef } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SessionManager } from '@/components/SessionManager';
import { EventsTab } from '@/components/tabs/EventsTab';
import { StateTab } from '@/components/tabs/StateTab';
import { ArtifactsTab } from '@/components/tabs/ArtifactsTab';
import { SessionsTab } from '@/components/tabs/SessionsTab';
import { EvalTab } from '@/components/tabs/EvalTab';
import { MessageInput } from '@/components/MessageInput';
import { useSSE } from '@/hooks/use-sse';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Folder, FileText, Database, GitBranch, TestTube } from 'lucide-react';
import { api, API_URL } from '@/lib/api';
import Link from 'next/link';
import { PlanetIcon } from '@/components/PlanetIcon';
import { ModeToggle } from '@/components/ThemeToggle';
import { cn, RENDERER_SERVICE_URL } from '@/lib/utils';

// Import Shadcn Tooltip components
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const queryClient = new QueryClient();

export default function AgentDevUI() {
  const [selectedApp, setSelectedApp] = useState<string>('cosm');
  const [currentSession, setCurrentSession] = useState<string>('');
  const [userId, setUserId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('events');
  const [sessionEvents, setSessionEvents] = useState<any[]>([]);
  const processedEventsRef = useRef<Set<string>>(new Set());
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const eventsTabRef = useRef<{ scrollToBottom: () => void }>(null);
  const initialBusinessQuerySent = useRef<boolean>(false);
  const [lastAiResponse, setLastAiResponse] = useState('');

  const {
    sendMessage,
    events: sseEvents,
    isLoading,
  } = useSSE(
    selectedApp && currentSession && userId
      ? `${API_URL}/run_live?app_name=${selectedApp}&user_id=${userId}&session_id=${currentSession}&modalities=TEXT`
      : null,
  );

  // Auto-scroll function
  const scrollToBottom = () => {
    if (eventsTabRef.current?.scrollToBottom) {
      eventsTabRef.current.scrollToBottom();
    }
  };

  useEffect(() => {
    if (!localStorage.getItem('userId')) {
      localStorage.setItem('userId', crypto.randomUUID());
    }
    setUserId(localStorage.getItem('userId'));
  }, []);

  // 🔥 FIXED: Process SSE events with proper deduplication
  useEffect(() => {
    if (sseEvents.length === 0) return;

    const latestEvent = sseEvents[sseEvents.length - 1];
    const text = latestEvent.content?.parts?.[0]?.text;
    if (!text) return;

    // Create a unique key for this event
    const eventKey = `${latestEvent.author}-${latestEvent.timestamp || Date.now()}-${text.substring(0, 50)}`;

    // Skip if we've already processed this exact event
    if (processedEventsRef.current.has(eventKey) && !latestEvent.isStreaming) {
      console.log('Skipping already processed event:', eventKey);
      return;
    }

    setSessionEvents((prev) => {
      // Handle streaming updates
      if (latestEvent.isStreaming || latestEvent.partial) {
        const lastIndex = prev.length - 1;
        if (
          lastIndex >= 0 &&
          prev[lastIndex].author === latestEvent.author &&
          prev[lastIndex].isStreaming
        ) {
          const updated = [...prev];
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: text,
            isStreaming: true,
          };
          return updated;
        }
      }

      // Create event object
      const eventToAdd = {
        id: latestEvent.id || `event-${Date.now()}-${Math.random()}`,
        author: latestEvent.author || 'assistant',
        text: text,
        timestamp: latestEvent.timestamp || Date.now() / 1000,
        isStreaming: latestEvent.isStreaming || false,
        function_calls: latestEvent.actions?.function_calls,
        function_responses: latestEvent.function_responses,
      };

      // Handle final message (not streaming)
      if (!latestEvent.partial && !latestEvent.isStreaming) {
        // Mark this event as processed
        processedEventsRef.current.add(eventKey);

        // Update TTS state for AI messages
        if (latestEvent.author === 'liminal_market_opportunity_coordinator') {
          setTimeout(() => {
            console.log(
              '🎵 Setting TTS message:',
              text.substring(0, 50) + '...',
            );
            setLastAiResponse(text);
          }, 0);
        }

        // Replace streaming message with final version
        const lastIndex = prev.length - 1;
        if (
          lastIndex >= 0 &&
          prev[lastIndex].author === eventToAdd.author &&
          prev[lastIndex].isStreaming
        ) {
          const updated = [...prev];
          updated[lastIndex] = {
            ...eventToAdd,
            isStreaming: false,
          };
          return updated;
        }
      }

      // Check for exact duplicates before adding
      const isDuplicate = prev.some(
        (e) =>
          e.author === eventToAdd.author &&
          e.text === eventToAdd.text &&
          !e.isStreaming &&
          Math.abs(e.timestamp - eventToAdd.timestamp) < 2, // Within 2 seconds
      );

      if (isDuplicate) {
        console.log(
          'Skipping duplicate event in state:',
          eventToAdd.text.substring(0, 50),
        );
        return prev;
      }

      return [...prev, eventToAdd];
    });
  }, [sseEvents]);

  // Auto-scroll when session events change
  useEffect(() => {
    if (sessionEvents.length > 0) {
      scrollToBottom();
    }
  }, [sessionEvents]);

  // Parse query parameter and create a new session if there's a query
  useEffect(() => {
    const checkAndHandleQueryParam = async () => {
      if (userId && !initialBusinessQuerySent.current) {
        const urlParams = new URLSearchParams(window.location.search);
        const queryParam = urlParams.get('query');

        if (queryParam) {
          initialBusinessQuerySent.current = true;

          try {
            const newSessionResponse = await api.post(
              `/apps/${selectedApp}/users/${userId}/sessions`,
            );
            const newSessionId = newSessionResponse.data.id;

            setCurrentSession(newSessionId);

            setTimeout(async () => {
              const message = {
                content: {
                  parts: [{ text: queryParam }],
                  role: 'user',
                },
              };

              const userMessage = {
                id: `user-${Date.now()}`,
                author: 'user',
                text: queryParam,
                timestamp: Date.now() / 1000,
                isStreaming: false,
              };

              setSessionEvents([userMessage]);

              if (sendMessage) {
                await sendMessage(message);
              }

              const newUrl = window.location.pathname;
              window.history.replaceState({}, document.title, newUrl);
            }, 500);
          } catch (error) {
            console.error('Error creating new session for query:', error);
          }
        }
      }
    };

    checkAndHandleQueryParam();
  }, [userId, selectedApp, sendMessage]);

  const handleSessionChange = async (sessionId: string) => {
    setCurrentSession(sessionId);
    setSessionEvents([]);
    processedEventsRef.current.clear(); // 🔥 IMPORTANT: Clear processed events tracker
    setLastAiResponse('');

    try {
      const response = await api.get(
        `/apps/${selectedApp}/users/${userId}/sessions/${sessionId}`,
      );
      if (response.data.events) {
        const events = response.data.events;

        // 🔥 FIXED: Mark loaded events as processed to prevent duplicates
        events.forEach((event: any) => {
          if (event.text) {
            const eventKey = `${event.author}-${event.timestamp}-${event.text.substring(0, 50)}`;
            processedEventsRef.current.add(eventKey);
          }
        });

        setSessionEvents(events);

        // Find the last complete AI message
        let lastAiMessage = '';
        for (let i = events.length - 1; i >= 0; i--) {
          const event = events[i];
          if (
            event.author === 'liminal_market_opportunity_coordinator' &&
            event.text &&
            !event.isStreaming
          ) {
            lastAiMessage = event.text;
            break;
          }
        }

        setTimeout(() => {
          if (lastAiMessage) {
            console.log(
              '🎵 Setting last AI message from session:',
              lastAiMessage.substring(0, 50) + '...',
            );
            setLastAiResponse(lastAiMessage);
          }
        }, 100);

        setTimeout(scrollToBottom, 100);
      }
    } catch (error) {
      console.error('Error loading session events:', error);
    }
  };

  const handleNewSession = () => {
    const newSessionId = crypto.randomUUID();
    setCurrentSession(newSessionId);
    setSessionEvents([]);
    processedEventsRef.current.clear(); // 🔥 IMPORTANT: Clear processed events tracker
    setLastAiResponse('');
  };

  const handleResendMessage = async (text: string) => {
    const message = {
      content: {
        parts: [{ text }],
        role: 'user',
      },
    };
    await handleSendMessage(message);
  };

  const handleSendMessage = async (message: any) => {
    console.log('🔥 handleSendMessage called with:', message);

    const userMessage = {
      id: `user-${Date.now()}`,
      author: 'user',
      text: message.content.parts?.[0]?.text || '',
      timestamp: Date.now() / 1000,
      isStreaming: false,
    };

    console.log('👤 Adding user message to UI:', userMessage);
    setSessionEvents((prev) => [...prev, userMessage]);

    setTimeout(scrollToBottom, 50);

    console.log('🤖 Calling sendMessage to trigger AI response...');

    try {
      await sendMessage(message);
      console.log('✅ sendMessage completed - AI should respond now');
    } catch (error) {
      console.error('❌ sendMessage failed:', error);
    }
  };

  const handleEditMessage = async (messageId: string, newText: string) => {
    setSessionEvents((prev) =>
      prev.map((event) =>
        event.id === messageId ? { ...event, text: newText } : event,
      ),
    );

    await handleResendMessage(newText);
  };

  // Initialize session on component mount
  useEffect(() => {
    const initializeSession = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const queryParam = urlParams.get('query');

      if (queryParam) {
        return;
      }

      try {
        const response = await api.get(
          `/apps/${selectedApp}/users/${userId}/sessions`,
        );
        const sessions = response.data;

        if (sessions.length > 0) {
          await handleSessionChange(sessions[0].id);
        } else {
          const newSessionResponse = await api.post(
            `/apps/${selectedApp}/users/${userId}/sessions`,
          );
          await handleSessionChange(newSessionResponse.data.id);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        handleNewSession();
      }
    };

    if (userId) {
      initializeSession();
    }
  }, [userId, selectedApp]);

  // 🔥 FIXED: Clear processed events when changing sessions
  useEffect(() => {
    processedEventsRef.current.clear();
  }, [currentSession]);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={300}>
        <div className="flex flex-col h-screen overflow-hidden">
          {/* Gradient background */}
          <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5 pointer-events-none" />

          {/* Subtle animated particles */}
          <div className="fixed inset-0 opacity-30 pointer-events-none">
            <div className="particles-container">
              {/* Particles will be rendered via CSS */}
            </div>
          </div>
          {/* Top Navigation Bar */}
          <header className="relative bg-background/60 backdrop-blur-md border-b border-primary/10 px-3 sm:px-6 py-3 shadow-sm z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 sm:gap-6">
                <Link href="/" className="flex items-center gap-2 group">
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 rounded-full blur-md group-hover:blur-lg transition-all duration-500 opacity-70 group-hover:opacity-100 scale-75 group-hover:scale-110"></div>
                    {/*@ts-ignore*/}
                    <PlanetIcon className="relative z-10 transition-transform duration-500 group-hover:rotate-[15deg]" />
                  </div>
                  <h1 className="text-lg sm:text-[1.3rem] font-normal tracking-[0.02em] text-foreground hidden sm:block">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80 font-medium">
                      agent
                    </span>{' '}
                    cosm
                  </h1>
                </Link>

                <Link
                  href={`${RENDERER_SERVICE_URL}/dashboard`}
                  className="text-xs text-muted-foreground/60 hover:text-muted-foreground transition-colors duration-200 hidden md:inline-flex items-center gap-1 px-2 py-1 rounded-md hover:bg-primary/5"
                  title="View deployed landing pages"
                >
                  <span className="w-1 h-1 rounded-full bg-current opacity-50 animate-pulse"></span>
                  view deployed landing pages & startup pitches
                </Link>
              </div>
              <div className="flex items-center gap-2 sm:gap-4">
                <SessionManager
                  appName={selectedApp}
                  userId={userId as string}
                  currentSession={currentSession}
                  onSessionChange={handleSessionChange}
                  onNewSession={handleNewSession}
                />
                <ModeToggle />
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <div className="flex-1 flex overflow-hidden relative">
            {/* Left Sidebar with Tabs */}
            <div className="w-14 md:w-16 bg-background/40 backdrop-blur-md border-r border-primary/10 flex-shrink-0 relative z-10 shadow-sm">
              <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-secondary/5 opacity-50 pointer-events-none"></div>
              <Tabs
                value={activeTab}
                onValueChange={setActiveTab}
                orientation="vertical"
                className="h-full relative z-10"
              >
                <TabsList className="flex flex-col w-full bg-transparent p-2 h-auto gap-2">
                  {/* Events Tab with Tooltip */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <TabsTrigger
                        value="events"
                        className={cn(
                          'w-full justify-center p-3 rounded-xl transition-all duration-300',
                          'text-muted-foreground hover:text-foreground',
                          'hover:bg-primary/10 hover:shadow-sm',
                          'data-[state=active]:bg-primary/15 data-[state=active]:text-primary',
                          'data-[state=active]:shadow-md data-[state=active]:shadow-primary/5',
                        )}
                      >
                        <Folder className="w-5 h-5" />
                      </TabsTrigger>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="bg-background/80 backdrop-blur-sm border-primary/10 text-sm font-medium text-black dark:text-white"
                    >
                      Events
                    </TooltipContent>
                  </Tooltip>

                  {/* State Tab with Tooltip */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <TabsTrigger
                        value="state"
                        className={cn(
                          'w-full justify-center p-3 rounded-xl transition-all duration-300',
                          'text-muted-foreground hover:text-foreground',
                          'hover:bg-primary/10 hover:shadow-sm',
                          'data-[state=active]:bg-primary/15 data-[state=active]:text-primary',
                          'data-[state=active]:shadow-md data-[state=active]:shadow-primary/5',
                        )}
                      >
                        <FileText className="w-5 h-5" />
                      </TabsTrigger>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="bg-background/80 backdrop-blur-sm border-primary/10 text-sm font-medium text-black dark:text-white"
                    >
                      State
                    </TooltipContent>
                  </Tooltip>

                  {/* Artifacts Tab with Tooltip */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <TabsTrigger
                        value="artifacts"
                        className={cn(
                          'w-full justify-center p-3 rounded-xl transition-all duration-300',
                          'text-muted-foreground hover:text-foreground',
                          'hover:bg-primary/10 hover:shadow-sm',
                          'data-[state=active]:bg-primary/15 data-[state=active]:text-primary',
                          'data-[state=active]:shadow-md data-[state=active]:shadow-primary/5',
                        )}
                      >
                        <Database className="w-5 h-5" />
                      </TabsTrigger>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="bg-background/80 backdrop-blur-sm border-primary/10 text-sm font-medium text-black dark:text-white"
                    >
                      Artifacts
                    </TooltipContent>
                  </Tooltip>

                  {/* Sessions Tab with Tooltip */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <TabsTrigger
                        value="sessions"
                        className={cn(
                          'w-full justify-center p-3 rounded-xl transition-all duration-300',
                          'text-muted-foreground hover:text-foreground',
                          'hover:bg-primary/10 hover:shadow-sm',
                          'data-[state=active]:bg-primary/15 data-[state=active]:text-primary',
                          'data-[state=active]:shadow-md data-[state=active]:shadow-primary/5',
                        )}
                      >
                        <GitBranch className="w-5 h-5" />
                      </TabsTrigger>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="bg-background/80 backdrop-blur-sm border-primary/10 text-sm font-medium text-black dark:text-white"
                    >
                      Sessions
                    </TooltipContent>
                  </Tooltip>

                  {/* Eval Tab with Tooltip */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <TabsTrigger
                        value="eval"
                        className={cn(
                          'w-full justify-center p-3 rounded-xl transition-all duration-300',
                          'text-muted-foreground hover:text-foreground',
                          'hover:bg-primary/10 hover:shadow-sm',
                          'data-[state=active]:bg-primary/15 data-[state=active]:text-primary',
                          'data-[state=active]:shadow-md data-[state=active]:shadow-primary/5',
                        )}
                      >
                        <TestTube className="w-5 h-5" />
                      </TabsTrigger>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="bg-background/80 backdrop-blur-sm border-primary/10 text-sm font-medium text-black dark:text-white"
                    >
                      Evaluation
                    </TooltipContent>
                  </Tooltip>
                </TabsList>
              </Tabs>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-h-0 relative">
              {/* Gradient overlay for content area */}
              <div className="absolute inset-0 bg-gradient-to-br from-background/30 via-background/10 to-background/20 pointer-events-none"></div>

              {activeTab === 'events' ? (
                <>
                  <div
                    className="flex-1 overflow-hidden"
                    ref={scrollContainerRef}
                  >
                    <div className="h-full custom-scrollbar pb-4">
                      <EventsTab
                        ref={eventsTabRef as any}
                        appName={selectedApp}
                        userId={userId as string}
                        sessionId={currentSession}
                        events={sessionEvents}
                        onResendMessage={handleResendMessage}
                        onEditMessage={handleEditMessage}
                        isLoading={isLoading}
                      />
                    </div>
                  </div>

                  <div className="flex-shrink-0 bg-transparent z-10">
                    <MessageInput
                      onSendMessage={handleSendMessage}
                      disabled={false}
                      lastAiMessage={lastAiResponse}
                      sendMessage={sendMessage}
                      isLoading={isLoading}
                    />
                  </div>
                </>
              ) : (
                <div className="flex-1 overflow-hidden relative">
                  <div className="absolute inset-0 bg-background/40 backdrop-blur-sm pointer-events-none"></div>
                  <div className="relative z-10 h-full custom-scrollbar">
                    {activeTab === 'state' && (
                      <StateTab
                        appName={selectedApp}
                        userId={userId as string}
                        sessionId={currentSession}
                      />
                    )}
                    {activeTab === 'artifacts' && (
                      <ArtifactsTab
                        appName={selectedApp}
                        userId={userId as string}
                        sessionId={currentSession}
                      />
                    )}
                    {activeTab === 'sessions' && (
                      <SessionsTab
                        appName={selectedApp}
                        userId={userId as string}
                        currentSession={currentSession}
                        onSessionChange={handleSessionChange}
                      />
                    )}
                    {activeTab === 'eval' && (
                      <EvalTab
                        appName={selectedApp}
                        userId={userId as string}
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Global styles for animations and custom elements */}
        <style jsx global>{`
          /* Custom scrollbar styling */
          .custom-scrollbar {
            scrollbar-width: thin;
            scrollbar-color: rgba(var(--primary-rgb), 0.3) transparent;
          }

          .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
          }

          .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
          }

          .custom-scrollbar::-webkit-scrollbar-thumb {
            background-color: rgba(var(--primary-rgb), 0.2);
            border-radius: 10px;
            border: 2px solid transparent;
          }

          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background-color: rgba(var(--primary-rgb), 0.4);
          }

          /* Floating animation for message bubbles */
          @keyframes float {
            0% {
              transform: translateY(0px);
            }
            50% {
              transform: translateY(-8px);
            }
            100% {
              transform: translateY(0px);
            }
          }

          /* Subtle particle animation */
          .particles-container {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
          }

          .particles-container::before,
          .particles-container::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background-image:
              radial-gradient(
                circle at 25% 25%,
                rgba(var(--primary-rgb), 0.1) 1px,
                transparent 1px
              ),
              radial-gradient(
                circle at 75% 75%,
                rgba(var(--secondary-rgb), 0.1) 1px,
                transparent 1px
              );
            background-size: 40px 40px;
            background-position: 0 0;
            animation: particlesDrift 60s linear infinite;
            opacity: 0.5;
          }

          .particles-container::after {
            background-size: 30px 30px;
            animation-duration: 90s;
            animation-direction: reverse;
            opacity: 0.3;
          }

          @keyframes particlesDrift {
            0% {
              background-position: 0 0;
            }
            100% {
              background-position: 100px 100px;
            }
          }

          /* Message bubble styling enhancements */
          /* These styles will be applied to the EventsTab component's message bubbles */
          :root {
            --user-message-bg: rgba(var(--primary-rgb), 0.1);
            --user-message-border: rgba(var(--primary-rgb), 0.2);
            --assistant-message-bg: rgba(var(--background-rgb), 0.7);
            --assistant-message-border: rgba(var(--border-rgb), 0.3);
          }
        `}</style>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
