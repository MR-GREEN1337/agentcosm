import { useState, useRef, useCallback, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Send, Paperclip, Mic, MicOff, Camera, X, Volume2, VolumeX } from 'lucide-react'
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
  lastAiMessage?: string
  gcpTtsEndpoint?: string
  voiceConfig?: {
    languageCode: string
    name: string
    ssmlGender: string
  }
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

// Audio cache to store recent TTS results
class TTSCache {
  private cache = new Map<string, ArrayBuffer>()
  private maxSize = 50
  private accessTime = new Map<string, number>()

  set(text: string, audioBuffer: ArrayBuffer) {
    // Clean cache if too large
    if (this.cache.size >= this.maxSize) {
      this.evictLRU()
    }

    const key = this.hashText(text)
    this.cache.set(key, audioBuffer)
    this.accessTime.set(key, Date.now())
  }

  get(text: string): ArrayBuffer | null {
    const key = this.hashText(text)
    const audioBuffer = this.cache.get(key)
    if (audioBuffer) {
      this.accessTime.set(key, Date.now())
      return audioBuffer
    }
    return null
  }

  private hashText(text: string): string {
    // Simple hash for text - in production you might want a better hash function
    return btoa(text.substring(0, 100)).replace(/[^a-zA-Z0-9]/g, '')
  }

  private evictLRU() {
    let oldestKey = ''
    let oldestTime = Date.now()

    for (const [key, time] of this.accessTime) {
      if (time < oldestTime) {
        oldestTime = time
        oldestKey = key
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey)
      this.accessTime.delete(oldestKey)
    }
  }
}

// Global TTS cache instance
const ttsCache = new TTSCache()

export function MessageInput({
  onSendMessage,
  disabled = false,
  lastAiMessage,
  gcpTtsEndpoint = '/api/gcp-tts',
  voiceConfig = {
    languageCode: 'en-US',
    name: 'en-US-Neural2-F', // High-quality neural voice
    ssmlGender: 'FEMALE'
  }
}: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [attachedImage, setAttachedImage] = useState<string | null>(null)
  const [isInputFocused, setIsInputFocused] = useState(false)

  // Audio states
  const [isListening, setIsListening] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isGeneratingTTS, setIsGeneratingTTS] = useState(false)
  const [transcript, setTranscript] = useState('')

  const webcamRef = useRef<Webcam>(null)
  const recognitionRef = useRef<any>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const pendingTTSRef = useRef<AbortController | null>(null)
  const lastProcessedMessageRef = useRef<string>('')
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 44,
    maxHeight: 160,
  })

  // Store the final transcript in a ref to avoid stale closures
  const finalTranscriptRef = useRef('')

  // Initialize Audio Context for low-latency playback
  useEffect(() => {
    const initAudioContext = () => {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }
    }

    // Initialize on first user interaction
    const handleUserInteraction = () => {
      initAudioContext()
      document.removeEventListener('click', handleUserInteraction)
      document.removeEventListener('keydown', handleUserInteraction)
    }

    document.addEventListener('click', handleUserInteraction)
    document.addEventListener('keydown', handleUserInteraction)

    return () => {
      document.removeEventListener('click', handleUserInteraction)
      document.removeEventListener('keydown', handleUserInteraction)
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close()
      }
    }
  }, [])

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
      recognitionRef.current = new SpeechRecognition()

      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started')
        setIsListening(true)
        finalTranscriptRef.current = '' // Reset on start
      }

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        // Update the ref with final transcript
        if (finalTranscript) {
          finalTranscriptRef.current += finalTranscript
        }

        // Only update transcript state for UI display
        const fullTranscript = finalTranscriptRef.current + interimTranscript
        setTranscript(fullTranscript)

        console.log('Speech result:', { finalTranscript, interimTranscript, fullTranscript, finalFromRef: finalTranscriptRef.current })
      }

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended, final transcript:', finalTranscriptRef.current)
        setIsListening(false)

        // Clear the transcript display
        setTranscript('')

        // Send the message using the ref value - do this after state updates
        const voiceText = finalTranscriptRef.current.trim()
        if (voiceText) {
          console.log('Triggering voice message send:', voiceText)
          // Call handleSend directly with the voice text
          setTimeout(() => {
            handleSend(voiceText)
          }, 100) // Small delay to ensure state updates are complete
        }
      }

      recognitionRef.current.onerror = (event: any) => {
        // Don't log "aborted" errors as they're normal when stopping recognition
        if (event.error !== 'aborted') {
          console.error('Speech recognition error:', event.error)
        }
        setIsListening(false)
        setTranscript('')
        finalTranscriptRef.current = ''
      }
    }

    return () => {
      if (recognitionRef.current && isListening) {
        recognitionRef.current.abort()
      }
      // Clean up audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, []) // Keep empty dependency array

  // Optimized TTS with GCP integration
  const generateAndPlayTTS = useCallback(async (text: string) => {
    if (isMuted || !text.trim()) return

    // Skip very short texts or code blocks
    if (text.length < 10 || text.includes('```')) {
      console.log('Skipping TTS for short/code content')
      return
    }

    // Cancel any pending TTS request
    if (pendingTTSRef.current) {
      pendingTTSRef.current.abort()
    }

    // Check cache first
    const cachedAudio = ttsCache.get(text)
    if (cachedAudio) {
      console.log('Playing cached TTS audio')
      await playAudioBuffer(cachedAudio)
      return
    }

    setIsGeneratingTTS(true)
    const abortController = new AbortController()
    pendingTTSRef.current = abortController

    try {
      // Prepare request payload for GCP TTS
      const ttsPayload = {
        input: {
          text: text
        },
        voice: voiceConfig,
        audioConfig: {
          audioEncoding: 'LINEAR16', // Uncompressed for lowest latency
          sampleRateHertz: 24000,    // High quality but not excessive
          speakingRate: 1.1,         // Slightly faster for conversational feel
          pitch: 0,
          volumeGainDb: 0
        }
      }

      const startTime = Date.now()
      console.log('Generating TTS with GCP...')

      const response = await fetch(gcpTtsEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ttsPayload),
        signal: abortController.signal,
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`GCP TTS API error: ${response.status} ${response.statusText} - ${errorText}`)
      }

      const audioBuffer = await response.arrayBuffer()
      const generationTime = Date.now() - startTime
      console.log(`TTS generated in ${generationTime}ms, size: ${audioBuffer.byteLength} bytes`)

      // Cache the result
      ttsCache.set(text, audioBuffer)

      // Play immediately if not aborted
      if (!abortController.signal.aborted) {
        await playAudioBuffer(audioBuffer)
      }

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('GCP TTS generation error:', error)
      }
    } finally {
      setIsGeneratingTTS(false)
      if (pendingTTSRef.current === abortController) {
        pendingTTSRef.current = null
      }
    }
  }, [isMuted, gcpTtsEndpoint, voiceConfig])

  // Low-latency audio playback using Web Audio API
  const playAudioBuffer = useCallback(async (arrayBuffer: ArrayBuffer) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }

      const audioContext = audioContextRef.current

      // Resume context if suspended
      if (audioContext.state === 'suspended') {
        await audioContext.resume()
      }

      setIsPlaying(true)

      // Decode audio data
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0))

      // Create and configure audio source
      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer

      // Connect to destination
      source.connect(audioContext.destination)

      // Set up completion handler
      source.onended = () => {
        console.log('TTS playback completed')
        setIsPlaying(false)
      }

      // Start playback immediately
      source.start(0)

    } catch (error: any) {
      console.error('Audio playback error:', error)
      setIsPlaying(false)
    }
  }, [])

  // Enhanced TTS trigger with streaming support and duplicate prevention
  useEffect(() => {
    if (!lastAiMessage || isMuted) return

    // Skip if we've already processed this exact message
    if (lastProcessedMessageRef.current === lastAiMessage) {
      return
    }

    // Debounce for streaming messages - only trigger TTS after message seems complete
    const timeoutId = setTimeout(() => {
      // Double-check the message hasn't changed (indicating streaming is still active)
      if (lastAiMessage && lastProcessedMessageRef.current !== lastAiMessage) {
        console.log('Triggering TTS for AI response:', lastAiMessage.substring(0, 100) + '...')
        lastProcessedMessageRef.current = lastAiMessage
        generateAndPlayTTS(lastAiMessage)
      }
    }, 500) // Increased delay to ensure message completion

    return () => clearTimeout(timeoutId)
  }, [lastAiMessage, isMuted, generateAndPlayTTS])

  const handleSend = async (textToSend?: string) => {
    const messageText = textToSend || message.trim()

    if ((messageText || attachedImage) && !disabled && !isSending) {
      setIsSending(true)

      // Stop any playing audio when user sends a message
      if (audioRef.current) {
        audioRef.current.pause()
        setIsPlaying(false)
      }
      if (pendingTTSRef.current) {
        pendingTTSRef.current.abort()
        setIsGeneratingTTS(false)
      }

      // Create content structure that matches backend format
      const parts: any[] = []

      if (messageText) {
        parts.push({
          text: messageText
        })
      }

      if (attachedImage) {
        parts.push({
          inline_data: {
            mime_type: "image/jpeg",
            data: attachedImage.split(',')[1]
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

        // Only clear the manual message input, not voice transcript
        if (!textToSend) {
          setMessage('')
          adjustHeight(true)
        }
        setAttachedImage(null)
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

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not supported in this browser')
      return
    }

    if (isListening) {
      console.log('Stopping speech recognition')
      // Use stop() instead of abort() for graceful shutdown
      recognitionRef.current.stop()
    } else {
      console.log('Starting speech recognition')
      setTranscript('')
      setMessage('') // Clear textarea when starting to listen
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Failed to start speech recognition:', error)
        setIsListening(false)
      }
    }
  }

  const toggleMute = () => {
    const newMutedState = !isMuted
    setIsMuted(newMutedState)

    if (newMutedState) {
      // Stop any playing audio when muting
      if (isPlaying && audioContextRef.current) {
        // Stop all audio sources (Web Audio API doesn't have a direct stop method for context)
        setIsPlaying(false)
      }
      if (pendingTTSRef.current) {
        pendingTTSRef.current.abort()
        setIsGeneratingTTS(false)
      }
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
      {/* Container - COMPLETELY transparent parent */}
      <div className="w-full px-2 sm:px-4 py-2 sm:py-4">
        <div className="max-w-3xl mx-auto">
          {/* Main input container with floating glass effect */}
          <div
            className={cn(
              "relative backdrop-blur-xl rounded-2xl",
              "border shadow-lg",
              "transition-all duration-300 ease-in-out",
              "overflow-hidden",
              // Light mode styling
              "bg-white/90 border-gray-200/50 text-gray-900",
              "hover:bg-white/95 hover:border-gray-300/50",
              "hover:shadow-xl hover:shadow-black/5",
              // Dark mode styling
              "dark:bg-gray-900/90 dark:border-gray-700/50 dark:text-white",
              "dark:hover:bg-gray-900/95 dark:hover:border-gray-600/60",
              "dark:hover:shadow-xl dark:hover:shadow-black/20",
              // Focus states
              isInputFocused ? "bg-white/95 border-blue-500/30 shadow-xl shadow-blue-500/10 dark:bg-gray-900/95 dark:border-blue-500/40 dark:shadow-blue-500/20" : "",
              // Listening states
              isListening ? "border-red-500/50 shadow-xl shadow-red-500/20 bg-red-50/90 dark:border-red-500/60 dark:shadow-red-500/30 dark:bg-gray-800/95" : "",
              // TTS generating state
              isGeneratingTTS ? "border-green-500/50 shadow-xl shadow-green-500/20 bg-green-50/90 dark:border-green-500/60 dark:shadow-green-500/30 dark:bg-gray-800/95" : "",
            )}
            style={{
              transform: "translateY(0)",
              animation: isInputFocused || isListening || isGeneratingTTS ? "none" : "float 6s ease-in-out infinite",
            }}
          >
            {/* Voice indicator - purely decorative overlay */}
            {isListening && (
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-pink-500/10 to-red-500/10 dark:from-red-500/20 dark:via-pink-500/20 dark:to-red-500/20 pointer-events-none">
                <div className="absolute inset-0 animate-pulse bg-red-500/5 dark:bg-red-500/10"></div>
              </div>
            )}

            {/* TTS generating indicator */}
            {isGeneratingTTS && (
              <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 via-blue-500/10 to-green-500/10 dark:from-green-500/20 dark:via-blue-500/20 dark:to-green-500/20 pointer-events-none">
                <div className="absolute inset-0 animate-pulse bg-green-500/5 dark:bg-green-500/10"></div>
              </div>
            )}

            {/* Subtle glow effect - purely decorative */}
            <div className={cn(
              "absolute inset-0 pointer-events-none opacity-30",
              isListening
                ? "bg-gradient-to-r from-red-500/15 via-pink-500/15 to-red-500/15 dark:from-red-500/25 dark:via-pink-500/25 dark:to-red-500/25"
                : isGeneratingTTS
                ? "bg-gradient-to-r from-green-500/15 via-blue-500/15 to-green-500/15 dark:from-green-500/25 dark:via-blue-500/25 dark:to-green-500/25"
                : "bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-blue-500/5 dark:from-blue-500/10 dark:via-purple-500/10 dark:to-blue-500/10"
            )}></div>

            {/* Voice transcript indicator */}
            {isListening && transcript && (
              <div className="p-3 border-b border-gray-200/30 bg-blue-50/20 dark:border-gray-600/30 dark:bg-gray-800/40">
                <div className="flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
                  <div className="w-2 h-2 bg-red-500 dark:bg-red-400 rounded-full animate-pulse"></div>
                  <span>Listening: {transcript}</span>
                </div>
              </div>
            )}

            {/* TTS status indicator */}
            {isGeneratingTTS && (
              <div className="p-3 border-b border-gray-200/30 bg-green-50/20 dark:border-gray-600/30 dark:bg-gray-800/40">
                <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-300">
                  <div className="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full animate-pulse"></div>
                  <span>Generating speech...</span>
                </div>
              </div>
            )}

            {/* Attached Image Preview */}
            {attachedImage && (
              <div className="p-3 border-b border-gray-200/30 bg-white/20 dark:border-gray-600/30 dark:bg-gray-800/40">
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

            {/* Main input area */}
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
                  placeholder={
                    isListening
                      ? "🎙️ Listening... (speak now)"
                      : isGeneratingTTS
                      ? "🔊 Generating speech..."
                      : "Type a message or click mic to speak..."
                  }
                  className={cn(
                    "w-full px-4 py-3.5",
                    "resize-none",
                    "bg-transparent",
                    "border-none",
                    "text-gray-900 dark:text-white text-sm",
                    "focus:outline-none",
                    "focus-visible:ring-0 focus-visible:ring-offset-0",
                    "placeholder:text-gray-500 dark:placeholder:text-gray-400 placeholder:text-sm",
                    "min-h-[44px]",
                    "transition-all duration-200"
                  )}
                  style={{
                    overflow: "hidden",
                  }}
                  disabled={disabled || isSending}
                />
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-1.5 px-3 pb-3">
                <button
                  type="button"
                  className={cn(
                    "p-2 rounded-xl transition-colors",
                    "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200",
                    "hover:bg-blue-500/10 active:bg-blue-500/15 dark:hover:bg-blue-500/20 dark:active:bg-blue-500/25",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-500/30",
                  )}
                  disabled={disabled || isSending}
                  aria-label="Attach file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>

                {/* Voice Control Button */}
                <button
                  type="button"
                  onClick={toggleListening}
                  className={cn(
                    "p-2 rounded-xl transition-all transform hover:scale-105",
                    "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900",
                    isListening
                      ? "bg-red-500 text-white hover:bg-red-600 focus:ring-red-500/20 dark:focus:ring-red-500/30 animate-pulse shadow-lg shadow-red-500/25"
                      : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-green-500/10 active:bg-green-500/15 dark:hover:bg-green-500/20 dark:active:bg-green-500/25 focus:ring-green-500/20 dark:focus:ring-green-500/30"
                  )}
                  disabled={disabled || isSending}
                  aria-label={isListening ? "Stop recording" : "Start voice input"}
                >
                  {isListening ? (
                    <MicOff className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </button>

                {/* Enhanced Mute Toggle for TTS */}
                <button
                  type="button"
                  onClick={toggleMute}
                  className={cn(
                    "p-2 rounded-xl transition-colors hidden sm:flex",
                    isMuted
                      ? "text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-500/10 dark:hover:bg-gray-500/20"
                      : isPlaying
                        ? "text-green-500 hover:text-green-600 dark:text-green-400 dark:hover:text-green-300 hover:bg-green-500/10 dark:hover:bg-green-500/20 animate-pulse"
                        : isGeneratingTTS
                        ? "text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-500/10 dark:hover:bg-blue-500/20 animate-pulse"
                        : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-blue-500/10 dark:hover:bg-blue-500/20",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-500/30",
                  )}
                  disabled={disabled || isSending}
                  aria-label={isMuted ? "Unmute responses" : "Mute responses"}
                  title={
                    isGeneratingTTS
                      ? "Generating speech..."
                      : isPlaying
                      ? "Playing response"
                      : isMuted
                      ? "Unmute responses"
                      : "Mute responses"
                  }
                >
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>

                <button
                  type="button"
                  onClick={() => setShowCamera(true)}
                  className={cn(
                    "p-2 rounded-xl transition-colors hidden sm:flex",
                    "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200",
                    "hover:bg-blue-500/10 active:bg-blue-500/15 dark:hover:bg-blue-500/20 dark:active:bg-blue-500/25",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-500/30",
                  )}
                  disabled={disabled || isSending}
                  aria-label="Take photo"
                >
                  <Camera className="w-4 h-4" />
                </button>

                <button
                  type="button"
                  onClick={() => handleSend()}
                  disabled={(!message.trim() && !attachedImage) || disabled || isSending}
                  className={cn(
                    "p-2 rounded-xl transition-all flex items-center justify-center ml-1",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-500/30",
                    (message.trim() || attachedImage) && !disabled && !isSending
                      ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md hover:shadow-lg hover:opacity-95 active:opacity-90"
                      : "bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed"
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
        <DialogContent className="sm:max-w-[600px] bg-white/95 backdrop-blur-xl border-gray-200/50 shadow-xl">
          <DialogHeader>
            <DialogTitle className="text-center text-lg font-medium text-gray-900">Take a Photo</DialogTitle>
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
                    className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-blue-500 hover:bg-blue-600 rounded-xl px-5 py-2 text-sm font-medium shadow-lg"
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
                    className="rounded-xl border-gray-300 hover:bg-gray-50 px-5"
                  >
                    Retake
                  </Button>
                  <Button
                    onClick={confirmImage}
                    className="bg-blue-500 hover:bg-blue-600 rounded-xl px-5 shadow-md"
                  >
                    Use Photo
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* CSS for floating animation and enhanced indicators */}
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

        @keyframes voicePulse {
          0% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
          }
        }

        @keyframes ttsPulse {
          0% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
          }
        }
      `}</style>
    </>
  )
}
