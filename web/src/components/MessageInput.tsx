import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Send, Paperclip, Mic, Camera } from 'lucide-react'

interface MessageInputProps {
  onSendMessage: (message: any) => void
  disabled?: boolean
}

export function MessageInput({ onSendMessage, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage({
        type: 'text',
        text: message.trim()
      })
      setMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-[#2a2a30] bg-[#17171b] p-4">
      <div className="flex items-end gap-3 max-w-7xl mx-auto">
        <div className="flex-1 relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="bg-[#0e0e10] border-[#2a2a30] text-white placeholder:text-[#6a6a70] 
                       min-h-[80px] max-h-[200px] pr-12 resize-none
                       focus:border-blue-500 focus:ring-blue-500/20"
            disabled={disabled}
          />
          <Button
            variant="ghost"
            size="icon"
            className="absolute bottom-2 right-2 text-[#6a6a70] hover:text-white hover:bg-[#2a2a30]"
            disabled={disabled}
          >
            <Paperclip className="w-4 h-4" />
          </Button>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="text-[#6a6a70] hover:text-white hover:bg-[#2a2a30]"
            disabled={disabled}
          >
            <Mic className="w-5 h-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-[#6a6a70] hover:text-white hover:bg-[#2a2a30]"
            disabled={disabled}
          >
            <Camera className="w-5 h-5" />
          </Button>
          <Button
            onClick={handleSend}
            disabled={!message.trim() || disabled}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}