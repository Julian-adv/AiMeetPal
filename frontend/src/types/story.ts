export interface StoryEntry {
  id: number
  speaker: string
  content: string
  image: string | null
  image_prompt?: string
}

export type StoryEntries = StoryEntry[]
