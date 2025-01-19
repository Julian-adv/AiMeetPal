<script lang="ts">
  import type { StoryEntries } from '../types/story'
  import StoryScene from './StoryScene.svelte'
  import { state } from '../lib/state.svelte'
  import { onMount } from 'svelte'
  import Handlebars from 'handlebars'
  import { Button, Popover } from 'svelte-5-ui-lib'
  import { ArrowUturnLeft } from 'svelte-heros-v2'

  let nextId = 1
  let user_name = 'Julien'
  let chatInputElement: HTMLInputElement
  let chatInputValue = ''
  let error: string | null = null

  function formatResponse(text: string): string {
    const match = text.match(
      /<\|start_header_id\|>writer character: (.*?)<\|end_header_id\|>\s*([^\s]+)$/
    )
    if (match) {
      state.story_entries[state.story_entries.length - 1].speaker = match[1]
      return match[2]
    }
    return text
  }

  function received_text(text: string) {
    if (state.story_entries[state.story_entries.length - 1].speaker === '') {
      state.story_entries[state.story_entries.length - 1].content = formatResponse(
        state.story_entries[state.story_entries.length - 1].content + text
      )
    } else {
      state.story_entries[state.story_entries.length - 1].content =
        state.story_entries[state.story_entries.length - 1].content + text
    }
  }

  async function send_chat(entries: StoryEntries, received: (text: string) => void) {
    const chatEntries = entries.map(({ id, speaker, content }) => ({
      id,
      speaker,
      content,
    }))

    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ info: state.selected_char?.info, entries: chatEntries }),
    })

    if (!response.ok) {
      throw new Error('Chat request failed')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Failed to get response reader')
    }
    const decoder = new TextDecoder()

    while (true) {
      const { value, done } = await reader.read()

      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ') && line.trim() !== 'data: ') {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.text) {
              received(data.text)
            }
          } catch (e) {
            console.error('Failed to parse JSON:', e)
          }
        }
      }
    }
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter') return
    if (!chatInputValue.trim()) return

    error = null

    try {
      state.story_entries = [
        ...state.story_entries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInputValue,
          state: 'no_image',
          image: null,
        },
        {
          id: nextId++,
          speaker: state.selected_char?.info.name ?? 'AI',
          content: '',
          state: 'wait_content',
          image: null,
        },
      ]
      chatInputValue = ''
      await send_chat(state.story_entries, received_text)
      state.story_entries[state.story_entries.length - 1].state = 'wait_prompt'
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'An unknown error occurred'
    } finally {
    }
  }

  async function start_chat() {
    if (state.selected_char) {
      const template = Handlebars.compile(state.selected_char.info.first_mes)
      state.story_entries = [
        {
          id: 0,
          speaker: '',
          content: template({
            user: 'Julien',
            char: state.selected_char.info.name,
          }),
          state: 'wait_prompt',
          image: null,
        },
      ]
      state.story_entries[0].speaker = state.selected_char.info.name
    }
  }

  function get_prev_prompt(i: number) {
    if (i > 0) {
      return state.story_entries[i - 1].image_prompt ?? ''
    }
    if (state.selected_char?.info.description) {
      const template = Handlebars.compile(state.selected_char.info.description)
      return template({ char: state.selected_char.info.name, user: 'Julien' })
    }
    return 'character appearance: blonde\nenvironment: living room'
  }

  function regenerate_content(i: number) {
    return async () => {
      if (i === state.story_entries.length - 1) {
        state.story_entries[state.story_entries.length - 1].content = ''
        state.story_entries[state.story_entries.length - 1].state = 'wait_content'
        await send_chat(state.story_entries, received_text)
        state.story_entries[state.story_entries.length - 1].state = 'wait_prompt'
      }
    }
  }

  const go_back = () => {
    chatInputValue = state.story_entries[state.story_entries.length - 2].content
    state.story_entries = state.story_entries.slice(0, state.story_entries.length - 2)
  }

  onMount(async () => {
    await start_chat()
    chatInputElement?.focus()
  })
</script>

<div class="chat-container">
  <div class="story">
    {#each state.story_entries as entry, i (entry.id)}
      <StoryScene
        {entry}
        prev_prompt={get_prev_prompt(i)}
        regenerate_content={regenerate_content(i)}
        index={i}
      />
    {/each}
  </div>

  <div class="flex justify-start">
    <Button
      id="go_back"
      color="light"
      size="sm"
      class="px-3 py-2 text-neutral-500 hover:border-neutral-300"
      onclick={go_back}><ArrowUturnLeft size="20" /></Button
    >
    <Popover triggeredBy="#go_back" class="text-sm p-2"
      >Go back to the previous step in the conversation</Popover
    >
  </div>
  <div class="chat-input-container">
    <span class="user-name">{user_name}:</span>
    <input
      bind:this={chatInputElement}
      type="text"
      bind:value={chatInputValue}
      on:keydown={handleChat}
      class="chat-input"
    />
  </div>
</div>

<style>
  .chat-container {
    margin-top: 2rem;
    margin-bottom: 2rem;
    width: 100%;
    padding: 0 70px;
  }

  .chat-input-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .user-name {
    font-weight: bold;
  }

  .chat-input {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    @apply focus:ring-2 ring-sky-500 outline-none;
  }
</style>
