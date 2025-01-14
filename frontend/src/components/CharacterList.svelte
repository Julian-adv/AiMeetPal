<script lang="ts">
  import type { Character } from '../types/character'

  export let characters: Character[] = []
  export let selectedCharacter: Character | null = null

  function selectCharacter(character: Character) {}
</script>

<div class="character-list">
  <h2>Choose Your Character</h2>
  <div class="character-grid">
    {#each characters as character (character.id)}
      <div
        role="button"
        tabindex="0"
        aria-pressed={selectedCharacter?.id === character.id}
        class="character-card {selectedCharacter?.id === character.id ? 'selected' : ''}"
        on:click={() => selectCharacter(character)}
        on:keydown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            selectCharacter(character)
          }
        }}
      >
        <img src={character.image} alt={character.info.name} />
        <h3>{character.info.name}</h3>
        <p>{@html character.info.personality}</p>
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
    max-width: 900px;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 0.5rem;
  }

  .character-card {
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
    border: 2px solid transparent;
  }

  .character-card:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .character-card.selected {
    background: rgba(100, 149, 237, 0.3);
    border-color: theme('colors.blue.500');
  }

  .character-card img {
    width: 100%;
    height: auto;
    aspect-ratio: auto;
    object-fit: contain;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .character-card h3 {
    margin: 0;
    text-align: center;
    font-size: 1rem;
    font-weight: bold;
    color: theme('colors.gray.800');
  }

  .character-card p {
    margin: 0;
    text-align: center;
    font-size: 0.9rem;
    color: theme('colors.gray.500');
  }
</style>
