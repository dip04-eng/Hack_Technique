import { initializeApp } from "firebase/app";
import { getAuth, GithubAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";
import { getAnalytics } from "firebase/analytics";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC_x-3Xpj2gMw9ltabXPJrzU7BXAiLDU8c",
  authDomain: "hack-technique.firebaseapp.com",
  projectId: "hack-technique",
  storageBucket: "hack-technique.firebasestorage.app",
  messagingSenderId: "854598074792",
  appId: "1:854598074792:web:c4f90f7f590f7dc4bd5d9d",
  measurementId: "G-YHMDPN032C"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics
export const analytics = getAnalytics(app);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize GitHub Auth Provider
export const githubProvider = new GithubAuthProvider();

// Add scopes for GitHub authentication
githubProvider.addScope("user:email");
githubProvider.addScope("read:user");
githubProvider.addScope("repo");

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

// Initialize Cloud Storage and get a reference to the service
export const storage = getStorage(app);

export default app;
