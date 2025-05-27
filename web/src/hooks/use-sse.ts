import { useState, useCallback, useRef } from 'react'

interface SSEEvent {
  id?: string
  author?: string
  content?: {
    parts?: Array<{
      text?: string
    }>
    role?: string
  }
  timestamp?: number
  actions?: any
  function_responses?: any
  partial?: boolean
  invocation_id?: string
  isStreaming?: boolean
}

export function useSSE(url: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const streamingMessagesRef = useRef<Map<string, string>>(new Map())

  const sendMessage = useCallback(async (message: any) => {
    if (!url) return

    const baseUrl = url.replace('/run_live', '/run_sse')
    const urlParams = new URLSearchParams(url.split('?')[1])

    try {
      setIsLoading(true)
      // Clear events and streaming messages for new request
      setEvents([])
      streamingMessagesRef.current.clear()

      const response = await fetch(baseUrl.split('?')[0], {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          app_name: urlParams.get('app_name'),
          user_id: urlParams.get('user_id'),
          session_id: urlParams.get('session_id'),
          new_message: message.content,
          streaming: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''
      const finalEvents: SSEEvent[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        // Process all complete lines except the last one
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim()
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              console.log('SSE event received:', data)

              // Handle streaming messages
              if (data.invocation_id && data.partial) {
                // This is a partial message - accumulate it
                const currentText = streamingMessagesRef.current.get(data.invocation_id) || ''
                const newText = data.content?.parts?.[0]?.text || ''
                streamingMessagesRef.current.set(data.invocation_id, currentText + newText)

                // Update the streaming event
                const streamingEvent = {
                  ...data,
                  content: {
                    ...data.content,
                    parts: [{
                      text: currentText + newText
                    }]
                  },
                  isStreaming: true
                }

                setEvents([streamingEvent])
              } else if (data.invocation_id && !data.partial) {
                // This is the final complete message
                const completeEvent = {
                  ...data,
                  isStreaming: false
                }

                // Clear the streaming message
                streamingMessagesRef.current.delete(data.invocation_id)
                finalEvents.push(completeEvent)
                setEvents([completeEvent])
              } else {
                // Regular non-streaming event
                finalEvents.push(data)
                setEvents([...finalEvents])
              }
            } catch (err) {
              console.error('Error parsing SSE data:', err, line)
            }
          }
        }

        // Keep the last line in the buffer
        buffer = lines[lines.length - 1]
      }
    } catch (error) {
      console.error('SSE error:', error)
    } finally {
      setIsLoading(false)
    }
  }, [url])

  return {
    sendMessage,
    events,
    isLoading
  }
}
