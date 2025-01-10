<script lang="ts">
  import type { StoryEntry } from '../types/story'
  
  export let entry: StoryEntry
</script>

<div class="story-scene">
  {#if entry.speaker}
    <span class="speaker">{entry.speaker}:</span>
  {/if}
  <div class="content">{entry.content}</div>
  {#if entry.image}
    <div class="scene-image">
      <img src={entry.image} alt="Scene visualization" />
    </div>
  {/if}
</div>

<style>
  .story-scene {
    text-align: left;
    margin: 1rem 0;
    white-space: pre-wrap;
  }

  .speaker {
    font-weight: bold;
  }

  .scene-image {
    margin-top: 1rem;
    max-width: 100%;
  }

  .scene-image img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .content {
    margin-top: 0.5rem;
  }
</style>
