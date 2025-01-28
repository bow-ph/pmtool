import React from 'react';
import SchedulingPanel from '../Scheduling/SchedulingPanel';

interface ProjectSchedulingProps {
  /** Die ID des Projekts, das geplant wird */
  projectId?: number; // Optional, um besser mit fehlenden IDs umzugehen
}

const ProjectScheduling: React.FC<ProjectSchedulingProps> = ({ projectId }) => {
  // Fallback für fehlende projectId
  if (!projectId) {
    return (
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4" id="no-project-title">
            Projektplanung
          </h2>
          <p className="text-sm text-gray-500" role="alert" aria-live="polite">
            Keine Projekt-ID angegeben. Bitte ein gültiges Projekt auswählen.
          </p>
        </div>
      </div>
    );
  }

  return (
    <section
      className="bg-white shadow sm:rounded-lg"
      aria-labelledby="project-scheduling-title"
    >
      <div className="px-4 py-5 sm:p-6">
        <h2
          id="project-scheduling-title"
          className="text-lg font-medium text-gray-900 mb-4"
        >
          Projektplanung
        </h2>
        <SchedulingPanel projectId={projectId} />
      </div>
    </section>
  );
};

export default ProjectScheduling;
