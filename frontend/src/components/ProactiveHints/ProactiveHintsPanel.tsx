import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/api/client';
import { PdfAnalysisResponse, Hint } from '../../types/api';

interface ProactiveHintsPanelProps {
  data: PdfAnalysisResponse;
  projectId: number;
}

const ProactiveHintsPanel: React.FC<ProactiveHintsPanelProps> = ({ data, projectId }) => {
  const [confirmedHints, setConfirmedHints] = useState<Set<number>>(new Set());

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Proaktive Hinweise</h3>
        <div className="space-y-3">
          {data.hints?.map((hint: Hint, index: number) => (
            <div key={index} className="flex items-start justify-between p-3 bg-gray-50 rounded-md">
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                  hint.priority === 'high' ? 'bg-red-500' :
                  hint.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                }`} />
                <div>
                  <p className="text-sm text-gray-900">{hint.message}</p>
                  {hint.related_task && (
                    <p className="text-xs text-gray-500 mt-1">
                      Bezogen auf: {hint.related_task}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    Auswirkung: {hint.impact.charAt(0).toUpperCase() + hint.impact.slice(1)}
                  </p>
                </div>
              </div>
              {!confirmedHints.has(index) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      await apiClient.post(`/api/v1/projects/${projectId}/confirm_hint`, {
                        message: hint.message,
                        related_task: hint.related_task,
                        priority: hint.priority,
                        impact: hint.impact
                      });
                      setConfirmedHints(prev => new Set([...prev, index]));
                    } catch (error) {
                      console.error('Error confirming hint:', error);
                    }
                  }}
                >
                  Bestätigen
                </Button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProactiveHintsPanel;
