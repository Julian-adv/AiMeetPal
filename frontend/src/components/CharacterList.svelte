<script lang="ts">
  import { onMount } from 'svelte'
  import type { Character } from '../types/character'
  import { g_state } from '../lib/state.svelte'

  let characters: Character[] = []

  onMount(async () => {
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
  })

  function removeHtmlTags(str: string): string {
    return str.replace(/<[^>]*>/g, '')
  }

  function selectCharacter(character: Character) {
    g_state.selected_char = character
  }
</script>

<div class="character-list">
  <h2>Choose Your Character</h2>
  <div class="character-grid">
    {#each characters as character (character.file_name)}
      <div
        role="button"
        tabindex="0"
        aria-pressed={g_state.selected_char?.file_name === character.file_name}
        class="character-card {g_state.selected_char?.file_name === character.file_name
          ? 'selected'
          : ''}"
        onclick={() => selectCharacter(character)}
        onkeydown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            selectCharacter(character)
          }
        }}
      >
        <img src={character.image} alt={character.info.name} />
        <div class="character-info">
          <h3>{character.info.name}</h3>
          <p>{removeHtmlTags(character.info.personality)}</p>
        </div>
        <div class="filename-container"><div class="filename">{character.file_name}</div></div>
      </div>
    {/each}
  </div>
</div>

<style lang="postcss">
  .character-list {
    padding: 2px;
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

  .character-card {
    cursor: pointer;
    padding: 0rem;
    border-radius: 8px;
    background: theme('colors.zinc.50');
    transition: all 0.2s ease;
    border: 1px solid theme('colors.zinc.300');
    @apply shadow-md;
  }

  .character-card:hover {
    background: theme('colors.zinc.50');
    transform: translateY(-2px);
    @apply shadow-lg;
  }

  .character-card.selected {
    background: rgba(100, 149, 237, 0.3);
    border-color: theme('colors.blue.500');
    @apply ring-2;
  }

  .character-card img {
    width: 100%;
    height: 255px;
    object-fit: cover;
    object-position: top;
    border-radius: 8px 8px 0 0;
  }

  .character-info {
    padding: 0.5rem;
    height: 8rem;
    overflow: hidden;
  }

  .character-card h3 {
    text-align: center;
    font-size: 0.9rem;
    font-weight: bold;
    color: theme('colors.gray.800');
  }

  .character-card p {
    text-align: left;
    font-size: 0.8rem;
    color: theme('colors.gray.500');
  }

  .filename-container {
    border-top: 1px solid theme('colors.zinc.300');
    background: theme('colors.zinc.200');
    height: 3rem;
    border-radius: 0 0 8px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 0.5rem;
    padding: 0.2rem;
  }

  .filename {
    font-size: 0.8rem;
    color: theme('colors.gray.600');
    overflow: hidden;
  }
</style>
