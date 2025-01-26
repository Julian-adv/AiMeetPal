import type { Character } from '../types/character'
import type { StoryEntry } from '../types/story'

interface State {
  active_tab: number
  start_index: number
  system_token_count: number
  selected_char: Character | null
  story_entries: StoryEntry[]
}

export const g_state: State = $state({
  active_tab: 1,
  start_index: 0,
  system_token_count: 0,
  selected_char: null,
  story_entries: [],
})
