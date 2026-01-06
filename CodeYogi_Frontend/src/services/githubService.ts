import { doc, updateDoc } from "firebase/firestore";
import { db } from "../config/firebase";

export interface GitHubUserData {
  login: string;
  id: number;
  avatar_url: string;
  name: string;
  company?: string;
  blog?: string;
  location?: string;
  email?: string;
  bio?: string;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description?: string;
  private: boolean;
  html_url: string;
  clone_url: string;
  language?: string;
  stargazers_count: number;
  forks_count: number;
  updated_at: string;
  default_branch: string;
  owner: {
    login: string;
    id: number;
    avatar_url: string;
  };
}

/**
 * Test if a username exists on GitHub
 */
export const testGitHubUsername = async (
  username: string
): Promise<boolean> => {
  try {
    const response = await fetch(
      `https://api.github.com/users/${encodeURIComponent(username)}`
    );
    return response.ok;
  } catch (error) {
    return false;
  }
};

/**
 * Get GitHub username from user ID
 */
export const getGitHubUsernameFromId = async (
  userId: string
): Promise<string | null> => {
  try {
    const response = await fetch(`https://api.github.com/user/${userId}`);
    if (response.ok) {
      const userData = await response.json();
      return userData.login;
    }
    return null;
  } catch (error) {
    console.error("Error fetching username from ID:", error);
    return null;
  }
};

/**
 * Manually update user's GitHub username after validation
 */
export const updateGitHubUsername = async (
  userId: string,
  newUsername: string
): Promise<boolean> => {
  try {
    // First, test if the username exists on GitHub
    const isValid = await testGitHubUsername(newUsername);
    if (!isValid) {
      console.error("GitHub username does not exist:", newUsername);
      return false;
    }

    // Fetch the GitHub data for this username
    const githubData = await fetchGitHubUserData(newUsername);
    if (githubData) {
      await updateUserProfileWithGitHubData(userId, githubData);
      return true;
    }

    return false;
  } catch (error) {
    console.error("Error updating GitHub username:", error);
    return false;
  }
};

/**
 * Fetch additional GitHub user data using the GitHub API
 * Note: This requires the user's GitHub username
 */
export const fetchGitHubUserData = async (
  username: string
): Promise<GitHubUserData | null> => {
  try {
    console.log("Fetching GitHub user data for:", username);

    // Since we're now getting the correct username from screenName,
    // we can use it directly without aggressive sanitization
    const trimmedUsername = username.trim();

    if (!trimmedUsername) {
      console.warn("Empty GitHub username provided");
      return null;
    }

    // Encode the username to handle any special characters
    const encodedUsername = encodeURIComponent(trimmedUsername);

    const apiUrl = `https://api.github.com/users/${encodedUsername}`;
    console.log("GitHub API URL:", apiUrl);

    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const userData: GitHubUserData = await response.json();
    return userData;
  } catch (error) {
    console.error("Error fetching GitHub user data:", error);
    return null;
  }
};

/**
 * Update user profile in Firestore with additional GitHub data
 */
export const updateUserProfileWithGitHubData = async (
  userId: string,
  githubData: GitHubUserData
): Promise<void> => {
  try {
    const userRef = doc(db, "users", userId);

    const updateData = {
      githubUsername: githubData.login,
      githubId: githubData.id.toString(),
      bio: githubData.bio || "",
      location: githubData.location || "",
      website: githubData.blog || "",
      company: githubData.company || "",
      publicRepos: githubData.public_repos,
      followers: githubData.followers,
      following: githubData.following,
    };

    await updateDoc(userRef, updateData);
    console.log("User profile updated with GitHub data");
  } catch (error) {
    console.error("Error updating user profile with GitHub data:", error);
    throw error;
  }
};

/**
 * Sync user profile with latest GitHub data
 * This can be called periodically or on user request
 */
export const syncWithGitHub = async (
  userId: string,
  githubUsername: string
): Promise<void> => {
  try {
    const githubData = await fetchGitHubUserData(githubUsername);

    if (githubData) {
      await updateUserProfileWithGitHubData(userId, githubData);
    }
  } catch (error) {
    console.error("Error syncing with GitHub:", error);
    throw error;
  }
};

/**
 * Fetch user's GitHub repositories
 */
export const fetchGitHubRepositories = async (
  username: string,
  accessToken?: string
): Promise<GitHubRepository[]> => {
  try {
    const headers: HeadersInit = {
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "CodeYogi-App", // GitHub requires a User-Agent header
    };

    // Add authorization header if access token is provided
    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`;
    }

    // Use the username directly since we're getting it from screenName
    const trimmedUsername = username.trim();
    if (!trimmedUsername) {
      console.warn("Empty GitHub username provided for repositories");
      return [];
    }

    // Encode the username to handle any special characters
    const encodedUsername = encodeURIComponent(trimmedUsername);
    const response = await fetch(
      `https://api.github.com/users/${encodedUsername}/repos?sort=updated&per_page=100`,
      { headers }
    );

    if (!response.ok) {
      if (response.status === 403) {
        console.warn("GitHub API rate limit exceeded or access denied");
        return [];
      }
      if (response.status === 404) {
        console.warn("GitHub user not found:", username);
        return [];
      }
      throw new Error(
        `GitHub API error: ${response.status} ${response.statusText}`
      );
    }

    const repositories: GitHubRepository[] = await response.json();

    // Filter repositories based on access level
    const filteredRepos = repositories.filter((repo) => {
      // Show public repos always, private repos only if authenticated
      return !repo.private || accessToken;
    });

    return filteredRepos;
  } catch (error) {
    console.error("Error fetching GitHub repositories:", error);

    // Return empty array instead of throwing to prevent app crashes
    return [];
  }
};

/**
 * Check if GitHub API rate limit is reached
 */
export const checkGitHubRateLimit = async (): Promise<{
  limit: number;
  remaining: number;
  reset: number;
}> => {
  try {
    const response = await fetch("https://api.github.com/rate_limit");
    const data = await response.json();

    return {
      limit: data.rate.limit,
      remaining: data.rate.remaining,
      reset: data.rate.reset,
    };
  } catch (error) {
    console.error("Error checking GitHub rate limit:", error);
    return { limit: 0, remaining: 0, reset: 0 };
  }
};
