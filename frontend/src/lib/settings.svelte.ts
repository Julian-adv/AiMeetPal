interface Settings {
  api_type: 'infermatic' | 'openai'
  infermaticAiApiKey: string
  openAiApiKey: string
  customUrl: string
  preset: string
  instruct: string
  context: string
  model: string
  max_tokens: number
  checkpoints_folder: string
  checkpoint_name: string
}

export const settings: Settings = $state({
  api_type: 'infermatic',
  infermaticAiApiKey: 'your api key',
  openAiApiKey: 'your api key',
  customUrl: 'https://api.infermatic.ai',
  preset: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json',
  instruct: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json',
  context: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json',
  model: 'anthracite-org-magnum-v4-72b-FP8-Dynamic',
  max_tokens: 1024,
  checkpoints_folder: '.',
  checkpoint_name: '',
})

interface Preset {
  max_length: number
}

export const preset: Preset = $state({
  max_length: 8192,
})

async function load_server_settings() {
  try {
    const response = await fetch('http://localhost:5000/api/settings')
    if (response.ok) {
      const data = await response.json()
      return data
    }
  } catch (error) {
    console.error('Error fetching model list:', error)
    return []
  }
}

export async function load_settings() {
  const server_settings = await load_server_settings()
  Object.assign(settings, server_settings.settings)
  Object.assign(preset, server_settings.preset)
}
