<script lang="ts">
  import { marked } from 'marked'
  import type { StoryEntry } from '../types/story'
  import { Button } from 'svelte-5-ui-lib'
  import { PencilSquare } from 'svelte-heros-v2'
  import { generate_image, generate_prompt } from '../lib/generate_image.svelte'
  import { onMount } from 'svelte'

  let { entry, prev_prompt }: { entry: StoryEntry; prev_prompt: string } = $props()
  let width = $derived(entry.width ?? 832)
  let height = $derived(entry.height ?? 1216)
  let edit_mode = $state(false)
  let edit_textarea: HTMLTextAreaElement | null = $state(null)

  function highlightQuotes(content: string) {
    let markedContent = marked(content, { async: false })
    markedContent = markedContent.replace(/"([^"]+)"/g, '<span class="quoted-text">"$1"</span>')
    return markedContent.replace(/&quot;(.+?)&quot;/g, '<span class="quoted-text">"$1"</span>')
  }

  function adjust_height() {
    if (edit_textarea) {
      edit_textarea.style.height = 'auto'
      edit_textarea.style.height = edit_textarea.scrollHeight + 1 + 'px'
    }
  }

  const toggle_edit_mode = () => {
    edit_mode = !edit_mode
    setTimeout(() => {
      adjust_height()
    }, 10)
  }

  function on_input(this: HTMLElement, ev: Event) {
    adjust_height()
  }

  async function save_entry() {
    toggle_edit_mode()
    const { prompt, width, height } = await generate_prompt(entry.content, prev_prompt)
    entry.image_prompt = prompt
    entry.image = await generate_image(prompt, width, height)
  }

  async function generate_initial_image() {
    entry.image = 'wait_prompt'
    const { prompt, width, height } = await generate_prompt(entry.content, prev_prompt)
    entry.width = width
    entry.height = height
    entry.image_prompt = prompt
    entry.image = 'wait_image'
    entry.image = await generate_image(prompt, width, height)
  }

  onMount(async () => {
    await generate_initial_image()
  })
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
  {#if edit_mode}
    <textarea
      bind:this={edit_textarea}
      bind:value={entry.content}
      class="p-2 rounded border border-gray-300 outline-none w-full block clear-both text-base h-auto"
      oninput={on_input}
    ></textarea>
    <Button class="m-2" onclick={save_entry}>Save</Button>
  {:else}
    {@html highlightQuotes(entry.content)}
    <Button
      color="light"
      size="xs"
      class="p-1 m-[-0.5rem] border-none text-neutral-400 focus:ring-0"
      onclick={toggle_edit_mode}><PencilSquare size="20" /></Button
    >
  {/if}
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
