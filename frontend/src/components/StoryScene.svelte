<script lang="ts">
  import type { StoryEntry } from '../types/story'
  import { Button, Popover, Toast } from 'svelte-5-ui-lib'
  import { PencilSquare, ArrowPath, Camera } from 'svelte-heros-v2'
  import { generate_image, generate_prompt } from '../lib/generate_image.svelte'
  import { highlightQuotes } from '../lib/util'
  import { StoryEntryState } from '../types/story'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import { settings } from '../lib/settings.svelte'
  import { g_state } from '../lib/state.svelte'
  import Handlebars from 'handlebars'
  import { TBoxLineDesign } from 'svelte-remix'
  import { onMount } from 'svelte'
  import type { ImageEntry } from '../types/story'

  interface Prop {
    entry: StoryEntry
    regenerate_content: () => void
    index: number
    image_generated: (entry: StoryEntry) => void
    disabled?: boolean
  }

  let { entry, regenerate_content, index, image_generated, disabled }: Prop = $props()
  let edit_mode = $state(false)
  let edit_textarea: HTMLTextAreaElement | null = $state(null)
  let rotationAngle = 0
  let show_toast_flag = $state(false)
  let toast_message = $state('')

  function show_toast(message: string) {
    toast_message = message
    show_toast_flag = true
    setTimeout(() => {
      show_toast_flag = false
    }, 5000)
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
    await generate_initial_image()
  }

  function get_prev_prompt(i: number) {
    if (i > 1) {
      const active_image = g_state.story_entries[i - 2].active_image
      if (active_image !== undefined) {
        return g_state.story_entries[i - 2].images[active_image].prompt
      }
      return ''
    }
    if (g_state.selected_char?.info.description) {
      const template = Handlebars.compile(g_state.selected_char.info.description)
      return template({ char: g_state.selected_char.info.name, user: 'Julien' })
    }
    return 'character appearance: blonde\nenvironment: living room'
  }

  async function generate_initial_image() {
    const prev_prompt = get_prev_prompt(index)
    const { prompt, width, height, error } = await generate_prompt(entry.content, prev_prompt)
    if (error) {
      show_toast(error)
      return
    }
    entry.state = StoryEntryState.WaitImage
    const image_entry: ImageEntry = {
      width: width,
      height: height,
      prompt: prompt,
      image: await generate_image(settings.checkpoint_name, prompt, width, height),
      path: '',
    }
    entry.images = [...entry.images, image_entry]
    entry.active_image = entry.images.length - 1
    entry.state = StoryEntryState.Image
    image_generated(entry)
  }

  $effect(() => {
    if (entry.state === StoryEntryState.WaitPrompt) {
      generate_initial_image()
    }
  })

  function regenerate_image() {
    entry.state = StoryEntryState.WaitPrompt
  }

  function on_think_click(this: HTMLElement) {
    const thinkElement = this.closest('.think')
    if (thinkElement) {
      thinkElement.classList.toggle('collapsed')
    }
  }

  function setup_think_buttons() {
    const think_buttons = document.querySelectorAll('.think-toggle')
    think_buttons.forEach((button) => {
      button.addEventListener('click', on_think_click)
    })
  }

  function get_thinking_tag(thinking: boolean) {
    if (thinking) {
      rotationAngle = (rotationAngle + 10) % 360
    } else {
      rotationAngle = 0
    }
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6" style="transform: rotate(${rotationAngle}deg)">
  <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12a7.5 7.5 0 0 0 15 0m-15 0a7.5 7.5 0 1 1 15 0m-15 0H3m16.5 0H21m-1.5 0H12m-8.457 3.077 1.41-.513m14.095-5.13 1.41-.513M5.106 17.785l1.15-.964m11.49-9.642 1.149-.964M7.501 19.795l.75-1.3m7.5-12.99.75-1.3m-6.063 16.658.26-1.477m2.605-14.772.26-1.477m0 17.726-.26-1.477M10.698 4.614l-.26-1.477M16.5 19.794l-.75-1.299M7.5 4.205 12 12m6.894 5.785-1.149-.964M6.256 7.178l-1.15-.964m15.352 8.864-1.41-.513M4.954 9.435l-1.41-.514M12.002 12l-3.75 6.495" />
</svg>
`
    return `<div class="think collapsed ${thinking ? 'thinking' : ''}"><button class="think-toggle">▼</button><div class="spinner">${thinking ? 'thinking' : 'thought'}${svg}
</div><span class="think-content">$1</span></div>`
  }

  function process_thinking(content: string) {
    const think_complete_regex = /<think>(.+?)<\/think>/s
    const thinking_regex = /<think>(.+?)$/s

    const think_complete = content.match(think_complete_regex)
    if (think_complete) {
      const replace_str = get_thinking_tag(false)
      const processed = content.replace(think_complete_regex, replace_str)
      // Set up button events asynchronously
      setTimeout(setup_think_buttons, 0)
      return processed
    } else {
      const thinking = content.match(thinking_regex)
      if (thinking) {
        const replace_str = get_thinking_tag(true)
        return content.replace(thinking_regex, replace_str)
      }
    }
    return content
  }

  onMount(() => {
    setup_think_buttons()
  })
</script>

<div class="story-scene">
  {#if entry.state !== StoryEntryState.NoImage}
    <ImageOrSpinner {entry} {disabled} {regenerate_image} />{/if}
  <Toast
    bind:toastStatus={show_toast_flag}
    dismissable={false}
    baseClass="absolute bottom-10 right-10 bg-red-200 text-red-700">{toast_message}</Toast
  >
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
    {@html process_thinking(highlightQuotes(entry.content))}
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

  .story-scene :global .think {
    color: theme('colors.gray.400');
  }

  .story-scene :global .think-toggle {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0;
    font-size: 0.8em;
    transition: transform 0.2s;
    margin-top: 0.25rem;
  }

  .story-scene :global .think .spinner {
    display: none;
  }

  .story-scene :global .think.collapsed .spinner {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-style: italic;
    margin-left: 0.5rem;
  }

  .story-scene :global .think.collapsed .think-content {
    display: none;
  }

  .story-scene :global .think.collapsed .think-toggle {
    transform: rotate(-90deg);
  }

  .story-scene :global .think.collapsed .spinner svg {
    display: none;
    transform-origin: center;
    transition: transform 0.4s ease-in-out;
  }

  .story-scene :global .think.collapsed.thinking .spinner svg {
    display: inline;
  }

  .speaker {
    font-weight: bold;
  }
</style>
