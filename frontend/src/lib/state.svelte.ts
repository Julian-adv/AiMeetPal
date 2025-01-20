import type { Character } from '../types/character'
import type { StoryEntry } from '../types/story'

interface State {
  selected_char: Character | null
  story_entries: StoryEntry[]
}

export const g_state: State = $state({
  selected_char: null,
  story_entries: [],
})
