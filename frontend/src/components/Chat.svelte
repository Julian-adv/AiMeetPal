<script lang="ts">
  import type { StoryEntries, StoryEntry } from '../types/story'
  import type { Character } from '../types/character'
  import StoryScene from './StoryScene.svelte'
  import { g_state } from '../lib/state.svelte'
  import { onMount } from 'svelte'
  import Handlebars from 'handlebars'
  import { Button, Popover } from 'svelte-5-ui-lib'
  import { ArrowUturnLeft, DocumentArrowUp, DocumentPlus } from 'svelte-heros-v2'
  import { preset, load_settings } from '../lib/settings.svelte'
  import { StoryEntryState } from '../types/story'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { TBoxLineDesign } from 'svelte-remix'
  import LoadSession from './LoadSession.svelte'
  import type { Session } from '../types/session'

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
  let load_session_modal: any = $state(false)

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
    const chatEntries = entries.map(({ id, speaker, content, token_count }) => ({
      id,
      speaker,
      content,
      token_count,
    }))

    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        system_token_count: g_state.system_token_count,
        info: g_state.selected_char?.info,
        entries: chatEntries,
      }),
    })

    if (!response.ok) {
      throw new Error('Chat request failed')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Failed to get response reader')
    }
    const decoder = new TextDecoder()

    g_state.story_entries = [
      ...g_state.story_entries,
      {
        id: nextId++,
        speaker: g_state.selected_char?.info.name ?? 'AI',
        content: '',
        state: StoryEntryState.WaitContent,
        image: null,
      },
    ]
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
            if (data.start_index !== undefined) {
              g_state.start_index = data.start_index
            }
          } catch (e) {
            console.error('Failed to parse JSON:', e)
          }
        }
      }
    }
  }

  async function count_tokens(system_prompt: boolean, info: any, entry: StoryEntry) {
    try {
      const response = await fetch('http://localhost:5000/api/count-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ system_prompt, info, entry }),
      })

      const data = await response.json()
      return data
    } catch (e) {
      console.error('Failed to count tokens:', e)
      return { success: false }
    }
  }

  async function update_token_count() {
    if (!g_state.selected_char) return
    let total_tokens = 0
    for (let i = g_state.story_entries.length - 1; i >= 0; i--) {
      if (!g_state.story_entries[i].token_count) {
        const response = await count_tokens(
          false,
          g_state.selected_char?.info,
          g_state.story_entries[i]
        )
        g_state.story_entries[i].token_count = response.total_tokens
      }
      total_tokens += g_state.story_entries[i].token_count ?? 0
    }
    if (g_state.system_token_count === 0) {
      const response = await count_tokens(
        true,
        g_state.selected_char?.info,
        g_state.story_entries[0]
      )
      g_state.system_token_count = response.total_tokens
    }
    total_tokens += g_state.system_token_count
    token_count = total_tokens
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter' || event.shiftKey || !chatInputElement) return
    if (!chatInputValue.trim()) return

    event.preventDefault()

    // Wait for the next frame to ensure the Enter key event is fully processed
    await new Promise((resolve) => requestAnimationFrame(resolve))

    try {
      error = null
      g_state.story_entries = [
        ...g_state.story_entries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInputValue,
          state: StoryEntryState.NoImage,
          image: null,
        },
      ]
      chatInputValue = ''
      await send_chat(g_state.story_entries, received_text)
      g_state.story_entries[g_state.story_entries.length - 1].state = StoryEntryState.WaitPrompt
      await update_token_count()
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

  const load_session = async () => {
    load_session_modal.toggle()
  }

  const on_init = (modal: any) => {
    load_session_modal = modal
  }

  const on_load = async (session: Session) => {
    session_char = session.selected_char
    g_state.system_token_count = session.system_token_count
    g_state.story_entries = session.story_entries
    session_name = session.session_name
    nextId = Math.max(...g_state.story_entries.map((entry) => entry.id)) + 1
    // Load images for entries that have image_path
    for (const entry of g_state.story_entries) {
      if (entry.image_path && !entry.image) {
        entry.image = `http://localhost:5000/data/${entry.image_path}`
      }
    }
    await update_token_count()
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
        on_load(lastSession.session)
      } else {
        await new_session()
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
        await update_token_count()
      }
    }
  }

  const go_back = async () => {
    chatInputValue = g_state.story_entries[g_state.story_entries.length - 2].content
    g_state.story_entries = g_state.story_entries.slice(0, g_state.story_entries.length - 2)
    const count = g_state.story_entries[g_state.story_entries.length - 1].token_count
    if (count) {
      token_count = count
    } else {
      await update_token_count()
    }
  }

  const new_session = async () => {
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
      await update_token_count()
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
        system_token_count: g_state.system_token_count,
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
      {#if i === g_state.start_index}
        <div class="context-separator"></div>
      {/if}
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
    <Button
      id="load_session"
      color="light"
      size="sm"
      class="px-3 py-2 text-neutral-500"
      onclick={load_session}><DocumentArrowUp size="20" /></Button
    >
    <Popover triggeredBy="#load_session" class="text-sm p-2">Load a saved session</Popover>
    <TBoxLineDesign size="24" class="text-neutral-300" />
    <div class="text-sm text-neutral-500">
      {token_count} / {preset.max_length}
    </div>
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
<LoadSession {on_init} {on_load} />

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

  .context-separator {
    border-top: 2px dotted #ff4444;
    margin: 8px 0;
  }
</style>
