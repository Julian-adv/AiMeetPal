<script lang="ts">
  import { onMount } from 'svelte'
  import type { Character } from '../types/character'
  import { g_state } from '../lib/state.svelte'
  import CharacterCard from './CharacterCard.svelte'
  import { delete_file } from '../lib/files.svelte'

  let characters: Character[] = []

  async function load_characters() {
    try {
      const response = await fetch('http://localhost:5000/api/characters')
      if (response.ok) {
        characters = await response.json()
      } else {
        console.error('Failed to fetch characters')
      }
    } catch (error) {
      console.error('Error fetching characters:', error)
    }
  }

  onMount(async () => {
    await load_characters()
  })

  function select_character(character: Character) {
    g_state.selected_char = character
  }

  function chat() {
    g_state.active_tab = 2
  }

  function edit_char() {
    g_state.active_tab = 3
  }

  async function delete_char() {
    if (!g_state.selected_char) return
    await delete_file(`characters/${g_state.selected_char?.file_name}.png`)
    await load_characters()
  }
</script>

<div class="character-list p-2">
  <h2>Choose Your Character</h2>
  <div class="character-grid">
    {#each characters as character (character.file_name)}
      <CharacterCard
        selected={g_state.selected_char?.file_name === character.file_name}
        onclick={() => select_character(character)}
        {character}
        {chat}
        {edit_char}
        {delete_char}
      />{/each}
  </div>
</div>

<style lang="postcss">
  .character-list {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .character-grid {
    display: grid;
    max-width: var(--max-width);
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 0.5rem;
  }
</style>
