import { settings } from './settings.svelte'
import type { Entry, DirEntries } from '../types/file'
import type { StoryEntry } from '@/types/story'

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

export async function get_session_entries(char_name: string): Promise<string[]> {
  try {
    const path = `../data/sessions/${char_name}`
    const entries = await get_dir_entries(path)
    const sessions = entries.entries.map((entry: Entry) => entry.name)
    return sessions
  } catch (error) {
    console.error('Error fetching session entries:', error)
    return []
  }
}

export async function get_session_json(char_name: string, session_name: string): Promise<any> {
  try {
    const response = await fetch(
      `http://localhost:5000/data/sessions/${char_name}/${session_name}/session.json`
    )
    if (!response.ok) {
      console.error('Failed to fetch session.json:', response.statusText)
      return null
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching session.json:', error)
    return null
  }
}

export async function load_json(path: string): Promise<any | null> {
  try {
    const response = await fetch(`http://localhost:5000/data/${path}`, {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      },
    })
    if (response.ok) {
      const data = await response.json()
      return data
    }
    return null
  } catch (error) {
    console.error('Error fetching file:', error)
    return null
  }
}

export async function save_json(path: string, json_data: any): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:5000/api/save-json', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        path: path,
        json_data: json_data,
      }),
    })

    if (!response.ok) {
      console.error('Failed to save JSON:', response)
      return false
    }

    return true
  } catch (error) {
    console.error('Error saving JSON:', error)
    return false
  }
}

export async function save_image_story_entry(
  dir: string,
  image_name: string,
  entry: StoryEntry
): Promise<StoryEntry> {
  for (let i = 0; i < entry.images.length; i++) {
    const image = entry.images[i]
    if (image.image && image.image.startsWith('data:image/png;base64,')) {
      // image exists but not saved yet
      try {
        const response = await fetch('http://localhost:5000/api/save-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            path: `${dir}/${image_name}_${i}.png`,
            image: image.image,
          }),
        })

        if (response.ok) {
          const data = await response.json()
          entry.images[i].image = `http://localhost:5000/data/${data.path}` // Clear the base64 image data after saving
        }
      } catch (error) {
        console.error('Error saving image:', error)
      }
    }
  }

  return entry
}
