import React from 'react';
import { Globe, Lock } from 'lucide-react';

interface Repository {
  name: string;
  description?: string;
  language?: string;
  stargazers_count: number;
  forks_count: number;
  private: boolean;
  updated_at: string;
}

interface RepositoryInfoProps {
  repo: Repository;
}

export const RepositoryInfo: React.FC<RepositoryInfoProps> = ({ repo }) => {
  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-theme-primary mb-2">{repo.name}</h2>
        {repo.description && (
          <p className="text-theme-secondary text-sm">{repo.description}</p>
        )}
      </div>

      <div className="space-y-4">
        {repo.language && (
          <div className="flex items-center gap-2 text-theme-secondary">
            <div className="w-3 h-3 rounded-full bg-accent-theme" />
            <span>{repo.language}</span>
          </div>
        )}

        <div className="flex items-center gap-4 text-gray-400 text-sm">
          <span>⭐ {repo.stargazers_count}</span>
          <span>🍴 {repo.forks_count}</span>
        </div>

        <div className="flex items-center gap-2 text-gray-400">
          {repo.private ? (
            <Lock className="w-4 h-4" />
          ) : (
            <Globe className="w-4 h-4" />
          )}
          <span>{repo.private ? "Private" : "Public"} repository</span>
        </div>

        {repo.updated_at && (
          <div className="text-sm text-gray-500">
            Last updated: {new Date(repo.updated_at).toLocaleDateString()}
          </div>
        )}
      </div>
    </div>
  );
};
