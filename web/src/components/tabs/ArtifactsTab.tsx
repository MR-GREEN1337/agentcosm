import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Download, Trash2 } from 'lucide-react';

interface ArtifactsTabProps {
  appName: string;
  userId: string;
  sessionId: string;
}

interface Artifact {
  name: string;
  versions: number[];
}

export function ArtifactsTab({
  appName,
  userId,
  sessionId,
}: ArtifactsTabProps) {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchArtifacts = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      const response = await api.get(
        `/apps/${appName}/users/${userId}/sessions/${sessionId}/artifacts`,
      );
      const artifactNames = response.data;

      const artifactsWithVersions = await Promise.all(
        artifactNames.map(async (name: string) => {
          const versionsResponse = await api.get(
            `/apps/${appName}/users/${userId}/sessions/${sessionId}/artifacts/${name}/versions`,
          );
          return {
            name,
            versions: versionsResponse.data,
          };
        }),
      );

      setArtifacts(artifactsWithVersions);
    } catch (error) {
      console.error('Error fetching artifacts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArtifacts();
  }, [appName, userId, sessionId]);

  const downloadArtifact = async (artifactName: string, version?: number) => {
    try {
      const url = version
        ? `/apps/${appName}/users/${userId}/sessions/${sessionId}/artifacts/${artifactName}/versions/${version}`
        : `/apps/${appName}/users/${userId}/sessions/${sessionId}/artifacts/${artifactName}`;

      const response = await api.get(url);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json',
      });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${artifactName}${version ? `_v${version}` : ''}.json`;
      link.click();
    } catch (error) {
      console.error('Error downloading artifact:', error);
    }
  };

  const deleteArtifact = async (artifactName: string) => {
    try {
      await api.delete(
        `/apps/${appName}/users/${userId}/sessions/${sessionId}/artifacts/${artifactName}`,
      );
      fetchArtifacts();
    } catch (error) {
      console.error('Error deleting artifact:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Loading artifacts...</p>
      </div>
    );
  }

  if (artifacts.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No artifacts</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-4">
        {artifacts.map((artifact) => (
          <Card key={artifact.name} className="bg-gray-800 border-gray-700 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-medium text-gray-100">
                {artifact.name}
              </h3>
              <div className="flex gap-2">
                <Button
                  onClick={() => downloadArtifact(artifact.name)}
                  variant="ghost"
                  size="sm"
                  className="text-blue-400 hover:text-blue-300"
                >
                  <Download className="w-4 h-4" />
                </Button>
                <Button
                  onClick={() => deleteArtifact(artifact.name)}
                  variant="ghost"
                  size="sm"
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-400">Versions:</p>
              <div className="flex gap-2 flex-wrap">
                {artifact.versions.map((version) => (
                  <Button
                    key={version}
                    onClick={() => downloadArtifact(artifact.name, version)}
                    variant="outline"
                    size="sm"
                    className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
                  >
                    v{version}
                  </Button>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </ScrollArea>
  );
}
