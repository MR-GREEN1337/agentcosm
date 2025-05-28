import { useState, useRef, useCallback, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';
import {
  Send,
  Paperclip,
  Mic,
  MicOff,
  Camera,
  X,
  Volume2,
  VolumeX,
  Square,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Webcam from 'react-webcam';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface MessageInputProps {
  onSendMessage: (message: any) => void;
  disabled?: boolean;
  lastAiMessage?: string;
  gcpTtsEndpoint?: string;
  voiceConfig?: {
    languageCode: string;
    name: string;
    ssmlGender: string;
  };
  // Add these optional props to help with debugging
  sendMessage?: (message: any) => void; // Direct SSE sendMessage function
  isLoading?: boolean; // SSE loading state
}

interface UseAutoResizeTextareaProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(textarea.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY),
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight],
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  return { textareaRef, adjustHeight };
}

// Simple TTS cache
class TTSCache {
  private cache = new Map<string, ArrayBuffer>();
  private maxSize = 20;

  set(text: string, audioBuffer: ArrayBuffer) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(this.hashText(text), audioBuffer);
  }

  get(text: string): ArrayBuffer | null {
    return this.cache.get(this.hashText(text)) || null;
  }

  private hashText(text: string): string {
    return btoa(text.substring(0, 50)).replace(/[^a-zA-Z0-9]/g, '');
  }
}

const ttsCache = new TTSCache();

export function MessageInput({
  onSendMessage,
  disabled = false,
  lastAiMessage,
  gcpTtsEndpoint = '/api/gcp-tts',
  voiceConfig = {
    languageCode: 'en-US',
    name: 'en-US-Neural2-F',
    ssmlGender: 'FEMALE',
  },
  sendMessage, // Optional direct SSE function
  isLoading, // Optional SSE loading state
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [isInputFocused, setIsInputFocused] = useState(false);

  // Audio states
  const [isListening, setIsListening] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isGeneratingTTS, setIsGeneratingTTS] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [conversationMode, setConversationMode] = useState(false);

  // Refs
  const webcamRef = useRef<Webcam>(null);
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const currentAudioSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const pendingTTSRef = useRef<AbortController | null>(null);
  const lastProcessedMessageRef = useRef<string>('');
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isProcessingRef = useRef(false);

  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 44,
    maxHeight: 160,
  });

  // Debug: Log what onSendMessage function we received
  useEffect(() => {
    console.log(
      '🔍 MessageInput received onSendMessage function:',
      typeof onSendMessage,
    );
    console.log('🔍 Function name:', onSendMessage?.name || 'anonymous');

    // Test call to see if function is working
    console.log('🧪 Testing onSendMessage function availability...');
  }, [onSendMessage]);

  // Debug wrapper for onSendMessage to intercept all calls
  const debugOnSendMessage = useCallback(
    async (payload: any) => {
      console.log('🚀 ===== DEBUG onSendMessage WRAPPER =====');
      console.log('📦 Payload received:', JSON.stringify(payload, null, 2));
      console.log('🔍 Payload type:', typeof payload);
      console.log('🔍 Payload parts:', payload?.content?.parts);
      console.log('🔍 Payload role:', payload?.content?.role);

      try {
        console.log('📡 Calling original onSendMessage...');
        const result = await onSendMessage(payload);
        console.log('✅ Original onSendMessage completed successfully');
        console.log('📤 Result:', result);
        return result;
      } catch (error) {
        console.error('❌ Original onSendMessage failed:', error);

        // Emergency fallback: try direct sendMessage if available
        if (sendMessage) {
          console.log(
            '🆘 Trying emergency fallback with direct sendMessage...',
          );
          try {
            const fallbackResult = await sendMessage(payload);
            console.log('✅ Emergency fallback succeeded!');
            return fallbackResult;
          } catch (fallbackError) {
            console.error('❌ Emergency fallback also failed:', fallbackError);
          }
        }

        throw error;
      } finally {
        console.log('🚀 ===== DEBUG onSendMessage WRAPPER END =====');
      }
    },
    [onSendMessage, sendMessage],
  );

  // Initialize Audio Context
  useEffect(() => {
    const initAudio = () => {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext ||
          window.webkitAudioContext)();
      }
    };

    const handleClick = () => {
      initAudio();
      document.removeEventListener('click', handleClick);
    };

    document.addEventListener('click', handleClick);
    return () => {
      document.removeEventListener('click', handleClick);
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Initialize Speech Recognition
  useEffect(() => {
    if (
      !('webkitSpeechRecognition' in window) &&
      !('SpeechRecognition' in window)
    ) {
      console.warn('Speech recognition not supported');
      return;
    }

    const SpeechRecognition =
      window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      console.log('🎤 Started listening');
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      const fullTranscript = finalTranscript || interimTranscript;
      setTranscript(fullTranscript);

      // Reset silence timeout on speech
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }

      // If we have final transcript, set timeout to process it
      if (finalTranscript.trim()) {
        console.log('📝 Final transcript:', finalTranscript);
        silenceTimeoutRef.current = setTimeout(() => {
          processSpeech(finalTranscript.trim());
        }, 1500); // 1.5 seconds after final speech
      }
    };

    recognition.onend = () => {
      console.log('🎤 Stopped listening');
      setIsListening(false);
      setTranscript('');

      // Auto-restart in conversation mode
      if (conversationMode && !isProcessingRef.current) {
        setTimeout(() => {
          if (conversationMode && !isPlaying && !isGeneratingTTS) {
            startListening();
          }
        }, 1000);
      }
    };

    recognition.onerror = (event) => {
      console.error('🚨 Speech recognition error:', event.error);
      setIsListening(false);
      setTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognition && isListening) {
        recognition.stop();
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, [conversationMode, isPlaying, isGeneratingTTS]);

  // Stop current audio
  const stopCurrentAudio = useCallback(() => {
    if (currentAudioSourceRef.current) {
      currentAudioSourceRef.current.stop();
      currentAudioSourceRef.current = null;
    }
    if (pendingTTSRef.current) {
      pendingTTSRef.current.abort();
      pendingTTSRef.current = null;
    }
    setIsPlaying(false);
    setIsGeneratingTTS(false);
  }, []);

  // Process speech and send message
  const processSpeech = useCallback(
    async (speechText: string) => {
      if (!speechText || isProcessingRef.current) return;

      console.log('🎤 ===== VOICE MESSAGE START =====');
      console.log('💬 Processing speech:', speechText);
      console.log('🔍 onSendMessage function:', onSendMessage);
      console.log('🔍 onSendMessage type:', typeof onSendMessage);

      isProcessingRef.current = true;

      // Stop current audio
      stopCurrentAudio();

      // Stop listening
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }

      setTranscript('');

      // Create message payload that matches your SSE format
      const messagePayload = {
        content: {
          parts: [{ text: speechText }],
          role: 'user',
        },
      };

      console.log(
        '📦 Voice message payload:',
        JSON.stringify(messagePayload, null, 2),
      );

      try {
        console.log('📤 Calling onSendMessage with voice payload...');

        // Call onSendMessage which should trigger the SSE stream
        await onSendMessage(messagePayload);

        console.log('✅ Voice message sent successfully');
        console.log('🎤 ===== VOICE MESSAGE END =====');
      } catch (error) {
        console.error('❌ Error sending speech message:', error);
        console.log('🎤 ===== VOICE MESSAGE ERROR =====');
      }

      isProcessingRef.current = false;
    },
    [onSendMessage, isListening, stopCurrentAudio],
  );

  // Start listening
  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;

    console.log('🎤 Starting to listen...');

    // Stop any current audio when user wants to speak
    stopCurrentAudio();

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start listening:', error);
    }
  }, [isListening, stopCurrentAudio]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
    }
  }, [isListening]);

  // Toggle conversation mode
  const toggleConversationMode = useCallback(() => {
    const newMode = !conversationMode;
    setConversationMode(newMode);

    if (newMode) {
      console.log('🗣️ Entering conversation mode');
      setTimeout(() => startListening(), 500);
    } else {
      console.log('🔇 Exiting conversation mode');
      stopListening();
    }
  }, [conversationMode, startListening, stopListening]);

  // Generate and play TTS
  const generateAndPlayTTS = useCallback(
    async (text: string) => {
      if (isMuted || !text.trim() || text.length < 10) return;

      console.log('🎵 Generating TTS for:', text.substring(0, 50) + '...');

      // Stop current audio
      stopCurrentAudio();

      // Check cache
      const cachedAudio = ttsCache.get(text);
      if (cachedAudio) {
        console.log('🔊 Playing cached audio');
        playAudioBuffer(cachedAudio);
        return;
      }

      setIsGeneratingTTS(true);
      const abortController = new AbortController();
      pendingTTSRef.current = abortController;

      try {
        const response = await fetch(gcpTtsEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            input: { text },
            voice: voiceConfig,
            audioConfig: {
              audioEncoding: 'LINEAR16',
              sampleRateHertz: 24000,
              speakingRate: 1.2,
            },
          }),
          signal: abortController.signal,
        });

        if (!response.ok) throw new Error(`TTS Error: ${response.status}`);

        const audioBuffer = await response.arrayBuffer();
        console.log('🎵 TTS generated, playing...');

        // Cache and play
        ttsCache.set(text, audioBuffer);

        if (!abortController.signal.aborted) {
          playAudioBuffer(audioBuffer);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('TTS Error:', error);
        }
      } finally {
        setIsGeneratingTTS(false);
      }
    },
    [isMuted, gcpTtsEndpoint, voiceConfig, stopCurrentAudio],
  );

  // Play audio buffer
  const playAudioBuffer = useCallback(
    async (arrayBuffer: ArrayBuffer) => {
      try {
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext ||
            window.webkitAudioContext)();
        }

        const audioContext = audioContextRef.current;
        if (audioContext.state === 'suspended') {
          await audioContext.resume();
        }

        setIsPlaying(true);
        console.log('🔊 Playing audio...');

        const audioBuffer = await audioContext.decodeAudioData(
          arrayBuffer.slice(0),
        );
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);

        currentAudioSourceRef.current = source;

        source.onended = () => {
          console.log('🔊 Audio finished');
          currentAudioSourceRef.current = null;
          setIsPlaying(false);

          // In conversation mode, start listening after AI finishes
          if (conversationMode) {
            setTimeout(() => {
              if (conversationMode && !isListening) {
                console.log('🎤 Auto-starting listening after AI speech');
                startListening();
              }
            }, 800);
          }
        };

        source.start(0);
      } catch (error) {
        console.error('Audio playback error:', error);
        setIsPlaying(false);
      }
    },
    [conversationMode, isListening, startListening],
  );

  // Handle new AI messages
  useEffect(() => {
    if (!lastAiMessage || lastProcessedMessageRef.current === lastAiMessage) {
      return;
    }

    console.log('🤖 New AI message received');
    lastProcessedMessageRef.current = lastAiMessage;

    // Small delay to ensure message is complete
    setTimeout(() => {
      if (lastAiMessage === lastProcessedMessageRef.current) {
        generateAndPlayTTS(lastAiMessage);
      }
    }, 300);
  }, [lastAiMessage, generateAndPlayTTS]);

  // Manual send message
  const handleSend = async (textToSend?: string) => {
    const messageText = textToSend || message.trim();

    if ((messageText || attachedImage) && !disabled && !isSending) {
      console.log('⌨️ ===== TEXT MESSAGE START =====');
      console.log('📝 Text message:', messageText);

      setIsSending(true);
      stopCurrentAudio();

      const parts: any[] = [];
      if (messageText) parts.push({ text: messageText });
      if (attachedImage) {
        parts.push({
          inline_data: {
            mime_type: 'image/jpeg',
            data: attachedImage.split(',')[1],
          },
        });
      }

      const messagePayload = {
        content: { parts, role: 'user' },
      };

      console.log(
        '📦 Text message payload:',
        JSON.stringify(messagePayload, null, 2),
      );

      try {
        console.log('📤 Calling onSendMessage with text payload...');
        await debugOnSendMessage(messagePayload);

        // Only clear manual message input, not voice transcript
        if (!textToSend) {
          setMessage('');
          adjustHeight(true);
        }
        setAttachedImage(null);
        console.log('✅ Text message sent successfully');
        console.log('⌨️ ===== TEXT MESSAGE END =====');
      } catch (error) {
        console.error('❌ Error sending text message:', error);
        console.log('⌨️ ===== TEXT MESSAGE ERROR =====');
      } finally {
        setIsSending(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (!isMuted) {
      stopCurrentAudio();
    }
  };

  // Camera functions
  const captureImage = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) setCapturedImage(imageSrc);
  }, []);

  const retakeImage = () => setCapturedImage(null);
  const confirmImage = () => {
    if (capturedImage) {
      setAttachedImage(capturedImage);
      setCapturedImage(null);
      setShowCamera(false);
    }
  };
  const removeAttachedImage = () => setAttachedImage(null);

  return (
    <>
      <div className="w-full px-2 sm:px-4 py-2 sm:py-4">
        <div className="max-w-3xl mx-auto">
          <div
            className={cn(
              'relative backdrop-blur-xl rounded-2xl border shadow-lg transition-all duration-300 overflow-hidden',
              'bg-white/90 border-gray-200/50 text-gray-900 hover:bg-white/95',
              'dark:bg-gray-900/90 dark:border-gray-700/50 dark:text-white dark:hover:bg-gray-900/95',
              isInputFocused && 'border-blue-500/30 shadow-xl',
              isListening && 'border-red-500/50 shadow-xl shadow-red-500/20',
              isPlaying && 'border-green-500/50 shadow-xl shadow-green-500/20',
              isGeneratingTTS &&
                'border-blue-500/50 shadow-xl shadow-blue-500/20',
            )}
          >
            {/* Status Bar */}
            {(isListening ||
              isPlaying ||
              isGeneratingTTS ||
              conversationMode) && (
              <div className="px-4 py-2 border-b border-gray-200/30 bg-gray-50/50 dark:border-gray-600/30 dark:bg-gray-800/40">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <div
                      className={cn(
                        'w-2 h-2 rounded-full animate-pulse',
                        isListening && 'bg-red-500',
                        isPlaying && 'bg-green-500',
                        isGeneratingTTS && 'bg-blue-500',
                        conversationMode &&
                          !isListening &&
                          !isPlaying &&
                          !isGeneratingTTS &&
                          'bg-purple-500',
                      )}
                    ></div>
                    <span className="text-gray-700 dark:text-gray-300">
                      {isListening
                        ? transcript || 'Listening...'
                        : isGeneratingTTS
                          ? 'Generating speech...'
                          : isPlaying
                            ? 'AI is speaking...'
                            : conversationMode
                              ? 'Conversation mode active'
                              : ''}
                    </span>
                  </div>
                  {conversationMode && (
                    <button
                      onClick={toggleConversationMode}
                      className="text-xs bg-purple-100 dark:bg-purple-900 px-2 py-1 rounded-full hover:bg-purple-200 dark:hover:bg-purple-800"
                    >
                      Exit
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Attached Image */}
            {attachedImage && (
              <div className="p-3 border-b border-gray-200/30">
                <div className="relative inline-block">
                  <img
                    src={attachedImage}
                    alt="Attached"
                    className="h-20 rounded-xl object-cover"
                  />
                  <button
                    onClick={removeAttachedImage}
                    className="absolute -top-1.5 -right-1.5 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="flex items-end">
              <div className="flex-1">
                <Textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value);
                    adjustHeight();
                  }}
                  onKeyDown={handleKeyDown}
                  onFocus={() => setIsInputFocused(true)}
                  onBlur={() => setIsInputFocused(false)}
                  placeholder={
                    conversationMode
                      ? 'Speak or type your message...'
                      : isListening
                        ? 'Listening...'
                        : 'Type a message or click mic to speak...'
                  }
                  className="w-full px-4 py-3.5 resize-none bg-transparent border-none focus:outline-none text-sm min-h-[44px]"
                  disabled={disabled || isSending || isListening}
                />
              </div>

              {/* Buttons */}
              <div className="flex items-center gap-1.5 px-3 pb-3">
                <button
                  type="button"
                  className="p-2 rounded-xl text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors"
                  disabled={disabled || isSending}
                >
                  <Paperclip className="w-4 h-4" />
                </button>

                {/* Voice Button */}
                <button
                  type="button"
                  onClick={
                    conversationMode
                      ? toggleConversationMode
                      : isListening
                        ? stopListening
                        : startListening
                  }
                  onDoubleClick={
                    !conversationMode ? toggleConversationMode : undefined
                  }
                  className={cn(
                    'p-2 rounded-xl transition-all',
                    isListening
                      ? 'bg-red-500 text-white animate-pulse'
                      : conversationMode
                        ? 'bg-purple-500 text-white'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800',
                  )}
                  disabled={disabled || isSending}
                  title={
                    conversationMode
                      ? 'Exit conversation mode'
                      : 'Click to speak, double-click for conversation mode'
                  }
                >
                  {isListening ? (
                    <MicOff className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </button>

                {/* Audio Control */}
                <button
                  type="button"
                  onClick={toggleMute}
                  className={cn(
                    'p-2 rounded-xl transition-colors',
                    isMuted
                      ? 'text-gray-400'
                      : isPlaying
                        ? 'text-green-500 animate-pulse'
                        : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200',
                  )}
                  disabled={disabled || isSending}
                >
                  {isMuted ? (
                    <VolumeX className="w-4 h-4" />
                  ) : (
                    <Volume2 className="w-4 h-4" />
                  )}
                </button>

                {/* Stop Audio Button */}
                {(isPlaying || isGeneratingTTS) && (
                  <button
                    type="button"
                    onClick={stopCurrentAudio}
                    className="p-2 rounded-xl text-orange-500 hover:text-orange-600 hover:bg-orange-100 dark:hover:bg-orange-900 transition-colors"
                  >
                    <Square className="w-4 h-4" />
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => setShowCamera(true)}
                  className="p-2 rounded-xl text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors hidden sm:flex"
                  disabled={disabled || isSending}
                >
                  <Camera className="w-4 h-4" />
                </button>

                <button
                  type="button"
                  onClick={() => handleSend()}
                  disabled={
                    (!message.trim() && !attachedImage) || disabled || isSending
                  }
                  className={cn(
                    'p-2 rounded-xl transition-all ml-1',
                    (message.trim() || attachedImage) && !disabled && !isSending
                      ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-md'
                      : 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed',
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

          {/* Help Text */}
          {conversationMode && (
            <div className="mt-2 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                🗣️ Conversation mode: AI will listen after speaking
              </p>
            </div>
          )}
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
              <div className="relative rounded-xl overflow-hidden">
                <Webcam
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full rounded-xl"
                />
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                  <Button
                    onClick={captureImage}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Capture
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <img
                  src={capturedImage}
                  alt="Captured"
                  className="w-full rounded-xl"
                />
                <div className="flex gap-4 justify-center">
                  <Button onClick={retakeImage} variant="outline">
                    Retake
                  </Button>
                  <Button
                    onClick={confirmImage}
                    className="bg-blue-500 hover:bg-blue-600"
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
  );
}
