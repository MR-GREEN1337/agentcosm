import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Plus,
  Play,
  Download,
  TestTube,
  FlaskConical,
  CheckCircle,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface EvalTabProps {
  appName: string;
  userId: string;
}

interface EvalSet {
  id: string;
  name: string;
}

interface EvalCase {
  id: string;
  name: string;
}

interface EvalMetric {
  id: string;
  name: string;
  description: string;
}

const AVAILABLE_METRICS: EvalMetric[] = [
  {
    id: 'exact_match',
    name: 'Exact Match',
    description: 'Checks for exact string match',
  },
  {
    id: 'semantic_similarity',
    name: 'Semantic Similarity',
    description: 'Measures semantic similarity',
  },
  {
    id: 'response_length',
    name: 'Response Length',
    description: 'Evaluates response length',
  },
];

export function EvalTab({ appName, userId }: EvalTabProps) {
  const [evalSets, setEvalSets] = useState<string[]>([]);
  const [selectedEvalSet, setSelectedEvalSet] = useState<string>('');
  const [evalCases, setEvalCases] = useState<string[]>([]);
  const [newEvalSetName, setNewEvalSetName] = useState('');
  const [showNewEvalSetDialog, setShowNewEvalSetDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [runningEval, setRunningEval] = useState(false);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);

  const fetchEvalSets = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/apps/${appName}/eval_sets`);
      setEvalSets(response.data);
    } catch (error) {
      console.error('Error fetching eval sets:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvalCases = async (evalSetId: string) => {
    try {
      const response = await api.get(
        `/apps/${appName}/eval_sets/${evalSetId}/evals`,
      );
      setEvalCases(response.data);
    } catch (error) {
      console.error('Error fetching eval cases:', error);
    }
  };

  useEffect(() => {
    fetchEvalSets();
  }, [appName]);

  useEffect(() => {
    if (selectedEvalSet) {
      fetchEvalCases(selectedEvalSet);
    }
  }, [selectedEvalSet]);

  const createEvalSet = async () => {
    if (!newEvalSetName.trim()) return;

    try {
      await api.post(`/apps/${appName}/eval_sets/${newEvalSetName}`);
      await fetchEvalSets();
      setNewEvalSetName('');
      setShowNewEvalSetDialog(false);
    } catch (error) {
      console.error('Error creating eval set:', error);
    }
  };

  const runEval = async () => {
    if (!selectedEvalSet || selectedMetrics.length === 0) return;

    setRunningEval(true);
    try {
      const response = await api.post(
        `/apps/${appName}/eval_sets/${selectedEvalSet}/run_eval`,
        {
          eval_ids: [],
          eval_metrics: selectedMetrics.map((id) => ({ name: id })),
        },
      );
      console.log('Eval results:', response.data);
    } catch (error) {
      console.error('Error running eval:', error);
    } finally {
      setRunningEval(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-[#a0a0a8]">Loading evaluation sets...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      <div className="w-96 border-r border-[#2a2a30]">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-medium text-white flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <FlaskConical className="w-4 h-4 text-white" />
              </div>
              Evaluation Sets
            </h2>
            <Dialog
              open={showNewEvalSetDialog}
              onOpenChange={setShowNewEvalSetDialog}
            >
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-blue-400 hover:text-blue-300 hover:bg-[#2a2a30]"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#1a1a1f] border-[#2a2a30]">
                <DialogHeader>
                  <DialogTitle className="text-white">
                    Create New Evaluation Set
                  </DialogTitle>
                  <DialogDescription className="text-[#a0a0a8]">
                    Enter a name for your new evaluation set
                  </DialogDescription>
                </DialogHeader>
                <Input
                  value={newEvalSetName}
                  onChange={(e) => setNewEvalSetName(e.target.value)}
                  placeholder="eval set name"
                  className="bg-[#0e0e10] border-[#2a2a30] text-white placeholder:text-[#6a6a70]"
                />
                <DialogFooter>
                  <Button
                    onClick={createEvalSet}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Create
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <ScrollArea className="h-[400px]">
            <div className="space-y-2">
              {evalSets.map((evalSet) => (
                <Card
                  key={evalSet}
                  className={`bg-[#1a1a1f] border-[#2a2a30] p-4 cursor-pointer hover:bg-[#1f1f24] transition-all ${
                    selectedEvalSet === evalSet
                      ? 'border-blue-500 bg-[#1f1f24]'
                      : ''
                  }`}
                  onClick={() => setSelectedEvalSet(evalSet)}
                >
                  <div className="flex items-center gap-3">
                    <TestTube className="w-4 h-4 text-[#a0a0a8]" />
                    <span className="text-sm text-white">{evalSet}</span>
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      <div className="flex-1 p-6">
        {selectedEvalSet ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-medium text-white">
                {selectedEvalSet}
              </h3>
              <div className="flex gap-3">
                <Select
                  value={selectedMetrics.join(',')}
                  onValueChange={(value) =>
                    setSelectedMetrics(value.split(',').filter(Boolean))
                  }
                >
                  <SelectTrigger className="w-64 bg-[#2a2a30] border-[#3a3a40] text-white">
                    <SelectValue placeholder="Select metrics" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#2a2a30] border-[#3a3a40]">
                    {AVAILABLE_METRICS.map((metric) => (
                      <SelectItem
                        key={metric.id}
                        value={metric.id}
                        className="text-white hover:bg-[#33333a]"
                      >
                        {metric.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  onClick={runEval}
                  disabled={runningEval || selectedMetrics.length === 0}
                  className="bg-blue-600 hover:bg-blue-700 button-glow"
                >
                  {runningEval ? (
                    <span className="flex items-center gap-2">
                      Running...{' '}
                      <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    </span>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Run Evaluation
                    </>
                  )}
                </Button>
              </div>
            </div>

            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {evalCases.map((evalCase) => (
                  <Card
                    key={evalCase}
                    className="bg-[#1a1a1f] border-[#2a2a30] p-4 hover:bg-[#1f1f24] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <span className="text-sm text-white font-medium">
                          {evalCase}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-[#a0a0a8] hover:text-white hover:bg-[#2a2a30]"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <FlaskConical className="w-16 h-16 text-[#3a3a40] mx-auto mb-4" />
              <p className="text-[#a0a0a8] text-lg">Select an evaluation set</p>
              <p className="text-[#6a6a70] text-sm mt-2">
                Choose a set to view and run evaluations
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
