import type { Character } from './character'
import type { StoryEntry } from './story'

export interface Session {
  session_name: string
  system_token_count: number
  selected_char: Character
  story_entries: StoryEntry[]
}
