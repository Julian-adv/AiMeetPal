<script lang="ts">
  import type { StoryEntry } from '../types/story'
  import { Button, Popover, Toast } from 'svelte-5-ui-lib'
  import { PencilSquare, ArrowPath } from 'svelte-heros-v2'
  import { generate_image, image_size } from '../lib/generate_image.svelte'
  import { get_prompt_with_prefix, highlightQuotes } from '../lib/util'
  import { StoryEntryState } from '../types/story'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import { settings } from '../lib/settings.svelte'
  import { g_state } from '../lib/state.svelte'
  import Handlebars from 'handlebars'
  import { TBoxLineDesign } from 'svelte-remix'
  import { onMount } from 'svelte'
  import { send_stream, type ReceivedData } from '../lib/stream'
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
  let rotate_angle = 0
  let show_toast_flag = $state(false)
  let toast_message = $state('')
  let angle_timer: number | undefined = undefined
  let angle = $state(0)

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

  const think_complete_regex = /<think>(.+?)<\/think>/s
  let prompt = ''

  function clear_angle_timer() {
    if (angle_timer !== undefined) {
      clearTimeout(angle_timer)
      angle_timer = undefined
    }
  }

  function update_angle() {
    clear_angle_timer()

    let amplitude = 360
    let time_constant = 30

    angle_timer = window.setInterval(() => {
      const delta = amplitude / time_constant
      angle += delta
      amplitude -= delta
      if (delta < 0.1) {
        clearInterval(angle_timer)
      }
    }, 1000 / time_constant)
  }

  function update_rotate_angle() {
    clear_angle_timer()

    let amplitude = 360
    let time_constant = 30

    angle_timer = window.setInterval(() => {
      const delta = amplitude / time_constant
      rotate_angle += delta
      amplitude -= delta
      if (delta < 0.1) {
        clearInterval(angle_timer)
      }
    }, 1000 / time_constant)
  }

  function received_prompt(data: ReceivedData) {
    if (data.reset) {
      prompt = ''
    }
    if (data.text) {
      prompt += data.text
      update_angle()
    }
  }

  async function generate_initial_image() {
    const prev_prompt = get_prev_prompt(index)
    prompt = ''
    angle = 0
    const error = await send_stream(
      'scene-to-prompt',
      { content: entry.content, prev_image_prompt: prev_prompt },
      received_prompt
    )
    if (error) {
      show_toast(error)
      return
    }
    prompt = prompt.replace(think_complete_regex, '')
    const { width, height } = image_size(prompt)
    entry.state = StoryEntryState.WaitImage
    const image_entry: ImageEntry = {
      width: width,
      height: height,
      prompt: prompt,
      image: await generate_image(
        settings.checkpoint_name,
        get_prompt_with_prefix(prompt),
        width,
        height
      ),
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

  let collapsed = true

  function on_think_click(this: HTMLElement) {
    const thinkElement = this.closest('.think')
    if (thinkElement) {
      collapsed = thinkElement.classList.toggle('collapsed')
    }
  }

  function setup_think_buttons() {
    const button = document.getElementById(`think-toggle${entry.id}`)
    if (!button) return
    if (!button.dataset.thinkListener) {
      button.addEventListener('click', on_think_click)
      button.dataset.thinkListener = 'true'
    }
  }

  function get_thinking_tag(thinking: boolean) {
    if (thinking) {
      update_rotate_angle()
    }
    const size = 14
    return `<div class="think ${collapsed ? 'collapsed' : ''} ${thinking ? 'thinking' : ''}"><button id="think-toggle${entry.id}" class="think-toggle">▼</button><div class="spinner">${thinking ? 'thinking' : 'thought'}<div class="spinner-square ${rotate_angle === 0 ? 'glow' : ''}" style="transform: rotate(${rotate_angle}deg); width: ${size}px; height: ${size}px;"></div></div><span class="think-content">$1</span></div>`
  }

  function process_thinking(content: string) {
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
        const processed = content.replace(thinking_regex, replace_str)
        setTimeout(setup_think_buttons, 0)
        return processed
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
    <ImageOrSpinner {entry} {disabled} {regenerate_image} {angle} />{/if}
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
  @reference "tailwindcss/theme";

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

  .story-scene :global .think.collapsed .spinner .spinner-square {
    display: none;
    transform-origin: center;
    transition: transform 0.4s ease-in-out;
  }

  .story-scene :global .think.collapsed.thinking .spinner .spinner-square {
    display: inline;
    margin-left: 0.3rem;
    border: 2px solid #bfc9eb;
    border-radius: 2px;
    transition: transform 1s linear;
  }

  .story-scene :global .think.collapsed.thinking .spinner .spinner-square .glow {
    animation: glow-animation 1.5s infinite alternate;
  }

  @keyframes glow-animation {
    from {
      box-shadow: 0 0 1px #bfc9eb;
      filter: brightness(1);
    }
    to {
      box-shadow: 0 0 10px #ddf;
      filter: brightness(1.1);
    }
  }

  .speaker {
    font-weight: bold;
  }
</style>
