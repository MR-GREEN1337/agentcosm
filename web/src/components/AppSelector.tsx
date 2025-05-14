import { useState, useEffect } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { api } from '@/lib/api'

interface AppSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function AppSelector({ value, onChange }: AppSelectorProps) {
  const [apps, setApps] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchApps = async () => {
      try {
        const response = await api.get('/list-apps')
        setApps(response.data)
      } catch (error) {
        console.error('Error fetching apps:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchApps()
  }, [])

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-64 bg-secondary/30 border-border text-foreground hover:bg-secondary transition-colors">
        <SelectValue placeholder={loading ? "Loading..." : "Select an app"} />
      </SelectTrigger>
      <SelectContent className="bg-popover border-border">
        {apps.map((app) => (
          <SelectItem 
            key={app} 
            value={app} 
            className="text-popover-foreground hover:bg-accent focus:bg-accent"
          >
            {app}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}