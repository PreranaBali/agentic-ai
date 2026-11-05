import { useEffect, useState } from 'react';
import { api } from '../services/api.js';

// 'checking' | 'online' | 'offline'
export function useHealth(intervalMs = 15000) {
  const [state, setState] = useState('checking');
  useEffect(() => {
    let alive = true;
    const check = async () => {
      try {
        await api.health();
        if (alive) setState('online');
      } catch {
        if (alive) setState('offline');
      }
    };
    check();
    const timer = setInterval(check, intervalMs);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [intervalMs]);
  return state;
}
