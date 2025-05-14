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

export function MessageInput({ onSendMessage, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 60,
    maxHeight: 200,
  })

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage({
        type: 'text',
        text: message.trim()
      })
      setMessage('')
      adjustHeight(true)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="w-full bg-transparent px-4 py-6">
      <div className="max-w-7xl mx-auto">
        <div className="relative bg-[#0e0e10] rounded-xl border border-[#2a2a30]">
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
                "text-white text-sm",
                "focus:outline-none",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-[#6a6a70] placeholder:text-sm",
                "min-h-[60px]"
              )}
              style={{
                overflow: "hidden",
              }}
              disabled={disabled}
            />
          </div>

          <div className="flex items-center justify-between p-3 border-t border-[#2a2a30]">
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="p-2 text-[#6a6a70] hover:text-white hover:bg-[#2a2a30] rounded-lg transition-colors"
                disabled={disabled}
              >
                <Paperclip className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="p-2 text-[#6a6a70] hover:text-white hover:bg-[#2a2a30] rounded-lg transition-colors"
                disabled={disabled}
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="p-2 text-[#6a6a70] hover:text-white hover:bg-[#2a2a30] rounded-lg transition-colors"
                disabled={disabled}
              >
                <Camera className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={!message.trim() || disabled}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1",
                  message.trim() && !disabled
                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                    : "bg-[#2a2a30] text-[#6a6a70] cursor-not-allowed"
                )}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}