import { useEffect, useRef, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Bot,
  User,
  Copy,
  Edit,
  RotateCcw,
  MoreVertical,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface EventsTabProps {
  ref: React.RefObject<{ scrollToBottom: () => void }>;
  appName: string;
  userId: string;
  sessionId: string;
  events: any[];
  onResendMessage?: (text: string) => void;
  onEditMessage?: (messageId: string, newText: string) => void;
  isLoading?: boolean; // Add this prop to track SSE loading state
}

// Loading component with animated dots
const LoadingMessage = () => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex gap-3 group relative justify-start animate-in fade-in-0 duration-300">
      <div className="flex-shrink-0">
        <div className="w-8 h-8 rounded-lg overflow-hidden">
          <img
            src="/face.png"
            alt="AI Assistant"
            className="w-full h-full object-cover"
          />
        </div>
      </div>

      <div className="flex flex-col gap-1 max-w-[70%]">
        <div className="flex items-end gap-2">
          <div className="rounded-2xl px-4 py-3 relative bg-gray-100 border border-gray-200 text-gray-900 dark:bg-[#1a1a1f] dark:border-[#2a2a30] dark:text-[#d0d0d8]">
            <div className="flex items-center gap-2">
              {/* Animated thinking indicator */}
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
              </div>
              <span className="text-gray-600 dark:text-gray-400 text-sm">
                Thinking{dots}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced loading component with more visual flair
const EnhancedLoadingMessage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const steps = [
    'Processing your request',
    'Analyzing context',
    'Generating response',
    'Almost ready',
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex gap-3 group relative justify-start animate-in fade-in-0 duration-300">
      <div className="flex-shrink-0">
        <div className="w-8 h-8 rounded-lg overflow-hidden relative">
          <img
            src="/face.png"
            alt="AI Assistant"
            className="w-full h-full object-cover"
          />
          {/* Pulsing overlay */}
          <div className="absolute inset-0 bg-blue-500/20 rounded-lg animate-pulse"></div>
        </div>
      </div>

      <div className="flex flex-col gap-1 max-w-[70%]">
        <div className="flex items-end gap-2">
          <div className="rounded-2xl px-4 py-3 relative bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-200 text-gray-900 dark:from-[#1a1a1f] dark:to-[#1e1e23] dark:border-[#2a2a30] dark:text-[#d0d0d8]">
            <div className="flex flex-col gap-2">
              {/* Progress bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                <div className="bg-blue-500 h-1.5 rounded-full animate-pulse transition-all duration-1000 w-3/4"></div>
              </div>

              {/* Dynamic status text */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                </div>
                <span className="text-sm font-medium transition-all duration-500">
                  {steps[currentStep]}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Minimal elegant loading
const MinimalLoadingMessage = () => (
  <div className="flex gap-3 group relative justify-start animate-in fade-in-0 duration-300">
    <div className="flex-shrink-0">
      <div className="w-8 h-8 rounded-lg overflow-hidden">
        <img
          src="/face.png"
          alt="AI Assistant"
          className="w-full h-full object-cover"
        />
      </div>
    </div>

    <div className="flex flex-col gap-1 max-w-[70%]">
      <div className="flex items-end gap-2">
        <div className="rounded-2xl px-4 py-3 relative bg-gray-100 border border-gray-200 text-gray-900 dark:bg-[#1a1a1f] dark:border-[#2a2a30] dark:text-[#d0d0d8]">
          <div className="flex items-center gap-3">
            <div className="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-ping"></div>
            <div className="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-ping [animation-delay:0.2s]"></div>
            <div className="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full animate-ping [animation-delay:0.4s]"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Simple markdown parser for basic formatting
const parseMarkdown = (text: string) => {
  if (!text) return text;

  return (
    text
      // Bold text (**text** or __text__)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')

      // Italic text (*text* or _text_)
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>')

      // Code inline (`code`)
      .replace(
        /`([^`]+)`/g,
        '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>',
      )

      // Headers (# ## ###)
      .replace(
        /^### (.*$)/gim,
        '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>',
      )
      .replace(
        /^## (.*$)/gim,
        '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>',
      )
      .replace(
        /^# (.*$)/gim,
        '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>',
      )

      // Code blocks (```code```)
      .replace(
        /```([\s\S]*?)```/g,
        '<pre class="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto my-2"><code class="text-sm">$1</code></pre>',
      )

      // Lists
      .replace(/^\* (.*$)/gim, '<li class="ml-4">• $1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4">• $1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li class="ml-4 list-decimal">$1</li>')

      // Line breaks
      .replace(/\n\n/g, '</p><p class="mb-2">')
      .replace(/\n/g, '<br />')
  );
};

// Component to render markdown text
const MarkdownText = ({
  text,
  className,
}: {
  text: string;
  className?: string;
}) => {
  const parsedText = parseMarkdown(text);

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: `<p class="mb-2">${parsedText}</p>` }}
    />
  );
};

export function EventsTab({
  ref,
  appName,
  userId,
  sessionId,
  events = [],
  onResendMessage,
  onEditMessage,
  isLoading = false, // Add this prop
}: EventsTabProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');

  // Auto-scroll to bottom when new messages arrive or when loading state changes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, isLoading]);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleEdit = (messageId: string, text: string) => {
    setEditingMessageId(messageId);
    setEditText(text);
  };

  const handleSaveEdit = (messageId: string) => {
    if (onEditMessage && editText.trim()) {
      onEditMessage(messageId, editText);
    }
    setEditingMessageId(null);
    setEditText('');
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditText('');
  };

  const formatTimestamp = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      const now = new Date();
      const isToday = date.toDateString() === now.toDateString();

      if (isToday) {
        // Format as HH:mm
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      } else {
        // Format as MMM d, HH:mm
        const months = [
          'Jan',
          'Feb',
          'Mar',
          'Apr',
          'May',
          'Jun',
          'Jul',
          'Aug',
          'Sep',
          'Oct',
          'Nov',
          'Dec',
        ];
        const month = months[date.getMonth()];
        const day = date.getDate();
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${month} ${day}, ${hours}:${minutes}`;
      }
    } catch {
      return '';
    }
  };

  // Show loading message if SSE is active but no events yet
  const shouldShowLoading = isLoading && events.length === 0;

  if (events.length === 0 && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <img
            src="/duck.gif"
            className="w-16 h-16 text-gray-300 dark:text-[#3a3a40] mx-auto mb-4"
          />
          <p className="text-gray-600 dark:text-[#a0a0a8] text-lg">
            Start a conversation
          </p>
          <p className="text-gray-500 dark:text-[#6a6a70] text-sm mt-2">
            Type a message below
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6" ref={scrollRef}>
        {events.map((event, index) => {
          // Create a unique key for each event
          const eventKey =
            event.id || `${event.author}-${event.timestamp}-${index}`;
          const isUser =
            event.author === 'user' || event.content?.role === 'user';

          // Extract message text and images
          let messageText = event.text || '';
          let messageImages: string[] = [];

          if (event.content?.parts) {
            for (const part of event.content.parts) {
              if (part.text) {
                messageText = part.text;
              } else if (part.inline_data) {
                // Convert inline_data to data URL
                const mimeType = part.inline_data.mime_type || 'image/jpeg';
                const dataUrl = `data:${mimeType};base64,${part.inline_data.data}`;
                messageImages.push(dataUrl);
              }
            }
          } else if (!messageText && event.content?.parts?.[0]?.text) {
            messageText = event.content.parts[0].text;
          } else if (!messageText && typeof event.content === 'string') {
            messageText = event.content;
          }

          // Also check for function calls from the event
          const functionCalls =
            event.function_calls || event.actions?.function_calls;
          const functionResponses =
            event.function_responses || event.actions?.function_responses;

          // Skip empty events
          if (
            !messageText &&
            !functionCalls &&
            !functionResponses &&
            messageImages.length === 0
          ) {
            return null;
          }

          const isEditing = editingMessageId === eventKey;

          return (
            <div
              key={eventKey}
              className={cn(
                'flex gap-3 group relative',
                isUser ? 'justify-end' : 'justify-start',
              )}
            >
              {!isUser && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-lg overflow-hidden">
                    <img
                      src="/face.png"
                      alt="AI Assistant"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              )}

              <div className="flex flex-col gap-1 max-w-[70%]">
                <div className="flex items-end gap-2">
                  <div
                    className={cn(
                      'rounded-2xl px-4 py-3 relative',
                      isUser
                        ? 'bg-blue-600 text-white dark:bg-blue-500'
                        : 'bg-gray-100 border border-gray-200 text-gray-900 dark:bg-[#1a1a1f] dark:border-[#2a2a30] dark:text-[#d0d0d8]',
                    )}
                  >
                    {isEditing ? (
                      <div className="space-y-2">
                        <Textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="min-h-[60px] bg-transparent border-0 p-0 resize-none focus:ring-0"
                          autoFocus
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleSaveEdit(eventKey)}
                            className="h-7 px-2"
                          >
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={handleCancelEdit}
                            className="h-7 px-2"
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {messageText && (
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <MarkdownText
                              text={messageText}
                              className="whitespace-pre-wrap break-words"
                            />
                            {event.isStreaming && (
                              <span className="inline-block w-1 h-4 bg-current opacity-70 animate-pulse ml-1 align-middle" />
                            )}
                          </div>
                        )}

                        {/* Display attached images */}
                        {messageImages.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {messageImages.map((imageUrl, idx) => (
                              <img
                                key={idx}
                                src={imageUrl}
                                alt={`Message attachment ${idx + 1}`}
                                className="max-w-full rounded-lg"
                                style={{ maxHeight: '300px' }}
                              />
                            ))}
                          </div>
                        )}
                      </>
                    )}

                    {functionCalls && functionCalls.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                          Function calls:
                        </p>
                        {functionCalls.map((call: any, idx: number) => (
                          <div
                            key={idx}
                            className="text-sm bg-gray-50 dark:bg-[#0e0e10] p-2 rounded text-blue-700 dark:text-blue-400 font-mono"
                          >
                            {call.name}(
                            {call.arguments
                              ? JSON.stringify(call.arguments)
                              : ''}
                            )
                          </div>
                        ))}
                      </div>
                    )}

                    {functionResponses && functionResponses.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                          Function responses:
                        </p>
                        {functionResponses.map((response: any, idx: number) => (
                          <div
                            key={idx}
                            className="text-sm bg-gray-50 dark:bg-[#0e0e10] p-2 rounded"
                          >
                            <span className="text-green-700 dark:text-green-400 font-mono">
                              {response.name}
                            </span>
                            <span className="text-gray-600 dark:text-[#a0a0a8]">
                              :{' '}
                              {JSON.stringify(
                                response.response_data || response.data,
                              )}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Action Menu */}
                  {messageText && !event.isStreaming && (
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align={isUser ? 'end' : 'start'}
                          className="bg-white dark:bg-[#2a2a30] border-gray-200 dark:border-[#3a3a40]"
                        >
                          <DropdownMenuItem
                            onClick={() => handleCopy(messageText, eventKey)}
                            className="text-gray-700 dark:text-[#d0d0d8] hover:bg-gray-100 dark:hover:bg-[#3a3a40] hover:text-gray-900 dark:hover:text-white"
                          >
                            {copiedMessageId === eventKey ? (
                              <>
                                <Check className="mr-2 h-4 w-4" />
                                Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="mr-2 h-4 w-4" />
                                Copy
                              </>
                            )}
                          </DropdownMenuItem>
                          {isUser && (
                            <>
                              <DropdownMenuItem
                                onClick={() =>
                                  handleEdit(eventKey, messageText)
                                }
                                className="text-gray-700 dark:text-[#d0d0d8] hover:bg-gray-100 dark:hover:bg-[#3a3a40] hover:text-gray-900 dark:hover:text-white"
                              >
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              {onResendMessage && (
                                <DropdownMenuItem
                                  onClick={() => onResendMessage(messageText)}
                                  className="text-gray-700 dark:text-[#d0d0d8] hover:bg-gray-100 dark:hover:bg-[#3a3a40] hover:text-gray-900 dark:hover:text-white"
                                >
                                  <RotateCcw className="mr-2 h-4 w-4" />
                                  Resend
                                </DropdownMenuItem>
                              )}
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  )}
                </div>

                {/* Timestamp */}
                {event.timestamp && (
                  <span
                    className={cn(
                      'text-xs text-gray-500 dark:text-[#6a6a70] px-1',
                      isUser ? 'text-right' : 'text-left',
                    )}
                  >
                    {formatTimestamp(event.timestamp)}
                  </span>
                )}
              </div>

              {isUser && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-[#2a2a30] flex items-center justify-center">
                    <User className="w-4 h-4 text-gray-600 dark:text-[#a0a0a8]" />
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {/* Show loading message when SSE is active but no events yet */}
        {shouldShowLoading && (
          <div className="space-y-4">
            {/* You can choose which loading style you prefer */}
            <EnhancedLoadingMessage />
            {/* Alternative loading styles: */}
            {/* <LoadingMessage /> */}
            {/* <MinimalLoadingMessage /> */}
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
