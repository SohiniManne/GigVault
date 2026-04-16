import { initializeApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";

let app: FirebaseApp | null = null;
let db: Firestore | null = null;
let auth: Auth | null = null;

function requiredEnv(): boolean {
  return Boolean(
    import.meta.env.VITE_FIREBASE_API_KEY && import.meta.env.VITE_FIREBASE_PROJECT_ID,
  );
}

export function getFirebaseApp(): FirebaseApp | null {
  if (!requiredEnv()) return null;
  if (!app) {
    app = initializeApp({
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
      storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
      appId: import.meta.env.VITE_FIREBASE_APP_ID,
    });
  }
  return app;
}

export function getDb(): Firestore | null {
  if (!requiredEnv()) return null;
  if (!db) {
    const a = getFirebaseApp();
    if (!a) return null;
    db = getFirestore(a);
  }
  return db;
}

export function getFirebaseAuth(): Auth | null {
  if (!requiredEnv()) return null;
  if (!auth) {
    const a = getFirebaseApp();
    if (!a) return null;
    auth = getAuth(a);
  }
  return auth;
}
