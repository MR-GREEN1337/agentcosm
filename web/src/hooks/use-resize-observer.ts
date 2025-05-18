import { useState, useEffect, useCallback, RefObject } from 'react'

/**
 * A hook that observes an element's size changes using ResizeObserver
 */
export function useResizeObserver<T extends HTMLElement = HTMLDivElement>(
  ref: RefObject<T | null>,
  options: { debounce?: number } = {}
) {
  const [size, setSize] = useState({
    width: 0,
    height: 0
  })
  const [isObserving, setIsObserving] = useState(false)
  
  const { debounce = 0 } = options
  
  // Use a more efficient update mechanism with debouncing for smoother UI
  const handleResize = useCallback(
    (entries: ResizeObserverEntry[]) => {
      if (!Array.isArray(entries) || !entries.length) return
      
      const entry = entries[0]
      const { width, height } = entry.contentRect
      
      const updateSize = () => {
        setSize((prevSize) => {
          // Only update if values have actually changed
          if (prevSize.width === width && prevSize.height === height) {
            return prevSize
          }
          return { width, height }
        })
      }
      
      if (debounce > 0) {
        // Clear previous timeout
        const timeoutId = (handleResize as any).timeoutId
        if (timeoutId) {
          clearTimeout(timeoutId)
        }
        
        // Set new timeout
        (handleResize as any).timeoutId = setTimeout(updateSize, debounce)
      } else {
        updateSize()
      }
    },
    [debounce]
  )
  
  // Set up and tear down the ResizeObserver
  useEffect(() => {
    const element = ref.current
    if (!element) return
    
    // Create ResizeObserver instance
    const resizeObserver = new ResizeObserver(handleResize)
    
    // Start observing
    resizeObserver.observe(element)
    setIsObserving(true)
    
    // Handle initial size
    setSize({
      width: element.offsetWidth,
      height: element.offsetHeight
    })
    
    // Clean up
    return () => {
      // Clear any pending debounced calls
      const timeoutId = (handleResize as any).timeoutId
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      
      resizeObserver.disconnect()
      setIsObserving(false)
    }
  }, [ref, handleResize])
  
  // Return the current size along with observation state
  return { ...size, isObserving }
}