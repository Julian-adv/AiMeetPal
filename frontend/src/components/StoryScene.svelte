<script lang="ts">
  import type { StoryEntry } from '../types/story'

  export let entry: StoryEntry
</script>

<div class="story-scene">
  {#if entry.image}
    <div class="scene-image">
      <img src={entry.image} alt="Scene visualization" />
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

  .speaker {
    font-weight: bold;
  }
</style>
