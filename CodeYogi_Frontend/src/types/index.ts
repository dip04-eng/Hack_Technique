// Firebase Auth and User types
export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
}

// User preferences
export interface UserPreferences {
  theme: "light" | "dark" | "system";
  notifications: boolean;
  language: string;
  emailNotifications?: boolean;
  pushNotifications?: boolean;
}

// Complete user profile stored in Firestore
export interface UserProfile {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;

  // GitHub specific data
  githubUsername?: string;
  githubId?: string;

  // Profile information
  bio?: string;
  location?: string;
  website?: string;
  company?: string;

  // GitHub stats
  publicRepos?: number;
  followers?: number;
  following?: number;

  // Timestamps
  createdAt: any; // Firestore Timestamp
  lastLoginAt: any; // Firestore Timestamp
  updatedAt?: any; // Firestore Timestamp

  // User preferences
  preferences: UserPreferences;

  // Additional metadata
  isActive?: boolean;
  lastSyncWithGitHub?: any; // Firestore Timestamp
}

// GitHub API response types
export interface GitHubUser {
  login: string;
  id: number;
  node_id: string;
  avatar_url: string;
  gravatar_id: string;
  url: string;
  html_url: string;
  followers_url: string;
  following_url: string;
  gists_url: string;
  starred_url: string;
  subscriptions_url: string;
  organizations_url: string;
  repos_url: string;
  events_url: string;
  received_events_url: string;
  type: string;
  site_admin: boolean;
  name: string | null;
  company: string | null;
  blog: string | null;
  location: string | null;
  email: string | null;
  hireable: boolean | null;
  bio: string | null;
  twitter_username: string | null;
  public_repos: number;
  public_gists: number;
  followers: number;
  following: number;
  created_at: string;
  updated_at: string;
}

// Auth context types
export interface AuthContextType {
  user: AuthUser | null;
  userProfile: UserProfile | null;
  loading: boolean;
  error: string | null;
  signInWithGitHub: () => Promise<any>;
  logout: () => Promise<void>;
  updateUserProfile: (updates: Partial<UserProfile>) => Promise<void>;
  refreshProfile: () => Promise<void>;
  syncWithGitHub: () => Promise<void>;
}

// Project View types
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  language: string;
  updatedAt: string;
  files: FileNode[];
}

export interface FileNode {
  name: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  path?: string;
}

export interface Repository {
  id: string;
  name: string;
  description?: string;
  language?: string;
  stargazers_count: number;
  forks_count: number;
  private: boolean;
  updated_at: string;
  html_url: string;
}

// Component prop types
export interface LoginProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export interface UserProfileProps {
  user?: UserProfile;
  editable?: boolean;
  onUpdate?: (updates: Partial<UserProfile>) => void;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// GitHub rate limit response
export interface GitHubRateLimit {
  limit: number;
  remaining: number;
  reset: number;
  used: number;
}

// Firebase error types
export interface FirebaseError {
  code: string;
  message: string;
  customData?: any;
}

// Form types
export interface ProfileUpdateForm {
  displayName: string;
  bio: string;
  location: string;
  website: string;
  company: string;
}

export interface PreferencesForm {
  theme: "light" | "dark" | "system";
  notifications: boolean;
  language: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
}

// Navigation types
export type DashboardPanel =
  | "chat"
  | "console"
  | "projects"
  | "analytics"
  | "settings"
  | "profile";

export interface NavigationItem {
  id: DashboardPanel;
  icon: any; // React component
  label: string;
  color: string;
  badge?: string | number;
}

// Utility types
export type LoadingState = "idle" | "loading" | "success" | "error";

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Event types
export interface AuthEvent {
  type: "login" | "logout" | "profile_update" | "sync";
  user?: UserProfile;
  timestamp: Date;
}

// Constants
export const USER_PREFERENCES_DEFAULTS: UserPreferences = {
  theme: "dark",
  notifications: true,
  language: "en",
  emailNotifications: true,
  pushNotifications: false,
};

export const GITHUB_OAUTH_SCOPES = ["user:email", "read:user"] as const;

export const FIRESTORE_COLLECTIONS = {
  USERS: "users",
  USER_SESSIONS: "user_sessions",
  USER_ACTIVITY: "user_activity",
} as const;
