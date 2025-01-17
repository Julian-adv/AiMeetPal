<script lang="ts">
  import { marked } from 'marked'
  import type { StoryEntry } from '../types/story'

  let { entry }: { entry: StoryEntry } = $props()
  let width = $derived(entry.width ?? 832)
  let height = $derived(entry.height ?? 1216)

  function highlightQuotes(content: string) {
    let markedContent = marked(content, { async: false })
    markedContent = markedContent.replace(/"([^"]+)"/g, '<span class="quoted-text">"$1"</span>')
    return markedContent.replace(/&quot;(.+?)&quot;/g, '<span class="quoted-text">"$1"</span>')
  }
</script>

<div class="story-scene">
  {#if entry.image}
    <div
      class={width > height ? 'scene-image-wide' : 'scene-image'}
      style="--image-width: {width}px; --image-height: {height}px;"
    >
      {#if entry.image === 'wait_prompt' || entry.image === 'wait_image'}
        <div class="image-placeholder">
          {#if entry.image === 'wait_prompt'}
            <div class="spinner_square"></div>
          {:else}
            <div class="spinner_circle"></div>
          {/if}
        </div>
      {:else}
        <img src={entry.image} alt="Scene visualization" />
      {/if}
    </div>
  {/if}
  {#if entry.speaker}
    <span class="speaker">{entry.speaker}:</span>
  {/if}
  {@html highlightQuotes(entry.content)}
</div>

<style>
  .story-scene {
    text-align: left;
    margin: 1rem 0;
    white-space: normal;
    overflow: auto;
    font-family: 'Segoe UI', Georgia, 'Times New Roman', Times, serif;
    font-size: 1.1rem;
    color: theme('colors.neutral.600');
  }

  .story-scene :global p {
    margin-block-end: 0.7rem;
  }

  .story-scene :global .quoted-text {
    color: theme('colors.blue.800');
  }

  .scene-image {
    float: left;
    width: calc(var(--image-width) * 0.45);
    height: calc(var(--image-height) * 0.45);
    margin: 0 1rem 0.5rem 0;
  }

  .scene-image-wide {
    width: calc(var(--image-width) * 0.6);
    height: calc(var(--image-height) * 0.6);
    float: none;
    margin: 0 auto 0.5rem auto;
  }

  .scene-image img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .scene-image-wide img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    background-color: #f0f0f0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .spinner_square {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border-radius: 0;
    border: 4px solid #bfc9eb;
  }

  .spinner_circle {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #bfc9eb;
    border-radius: 50%;
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
