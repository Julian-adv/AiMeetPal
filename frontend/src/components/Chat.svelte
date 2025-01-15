<script lang="ts">
  import type { StoryEntry, StoryEntries } from '../types/story'
  import StoryScene from './StoryScene.svelte'
  import { state } from '../lib/state.svelte'
  import { onMount } from 'svelte'
  import Handlebars from 'handlebars'

  let nextId = 1
  let currentEntry: StoryEntry = {
    id: 0,
    speaker: '',
    content: '',
    image: null,
  }
  let user_name = 'Julien'
  let chatInputElement: HTMLInputElement
  let chatInputValue = ''
  let error: string | null = null

  function formatResponse(text: string): string {
    const match = text.match(
      /<\|start_header_id\|>writer character: (.*?)<\|end_header_id\|>\s*([^\s]+)$/
    )
    if (match) {
      currentEntry.speaker = match[1]
      return match[2]
    }
    return text
  }

  function received_text(text: string) {
    if (currentEntry.speaker === '') {
      currentEntry.content = formatResponse(currentEntry.content + text)
    } else {
      currentEntry.content += text
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

  async function scene_to_prompt(text: string, prev_image_prompt: string) {
    const response = await fetch('http://localhost:5000/api/scene-to-prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: text, prev_image_prompt: prev_image_prompt }),
    })
    const data = await response.json()
    return data.prompt
  }

  async function generate_image(text: string, width: number, height: number) {
    const response = await fetch('http://localhost:5000/api/generate-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: text,
        guidance_scale: 4.5,
        width: width * 1,
        height: height * 1,
        face_steps: 20,
      }),
    })
    const data = await response.json()
    const image = data.image
    return image
  }

  function image_size(prompt: string) {
    const portrait = !!prompt.match(/format:\s*portrait/i)
    if (portrait) {
      return { width: 832, height: 1216 }
    } else {
      return { width: 1216, height: 832 }
    }
  }

  async function generate_last_image() {
    const last_index = state.story_entries.length - 1
    state.story_entries[last_index].image = 'wait_prompt'
    let prev_image_prompt = 'character appearance: blonde\nenvironment: living room'
    if (last_index > 0) {
      const prevEntry = state.story_entries[last_index - 1]
      if (prevEntry.image_prompt) {
        prev_image_prompt = prevEntry.image_prompt
      }
    } else {
      if (state.selected_char?.info.description) {
        const template = Handlebars.compile(state.selected_char.info.description)
        prev_image_prompt = template({ char: state.selected_char.info.name, user: 'Juliean' })
      }
    }
    let prompt = await scene_to_prompt(state.story_entries[last_index].content, prev_image_prompt)
    if (!prompt) {
      prompt = state.story_entries[last_index].content
    }
    state.story_entries[last_index].image = 'wait_image'
    const prefix = 'score_9, score_8_up, score_7_up'
    const { width, height } = image_size(prompt)
    state.story_entries[last_index].width = width
    state.story_entries[last_index].height = height
    const image = await generate_image(`${prefix}, ${prompt}`, width, height)
    state.story_entries[last_index].image = image
    state.story_entries[last_index].image_prompt = prompt
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter') return
    if (!chatInputValue.trim()) return

    currentEntry = {
      id: 0,
      speaker: state.selected_char?.info.name || 'AI',
      content: '',
      image: 'wait_prompt',
    }
    error = null

    try {
      state.story_entries = [
        ...state.story_entries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInputValue,
          image: null,
        },
      ]
      chatInputValue = ''
      await send_chat(state.story_entries, received_text)
      state.story_entries = [...state.story_entries, { ...currentEntry, id: nextId++ }]
      currentEntry = {
        id: 0,
        speaker: state.selected_char?.info.name || 'AI',
        content: '',
        image: 'wait_prompt',
      }
      await generate_last_image()
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'An unknown error occurred'
    } finally {
    }
  }

  async function start_chat() {
    if (state.selected_char) {
      const template = Handlebars.compile(state.selected_char.info.first_mes)
      state.story_entries = []
      state.story_entries[0] = {
        id: 0,
        speaker: '',
        content: '',
        image: null,
      }
      state.story_entries[0].content = template({
        user: 'Juliean',
        char: state.selected_char.info.name,
      })
      state.story_entries[0].speaker = state.selected_char.info.name
    }
    await generate_last_image()
  }

  onMount(async () => {
    await start_chat()
    chatInputElement?.focus()
  })
</script>

<div class="chat-container">
  <div class="story">
    {#each state.story_entries as entry (entry.id)}
      <StoryScene {entry} />
    {/each}

    {#if currentEntry.content}
      <StoryScene entry={currentEntry} />
    {/if}
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
    max-width: 902px;
    margin-top: 2rem;
    margin-bottom: 2rem;
    width: 100%;
  }

  .chat-input-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
  }
</style>
