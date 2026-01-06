import { initializeApp } from "firebase/app";
import { getAuth, GithubAuthProvider } from "firebase/auth";
import { getFirestore, initializeFirestore, persistentLocalCache, persistentMultipleTabManager } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize GitHub Auth Provider
export const githubProvider = new GithubAuthProvider();

// Add scopes for GitHub authentication
githubProvider.addScope("user:email");
githubProvider.addScope("read:user");
githubProvider.addScope("repo");

// Force account selection on every login (no auto sign-in)
githubProvider.setCustomParameters({
  prompt: 'consent', // Forces re-authentication and account selection
  allow_signup: 'true'
});

// Initialize Cloud Firestore with persistence using the new API
export const db = initializeFirestore(app, {
  localCache: persistentLocalCache({
    tabManager: persistentMultipleTabManager()
  })
});

// Initialize Cloud Storage and get a reference to the service
export const storage = getStorage(app);

export default app;
