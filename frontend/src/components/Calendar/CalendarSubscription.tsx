import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';

interface CalendarSubscriptionProps {
  projectId: string | undefined;
}

interface ProjectDetails {
  title: string;
  user_id: number;
}

export default function CalendarSubscription({ projectId }: CalendarSubscriptionProps) {
  const [calendarUrl, setCalendarUrl] = useState('');
  const [copied, setCopied] = useState(false);
  const [projectTitle, setProjectTitle] = useState('');

  useEffect(() => {
    if (projectId) {
      fetchProjectDetails();
    }
  }, [projectId]);

  const fetchProjectDetails = async () => {
    try {
      const response = await apiClient.get<ProjectDetails>(`/api/v1/projects/${projectId}`);
      setProjectTitle(response.data.title);
      setCalendarUrl(`${window.location.origin}/api/v1/calendar/${response.data.user_id}.ics`);
    } catch (error) {
      console.error('Failed to fetch project details:', error);
    }
  };

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(calendarUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy URL:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Calendar Subscription: {projectTitle}</h2>
      <div className="flex items-center space-x-4">
        <input
          type="text"
          value={calendarUrl}
          readOnly
          className="flex-1 p-2 border rounded bg-gray-50"
        />
        <button
          onClick={handleCopyUrl}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {copied ? 'Copied!' : 'Copy URL'}
        </button>
      </div>
      <p className="mt-2 text-sm text-gray-600">
        Use this URL to subscribe to your tasks in your calendar application.
      </p>
    </div>
  );
}
