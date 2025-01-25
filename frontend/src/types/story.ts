export enum StoryEntryState {
  WaitContent = 'wait_content',
  WaitPrompt = 'wait_prompt',
  WaitImage = 'wait_image',
  Image = 'image',
  NoImage = 'no_image',
}

export interface StoryEntry {
  id: number
  speaker: string
  content: string
  state: StoryEntryState
  image: string | null
  image_path?: string
  width?: number
  height?: number
  image_prompt?: string
  token_count?: number
}

export type StoryEntries = StoryEntry[]
