<script lang="ts">
  import type { StoryEntries, StoryEntry } from '../types/story'
  import type { Character } from '../types/character'
  import StoryScene from './StoryScene.svelte'
  import { g_state } from '../lib/state.svelte'
  import { onMount } from 'svelte'
  import Handlebars from 'handlebars'
  import { Button, Popover } from 'svelte-5-ui-lib'
  import { ArrowUturnLeft, DocumentPlus } from 'svelte-heros-v2'
  import { preset, load_settings } from '../lib/settings.svelte'
  import { StoryEntryState } from '../types/story'
  import FlexibleTextarea from './FlexibleTextarea.svelte'

  let nextId = 1
  let user_name = 'Julien'
  let chatInputElement: HTMLTextAreaElement | undefined = $state(undefined)
  let chatInputValue = $state('')
  let error: string | null = null
  let session_name: string = ''
  let token_count: number = $state(0)
  let session_char: Character = {
    file_name: '',
    image: '',
    info: {
      name: '',
      description: '',
      personality: '',
      scenario: '',
      first_mes: '',
      mes_example: '',
      image_prompt: '',
    },
  }

  function formatResponse(text: string): string {
    const match = text.match(
      /<\|start_header_id\|>writer character: (.*?)<\|end_header_id\|>\s*([^\s]+)$/
    )
    if (match) {
      g_state.story_entries[g_state.story_entries.length - 1].speaker = match[1]
      return match[2]
    }
    return text
  }

  function received_text(text: string) {
    if (g_state.story_entries[g_state.story_entries.length - 1].speaker === '') {
      g_state.story_entries[g_state.story_entries.length - 1].content = formatResponse(
        g_state.story_entries[g_state.story_entries.length - 1].content + text
      )
    } else {
      g_state.story_entries[g_state.story_entries.length - 1].content =
        g_state.story_entries[g_state.story_entries.length - 1].content + text
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
      body: JSON.stringify({ info: g_state.selected_char?.info, entries: chatEntries }),
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

  async function count_tokens(info: any, entries: StoryEntry[]) {
    try {
      const response = await fetch('http://localhost:5000/api/count-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ info, entries }),
      })

      const data = await response.json()
      return data
    } catch (e) {
      console.error('Failed to count tokens:', e)
      return { success: false }
    }
  }

  function update_token_count() {
    count_tokens(g_state.selected_char?.info, g_state.story_entries).then((response) => {
      token_count = response.total_tokens
      g_state.story_entries[g_state.story_entries.length - 1].token_count = token_count
    })
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter' || event.shiftKey || !chatInputElement) return
    if (!chatInputValue.trim()) return

    error = null

    try {
      g_state.story_entries = [
        ...g_state.story_entries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInputValue,
          state: StoryEntryState.NoImage,
          image: null,
        },
        {
          id: nextId++,
          speaker: g_state.selected_char?.info.name ?? 'AI',
          content: '',
          state: StoryEntryState.WaitContent,
          image: null,
        },
      ]
      if (chatInputElement) {
        chatInputElement.rows = 1
      }
      chatInputValue = ''
      await send_chat(g_state.story_entries, received_text)
      g_state.story_entries[g_state.story_entries.length - 1].state = StoryEntryState.WaitPrompt
      update_token_count()
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'An unknown error occurred'
    } finally {
    }
  }

  async function load_last_session() {
    try {
      const response = await fetch('http://localhost:5000/api/load-last-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: g_state.selected_char?.file_name.replace('.card', '') }),
      })
      const data = await response.json()
      return data
    } catch (e) {
      console.error('Failed to load last session:', e)
      return { success: false }
    }
  }

  async function load_session_image(
    entry: StoryEntry,
    character_name: string,
    session_name: string
  ) {
    try {
      const response = await fetch('http://localhost:5000/api/load-session-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name,
          session_name,
          index: entry.id,
        }),
      })
      const data = await response.json()
      if (data.success) {
        entry.image = data.image
      }
    } catch (e) {
      console.error('Failed to load session image:', e)
    }
  }

  async function start_chat() {
    if (g_state.selected_char) {
      const lastSession = await load_last_session()

      if (lastSession.success && lastSession.session) {
        session_char = lastSession.session.selected_char
        g_state.story_entries = lastSession.session.story_entries
        session_name = lastSession.session_name
        nextId = Math.max(...g_state.story_entries.map((entry) => entry.id)) + 1

        // Load images for entries that have image_path
        const character_name = g_state.selected_char.file_name.replace('.card', '')
        for (const entry of g_state.story_entries) {
          if (entry.image_path && !entry.image) {
            await load_session_image(entry, character_name, session_name)
          }
        }
        update_token_count()
      } else {
        new_session()
      }
    }
  }

  function regenerate_content(i: number) {
    return async () => {
      if (i === g_state.story_entries.length - 1) {
        g_state.story_entries[g_state.story_entries.length - 1].content = ''
        g_state.story_entries[g_state.story_entries.length - 1].state = StoryEntryState.WaitContent
        await send_chat(g_state.story_entries, received_text)
        g_state.story_entries[g_state.story_entries.length - 1].state = StoryEntryState.WaitPrompt
      }
    }
  }

  const go_back = () => {
    chatInputValue = g_state.story_entries[g_state.story_entries.length - 2].content
    g_state.story_entries = g_state.story_entries.slice(0, g_state.story_entries.length - 2)
    const count = g_state.story_entries[g_state.story_entries.length - 1].token_count
    if (count) {
      token_count = count
    } else {
      update_token_count()
    }
  }

  const new_session = () => {
    if (g_state.selected_char) {
      const template = Handlebars.compile(g_state.selected_char.info.first_mes)
      g_state.story_entries = [
        {
          id: 0,
          speaker: '',
          content: template({
            user: 'Julien',
            char: g_state.selected_char.info.name,
          }),
          state: StoryEntryState.WaitPrompt,
          image: null,
        },
      ]
      g_state.story_entries[0].speaker = g_state.selected_char.info.name
      session_name = new Date().toLocaleString('sv').replace(/:/g, '-')
      session_char = { ...g_state.selected_char }
      update_token_count()
    }
  }

  async function save_session_image(file_name: string, image: string | null) {
    if (image) {
      const imageResponse = await fetch('http://localhost:5000/api/save-session-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: session_char.file_name.replace('.card', ''),
          session_name,
          index: file_name,
          image: image,
        }),
      })
      const result = await imageResponse.json()
      if (result.success) {
        return result.path
      }
    }
    return null
  }

  const image_generated = async (entry: StoryEntry) => {
    try {
      if (session_char.image.startsWith('data:image/png;base64,')) {
        const path = await save_session_image('character', session_char.image)
        if (path) {
          session_char.image = path
        }
      }

      // First save the image
      const path = await save_session_image(entry.id.toString(), entry.image)
      if (path) {
        entry.image_path = path
      }

      // Then save the session
      const payload = {
        session_name: session_name,
        selected_char: session_char,
        story_entries: g_state.story_entries.map(({ image, ...entry }) => entry),
      }
      await fetch('http://localhost:5000/api/save-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
    } catch (e) {
      console.error('Failed to save session:', e)
    }
  }

  onMount(async () => {
    await start_chat()
    await load_settings()
    setTimeout(() => {
      chatInputElement?.focus()
    }, 0)
  })
</script>

<div class="chat-container">
  <div class="story">
    {#each g_state.story_entries as entry, i (entry.id)}
      <StoryScene {entry} regenerate_content={regenerate_content(i)} index={i} {image_generated} />
    {/each}
  </div>

  <div class="flex justify-start items-center gap-2">
    <Button
      id="go_back"
      color="light"
      size="sm"
      class="px-3 py-2 text-neutral-500"
      onclick={go_back}><ArrowUturnLeft size="20" /></Button
    >
    <Popover triggeredBy="#go_back" class="text-sm p-2"
      >Go back to the previous step in the conversation</Popover
    >
    <Button
      id="new_session"
      color="light"
      size="sm"
      class="px-3 py-2 text-neutral-500"
      onclick={new_session}><DocumentPlus size="20" /></Button
    >
    <Popover triggeredBy="#new_session" class="text-sm p-2">Start a new session</Popover>
    <div class="text-sm text-neutral-500">Tokens: {token_count} / {preset.max_length}</div>
  </div>
  <div class="chat-input-container">
    <span class="user-name">{user_name}:</span>
    <FlexibleTextarea
      bind:textarea={chatInputElement}
      bind:value={chatInputValue}
      onkeydown={handleChat}
      class="chat-input"
    />
  </div>
</div>

<style lang="postcss">
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
