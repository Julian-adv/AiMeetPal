import type { Character } from '../types/character'
import type { StoryEntry } from '../types/story'

interface State {
  active_tab: number
  selected_char: Character | null
  story_entries: StoryEntry[]
}

export const g_state: State = $state({
  active_tab: 1,
  selected_char: null,
  story_entries: [],
})
