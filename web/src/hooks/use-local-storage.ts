import { useState, useRef, useEffect, useCallback } from 'react'

type UseLocalStorageOptions<T> = {
  defaultValue: T
  serialize?: (value: T) => string
  deserialize?: (value: string) => T
}

/**
 * A hook for managing state with localStorage persistence, with proper typing and error handling
 */
export function useLocalStorage<T>(
  key: string,
  options: UseLocalStorageOptions<T>
) {
  const {
    defaultValue,
    serialize = JSON.stringify,
    deserialize = JSON.parse,
  } = options

  // State to store our value
  // Pass initial state function to useState so logic is only executed once
  const [storedValue, setStoredValue] = useState<T>(() => {
    // Prevent build errors
    if (typeof window === 'undefined') {
      return defaultValue
    }

    try {
      // Get from local storage by key
      const item = window.localStorage.getItem(key)
      
      // Parse stored json or if none return initialValue
      return item ? deserialize(item) : defaultValue
    } catch (error) {
      // If error also return initialValue
      console.error(`Error reading localStorage key "${key}":`, error)
      return defaultValue
    }
  })

  // Track if component is mounted to prevent setState on unmounted component
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  // Effect to update localStorage when the state changes
  useEffect(() => {
    if (typeof window === 'undefined') return

    try {
      // Save to local storage
      window.localStorage.setItem(key, serialize(storedValue))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }, [key, storedValue, serialize])

  // Create a version of setState that also updates localStorage
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore =
        value instanceof Function ? value(storedValue) : value
      
      // Save state
      if (mounted.current) {
        setStoredValue(valueToStore)
      }
    } catch (error) {
      console.error(`Error updating localStorage value:`, error)
    }
  }, [storedValue])

  return [storedValue, setValue] as const
}
