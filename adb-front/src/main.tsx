import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { AdbApp } from './AdbApp'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AdbApp />
  </StrictMode>,
)
