export interface StoryEntry {
  id: number
  speaker: string
  content: string
  image: string | null
  width?: number
  height?: number
  image_prompt?: string
}

export type StoryEntries = StoryEntry[]
