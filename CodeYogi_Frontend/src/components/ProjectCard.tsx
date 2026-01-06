import React from 'react';
import { Project } from '../types';

interface ProjectCardProps {
  project: Project;
  isSelected: boolean;
  onSelect: () => void;
  getStatusColor: (status: string) => string;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  isSelected,
  onSelect,
  getStatusColor
}) => {
  return (
    <div
      onClick={onSelect}
      className={`
        p-4 rounded-lg cursor-pointer transition-all
        ${isSelected ? 'bg-green-500/20 border-green-500/50' : 'bg-gray-800/50 border-gray-700'}
        border hover:border-green-500/30
      `}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-2 h-2 rounded-full ${getStatusColor(project.status)}`}
        />
        <h3 className="font-medium text-white">{project.name}</h3>
      </div>
      {project.description && (
        <p className="mt-2 text-sm text-gray-400">{project.description}</p>
      )}
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
        <span>{project.language}</span>
        <span>Updated {new Date(project.updatedAt).toLocaleDateString()}</span>
      </div>
    </div>
  );
};
