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
import { api } from '@/lib/api';
import Link from 'next/link';
import { PlanetIcon } from '@/components/PlanetIcon';
import { ModeToggle } from '@/components/ThemeToggle';
import { cn } from '@/lib/utils';

// Import Shadcn Tooltip components
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const queryClient = new QueryClient();

export default function AgentDevUI() {
  const [selectedApp, setSelectedApp] = useState<string>('cosm'); // Default to "cosm"
  const [currentSession, setCurrentSession] = useState<string>('');
  const [userId, setUserId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('events');
  const [sessionEvents, setSessionEvents] = useState<any[]>([]);
  const processedEventsRef = useRef<Set<string>>(new Set());
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const eventsTabRef = useRef<{ scrollToBottom: () => void }>(null);
  const initialBusinessQuerySent = useRef<boolean>(false);
  const [lastAiResponse, setLastAiResponse] = useState('');

  // Add new ref to track the most recent complete AI message
  const latestCompleteAiMessageRef = useRef<string>('');

  const {
    sendMessage,
    events: sseEvents,
    isLoading,
  } = useSSE(
    selectedApp && currentSession && userId
      ? `${process.env.NEXT_PUBLIC_API_URL}/run_live?app_name=${selectedApp}&user_id=${userId}&session_id=${currentSession}&modalities=TEXT`
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

  // Process SSE events
  useEffect(() => {
    if (sseEvents.length === 0) return;

    // Get the latest event
    const latestEvent = sseEvents[sseEvents.length - 1];

    // Only process events with text content
    const text = latestEvent.content?.parts?.[0]?.text;
    if (!text) return;

    setSessionEvents((prev) => {
      // If this is a streaming event, update the last message
      if (latestEvent.isStreaming || latestEvent.partial) {
        const lastIndex = prev.length - 1;
        if (lastIndex >= 0 && prev[lastIndex].author === latestEvent.author) {
          // Update the last message with the new streaming content
          const updated = [...prev];
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: text,
            isStreaming: true,
          };
          return updated;
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
        function_responses: latestEvent.function_responses,
      };

      // If we were streaming and this is the final message, replace the last one
      if (!latestEvent.partial && !latestEvent.isStreaming) {
        const lastIndex = prev.length - 1;
        if (
          lastIndex >= 0 &&
          prev[lastIndex].author === eventToAdd.author &&
          prev[lastIndex].isStreaming
        ) {
          // Replace the streaming message with the final one
          const updated = [...prev];
          updated[lastIndex] = {
            ...eventToAdd,
            isStreaming: false,
          };

          // 🔥 CRITICAL FIX: Update the latest complete AI message immediately
          if (
            eventToAdd.author !== 'user' &&
            eventToAdd.text &&
            !eventToAdd.isStreaming
          ) {
            console.log(
              '🎵 Setting latest complete AI message:',
              eventToAdd.text.substring(0, 50) + '...',
            );
            latestCompleteAiMessageRef.current = eventToAdd.text;
            setLastAiResponse(eventToAdd.text);
          }

          return updated;
        }
      }

      // Check if this exact text already exists from the same author
      const exists = prev.some(
        (e) =>
          e.author === eventToAdd.author &&
          e.text === eventToAdd.text &&
          !e.isStreaming,
      );

      if (exists) {
        console.log('Skipping duplicate in state:', eventToAdd.text);
        return prev;
      }

      // 🔥 CRITICAL FIX: Also update for new complete messages
      if (
        eventToAdd.author !== 'user' &&
        eventToAdd.text &&
        !eventToAdd.isStreaming
      ) {
        console.log(
          '🎵 Setting latest complete AI message (new):',
          eventToAdd.text.substring(0, 50) + '...',
        );
        latestCompleteAiMessageRef.current = eventToAdd.text;
        setLastAiResponse(eventToAdd.text);
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
      // Only proceed if we have a userId and haven't handled the query yet
      if (userId && !initialBusinessQuerySent.current) {
        // Get query parameter from URL
        const urlParams = new URLSearchParams(window.location.search);
        const queryParam = urlParams.get('query');

        if (queryParam) {
          initialBusinessQuerySent.current = true; // Mark as handled immediately to prevent duplicate processing

          try {
            // Create a new session in the backend
            const newSessionResponse = await api.post(
              `/apps/${selectedApp}/users/${userId}/sessions`,
            );
            const newSessionId = newSessionResponse.data.id;

            // Update the current session state
            setCurrentSession(newSessionId);

            // Wait a short time for the session to be fully initialized
            setTimeout(async () => {
              // Create the message object
              const message = {
                content: {
                  parts: [{ text: queryParam }],
                  role: 'user',
                },
              };

              // Add the user message to the UI immediately
              const userMessage = {
                id: `user-${Date.now()}`,
                author: 'user',
                text: queryParam,
                timestamp: Date.now() / 1000,
                isStreaming: false,
              };

              setSessionEvents([userMessage]);

              // IMPORTANT: Call the actual sendMessage function to trigger AI response
              // This is what was missing - you need to call sendMessage from useSSE
              if (sendMessage) {
                await sendMessage(message);
              }

              // Remove the query parameter from URL without refreshing the page
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
  }, [userId, selectedApp, sendMessage]); // Add sendMessage to dependencies

  const handleSessionChange = async (sessionId: string) => {
    setCurrentSession(sessionId);
    setSessionEvents([]);
    processedEventsRef.current.clear();

    // 🔥 CRITICAL FIX: Clear the latest AI message when switching sessions
    latestCompleteAiMessageRef.current = '';
    setLastAiResponse('');

    // Load session events
    try {
      const response = await api.get(
        `/apps/${selectedApp}/users/${userId}/sessions/${sessionId}`,
      );
      if (response.data.events) {
        const events = response.data.events;
        setSessionEvents(events);

        // 🔥 CRITICAL FIX: Find the last complete AI message from loaded events
        for (let i = events.length - 1; i >= 0; i--) {
          const event = events[i];
          if (event.author !== 'user' && event.text && !event.isStreaming) {
            console.log(
              '🎵 Found last AI message in loaded session:',
              event.text.substring(0, 50) + '...',
            );
            latestCompleteAiMessageRef.current = event.text;
            setLastAiResponse(event.text);
            break;
          }
        }

        // Scroll to bottom after loading session events
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
    processedEventsRef.current.clear();

    // 🔥 CRITICAL FIX: Clear the latest AI message for new session
    latestCompleteAiMessageRef.current = '';
    setLastAiResponse('');
  };

  const handleResendMessage = async (text: string) => {
    // Create a new message with the resent text
    const message = {
      content: {
        parts: [{ text }],
        role: 'user',
      },
    };
    await handleSendMessage(message);
  };

  // Fix for your chat page handleSendMessage function
  const handleSendMessage = async (message: any) => {
    console.log('🔥 handleSendMessage called with:', message);

    // Add user message to events immediately
    const userMessage = {
      id: `user-${Date.now()}`,
      author: 'user',
      text: message.content.parts?.[0]?.text || '',
      timestamp: Date.now() / 1000,
      isStreaming: false,
    };

    console.log('👤 Adding user message to UI:', userMessage);
    setSessionEvents((prev) => [...prev, userMessage]);

    // Scroll to bottom after adding user message
    setTimeout(scrollToBottom, 50);

    // 🚨 CRITICAL: Always call sendMessage for AI response
    console.log('🤖 Calling sendMessage to trigger AI response...');

    try {
      await sendMessage(message);
      console.log('✅ sendMessage completed - AI should respond now');
    } catch (error) {
      console.error('❌ sendMessage failed:', error);
    }
  };

  const handleEditMessage = async (messageId: string, newText: string) => {
    // Find the message and update it
    setSessionEvents((prev) =>
      prev.map((event) =>
        event.id === messageId ? { ...event, text: newText } : event,
      ),
    );

    // Optionally resend the edited message
    await handleResendMessage(newText);
  };

  // Initialize session on component mount
  useEffect(() => {
    const initializeSession = async () => {
      // Check if we have a query parameter - if so, we'll handle session creation in the other effect
      const urlParams = new URLSearchParams(window.location.search);
      const queryParam = urlParams.get('query');

      // If there's a query parameter, skip the normal initialization
      if (queryParam) {
        return;
      }

      try {
        const response = await api.get(
          `/apps/${selectedApp}/users/${userId}/sessions`,
        );
        const sessions = response.data;

        if (sessions.length > 0) {
          // Auto-select the most recent session (first in the list)
          const mostRecentSession = sessions[0];
          console.log(
            'Auto-selecting most recent session:',
            mostRecentSession.id,
          );
          await handleSessionChange(mostRecentSession.id);
        } else {
          // Create a new session if none exist
          console.log('No sessions found, creating new session');
          const newSessionResponse = await api.post(
            `/apps/${selectedApp}/users/${userId}/sessions`,
          );
          await handleSessionChange(newSessionResponse.data.id);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        // If there's an error, create a new session anyway
        handleNewSession();
      }
    };

    // Only initialize if we have userId and selectedApp, and don't already have a current session
    if (userId && selectedApp && !currentSession) {
      console.log('Initializing session...');
      initializeSession();
    }
  }, [userId, selectedApp]);

  // Clear processed events when changing sessions
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
                      lastAiMessage={lastAiResponse} // 🔥 This now gets the correct latest message
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
                        onSessionChange={handleSessionChange} // Add this line
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
