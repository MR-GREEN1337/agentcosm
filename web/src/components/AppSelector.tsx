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
      <SelectTrigger className="w-64 bg-[#2a2a30] border-[#3a3a40] text-white hover:bg-[#33333a] transition-colors">
        <SelectValue placeholder={loading ? "Loading..." : "Select an app"} />
      </SelectTrigger>
      <SelectContent className="bg-[#2a2a30] border-[#3a3a40]">
        {apps.map((app) => (
          <SelectItem 
            key={app} 
            value={app} 
            className="text-white hover:bg-[#33333a] focus:bg-[#33333a]"
          >
            {app}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}