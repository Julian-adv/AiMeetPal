export interface StoryEntry {
  id: number
  speaker: string
  content: string
  state: 'wait_content' | 'wait_prompt' | 'wait_image' | 'image' | 'no_image'
  image: string | null
  image_path?: string
  width?: number
  height?: number
  image_prompt?: string
  token_count?: number
}

export type StoryEntries = StoryEntry[]
