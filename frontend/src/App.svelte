<script lang="ts">
  let prompt = ''
  let loading = false
  let generatedImage: string | null = null
  let error: string | null = null
  let chatInput = ''
  let chatResponse = ''
  let chatLoading = false

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
        body: JSON.stringify({ prompt: `${prefix}, ${prompt}`, guidance_scale, width, height, face_steps }),
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

  function received_text(text: string) {
    chatResponse += text
  }

  async function send_chat(received: (text: string) => void) {
    const url = 'https://api.totalgpt.ai/v1/completions'
    const userName = 'Julian'
    const charName = 'Stellar'
    const stopping_strings = [
      '\nJulien:',
      '\nStellar:',
      '<|eot_id|>'
    ]
    const request = {
      prompt: '<|start_header_id|>system<|end_header_id|>\n' +
              '\n' +
              'Develop the plot slowly, always stay in character. Describe all actions in full, elaborate, explicit, graphic, and vivid detail. Mention all relevant sensory perceptions. Keep the story immersive and engaging.\n' +
              '\n' +
              '\n' +
              '## Overall plot description:\n' +
              '\n' +
              'Conversation between Stellar and Julien.\n' +
              '\n' +
              '\n' +
              '## Characters:\n' +
              '\n' +
              '### Stellar\n' +
              '\n' +
              `[Stellar's Personality= "loyal", "cheerful", "intelligent", "smart", "wise", "mischievous", "proactive", "young (20 years old)"]\n` +
              `[Stellar's body= "silver-blonde hair", "long straight hair", "turquoise eyes", "long eyelashes", "white teeth", "pink plump glossy lips", "milky white skin", "porcelain-smooth skin", "large breasts (32F cup)", "firm breasts that seem to defy gravity", "long, slender legs", "slender waist (56cm, 22in)", "tight buttocks", "small feet", "long slender fingers", "tall height (175cm, 5'9)"]\n` +
              "[Genre: romance fantasy; Tags: adult; Scenario: Stellar is working at Julien's mansion as a head maid.]\n" +
              '\n' +
              '### Julien\n' +
              '\n' +
              'Julien is living alone in a luxury mansion.\n' +
              '\n' +
              'The first floor of the mansion includes the master bedroom, master bathroom, living room, kitchen, family room, and study. On the second floor, there are rooms for the maids.<|eot_id|>\n' +
              '<|start_header_id|>user<|end_header_id|>\n' +
              '\n' +
              'Start the role-play between Stellar and Julien.\n' +
              '<|eot_id|>\n' +
              '<|start_header_id|>writer character: Stellar<|end_header_id|>\n' +
              '\n' +
              'Good morning. Master. Jessica, your new maid candidate, has arrived and is waiting for you. Shall I bring her here?<|eot_id|>\n' +
              '<|start_header_id|>writer character: Julien<|end_header_id|>\n' +
              '\n' +
              'Yes please<|eot_id|>\n',
      model: 'anthracite-org-magnum-v4-72b-FP8-Dynamic',
      max_new_tokens: 512,
      max_tokens: 512,
      temperature: 1,
      top_p: 1,
      typical_p: 1,
      typical: 1,
      sampler_seed: -1,
      min_p: 0.02,
      repetition_penalty: 1,
      frequency_penalty: 0,
      presence_penalty: 0,
      top_k: -1,
      skew: 0,
      min_tokens: 0,
      add_bos_token: true,
      smoothing_factor: 0,
      smoothing_curve: 1,
      dry_allowed_length: 2,
      dry_multiplier: 0.75,
      dry_base: 1.75,
      dry_sequence_breakers: '["\\n",":","\\"","*"]',
      dry_penalty_last_n: 0,
      max_tokens_second: 0,
      stopping_strings: [
        '\nJulien:',
        '\nStellar:',
        '<|eot_id|>'
      ],
      stop: [
        '\nJulien:',
        '\nStellar:',
        '<|eot_id|>'
      ],
      truncation_length: 8192,
      ban_eos_token: false,
      skip_special_tokens: true,
      top_a: 0,
      tfs: 1,
      mirostat_mode: 0,
      mirostat_tau: 5,
      mirostat_eta: 0.1,
      custom_token_bans: '',
      banned_strings: [],
      api_type: 'infermaticai',
      api_server: 'https://api.totalgpt.ai',
      xtc_threshold: 0.1,
      xtc_probability: 0.5,
      nsigma: 0,
      n: 1,
      ignore_eos: false,
      spaces_between_special_tokens: true,
      stream: true
    }
    const respFromInfermatic = await fetch(url, {
      body: JSON.stringify(request),
      headers: {
        Authorization: 'Bearer sk-8jR-oZvU6VmFM_BYKXOP6g',
        'Content-Type': 'application/json'
      },
      method: 'POST',
      signal: null
    })
    if (
      respFromInfermatic.ok &&
      respFromInfermatic.status >= 200 &&
      respFromInfermatic.status < 300
    ) {
      const reader = respFromInfermatic.body?.getReader()
      const decoder = new TextDecoder()
      reader?.read().then(async function processText({ value }): Promise<void> {
        if (value === undefined) {
          return
        }
        const str = decoder.decode(value)
        const strs = str.split('\n')
        for (const str of strs) {
          if (str.startsWith('data: ')) {
            const text = str.slice(6)
            if (text === '[DONE]') {
              return
            } else {
              const json = JSON.parse(text)
              if (json.choices[0].text) {
                received(json.choices[0].text)
              }
            }
          }
        }
        return reader?.read().then(processText)
      })
    }
  }

  async function handleChat(event: KeyboardEvent) {
    if (event.key !== 'Enter') return
    if (!chatInput.trim()) return

    chatLoading = true
    chatResponse = ''
    error = null

    try {
      send_chat(received_text)
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
    <textarea
      bind:value={prompt}
      placeholder="Enter your prompt here..."
    ></textarea>
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
    <input
      type="text"
      bind:value={chatInput}
      on:keydown={handleChat}
      placeholder="Type your message and press Enter..."
      disabled={chatLoading}
      class="chat-input"
    />
    {#if chatLoading}
      <p>Loading...</p>
    {/if}
    {#if chatResponse}
      <div class="chat-response">
        {chatResponse}
      </div>
    {/if}
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

  .loading {
    text-align: center;
    color: #666;
    margin: 2rem 0;
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

  .chat-response {
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 4px;
    white-space: pre-wrap;
    margin-top: 1rem;
  }
</style>
