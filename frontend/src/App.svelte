<script lang="ts">
  import StoryScene from './components/StoryScene.svelte'
  import type { StoryEntry, StoryEntries } from './types/story'

  let nextId = 1
  let prompt = ''
  let loading = false
  let generatedImage: string | null = null
  let chatInput = ''
  let currentEntry: StoryEntry = {
    id: 0,
    speaker: '',
    content: '',
    image: null,
  }
  let storyEntries: StoryEntries = [{
    id: nextId++,
    speaker: 'Stellar',
    content: 'Good morning. Master. Jessica, your new maid candidate, has arrived and is waiting for you. Shall I bring her here?',
    image: null,
  }]
  let chatLoading = false
  let error: string | null = null

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
      body: JSON.stringify({ entries: chatEntries }),
    })

    if (!response.ok) {
      throw new Error('Chat request failed')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Failed to get response reader')
    }
    const decoder = new TextDecoder()
    let lastActivity = Date.now()
    const TIMEOUT_MS = 10000 // 10 seconds timeout

    try {
      while (true) {
        const { value, done } = await reader.read()

        if (done) break

        // Check for timeout
        const now = Date.now()
        if (now - lastActivity > TIMEOUT_MS) {
          throw new Error('Stream timeout')
        }
        lastActivity = now

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ') && line.trim() !== 'data: ') {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.text) {
                received(data.text)
                lastActivity = Date.now() // Reset timeout on valid data
              }
            } catch (e) {
              console.error('Failed to parse JSON:', e)
            }
          }
        }
      }
    } finally {
      reader.cancel()
    }
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter') return
    if (!chatInput.trim()) return

    chatLoading = true
    currentEntry = {
      id: 0,
      speaker: '',
      content: '',
      image: null,
    }
    error = null

    try {
      storyEntries = [
        ...storyEntries,
        {
          id: nextId++,
          speaker: 'Julien',
          content: chatInput,
          image: null,
        },
      ]
      chatInput = ''
      await send_chat(storyEntries, received_text)
      storyEntries = [...storyEntries, { ...currentEntry, id: nextId++ }]
      currentEntry = {
        id: 0,
        speaker: '',
        content: '',
        image: null,
      }
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'An unknown error occurred'
    } finally {
      chatLoading = false
    }
  }
</script>

<main class="container">
  <h1>AiMeetPal Image Generator</h1>

  <div class="input-section">
    <textarea bind:value={prompt} placeholder="Enter your prompt here..."></textarea>
    <button on:click={generateImage} disabled={loading || !prompt.trim()}>
      {loading ? 'Generating...' : 'Generate Image'}
    </button>
  </div>

  {#if error}
    <div class="error">
      {error}
    </div>
  {/if}

  {#if generatedImage}
    <div class="image-container">
      <img src={generatedImage} alt={prompt} />
      <p class="prompt">Prompt: {prompt}</p>
    </div>
  {/if}

  <div class="chat-container">
    {#if chatLoading}
      <p>Loading...</p>
    {/if}
    {#each storyEntries as entry (entry.id)}
      <StoryScene {entry} />
    {/each}
    {#if currentEntry.content}
      <StoryScene entry={currentEntry} />
    {/if}
    <input
      type="text"
      bind:value={chatInput}
      on:keydown={handleChat}
      placeholder="Type your message and press Enter..."
      disabled={chatLoading}
      class="chat-input"
    />
  </div>
</main>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
  }

  .input-section {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  textarea {
    flex: 1;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: consolas;
  }

  button {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  button:hover:not(:disabled) {
    background-color: #45a049;
  }

  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .error {
    color: #ff0000;
    padding: 1rem;
    background-color: #ffebee;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .image-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .image-container img {
    max-width: 700px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .prompt {
    color: #666;
    font-style: italic;
  }

  .chat-container {
    margin-top: 2rem;
    width: 100%;
  }

  .chat-input {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style>
