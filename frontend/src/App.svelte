<script lang="ts">
  import StoryScene from './components/StoryScene.svelte'
  import CharacterList from './components/CharacterList.svelte'
  import { Icon } from '@steeze-ui/svelte-icon'
  import { UserGroup, ChatBubbleLeftRight } from '@steeze-ui/heroicons'
  import type { StoryEntry, StoryEntries } from './types/story'
  import type { Character } from './types/character'
  import { onMount } from 'svelte'
  import Handlebars from 'handlebars'

  let nextId = 1
  let prompt = ''
  let loading = false
  let generatedImage: string | null = null
  let chatInputValue = ''
  let currentEntry: StoryEntry = {
    id: 0,
    speaker: '',
    content: '',
    image: null,
  }
  let storyEntries: StoryEntries = [
    {
      id: nextId++,
      speaker: '',
      content: '',
      image: null,
    },
  ]
  let error: string | null = null
  let user_name = 'Julien'
  let chatInputElement: HTMLInputElement

  let characters: Character[] = []
  let selectedCharacter: Character | null = null
  let activeTab = 'characters'

  const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

  async function generateImage() {
    if (!prompt.trim()) return

    loading = true
    error = null
    // generatedImage = null

    const guidance_scale = 4.5
    const width = 832 * 1
    const height = 1216 * 1
    const prefix = 'score_9, score_8_up, score_7_up'
    const face_steps = 20

    try {
      const response = await fetch('http://localhost:5000/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `${prefix}, ${prompt}`,
          guidance_scale,
          width,
          height,
          face_steps,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate image')
      }

      generatedImage = data.image
    } catch (e) {
      error = e instanceof Error ? e.message : 'An error occurred'
    } finally {
      loading = false
    }
  }

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
      body: JSON.stringify({ info: selectedCharacter?.info, entries: chatEntries }),
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

  async function generate_image(text: string, portrait: boolean = true) {
    let width = 832
    let height = 1216
    if (!portrait) {
      width = 1216
      height = 832
    }
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
    return { image, width, height }
  }

  async function generate_last_image() {
    const last_index = storyEntries.length - 1
    storyEntries[last_index].image = 'wait_prompt'
    let prev_image_prompt = 'character appearance: blonde\nenvironment: living room'
    if (last_index > 0) {
      const prevEntry = storyEntries[last_index - 1]
      if (prevEntry.image_prompt) {
        prev_image_prompt = prevEntry.image_prompt
      }
    } else {
      if (selectedCharacter?.info.description) {
        const template = Handlebars.compile(selectedCharacter.info.description)
        prev_image_prompt = template({ char: selectedCharacter.info.name, user: 'Juliean' })
      }
    }
    let prompt = await scene_to_prompt(storyEntries[last_index].content, prev_image_prompt)
    if (!prompt) {
      prompt = storyEntries[last_index].content
    }
    storyEntries[last_index].image = 'wait_image'
    const prefix = 'score_9, score_8_up, score_7_up'
    const portrait = !!prompt.match(/format:\s*portrait/i)
    const { image, width, height } = await generate_image(`${prefix}, ${prompt}`, portrait)
    storyEntries[last_index].image = image
    storyEntries[last_index].width = width
    storyEntries[last_index].height = height
    storyEntries[last_index].image_prompt = prompt
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter') return
    if (!chatInputValue.trim()) return

    currentEntry = {
      id: 0,
      speaker: selectedCharacter?.info.name || 'AI',
      content: '',
      image: 'wait_prompt',
    }
    error = null

    try {
      storyEntries = [
        ...storyEntries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInputValue,
          image: null,
        },
      ]
      chatInputValue = ''
      await send_chat(storyEntries, received_text)
      storyEntries = [...storyEntries, { ...currentEntry, id: nextId++ }]
      currentEntry = {
        id: 0,
        speaker: selectedCharacter?.info.name || 'AI',
        content: '',
        image: 'wait_prompt',
      }
      await generate_last_image()
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'An unknown error occurred'
    } finally {
    }
  }

  function selectCharacter(character: Character) {
    selectedCharacter = character
  }

  function active_class(tab: string) {
    return activeTab === tab ? 'active' : ''
  }

  async function start_chat() {
    activeTab = 'chat'
    if (selectedCharacter) {
      const template = Handlebars.compile(selectedCharacter.info.first_mes)
      storyEntries[0].content = template({ user: 'Juliean', char: selectedCharacter.info.name })
      storyEntries[0].speaker = selectedCharacter.info.name
    }
    await generate_last_image()
  }

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/characters')
      if (response.ok) {
        characters = await response.json()
      } else {
        console.error('Failed to fetch characters')
      }
    } catch (error) {
      console.error('Error fetching characters:', error)
    }
    chatInputElement?.focus()
  })
</script>

<main class="container">
  <h1>Ai Meet Pal</h1>

  <!-- Tabs -->
  <div class="tabs">
    <button
      class="tab-button {active_class('characters')}"
      on:click={() => (activeTab = 'characters')}
    >
      <Icon src={UserGroup} width="24" height="24" class={active_class('characters')} />
      Characters
    </button>
    <button class="tab-button {active_class('chat')}" on:click={start_chat}>
      <Icon src={ChatBubbleLeftRight} width="24" height="24" class={active_class('chat')} />
      Chat
    </button>
  </div>

  {#if activeTab === 'characters'}
    <CharacterList {characters} {selectedCharacter} {selectCharacter} />
  {:else}
    <div class="chat-container">
      <div class="story">
        {#each storyEntries as entry (entry.id)}
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
  {/if}
</main>

<style>
  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
    font-family: 'Edwardian Script ITC', Georgia, 'Times New Roman', Times, serif;
    margin-top: 2rem;
  }

  button:hover:not(:disabled) {
    border-color: theme('colors.sky.100');
    border-bottom: 3px solid theme('colors.sky.100');
    border-radius: 0;
  }

  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .chat-container {
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

  .tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .tab-button {
    padding: 0.3rem 1rem;
    border: none;
    border-radius: 0;
    background: transparent;
    color: theme('colors.slate.400');
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.1rem;
    font-size: 0.8rem;
  }

  button.tab-icon {
    width: 32px;
    height: 32px;
    color: theme('colors.slate.100');
  }

  .tab-icon.active {
    color: theme('colors.blue.700');
  }

  .tab-button.active {
    color: theme('colors.sky.700');
    border-bottom: 3px solid theme('colors.sky.300');
  }

  .tab-button.active:hover {
    color: theme('colors.sky.800');
    border-bottom: 3px solid theme('colors.sky.500');
  }
</style>
