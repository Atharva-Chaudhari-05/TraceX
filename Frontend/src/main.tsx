// Ensure fetch is writable and configurable on window and Window.prototype
try {
  const origFetch = typeof window !== 'undefined' && window.fetch ? window.fetch.bind(window) : undefined;
  if (origFetch) {
    let currentFetch = origFetch;
    const descriptor: PropertyDescriptor = {
      get() { return currentFetch; },
      set(val) { currentFetch = val; },
      configurable: true,
      enumerable: true,
    };
    try { Object.defineProperty(window, 'fetch', descriptor); } catch (_) {}
    if (typeof Window !== 'undefined' && Window.prototype) {
      try { Object.defineProperty(Window.prototype, 'fetch', descriptor); } catch (_) {}
    }
  }
} catch (_) {}

import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

