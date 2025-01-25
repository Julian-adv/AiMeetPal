import { settings } from './settings.svelte'
import type { Entry, DirEntries } from '../types/file'

export async function get_dir_entries(path: string): Promise<DirEntries> {
  const response = await fetch('http://localhost:5000/api/files', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ path: path }),
  })
  if (response.ok) {
    return await response.json()
  }
  throw new Error('Failed to fetch directory entries')
}

export async function get_checkpoints(): Promise<string[]> {
  try {
    const entries = await get_dir_entries(settings.checkpoints_folder)
    const checkpoints = entries.entries.map((entry: Entry) => entry.name)
    return checkpoints
  } catch (error) {
    console.error('Error fetching checkpoints:', error)
    return []
  }
}
