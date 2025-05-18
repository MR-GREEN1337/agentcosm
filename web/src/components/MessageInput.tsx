import { useState, useRef, useCallback, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Send, Paperclip, Mic, Camera, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import Webcam from 'react-webcam'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

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
  const [showCamera, setShowCamera] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [attachedImage, setAttachedImage] = useState<string | null>(null)
  
  const webcamRef = useRef<Webcam>(null)
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 44,
    maxHeight: 160,
  })

  const handleSend = async () => {
    if ((message.trim() || attachedImage) && !disabled && !isSending) {
      setIsSending(true)
      
      // Create content structure that matches backend format
      const parts: any[] = []
      
      if (message.trim()) {
        parts.push({
          text: message.trim()
        })
      }
      
      if (attachedImage) {
        // Convert base64 to a format the backend expects
        // Assuming backend accepts inline_data format
        parts.push({
          inline_data: {
            mime_type: "image/jpeg",
            data: attachedImage.split(',')[1] // Remove data:image/jpeg;base64, prefix
          }
        })
      }
      
      const messagePayload = {
        content: {
          parts,
          role: "user"
        }
      }
      
      try {
        await onSendMessage(messagePayload)
        setMessage('')
        setAttachedImage(null)
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

  const captureImage = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot()
    if (imageSrc) {
      setCapturedImage(imageSrc)
    }
  }, [])

  const retakeImage = () => {
    setCapturedImage(null)
  }

  const confirmImage = () => {
    if (capturedImage) {
      setAttachedImage(capturedImage)
      setCapturedImage(null)
      setShowCamera(false)
    }
  }

  const removeAttachedImage = () => {
    setAttachedImage(null)
  }

  return (
    <>
      <div className="sticky bottom-0 w-full px-2 sm:px-4 py-2 sm:py-4 bg-transparent">
        <div className="max-w-3xl mx-auto">
          <div className="relative bg-secondary/30 backdrop-blur-sm rounded-xl border border-border shadow-lg">
            {/* Attached Image Preview */}
            {attachedImage && (
              <div className="p-2 border-b border-border">
                <div className="relative inline-block">
                  <img 
                    src={attachedImage} 
                    alt="Attached" 
                    className="h-16 rounded-lg object-cover"
                  />
                  <button
                    onClick={removeAttachedImage}
                    className="absolute -top-1 -right-1 p-0.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              </div>
            )}

            <div className="flex items-end">
              <div className="flex-1">
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
                    "w-full px-3 py-2.5",
                    "resize-none",
                    "bg-transparent",
                    "border-none",
                    "text-foreground text-sm",
                    "focus:outline-none",
                    "focus-visible:ring-0 focus-visible:ring-offset-0",
                    "placeholder:text-muted-foreground placeholder:text-sm",
                    "min-h-[44px]"
                  )}
                  style={{
                    overflow: "hidden",
                  }}
                  disabled={disabled || isSending}
                />
              </div>

              <div className="flex items-center gap-1 px-2 pb-2">
                <button
                  type="button"
                  className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
                  disabled={disabled || isSending}
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
                  disabled={disabled || isSending}
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowCamera(true)}
                  className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors hidden sm:block"
                  disabled={disabled || isSending}
                >
                  <Camera className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={handleSend}
                  disabled={(!message.trim() && !attachedImage) || disabled || isSending}
                  className={cn(
                    "p-1.5 rounded-lg transition-all flex items-center justify-center",
                    (message.trim() || attachedImage) && !disabled && !isSending
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

      {/* Camera Dialog */}
      <Dialog open={showCamera} onOpenChange={setShowCamera}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Take a Photo</DialogTitle>
          </DialogHeader>
          <div className="mt-4">
            {!capturedImage ? (
              <div className="relative rounded-lg overflow-hidden">
                <Webcam
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full rounded-lg"
                  videoConstraints={{
                    facingMode: "user",
                    width: 1280,
                    height: 720
                  }}
                />
                <Button
                  onClick={captureImage}
                  className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-blue-600 hover:bg-blue-700"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Capture
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <img
                  src={capturedImage}
                  alt="Captured"
                  className="w-full rounded-lg"
                />
                <div className="flex gap-3 justify-center">
                  <Button
                    onClick={retakeImage}
                    variant="outline"
                  >
                    Retake
                  </Button>
                  <Button
                    onClick={confirmImage}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Use Photo
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}