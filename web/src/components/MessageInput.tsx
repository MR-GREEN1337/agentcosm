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
  const [isInputFocused, setIsInputFocused] = useState(false)
  
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
      {/* Important: Removed sticky positioning and bottom margin to prevent overlap */}
      <div className="w-full px-2 sm:px-4 py-2 sm:py-4 bg-transparent pointer-events-none">
        <div className="max-w-3xl mx-auto">
          <div 
            className={cn(
              "relative bg-background/40 backdrop-blur-xl rounded-2xl",
              "border border-primary/10 shadow-lg pointer-events-auto",
              "transition-all duration-300 ease-in-out",
              "hover:bg-background/50 hover:border-primary/20",
              "hover:shadow-xl hover:shadow-primary/5",
              isInputFocused ? "bg-background/60 border-primary/30 shadow-xl shadow-primary/10" : "",
              "overflow-hidden"
            )}
            style={{
              transform: "translateY(0)",
              animation: "float 6s ease-in-out infinite",
            }}
          >
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-secondary/5 to-primary/5 opacity-30 pointer-events-none"></div>
            
            {/* Attached Image Preview */}
            {attachedImage && (
              <div className="p-3 border-b border-primary/10 bg-background/30">
                <div className="relative inline-block">
                  <img 
                    src={attachedImage} 
                    alt="Attached" 
                    className="h-20 rounded-xl object-cover shadow-sm"
                  />
                  <button
                    onClick={removeAttachedImage}
                    className="absolute -top-1.5 -right-1.5 p-1 bg-red-500/90 backdrop-blur-sm text-white rounded-full hover:bg-red-600 transition-colors shadow-sm"
                    aria-label="Remove image"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              </div>
            )}

            <div className="flex items-end bg-transparent">
              <div className="flex-1 bg-transparent">
                <Textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value)
                    adjustHeight()
                  }}
                  onKeyDown={handleKeyDown}
                  onFocus={() => setIsInputFocused(true)}
                  onBlur={() => setIsInputFocused(false)}
                  placeholder="Type a message..."
                  className={cn(
                    "w-full px-4 py-3.5",
                    "resize-none",
                    "bg-transparent",
                    "border-none",
                    "text-foreground text-sm",
                    "focus:outline-none",
                    "focus-visible:ring-0 focus-visible:ring-offset-0",
                    "placeholder:text-muted-foreground/70 placeholder:text-sm",
                    "min-h-[44px]",
                    "transition-all duration-200"
                  )}
                  style={{
                    overflow: "hidden",
                  }}
                  disabled={disabled || isSending}
                />
              </div>

              <div className="flex items-center gap-1.5 px-3 pb-3">
                <button
                  type="button"
                  className={cn(
                    "p-2 rounded-xl transition-colors",
                    "text-muted-foreground/70 hover:text-foreground",
                    "hover:bg-primary/10 active:bg-primary/15",
                    "focus:outline-none focus:ring-2 focus:ring-primary/20",
                  )}
                  disabled={disabled || isSending}
                  aria-label="Attach file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  className={cn(
                    "p-2 rounded-xl transition-colors",
                    "text-muted-foreground/70 hover:text-foreground",
                    "hover:bg-primary/10 active:bg-primary/15",
                    "focus:outline-none focus:ring-2 focus:ring-primary/20",
                  )}
                  disabled={disabled || isSending}
                  aria-label="Record audio"
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowCamera(true)}
                  className={cn(
                    "p-2 rounded-xl transition-colors hidden sm:flex",
                    "text-muted-foreground/70 hover:text-foreground",
                    "hover:bg-primary/10 active:bg-primary/15",
                    "focus:outline-none focus:ring-2 focus:ring-primary/20",
                  )}
                  disabled={disabled || isSending}
                  aria-label="Take photo"
                >
                  <Camera className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={handleSend}
                  disabled={(!message.trim() && !attachedImage) || disabled || isSending}
                  className={cn(
                    "p-2 rounded-xl transition-all flex items-center justify-center ml-1",
                    "focus:outline-none focus:ring-2 focus:ring-primary/20",
                    (message.trim() || attachedImage) && !disabled && !isSending
                      ? "bg-gradient-to-r from-primary to-primary/90 text-white shadow-md hover:shadow-lg hover:opacity-95 active:opacity-90"
                      : "bg-background/50 text-muted-foreground/50 cursor-not-allowed"
                  )}
                  aria-label="Send message"
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
        <DialogContent className="sm:max-w-[600px] bg-background/95 backdrop-blur-xl border-primary/10 shadow-xl">
          <DialogHeader>
            <DialogTitle className="text-center text-lg font-medium">Take a Photo</DialogTitle>
          </DialogHeader>
          <div className="mt-4">
            {!capturedImage ? (
              <div className="relative rounded-xl overflow-hidden shadow-md">
                <Webcam
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full rounded-xl"
                  videoConstraints={{
                    facingMode: "user",
                    width: 1280,
                    height: 720
                  }}
                />
                <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/70 to-transparent">
                  <Button
                    onClick={captureImage}
                    className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-primary hover:bg-primary/90 rounded-xl px-5 py-2 text-sm font-medium shadow-lg"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Capture
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-xl overflow-hidden shadow-md">
                  <img
                    src={capturedImage}
                    alt="Captured"
                    className="w-full rounded-xl"
                  />
                </div>
                <div className="flex gap-4 justify-center pt-2">
                  <Button
                    onClick={retakeImage}
                    variant="outline"
                    className="rounded-xl border-primary/20 hover:bg-primary/5 px-5"
                  >
                    Retake
                  </Button>
                  <Button
                    onClick={confirmImage}
                    className="bg-primary hover:bg-primary/90 rounded-xl px-5 shadow-md"
                  >
                    Use Photo
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* CSS for floating animation */}
      <style jsx global>{`
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
      `}</style>
    </>
  )
}
