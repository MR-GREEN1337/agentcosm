import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Bot, User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EventsTabProps {
  appName: string
  userId: string
  sessionId: string
  events: any[]
}

export function EventsTab({ appName, userId, sessionId, events = [] }: EventsTabProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events])

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Bot className="w-16 h-16 text-[#3a3a40] mx-auto mb-4" />
          <p className="text-[#a0a0a8] text-lg">Start a conversation</p>
          <p className="text-[#6a6a70] text-sm mt-2">Type a message below</p>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6" ref={scrollRef}>
        {events.map((event, index) => {
          // Create a unique key for each event
          const eventKey = event.id || `${event.author}-${event.timestamp}-${index}`
          const isUser = event.author === 'user' || event.content?.role === 'user'
          
          // Extract message text
          let messageText = event.text || ''
          if (!messageText && event.content?.parts?.[0]?.text) {
            messageText = event.content.parts[0].text
          }
          if (!messageText && typeof event.content === 'string') {
            messageText = event.content
          }
          
          // Also check for function calls from the event
          const functionCalls = event.function_calls || event.actions?.function_calls
          const functionResponses = event.function_responses || event.actions?.function_responses
          
          // Skip empty events
          if (!messageText && !functionCalls && !functionResponses) {
            return null
          }
          
          return (
            <div
              key={eventKey}
              className={cn(
                "flex gap-3",
                isUser ? "justify-end" : "justify-start"
              )}
            >
              {!isUser && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}
              
              <div
                className={cn(
                  "max-w-[70%] rounded-2xl px-4 py-3",
                  isUser 
                    ? "bg-blue-600 text-white" 
                    : "bg-[#1a1a1f] border border-[#2a2a30] text-[#d0d0d8]"
                )}
              >
                {messageText && (
                  <p className="whitespace-pre-wrap break-words">
                    {messageText}
                    {event.isStreaming && (
                      <span className="inline-block w-1 h-4 bg-current opacity-70 animate-pulse ml-1 align-middle" />
                    )}
                  </p>
                )}
                
                {functionCalls && functionCalls.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-sm text-blue-400 font-medium">Function calls:</p>
                    {functionCalls.map((call: any, idx: number) => (
                      <div key={idx} className="text-sm bg-[#0e0e10] p-2 rounded text-blue-400 font-mono">
                        {call.name}({call.arguments ? JSON.stringify(call.arguments) : ''})
                      </div>
                    ))}
                  </div>
                )}
                
                {functionResponses && functionResponses.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-sm text-green-400 font-medium">Function responses:</p>
                    {functionResponses.map((response: any, idx: number) => (
                      <div key={idx} className="text-sm bg-[#0e0e10] p-2 rounded">
                        <span className="text-green-400 font-mono">{response.name}</span>
                        <span className="text-[#a0a0a8]">: {JSON.stringify(response.response_data || response.data)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {isUser && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-lg bg-[#2a2a30] flex items-center justify-center">
                    <User className="w-4 h-4 text-[#a0a0a8]" />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </ScrollArea>
  )
}