export interface StoryEntry {
  id: number
  speaker: string
  content: string
  image?: string | null
}

export type StoryEntries = StoryEntry[]
