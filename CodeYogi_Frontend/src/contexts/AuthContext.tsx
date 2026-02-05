import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import {
  User,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  UserCredential,
} from "firebase/auth";
import {
  doc,
  setDoc,
  getDoc,
  updateDoc,
  serverTimestamp,
} from "firebase/firestore";
import { auth, githubProvider, db } from "../config/firebase";
import {
  fetchGitHubUserData,
  getGitHubUsernameFromId,
  fetchGitHubRepositories,
} from "../services/githubService";

// User profile interface
export interface UserProfile {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  githubUsername?: string;
  githubId?: string;
  bio?: string;
  location?: string;
  website?: string;
  company?: string;
  publicRepos?: number;
  followers?: number;
  following?: number;
  createdAt: any;
  lastLoginAt: any;
  repositories?: any[];
  preferences?: {
    theme?: "light" | "dark";
    notifications?: boolean;
    language?: string;
  };
}

// Auth context interface
interface AuthContextType {
  user: User | null;
  userProfile: UserProfile | null;
  loading: boolean;
  error: string | null;
  signInWithGitHub: () => Promise<UserCredential | null>;
  logout: () => Promise<void>;
  updateUserProfile: (updates: Partial<UserProfile>) => Promise<void>;
  refreshGitHubRepos: () => Promise<void>;
}

// Create auth context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// Auth provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create or update user profile in Firestore
  const createOrUpdateUserProfile = async (
    user: User,
    additionalData?: any
  ) => {
    if (!user) return;

    const userRef = doc(db, "users", user.uid);
    const userSnapshot = await getDoc(userRef);

    // Fetch GitHub repositories if githubUsername is available
    let repositories: any[] | undefined = undefined;
    if (additionalData && additionalData.githubUsername) {
      try {
        repositories = await fetchGitHubRepositories(
          additionalData.githubUsername
        );
      } catch (err) {
        console.warn("Could not fetch GitHub repositories:", err);
      }
    }

    const userData: Partial<UserProfile> = {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      lastLoginAt: serverTimestamp(),
      ...additionalData,
      ...(repositories ? { repositories } : {}),
    };

    try {
      if (!userSnapshot.exists()) {
        // Create new user profile
        const newUserData: UserProfile = {
          ...userData,
          createdAt: serverTimestamp(),
          preferences: {
            theme: "dark",
            notifications: true,
            language: "en",
          },
        } as UserProfile;

        await setDoc(userRef, newUserData);
        setUserProfile(newUserData);
      } else {
        // Update existing user profile
        await updateDoc(userRef, userData);
        const updatedProfile = {
          ...userSnapshot.data(),
          ...userData,
        } as UserProfile;
        setUserProfile(updatedProfile);
      }
    } catch (err) {
      console.error("Error creating/updating user profile:", err);
      setError("Failed to create user profile");
    }
  };
  // Manually refresh GitHub repositories and update Firestore
  const refreshGitHubRepos = async () => {
    if (!userProfile || !userProfile.githubUsername || !user) return;
    setLoading(true);
    try {
      const repos = await fetchGitHubRepositories(userProfile.githubUsername);
      const userRef = doc(db, "users", user.uid);
      await updateDoc(userRef, { repositories: repos });
      setUserProfile({ ...userProfile, repositories: repos });
    } catch (err) {
      console.error("Failed to refresh GitHub repositories:", err);
      setError("Failed to refresh GitHub repositories");
    } finally {
      setLoading(false);
    }
  };

  // Sign in with GitHub
  const signInWithGitHub = async (): Promise<UserCredential | null> => {
    try {
      setError(null);
      setLoading(true);

      const result = await signInWithPopup(auth, githubProvider);

      // Extract GitHub username from the provider data
      let githubUsername = "";

      // Get the GitHub username from reloadUserInfo.screenName
      // Note: reloadUserInfo is not in the official User type but exists in the actual object
      const userWithInfo = result.user as any;
      if (
        userWithInfo.reloadUserInfo &&
        userWithInfo.reloadUserInfo.screenName
      ) {
        githubUsername = userWithInfo.reloadUserInfo.screenName;
        console.log("GitHub username from screenName:", githubUsername);
      }

      // Fallback: Try to extract from provider data
      if (!githubUsername && result.user.providerData[0]) {
        const githubData = result.user.providerData[0];
        console.log("GitHub data uid:", githubData.uid);

        if (githubData.providerId === "github.com" && githubData.uid) {
          githubUsername = githubData.uid;
        }
      }

      // Fallback: Try to extract from email
      if (!githubUsername && result.user.email) {
        githubUsername = result.user.email.split("@")[0];
      }

      console.log("Final extracted GitHub username:", githubUsername);

      // Initialize additional data
      let additionalData: any = {
        githubId: result.user.uid,
      };

      // Try to fetch enhanced GitHub data from GitHub API using the extracted username
      try {
        if (githubUsername) {
          // If the username is numeric (user ID), try to convert it to username
          if (/^\d+$/.test(githubUsername)) {
            console.log(
              "Username appears to be numeric ID, attempting to convert:",
              githubUsername
            );
            const actualUsername = await getGitHubUsernameFromId(
              githubUsername
            );
            if (actualUsername) {
              githubUsername = actualUsername;
              console.log("Converted ID to username:", githubUsername);
            } else {
              console.warn(
                "Could not convert numeric ID to username:",
                githubUsername
              );
              githubUsername = ""; // Clear invalid username
            }
          }

          if (githubUsername) {
            console.log(
              "Attempting to fetch GitHub data for username:",
              githubUsername
            );
            const enhancedData = await fetchGitHubUserData(githubUsername);
            if (enhancedData) {
              console.log("Successfully fetched GitHub data:", enhancedData);
              additionalData = {
                ...additionalData,
                githubUsername: enhancedData.login, // Use the verified login from GitHub API
                githubId: enhancedData.id.toString(),
                bio: enhancedData.bio || "",
                location: enhancedData.location || "",
                website: enhancedData.blog || "",
                company: enhancedData.company || "",
                publicRepos: enhancedData.public_repos,
                followers: enhancedData.followers,
                following: enhancedData.following,
              };
            } else {
              console.warn(
                "Failed to fetch GitHub data for username:",
                githubUsername
              );
            }
          }
        }
      } catch (githubError) {
        console.warn("Could not fetch enhanced GitHub data:", githubError);
        // Continue with basic data if GitHub API fails
      }

      await createOrUpdateUserProfile(result.user, additionalData);

      return result;
    } catch (err: any) {
      console.error("GitHub sign in error:", err);
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const logout = async (): Promise<void> => {
    try {
      setError(null);
      await signOut(auth);
      setUser(null);
      setUserProfile(null);
    } catch (err: any) {
      console.error("Logout error:", err);
      setError(err.message);
    }
  };

  // Update user profile
  const updateUserProfile = async (
    updates: Partial<UserProfile>
  ): Promise<void> => {
    if (!user) return;

    try {
      setError(null);
      const userRef = doc(db, "users", user.uid);
      const updateData = {
        ...updates,
        lastLoginAt: serverTimestamp(),
      };

      await updateDoc(userRef, updateData);

      if (userProfile) {
        setUserProfile({ ...userProfile, ...updates });
      }
    } catch (err: any) {
      console.error("Error updating user profile:", err);
      setError(err.message);
    }
  };

  // Listen to auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setLoading(true);

      if (user) {
        setUser(user);

        // Fetch user profile from Firestore
        try {
          const userRef = doc(db, "users", user.uid);
          const userSnapshot = await getDoc(userRef);

          if (userSnapshot.exists()) {
            setUserProfile(userSnapshot.data() as UserProfile);
          } else {
            // Create profile if it doesn't exist
            await createOrUpdateUserProfile(user);
          }
        } catch (err) {
          console.error("Error fetching user profile:", err);
          setError("Failed to fetch user profile");
        }
      } else {
        setUser(null);
        setUserProfile(null);
      }

      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value: AuthContextType = {
    user,
    userProfile,
    loading,
    error,
    signInWithGitHub,
    logout,
    updateUserProfile,
    refreshGitHubRepos,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
