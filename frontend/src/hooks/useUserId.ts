import { onAuthStateChanged } from "firebase/auth";
import { useCallback, useEffect, useState } from "react";
import { getFirebaseAuth } from "../firebase";

const KEY = "gigvault_user_id";

export function useUserId(): [string, (id: string) => void] {
  const [id, setId] = useState(() => getFirebaseAuth()?.currentUser?.uid || localStorage.getItem(KEY) || "");

  useEffect(() => {
    if (id) localStorage.setItem(KEY, id);
  }, [id]);

  useEffect(() => {
    const auth = getFirebaseAuth();
    if (!auth) return;
    return onAuthStateChanged(auth, (user) => {
      if (user?.uid) setId(user.uid);
      else setId("");
    });
  }, []);

  const update = useCallback((next: string) => {
    setId(next.trim());
  }, []);

  return [id, update];
}
