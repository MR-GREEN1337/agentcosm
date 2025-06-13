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
  Brain,
  Cpu,
  Zap,
  Target,
  ChevronDown,
  ChevronUp,
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface EventsTabProps {
  ref: React.RefObject<{ scrollToBottom: () => void }>;
  appName: string;
  userId: string;
  sessionId: string;
  events: any[];
  onResendMessage?: (text: string) => void;
  onEditMessage?: (messageId: string, newText: string) => void;
  isLoading?: boolean;
}

// Agent avatar configurations
const AGENT_CONFIGS = {
  liminal_market_opportunity_coordinator: {
    name: 'Market Coordinator',
    avatar: '/face.png',
    color: 'blue',
    showMessages: true,
  },
  research_agent: {
    name: 'Research Agent',
    avatar: null,
    icon: Brain,
    color: 'purple',
    showMessages: false,
  },
  analysis_agent: {
    name: 'Analysis Agent',
    avatar: null,
    icon: Cpu,
    color: 'green',
    showMessages: false,
  },
  strategy_agent: {
    name: 'Strategy Agent',
    avatar: null,
    icon: Target,
    color: 'orange',
    showMessages: false,
  },
  execution_agent: {
    name: 'Execution Agent',
    avatar: null,
    icon: Zap,
    color: 'red',
    showMessages: false,
  },
};

// Agent message modal component using shadcn dialog
const AgentMessageModal = ({
  agent,
  messages,
  isOpen,
  onClose,
}: {
  agent: string;
  messages: any[];
  isOpen: boolean;
  onClose: () => void;
}) => {
  const config: any = AGENT_CONFIGS[agent as keyof typeof AGENT_CONFIGS] || {
    name: agent,
    icon: Bot,
    color: 'blue',
  };

  const IconComponent = config.icon;
  const colorClasses = {
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    orange: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
  };

  // Helper function to extract meaningful content from messages
  const getMessageContent = (message: any) => {
    // Check for text in various locations
    if (message.text && message.text.trim()) {
      return { content: message.text, type: 'text' };
    }
    if (
      message.content?.parts?.[0]?.text &&
      message.content.parts[0].text.trim()
    ) {
      return { content: message.content.parts[0].text, type: 'text' };
    }
    if (typeof message.content === 'string' && message.content.trim()) {
      return { content: message.content, type: 'text' };
    }

    // Check for function calls or other structured data
    if (message.function_calls || message.actions?.function_calls) {
      const data = message.function_calls || message.actions.function_calls;
      return { content: JSON.stringify(data, null, 2), type: 'json' };
    }

    if (message.function_responses || message.actions?.function_responses) {
      const data =
        message.function_responses || message.actions.function_responses;
      return { content: JSON.stringify(data, null, 2), type: 'json' };
    }

    // If nothing meaningful found, return null to skip this message
    return null;
  };

  // Helper function to detect if content is JSON
  const isJsonContent = (content: string) => {
    try {
      JSON.parse(content);
      return true;
    } catch {
      return false;
    }
  };

  // Filter out messages with no meaningful content
  const meaningfulMessages = messages.filter(
    (message) => getMessageContent(message) !== null,
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl w-[90vw] h-[85vh] flex flex-col p-0">
        <DialogHeader className="p-6 pb-4 border-b shrink-0">
          <DialogTitle className="flex items-center gap-3">
            <div
              className={cn(
                'w-8 h-8 rounded-lg border flex items-center justify-center',
                colorClasses[config.color as keyof typeof colorClasses],
              )}
            >
              {IconComponent && <IconComponent className="w-4 h-4" />}
            </div>
            <span>{config.name}</span>
            <span className="text-sm font-normal text-muted-foreground">
              ({meaningfulMessages.length} messages)
            </span>
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-6 space-y-4">
              {meaningfulMessages.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No messages available for this agent
                </div>
              ) : (
                meaningfulMessages.map((message, idx) => {
                  const contentData = getMessageContent(message);
                  if (!contentData) return null;

                  const { content, type } = contentData;
                  const shouldUseMarkdown =
                    type === 'text' && !isJsonContent(content);

                  return (
                    <div
                      key={idx}
                      className="p-4 bg-muted/50 rounded-lg border"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="text-xs text-muted-foreground font-medium">
                          Message {idx + 1}
                        </div>
                        {message.timestamp && (
                          <div className="text-xs text-muted-foreground">
                            {new Date(
                              message.timestamp * 1000,
                            ).toLocaleString()}
                          </div>
                        )}
                      </div>

                      <div className="text-sm">
                        {shouldUseMarkdown ? (
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <MarkdownText
                              text={content}
                              className="whitespace-pre-wrap break-words"
                            />
                          </div>
                        ) : (
                          <pre className="whitespace-pre-wrap break-words font-mono text-xs bg-background p-3 rounded border overflow-x-auto">
                            {content}
                          </pre>
                        )}
                      </div>

                      {/* Content type indicator */}
                      <div className="mt-2 pt-2 border-t">
                        <span
                          className={cn(
                            'inline-block px-2 py-1 text-xs rounded-full',
                            type === 'json'
                              ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400'
                              : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
                          )}
                        >
                          {type === 'json' ? 'Structured Data' : 'Text Content'}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Agent thinking avatar component with click functionality
const AgentThinkingAvatar = ({
  agentName,
  config,
  messages,
  onClick,
}: {
  agentName: string;
  config: any;
  messages: any[];
  onClick: () => void;
}) => {
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

  const IconComponent = config.icon;
  const colorClasses = {
    purple:
      'bg-purple-500/20 text-purple-400 border-purple-500/30 hover:bg-purple-500/30',
    green:
      'bg-green-500/20 text-green-400 border-green-500/30 hover:bg-green-500/30',
    orange:
      'bg-orange-500/20 text-orange-400 border-orange-500/30 hover:bg-orange-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30 hover:bg-red-500/30',
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30 hover:bg-blue-500/30',
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-all cursor-pointer animate-pulse hover:animate-none',
        colorClasses[config.color as keyof typeof colorClasses],
      )}
    >
      <div
        className={cn(
          'w-6 h-6 rounded-lg border flex items-center justify-center',
          colorClasses[config.color as keyof typeof colorClasses],
        )}
      >
        {IconComponent && <IconComponent className="w-3 h-3" />}
      </div>
      <span>
        {config.name} thinking{dots}
      </span>
      <span className="ml-1 px-1.5 py-0.5 bg-white/20 rounded-full text-xs">
        {messages.length}
      </span>
    </button>
  );
};

// Agent activity panel that shows below user messages
const AgentActivityPanel = ({
  agentMessages,
  onAgentClick,
}: {
  agentMessages: Record<string, any[]>;
  onAgentClick: (agent: string) => void;
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const activeAgents = Object.keys(agentMessages).filter(
    (agent) =>
      agent !== 'liminal_market_opportunity_coordinator' &&
      agent !== 'user' &&
      agentMessages[agent].length > 0,
  );

  if (activeAgents.length === 0) return null;

  return (
    <div className="mt-3 p-3 bg-gray-50 dark:bg-[#0e0e10] rounded-lg border border-gray-200 dark:border-[#2a2a30]">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-sm font-medium text-gray-700 dark:text-[#d0d0d8] mb-2"
      >
        <span>Agent Activity ({activeAgents.length} active)</span>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
      </button>

      {isExpanded && (
        <div className="flex flex-wrap gap-2">
          {activeAgents.map((agentName) => {
            const config = AGENT_CONFIGS[
              agentName as keyof typeof AGENT_CONFIGS
            ] || {
              name: agentName,
              icon: Bot,
              color: 'blue',
            };
            return (
              <AgentThinkingAvatar
                key={agentName}
                agentName={agentName}
                config={config}
                messages={agentMessages[agentName]}
                onClick={() => onAgentClick(agentName)}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};

// Component to display the last agent's message
const LastAgentMessage = ({
  agent,
  message,
  onCopy,
  onAgentClick,
  copiedMessageId,
  messageId,
}: {
  agent: string;
  message: any;
  onCopy: (text: string, messageId: string) => void;
  onAgentClick: (agent: string) => void;
  copiedMessageId: string | null;
  messageId: string;
}) => {
  const config: any = AGENT_CONFIGS[agent as keyof typeof AGENT_CONFIGS] || {
    name: agent,
    icon: Bot,
    color: 'blue',
  };

  const IconComponent = config.icon;
  const colorClasses = {
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    orange: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
  };

  const getMessageContent = (event: any) => {
    let messageText = '';
    if (event.text && typeof event.text === 'string' && event.text.trim()) {
      messageText = event.text.trim();
    } else if (event.content?.parts?.length > 0) {
      for (const part of event.content.parts) {
        if (part.text && typeof part.text === 'string' && part.text.trim()) {
          messageText = part.text.trim();
          break;
        }
      }
    } else if (typeof event.content === 'string' && event.content.trim()) {
      messageText = event.content.trim();
    }
    return messageText;
  };

  const formatTimestamp = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      const now = new Date();
      const isToday = date.toDateString() === now.toDateString();

      if (isToday) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      } else {
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

  const messageContent = getMessageContent(message);
  if (!messageContent) return null;

  return (
    <div className="flex gap-3 group relative justify-start">
      <div className="flex-shrink-0">
        <button
          onClick={() => onAgentClick(agent)}
          className={cn(
            'w-8 h-8 rounded-lg border flex items-center justify-center transition-all hover:scale-105',
            colorClasses[config.color as keyof typeof colorClasses],
          )}
        >
          {config.avatar ? (
            <img
              src={config.avatar}
              alt={config.name}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            IconComponent && <IconComponent className="w-4 h-4" />
          )}
        </button>
      </div>
      <div className="flex flex-col gap-1 max-w-[70%]">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium text-gray-600 dark:text-[#a0a0a8]">
            {config.name}
          </span>
        </div>
        <div className="flex items-end gap-2">
          <div
            className={cn(
              'rounded-2xl px-4 py-3 relative border',
              colorClasses[config.color as keyof typeof colorClasses],
            )}
          >
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <MarkdownText
                text={messageContent}
                className="whitespace-pre-wrap break-words"
              />
            </div>
          </div>

          {/* Message actions */}
          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem
                  onClick={() => onCopy(messageContent, messageId)}
                >
                  {copiedMessageId === messageId ? (
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
                <DropdownMenuItem onClick={() => onAgentClick(agent)}>
                  <Bot className="mr-2 h-4 w-4" />
                  View Agent Details
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        {message.timestamp && (
          <span className="text-xs text-gray-500 dark:text-[#6a6a70] px-1 text-left">
            {formatTimestamp(message.timestamp)}
          </span>
        )}
      </div>
    </div>
  );
};

// Loading component for main coordinator
const CoordinatorLoadingMessage = ({
  agentMessages,
  onAgentClick,
}: {
  agentMessages: Record<string, any[]>;
  onAgentClick: (agent: string) => void;
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const steps = [
    'Booting up innovation protocols 🤖💡',
    'Scanning VC radar for hot sectors 📡💸',
    'Sniffing out unmet founder needs 🕵️‍♀️',
    'Indexing AI-first business ideas 📚🧠',
    'Gathering GPT-era insights 📊✨',
    'Whispering with market sentiment bots 🗣️📈',
    'Plotting disruption trajectories 🚀📍',
    'Translating hype into strategy 🔄🔥',
    'Aligning product-market-vision fit 🧲🎯',
    'Fetching SaaS gold from data mines ⛏️📊',
    'Tapping into the startup hive-mind 🐝🧬',
    'Sourcing gaps in billion-dollar markets 💼🧭',
    'Scanning angel tweets for inspiration 🐦💭',
    'Connecting dots like a VC whisperer 🔗🧞‍♂️',
    'Processing founder FOMO signals 😱📉📈',
    'Simulating launch scenarios in parallel universes 🌌🚦',
    'Loading lean startup wisdom 📦📘',
    'Unpacking user pain points 🔍💔',
    'Spying on trends before they trend 👁️🚨',
    'Converting chaos into clarity 🌪️➡️🔍',
    'Consulting with the algorithmic boardroom 🧑‍💼📟',
    'Visualizing exits before the entry 🛣️🚪💰',
    'Forecasting virality spikes 📊🚀',
    'Drafting elevator pitches for Mars 🪐📢',
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 3500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-3">
      <div className="flex gap-3 group relative justify-start animate-in fade-in-0 duration-300">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-lg overflow-hidden relative">
            <img
              src="/face.png"
              alt="Market Coordinator"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-blue-500/20 rounded-lg animate-pulse"></div>
          </div>
        </div>

        <div className="flex flex-col gap-1 max-w-[70%]">
          <div className="flex items-end gap-2">
            <div className="rounded-2xl px-4 py-3 relative bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-200 text-gray-900 dark:from-[#1a1a1f] dark:to-[#1e1e23] dark:border-[#2a2a30] dark:text-[#d0d0d8]">
              <div className="flex flex-col gap-2">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-blue-500 h-1.5 rounded-full animate-pulse transition-all duration-1000 w-3/4"></div>
                </div>
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

      {/* Show agent activity while coordinator is loading */}
      <AgentActivityPanel
        agentMessages={agentMessages}
        onAgentClick={onAgentClick}
      />
    </div>
  );
};

// Simple markdown parser for basic formatting
const parseMarkdown = (text: string) => {
  if (!text) return text;

  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    .replace(
      /`([^`]+)`/g,
      '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>',
    )
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" class="text-blue-600 dark:text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>',
    )
    .replace(
      /^### (.*$)/gim,
      '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>',
    )
    .replace(
      /^## (.*$)/gim,
      '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>',
    )
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
    .replace(
      /```([\s\S]*?)```/g,
      '<pre class="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto my-2"><code class="text-sm">$1</code></pre>',
    )
    .replace(/^\* (.*$)/gim, '<li class="ml-4">• $1</li>')
    .replace(/^- (.*$)/gim, '<li class="ml-4">• $1</li>')
    .replace(/^\d+\. (.*$)/gim, '<li class="ml-4 list-decimal">$1</li>')
    .replace(/\n\n/g, '</p><p class="mb-2">')
    .replace(/\n/g, '<br />');
};

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
  isLoading = false,
}: EventsTabProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [agentMessages, setAgentMessages] = useState<Record<string, any[]>>({});

  // Group messages by agent
  useEffect(() => {
    const messagesByAgent: Record<string, any[]> = {};

    events.forEach((event) => {
      const author = event.author || 'unknown';
      if (!messagesByAgent[author]) {
        messagesByAgent[author] = [];
      }
      messagesByAgent[author].push(event);
    });

    setAgentMessages(messagesByAgent);
  }, [events]);

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

  const handleAgentClick = (agentName: string) => {
    setSelectedAgent(agentName);
  };

  // Helper function to extract and validate message content
  const getMessageContent = (event: any) => {
    // Priority order for extracting content
    let messageText = '';

    // 1. Direct text property
    if (event.text && typeof event.text === 'string' && event.text.trim()) {
      messageText = event.text.trim();
    }
    // 2. Content parts array
    else if (event.content?.parts?.length > 0) {
      for (const part of event.content.parts) {
        if (part.text && typeof part.text === 'string' && part.text.trim()) {
          messageText = part.text.trim();
          break;
        }
      }
    }
    // 3. Direct content string
    else if (typeof event.content === 'string' && event.content.trim()) {
      messageText = event.content.trim();
    }

    return messageText;
  };

  // Helper function to check if event has meaningful content
  const hasValidContent = (event: any) => {
    const text = getMessageContent(event);
    const hasText = text && text.length > 0;
    const hasFunctionCalls =
      event.function_calls?.length > 0 ||
      event.actions?.function_calls?.length > 0;
    const hasFunctionResponses =
      event.function_responses?.length > 0 ||
      event.actions?.function_responses?.length > 0;
    const hasImages = event.content?.parts?.some(
      (part: any) => part.inline_data,
    );

    return hasText || hasFunctionCalls || hasFunctionResponses || hasImages;
  };

  const formatTimestamp = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      const now = new Date();
      const isToday = date.toDateString() === now.toDateString();

      if (isToday) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      } else {
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

  // Group events into conversation blocks (user message + responses + agent activity)
  // Filter out events with no meaningful content first
  const validEvents = events.filter(hasValidContent);

  const conversationBlocks: Array<{
    userMessage?: any;
    coordinatorMessage?: any;
    lastAgentMessage?: { agent: string; message: any }; // Add this
    agentActivity: Record<string, any[]>;
    timestamp: number;
  }> = [];

  let currentBlock: any = null;

  validEvents.forEach((event) => {
    const author = event.author || '';
    const isUser = author === 'user' || event.content?.role === 'user';
    const isCoordinator = author === 'liminal_market_opportunity_coordinator';

    if (isUser) {
      // Start new conversation block with user message
      currentBlock = {
        userMessage: event,
        coordinatorMessage: null,
        lastAgentMessage: null, // Add this
        agentActivity: {},
        timestamp: event.timestamp || Date.now() / 1000,
      };
      conversationBlocks.push(currentBlock);
    } else if (isCoordinator && currentBlock) {
      // Add coordinator response to current block
      currentBlock.coordinatorMessage = event;
    } else if (!isUser && !isCoordinator && currentBlock) {
      // Add other agent activity to current block
      if (!currentBlock.agentActivity[author]) {
        currentBlock.agentActivity[author] = [];
      }
      currentBlock.agentActivity[author].push(event);

      // Track last agent message
      currentBlock.lastAgentMessage = { agent: author, message: event };
    }
  });

  const shouldShowLoading = isLoading && conversationBlocks.length === 0;

  if (conversationBlocks.length === 0 && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <img
            src="/duck.gif"
            className="w-16 h-16 text-gray-300 dark:text-[#3a3a40] mx-auto mb-4"
          />
          <p className="text-gray-600 dark:text-[#a0a0a8] text-lg">
            Start exploring market opportunities
          </p>
          <p className="text-gray-500 dark:text-[#6a6a70] text-sm mt-2">
            Ask about business ideas and market validation
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <ScrollArea className="h-full">
        <div className="p-6 space-y-6" ref={scrollRef}>
          {conversationBlocks.map((block, blockIndex) => (
            <div key={blockIndex} className="space-y-4">
              {/* User Message */}
              {block.userMessage && (
                <div className="flex gap-3 group relative justify-end">
                  <div className="flex flex-col gap-1 max-w-[70%]">
                    <div className="flex items-end gap-2">
                      <div className="rounded-2xl px-4 py-3 relative bg-blue-600 text-white dark:bg-blue-500">
                        {/* User message content */}
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <MarkdownText
                            text={getMessageContent(block.userMessage)}
                            className="whitespace-pre-wrap break-words"
                          />
                        </div>
                      </div>

                      {/* User message actions */}
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
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() =>
                                handleCopy(
                                  getMessageContent(block.userMessage),
                                  `user-${blockIndex}`,
                                )
                              }
                            >
                              {copiedMessageId === `user-${blockIndex}` ? (
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
                            <DropdownMenuItem
                              onClick={() =>
                                handleEdit(
                                  `user-${blockIndex}`,
                                  getMessageContent(block.userMessage),
                                )
                              }
                            >
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            {onResendMessage && (
                              <DropdownMenuItem
                                onClick={() =>
                                  onResendMessage(
                                    getMessageContent(block.userMessage),
                                  )
                                }
                              >
                                <RotateCcw className="mr-2 h-4 w-4" />
                                Resend
                              </DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    {block.userMessage.timestamp && (
                      <span className="text-xs text-gray-500 dark:text-[#6a6a70] px-1 text-right">
                        {formatTimestamp(block.userMessage.timestamp)}
                      </span>
                    )}
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-[#2a2a30] flex items-center justify-center">
                      <User className="w-4 h-4 text-gray-600 dark:text-[#a0a0a8]" />
                    </div>
                  </div>
                </div>
              )}

              {/* Agent Activity Panel (below user message) */}
              <AgentActivityPanel
                agentMessages={block.agentActivity}
                onAgentClick={handleAgentClick}
              />

              {/* Coordinator Response */}
              {block.coordinatorMessage && (
                <div className="flex gap-3 group relative justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-lg overflow-hidden">
                      <img
                        src="/face.png"
                        alt="Market Coordinator"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 max-w-[70%]">
                    <div className="flex items-end gap-2">
                      <div className="rounded-2xl px-4 py-3 relative bg-gray-100 border border-gray-200 text-gray-900 dark:bg-[#1a1a1f] dark:border-[#2a2a30] dark:text-[#d0d0d8]">
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <MarkdownText
                            text={getMessageContent(block.coordinatorMessage)}
                            className="whitespace-pre-wrap break-words"
                          />
                          {block.coordinatorMessage.isStreaming && (
                            <span className="inline-block w-1 h-4 bg-current opacity-70 animate-pulse ml-1 align-middle" />
                          )}
                        </div>
                      </div>

                      {/* Coordinator message actions */}
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
                          <DropdownMenuContent align="start">
                            <DropdownMenuItem
                              onClick={() =>
                                handleCopy(
                                  getMessageContent(block.coordinatorMessage),
                                  `coordinator-${blockIndex}`,
                                )
                              }
                            >
                              {copiedMessageId ===
                              `coordinator-${blockIndex}` ? (
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
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    {block.coordinatorMessage.timestamp && (
                      <span className="text-xs text-gray-500 dark:text-[#6a6a70] px-1 text-left">
                        {formatTimestamp(block.coordinatorMessage.timestamp)}
                      </span>
                    )}
                    {!block.coordinatorMessage && block.lastAgentMessage && (
                      <LastAgentMessage
                        agent={block.lastAgentMessage.agent}
                        message={block.lastAgentMessage.message}
                        onCopy={handleCopy}
                        onAgentClick={handleAgentClick}
                        copiedMessageId={copiedMessageId}
                        messageId={`agent-${blockIndex}`}
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Show loading when waiting for coordinator response */}
          {shouldShowLoading && (
            <CoordinatorLoadingMessage
              agentMessages={agentMessages}
              onAgentClick={handleAgentClick}
            />
          )}

          {/* Show loading for current incomplete block */}
          {isLoading &&
            conversationBlocks.length > 0 &&
            !conversationBlocks[conversationBlocks.length - 1]
              .coordinatorMessage && (
              <CoordinatorLoadingMessage
                agentMessages={
                  conversationBlocks[conversationBlocks.length - 1]
                    .agentActivity
                }
                onAgentClick={handleAgentClick}
              />
            )}
        </div>
      </ScrollArea>

      {/* Agent Message Modal */}
      <AgentMessageModal
        agent={selectedAgent || ''}
        messages={agentMessages[selectedAgent || ''] || []}
        isOpen={!!selectedAgent}
        onClose={() => setSelectedAgent(null)}
      />
    </>
  );
}
