import React from 'react';

export const PlanetIcon = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 512 512" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className="w-6 h-6"
  >
    {/* Outer glow effect */}
    <circle 
      cx="256" 
      cy="256" 
      r="245" 
      stroke="rgba(255,255,255,0.1)" 
      strokeWidth="2" 
      fill="none"
    />
    
    {/* Main planet body with dark gradient */}
    <circle cx="256" cy="256" r="234" fill="url(#planetGradient)"/>
    
    {/* Subtle inner shadow for depth */}
    <path 
      d="M256 22C126.8 22 22 126.8 22 256s104.8 234 234 234c42.5 0 82.3-11.3 116.6-31.1C342.8 470.3 300.5 478 256 478c-123.5 0-224-100.5-224-224S132.5 30 256 30c44.5 0 86.8 7.7 116.6 19.1C338.3 33.3 298.5 22 256 22z" 
      fill="rgba(0,0,0,0.3)" 
    />
    
    {/* Wavy stripes with muted colors matching the theme */}
    <path 
      d="M55 140c40-30 80-20 120 10s100 30 140 0s80-30 120 0c30 22.5 60 45 87 67.5" 
      stroke="rgba(255,255,255,0.1)" 
      strokeWidth="45" 
      fill="none"
    />
    <path 
      d="M25 210c40-30 80-20 120 10s100 30 140 0s80-30 120 0c30 22.5 60 45 107 67.5" 
      stroke="rgba(255,255,255,0.2)" 
      strokeWidth="45" 
      fill="none"
    />
    <path 
      d="M15 280c40-30 80-20 120 10s100 30 140 0s80-30 120 0c30 22.5 60 45 117 67.5" 
      stroke="rgba(255,255,255,0.15)" 
      strokeWidth="45" 
      fill="none"
    />
    <path 
      d="M45 350c40-30 80-20 120 10s100 30 140 0s80-30 120 0c30 22.5 60 45 87 67.5" 
      stroke="rgba(255,255,255,0.2)" 
      strokeWidth="45" 
      fill="none"
    />
    <path 
      d="M75 420c40-30 80-20 120 10s100 30 140 0s80-30 120 0c20 15 40 30 57 45" 
      stroke="rgba(255,255,255,0.1)" 
      strokeWidth="45" 
      fill="none"
    />
    
    {/* Small details/spots with reduced opacity */}
    <rect x="248" y="58" width="16" height="16" fill="rgba(255,255,255,0.05)"/>
    <rect x="208" y="178" width="16" height="16" fill="rgba(255,255,255,0.05)"/>
    <rect x="56" y="314" width="16" height="16" fill="rgba(255,255,255,0.05)"/>
    <rect x="400" y="384" width="16" height="16" fill="rgba(255,255,255,0.05)"/>
    
    {/* Optional: subtle highlights */}
    <circle cx="220" cy="120" r="3" fill="rgba(255,255,255,0.2)"/>
    <circle cx="340" cy="180" r="2" fill="rgba(255,255,255,0.15)"/>
    
    {/* Gradient definition */}
    <defs>
      <radialGradient id="planetGradient" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#333333" />
        <stop offset="70%" stopColor="#222222" />
        <stop offset="100%" stopColor="#111111" />
      </radialGradient>
    </defs>
  </svg>
);