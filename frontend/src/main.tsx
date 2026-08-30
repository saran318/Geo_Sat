import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { TypographyGuide } from './TypographyGuide.tsx'

const rootElement = document.getElementById('root')!

if (window.location.pathname === '/style-guide') {
  createRoot(rootElement).render(
    <StrictMode>
      <TypographyGuide />
    </StrictMode>,
  )
} else {
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}

