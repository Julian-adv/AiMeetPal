<script lang="ts">
  import type { Character } from '../types/character'

  export let characters: Character[] = []
  export let selectedCharacter: Character | null = null
  export let onSelect: (character: Character) => void
</script>

<div class="character-list">
  <h2>Select Character</h2>
  <div class="character-grid">
    {#each characters as character (character.id)}
      <div
        role="button"
        tabindex="0"
        aria-pressed={selectedCharacter?.id === character.id}
        class="character-card {selectedCharacter?.id === character.id ? 'selected' : ''}"
        on:click={() => onSelect(character)}
        on:keydown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onSelect(character)
          }
        }}
      >
        <img src={character.image} alt={character.id} />
        <p>{character.id}</p>
      </div>
    {/each}
  </div>
</div>

<style>
  .character-list {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .character-list h2 {
    margin: 0 0 1rem 0;
    font-size: 1.2rem;
    color: #eee;
  }

  .character-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1rem;
  }

  .character-card {
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
  }

  .character-card:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }

  .character-card.selected {
    background: rgba(100, 149, 237, 0.3);
    border: 2px solid cornflowerblue;
  }

  .character-card img {
    width: 100%;
    height: auto;
    aspect-ratio: auto;
    object-fit: contain;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .character-card p {
    margin: 0;
    text-align: center;
    font-size: 0.9rem;
    color: #eee;
  }
</style>
