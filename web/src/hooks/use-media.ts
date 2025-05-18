import { useEffect, useState } from 'react'

/**
 * A hook that returns whether a media query matches or not
 * @param query The media query to check against
 */
export function useMediaQuery(query: string): boolean {
  // State for storing whether the media query matches
  const [matches, setMatches] = useState<boolean>(false)
  
  // Effect to add and remove the media query listener
  useEffect(() => {
    // Default to false for SSR
    if (typeof window === 'undefined') {
      return
    }
    
    // Create a media query list
    const mediaQueryList = window.matchMedia(query)
    
    // Set initial value
    setMatches(mediaQueryList.matches)
    
    // Define the change handler
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }
    
    // Add the event listener
    if (mediaQueryList.addEventListener) {
      // Modern browsers
      mediaQueryList.addEventListener('change', handleChange)
      return () => {
        mediaQueryList.removeEventListener('change', handleChange)
      }
    } else {
      // For older browsers (mainly IE and older Edge)
      // @ts-ignore - Legacy API
      mediaQueryList.addListener(handleChange)
      return () => {
        // @ts-ignore - Legacy API
        mediaQueryList.removeListener(handleChange)
      }
    }
  }, [query])
  
  return matches
}