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
  import CollapsableText from './CollapsableText.svelte'

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
  let show_toast_flag = $state(false)
  let toast_message = $state('')
  let show_thinking = $state(false)
  let thinking = $state(false)
  let thinking_content = $state('')
  let rest_content = $state('')
  let tick = $state(0)

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

  function received_prompt(data: ReceivedData) {
    if (data.reset) {
      prompt = ''
    }
    if (data.text) {
      prompt += data.text
      tick += 1
    }
  }

  async function generate_initial_image() {
    const prev_prompt = get_prev_prompt(index)
    prompt = ''
    tick = 0
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

  function match_and_rest(
    regex: RegExp,
    content: string
  ): { matched: boolean; match_content: string; rest: string } {
    const match = content.match(regex)
    if (match) {
      const processed = content.replace(regex, '')
      return { matched: true, match_content: match[1], rest: processed }
    } else {
      return { matched: false, match_content: '', rest: content }
    }
  }

  function process_thinking(content: string) {
    const thinking_regex = /<think>(.+?)$/s
    const response_regex = /<h1>Response(.+?)Chapter[^<]+<\/h3>/s

    content = content.replace(response_regex, '')

    const { matched, match_content, rest } = match_and_rest(think_complete_regex, content)
    if (matched) {
      show_thinking = true
      thinking = false
      thinking_content = match_content
      rest_content = rest
      return
    } else {
      const { matched, match_content, rest } = match_and_rest(thinking_regex, content)
      if (matched) {
        show_thinking = true
        thinking = true
        thinking_content = match_content
        rest_content = rest
        return
      }
    }
    show_thinking = false
    rest_content = content
  }

  $effect(() => {
    process_thinking(highlightQuotes(entry.content))
  })

  onMount(() => {})
</script>

<div class="story-scene">
  {#if entry.state !== StoryEntryState.NoImage}
    <ImageOrSpinner {entry} {disabled} {regenerate_image} {tick} />{/if}
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
    {#if show_thinking}
      <CollapsableText {thinking} content={thinking_content} />
    {/if}
    {@html rest_content}
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
    font-family: 'Noto Serif KR', 'Segoe UI', Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
    font-size: 1.1rem;
    color: theme('colors.neutral.600');
    padding: 0 0.5rem;
  }

  .story-scene :global p {
    margin-block-end: 0.7rem;
  }

  .story-scene :global p em {
    color: var(--color-neutral-400);
    font-synthesis: none;
    transform: skew(-8deg);
    display: inline-block;
  }

  .story-scene :global .quoted-text {
    color: theme('colors.blue.800');
  }

  .speaker {
    font-weight: bold;
  }
</style>
