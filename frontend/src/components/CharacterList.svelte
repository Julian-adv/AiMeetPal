<script lang="ts">
  import { onMount } from 'svelte'
  import type { Character } from '../types/character'
  import { state } from '../lib/state.svelte'

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
    state.selected_char = character
  }
</script>

<div class="character-list">
  <h2>Choose Your Character</h2>
  <div class="character-grid">
    {#each characters as character (character.id)}
      <div
        role="button"
        tabindex="0"
        aria-pressed={state.selected_char?.id === character.id}
        class="character-card {state.selected_char?.id === character.id ? 'selected' : ''}"
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
      </div>
    {/each}
  </div>
</div>

<style>
  .character-list {
    padding: 0rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .character-list h2 {
    margin: 0 0 1rem 0;
    font-size: 1.2rem;
    color: theme('colors.gray.700');
  }

  .character-grid {
    display: grid;
    max-width: 902px;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 0.5rem;
  }

  .character-card {
    cursor: pointer;
    padding: 0rem;
    border-radius: 8px;
    background: theme('colors.zinc.200');
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
  }

  .character-card h3 {
    text-align: center;
    font-size: 1rem;
    font-weight: bold;
    color: theme('colors.gray.800');
  }

  .character-card p {
    text-align: center;
    font-size: 0.9rem;
    color: theme('colors.gray.500');
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
