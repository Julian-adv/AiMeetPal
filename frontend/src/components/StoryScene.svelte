<script lang="ts">
  import type { StoryEntry } from '../types/story'

  export let entry: StoryEntry
  export let showImage = true
</script>

<div class="story-scene">
  {#if showImage}
    <div class="scene-image">
      {#if entry.image}
        <img src={entry.image} alt="Scene visualization" />
      {:else}
        <div class="image-placeholder">
          <div class="spinner"></div>
        </div>
      {/if}
    </div>
  {/if}
  {#if entry.speaker}
    <span class="speaker">{entry.speaker}:</span>
  {/if}
  {entry.content}
</div>

<style>
  .story-scene {
    text-align: left;
    margin: 1rem 0;
    white-space: pre-wrap;
    overflow: auto;
  }

  .scene-image {
    float: left;
    width: 384px;
    margin: 0 1rem 0.5rem 0;
  }

  .scene-image img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .image-placeholder {
    width: 100%;
    aspect-ratio: 832/1216;
    background-color: #f0f0f0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #bfc9eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .speaker {
    font-weight: bold;
  }
</style>
