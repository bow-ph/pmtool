import React from 'react';
import { toast } from 'react-hot-toast';

interface CalendarSubscriptionProps {
  projectTitle?: string;
  userId: string | number;
}

const CalendarSubscription: React.FC<CalendarSubscriptionProps> = ({ projectTitle, userId }) => {
  const calendarUrl = `${window.location.origin}/api/v1/calendar/${userId}.ics`;

  const copyUrl = async () => {
    try {
      await navigator.clipboard.writeText(calendarUrl);
      toast.success('Calendar URL copied to clipboard');
    } catch (error) {
      toast.error('Failed to copy URL');
    }
  };

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h2 className="text-lg font-semibold mb-2">
        {projectTitle ? `Calendar Subscription: ${projectTitle}` : 'Calendar Subscription'}
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Subscribe to your tasks in your preferred calendar application:
      </p>
      <div className="flex items-center space-x-2">
        <input
          type="text"
          readOnly
          value={calendarUrl}
          className="flex-1 p-2 border rounded-md bg-white"
        />
        <button
          onClick={copyUrl}
          className="bg-gray-200 hover:bg-gray-300 p-2 rounded-md"
        >
          📋
        </button>
      </div>
    </div>
  );
};

export default CalendarSubscription;
