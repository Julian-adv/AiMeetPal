export enum StoryEntryState {
  WaitContent = 'wait_content',
  WaitPrompt = 'wait_prompt',
  WaitImage = 'wait_image',
  Image = 'image',
  NoImage = 'no_image',
  NoSpinner = 'no_spinner',
}

export interface ImageEntry {
  image: string | null
  path: string
  width: number
  height: number
  prompt: string
}

export interface StoryEntry {
  id: number
  speaker: string
  content: string
  state: StoryEntryState
  images: ImageEntry[]
  active_image?: number
  token_count?: number
}

export type StoryEntries = StoryEntry[]
