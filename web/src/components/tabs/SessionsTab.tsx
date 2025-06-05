import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

interface SessionsTabProps {
  appName: string;
  userId: string;
  currentSession: string;
  onSessionChange?: (sessionId: string) => void; // Add this prop for auto-selection
}

interface Session {
  id: string;
  app_name: string;
  user_id: string;
  creation_timestamp: number;
  state: any;
  events: any[];
}

export function SessionsTab({
  appName,
  userId,
  currentSession,
  onSessionChange, // Add this prop
}: SessionsTabProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      try {
        const response = await api.get(
          `/apps/${appName}/users/${userId}/sessions`,
        );
        const fetchedSessions = response.data;
        setSessions(fetchedSessions);

        // Auto-select the first session if no current session is set and callback is provided
        if (!currentSession && fetchedSessions.length > 0 && onSessionChange) {
          const firstSession = fetchedSessions[0];
          console.log('Auto-selecting first session:', firstSession.id);
          onSessionChange(firstSession.id);
        }
      } catch (error) {
        console.error('Error fetching sessions:', error);
      } finally {
        setLoading(false);
      }
    };

    if (appName && userId) {
      fetchSessions();
    }
  }, [appName, userId, currentSession, onSessionChange]);

  const fetchSessionDetails = async (sessionId: string) => {
    try {
      const response = await api.get(
        `/apps/${appName}/users/${userId}/sessions/${sessionId}`,
      );
      setSelectedSession(response.data);
    } catch (error) {
      console.error('Error fetching session details:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500 dark:text-[#a0a0a8]">Loading sessions...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      <div className="w-1/3 border-r border-gray-700 dark:border-[#2a2a30]">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-2">
            {sessions.map((session) => (
              <Card
                key={session.id}
                className={`bg-gray-100 dark:bg-[#1a1a1f] border-gray-200 dark:border-[#2a2a30] p-3 cursor-pointer hover:bg-gray-200 dark:hover:bg-[#1f1f24] transition-colors ${
                  selectedSession?.id === session.id
                    ? 'border-blue-500 bg-gray-200 dark:bg-[#1f1f24]'
                    : ''
                }`}
                onClick={() => fetchSessionDetails(session.id)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-900 dark:text-[#d0d0d8]">
                    {session.id === currentSession ? '(Current) ' : ''}
                    {session.id.substring(0, 8)}...
                  </span>
                  <span className="text-xs text-gray-500 dark:text-[#6a6a70]">
                    {new Date(
                      session.creation_timestamp * 1000,
                    ).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      <div className="flex-1">
        {selectedSession ? (
          <ScrollArea className="h-full">
            <div className="p-4">
              <Card className="bg-gray-100 dark:bg-[#1a1a1f] border-gray-200 dark:border-[#2a2a30] p-4 mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-[#d0d0d8] mb-2">
                  Session Details
                </h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-[#6a6a70]">
                      ID:
                    </span>{' '}
                    <span className="text-gray-900 dark:text-[#d0d0d8]">
                      {selectedSession.id}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-[#6a6a70]">
                      Created:
                    </span>{' '}
                    <span className="text-gray-900 dark:text-[#d0d0d8]">
                      {new Date(
                        selectedSession.creation_timestamp * 1000,
                      ).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-[#6a6a70]">
                      Events:
                    </span>{' '}
                    <span className="text-gray-900 dark:text-[#d0d0d8]">
                      {selectedSession.events?.length || 0}
                    </span>
                  </div>
                </div>
              </Card>

              <Card className="bg-gray-100 dark:bg-[#1a1a1f] border-gray-200 dark:border-[#2a2a30] p-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-[#d0d0d8] mb-2">
                  State
                </h3>
                <pre className="text-sm text-gray-700 dark:text-[#a0a0a8] overflow-x-auto">
                  {JSON.stringify(selectedSession.state, null, 2)}
                </pre>
              </Card>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 dark:text-[#6a6a70]">
              Select a session to view details
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
