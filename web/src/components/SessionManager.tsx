import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Trash2, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

interface SessionManagerProps {
  appName: string;
  userId: string;
  currentSession: string;
  onSessionChange: (sessionId: string) => void;
  onNewSession: () => void;
}

export function SessionManager({
  appName,
  userId,
  currentSession,
  onSessionChange,
  onNewSession,
}: SessionManagerProps) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = async () => {
    if (!appName) return;

    setLoading(true);
    try {
      const response = await api.get(
        `/apps/${appName}/users/${userId}/sessions`,
      );
      setSessions(response.data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [appName, userId]);

  const createNewSession = async () => {
    try {
      const response = await api.post(
        `/apps/${appName}/users/${userId}/sessions`,
      );
      await fetchSessions();
      onSessionChange(response.data.id);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await api.delete(
        `/apps/${appName}/users/${userId}/sessions/${sessionId}`,
      );
      await fetchSessions();
      if (currentSession === sessionId) {
        const remainingSessions = sessions.filter((s) => s.id !== sessionId);
        if (remainingSessions.length > 0) {
          onSessionChange(remainingSessions[0].id);
        } else {
          onNewSession();
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  // Format date and time from Unix timestamp
  const formatDateTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);

    // Format date as "May 18, 2025"
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    };

    return date.toLocaleString(undefined, options);
  };

  return (
    <div className="flex items-center gap-2">
      <Select value={currentSession} onValueChange={onSessionChange}>
        <SelectTrigger className="w-64 bg-secondary/30 border-border text-foreground hover:bg-secondary transition-colors">
          <SelectValue
            placeholder={loading ? 'Loading...' : 'Select a session'}
          />
        </SelectTrigger>
        <SelectContent className="bg-popover border-border">
          {sessions.map((session) => (
            <SelectItem
              key={session.id}
              value={session.id}
              className="text-popover-foreground hover:bg-accent focus:bg-accent"
            >
              <div className="flex items-center justify-between w-full">
                <span>{session.id.substring(0, 8)}...</span>
                <span className="text-xs text-muted-foreground ml-2">
                  {session.creation_timestamp
                    ? formatDateTime(session.creation_timestamp)
                    : session.last_update_time
                      ? formatDateTime(session.last_update_time)
                      : 'No date'}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        onClick={createNewSession}
        variant="ghost"
        size="icon"
        className="text-blue-400 hover:text-blue-300 hover:bg-accent/50"
      >
        <Plus className="w-4 h-4" />
      </Button>

      <Button
        onClick={fetchSessions}
        variant="ghost"
        size="icon"
        className="text-muted-foreground hover:text-foreground hover:bg-accent/50"
      >
        <RefreshCw className="w-4 h-4" />
      </Button>

      {currentSession && (
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-red-400 hover:text-red-300 hover:bg-accent/50"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="bg-popover border-border">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-popover-foreground">
                Confirm delete
              </AlertDialogTitle>
              <AlertDialogDescription className="text-muted-foreground">
                Are you sure you want to delete this session{' '}
                {currentSession.substring(0, 8)}...?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="bg-secondary text-secondary-foreground border-border hover:bg-secondary/80">
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={() => deleteSession(currentSession)}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </div>
  );
}
