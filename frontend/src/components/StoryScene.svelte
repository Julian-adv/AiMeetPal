<script lang="ts">
  import type { StoryEntry } from '../types/story'
  import { Button, Popover } from 'svelte-5-ui-lib'
  import { PencilSquare, ArrowPath, Camera } from 'svelte-heros-v2'
  import { generate_image, generate_prompt } from '../lib/generate_image.svelte'
  import { highlightQuotes } from '../lib/util'

  let {
    entry,
    prev_prompt,
    regenerate_content,
    index,
  }: { entry: StoryEntry; prev_prompt: string; regenerate_content: () => void; index: number } =
    $props()
  let width = $derived(entry.width ?? 832)
  let height = $derived(entry.height ?? 1216)
  let edit_mode = $state(false)
  let edit_textarea: HTMLTextAreaElement | null = $state(null)

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
    await generate_initial_image()
  }

  async function generate_initial_image() {
    const { prompt, width, height } = await generate_prompt(entry.content, prev_prompt)
    entry.state = 'wait_image'
    entry.width = width
    entry.height = height
    entry.image_prompt = prompt
    entry.image = await generate_image(prompt, width, height)
    entry.state = 'image'
  }

  $effect(() => {
    if (entry.state === 'wait_prompt') {
      generate_initial_image()
    }
  })

  async function regenerate_image() {
    entry.state = 'wait_prompt'
  }
</script>

<div class="story-scene">
  {#if entry.state !== 'no_image'}
    <div
      id="scene-image{index}"
      class={width > height ? 'scene-image-wide' : 'scene-image'}
      style="--image-width: {width}px; --image-height: {height}px;"
    >
      {#if entry.state === 'wait_prompt' || entry.state === 'wait_content'}
        <div class="image-placeholder">
          <div class="spinner_square"></div>
        </div>
      {:else if entry.state === 'wait_image'}
        <div class="image-placeholder">
          <div class="spinner_circle"></div>
        </div>
      {/if}
      {#if entry.image}
        <img src={entry.image} alt="Scene visualization" />
      {/if}
    </div>
    <Popover class="text-sm p-2 w-[50%] z-20" triggeredBy="#scene-image{index}" position="bottom"
      >{entry.image_prompt ?? 'Waiting for prompt...'}</Popover
    >
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
      id="edit_content{index}"
      color="light"
      size="xs"
      class="p-1 ml-[-0.5rem] mt-[-0.5rem] border-none text-neutral-400 focus:ring-0"
      onclick={toggle_edit_mode}><PencilSquare size="20" /></Button
    >
    <Popover triggeredBy="#edit_content{index}" class="text-sm p-2">Edit content</Popover>
    {#if entry.state !== 'no_image'}
      <Button
        id="regenerate_image{index}"
        color="light"
        size="xs"
        class="p-1 mt-[-0.5rem] border-none text-neutral-400 focus:ring-0"
        onclick={regenerate_image}><Camera size="20" /></Button
      >
      <Popover triggeredBy="#regenerate_image{index}" class="text-sm p-2">Regenerate image</Popover>
      <Button
        id="regenerate_content{index}"
        color="light"
        size="xs"
        class="p-1 mt-[-0.5rem] border-none text-neutral-400 focus:ring-0"
        onclick={regenerate_content}><ArrowPath size="20" /></Button
      >
      <Popover triggeredBy="#regenerate_content{index}" class="text-sm p-2"
        >Regenerate content</Popover
      >
    {/if}
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
    padding: 0 0.5rem;
  }

  .story-scene :global p {
    margin-block-end: 0.7rem;
  }

  .story-scene :global .quoted-text {
    color: theme('colors.blue.800');
  }

  .scene-image {
    position: relative;
    float: left;
    width: calc(var(--image-width) * 0.45);
    height: calc(var(--image-height) * 0.45);
    margin: 0 1rem 0.5rem 0;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
  }

  .scene-image-wide {
    position: relative;
    width: calc(var(--image-width) * 0.6);
    height: calc(var(--image-height) * 0.6);
    float: none;
    margin: 0 auto 0.5rem auto;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
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
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    padding: 1rem;
    justify-content: end;
    align-items: end;
    z-index: 1;
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
