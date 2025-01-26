<script lang="ts">
  import type { StoryEntry } from '../types/story'
  import { Button, Popover } from 'svelte-5-ui-lib'
  import { PencilSquare, ArrowPath, Camera } from 'svelte-heros-v2'
  import { generate_image, generate_prompt } from '../lib/generate_image.svelte'
  import { highlightQuotes } from '../lib/util'
  import { StoryEntryState } from '../types/story'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import { settings } from '../lib/settings.svelte'
  import { g_state } from '../lib/state.svelte'
  import Handlebars from 'handlebars'
  import { TBoxLineDesign } from 'svelte-remix'

  interface Prop {
    entry: StoryEntry
    regenerate_content: () => void
    index: number
    image_generated: (entry: StoryEntry) => void
    disabled?: boolean
  }

  let { entry, regenerate_content, index, image_generated, disabled }: Prop = $props()
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

  function get_prev_prompt(i: number) {
    if (i > 1) {
      return g_state.story_entries[i - 2].image_prompt ?? ''
    }
    if (g_state.selected_char?.info.description) {
      const template = Handlebars.compile(g_state.selected_char.info.description)
      return template({ char: g_state.selected_char.info.name, user: 'Julien' })
    }
    return 'character appearance: blonde\nenvironment: living room'
  }

  async function generate_initial_image() {
    const prev_prompt = get_prev_prompt(index)
    const { prompt, width, height } = await generate_prompt(entry.content, prev_prompt)
    entry.state = StoryEntryState.WaitImage
    entry.width = width
    entry.height = height
    entry.image_prompt = prompt
    entry.image = await generate_image(settings.checkpoint_name, prompt, width, height)
    entry.state = StoryEntryState.Image
    image_generated(entry)
  }

  $effect(() => {
    if (entry.state === StoryEntryState.WaitPrompt) {
      generate_initial_image()
    }
  })

  async function regenerate_image() {
    entry.state = StoryEntryState.WaitPrompt
  }
</script>

<div class="story-scene">
  {#if entry.state !== StoryEntryState.NoImage}
    <ImageOrSpinner
      {width}
      {height}
      image_state={entry.state}
      image={entry.image}
      image_prompt={entry.image_prompt}
      scale={width > height ? 0.61 : 0.45}
    />{/if}
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
    {#if !disabled}
      <div class="flex gap-0 items-center">
        <Button
          id="edit_content{index}"
          color="light"
          size="xs"
          class="p-1 border-none text-neutral-400 focus:ring-0"
          onclick={toggle_edit_mode}><PencilSquare size="20" /></Button
        >
        <Popover triggeredBy="#edit_content{index}" class="text-sm p-2">Edit content</Popover>
        {#if entry.state !== 'no_image'}
          <Button
            id="regenerate_image{index}"
            color="light"
            size="xs"
            class="p-1 border-none text-neutral-400 focus:ring-0"
            onclick={regenerate_image}><Camera size="20" /></Button
          >
          <Popover triggeredBy="#regenerate_image{index}" class="text-sm p-2"
            >Regenerate image</Popover
          >
          <Button
            id="regenerate_content{index}"
            color="light"
            size="xs"
            class="p-1 border-none text-neutral-400 focus:ring-0"
            onclick={regenerate_content}><ArrowPath size="20" /></Button
          >
          <Popover triggeredBy="#regenerate_content{index}" class="text-sm p-2"
            >Regenerate content</Popover
          >
        {/if}
        <TBoxLineDesign size="20" class="text-neutral-300" />
        <div class="text-xs italic ml-1 text-neutral-300">
          {entry.token_count}
        </div>
      </div>
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

  .speaker {
    font-weight: bold;
  }
</style>
