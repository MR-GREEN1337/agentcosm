import { useState, useRef, useCallback, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Send, Paperclip, Mic, Camera } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageInputProps {
  onSendMessage: (message: any) => void
  disabled?: boolean
}

interface UseAutoResizeTextareaProps {
  minHeight: number
  maxHeight?: number
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current
      if (!textarea) return

      if (reset) {
        textarea.style.height = `${minHeight}px`
        return
      }

      // Temporarily shrink to get the right scrollHeight
      textarea.style.height = `${minHeight}px`

      // Calculate new height
      const newHeight = Math.max(
        minHeight,
        Math.min(
          textarea.scrollHeight,
          maxHeight ?? Number.POSITIVE_INFINITY
        )
      )

      textarea.style.height = `${newHeight}px`
    },
    [minHeight, maxHeight]
  )

  useEffect(() => {
    // Set initial height
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = `${minHeight}px`
    }
  }, [minHeight])

  // Adjust height on window resize
  useEffect(() => {
    const handleResize = () => adjustHeight()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [adjustHeight])

  return { textareaRef, adjustHeight }
}

export function MessageInput({ onSendMessage, disabled = false }: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 60,
    maxHeight: 200,
  })

  const handleSend = async () => {
    if (message.trim() && !disabled && !isSending) {
      setIsSending(true)
      
      // Create content structure that matches backend format
      const messagePayload = {
        content: {
          parts: [{
            text: message.trim()
          }],
          role: "user"
        }
      }
      
      try {
        await onSendMessage(messagePayload)
        setMessage('')
        adjustHeight(true)
      } catch (error) {
        console.error('Error sending message:', error)
      } finally {
        setIsSending(false)
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="sticky bottom-0 w-full px-4 py-4 bg-background border-t border-border">
      <div className="max-w-7xl mx-auto">
        <div className="relative bg-secondary/30 rounded-xl border border-border">
          <div className="overflow-y-auto">
            <Textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value)
                adjustHeight()
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              className={cn(
                "w-full px-4 py-3",
                "resize-none",
                "bg-transparent",
                "border-none",
                "text-foreground text-sm",
                "focus:outline-none",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-muted-foreground placeholder:text-sm",
                "min-h-[60px]"
              )}
              style={{
                overflow: "hidden",
              }}
              disabled={disabled || isSending}
            />
          </div>

          <div className="flex items-center justify-between p-3 border-t border-border">
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
                disabled={disabled || isSending}
              >
                <Paperclip className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
                disabled={disabled || isSending}
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
                disabled={disabled || isSending}
              >
                <Camera className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={!message.trim() || disabled || isSending}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1",
                  message.trim() && !disabled && !isSending
                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                    : "bg-secondary text-muted-foreground cursor-not-allowed"
                )}
              >
                {isSending ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}