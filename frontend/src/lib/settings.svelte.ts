import { load_json, save_json } from './files.svelte'

interface InfermaticAISettings {
  api_key: string
  preset: string
  instruct: string
  context: string
  model: string
  max_tokens: number
}

interface OpenAISettings {
  api_key: string
  custom_url: string
  preset: string
  model: string
  max_tokens: number
}

interface Settings {
  api_type: 'infermaticai' | 'openai'
  infermaticai: InfermaticAISettings
  openai: OpenAISettings
  checkpoints_folder: string
  checkpoint_name: string
  prefix: string
}

export const settings: Settings = $state({
  api_type: 'infermaticai',
  infermaticai: {
    api_key: 'your api key',
    preset: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json',
    instruct: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json',
    context: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json',
    model: 'anthracite-org-magnum-v4-72b-FP8-Dynamic',
    max_tokens: 1024,
  },
  openai: {
    api_key: 'your api key',
    custom_url: 'https://api.kluster.ai/v1',
    preset: 'default.json',
    model: 'deepseek-ai/DeepSeek-R1',
    max_tokens: 1024,
  },
  checkpoints_folder: '.',
  checkpoint_name: '',
  prefix: '',
})

interface Preset {
  max_length: number
}

export const preset: Preset = $state({
  max_length: 8192,
})

function updateObject(target: any, source: any): void {
  for (const key of Object.keys(target)) {
    if (key in source) {
      if (typeof target[key] === 'object') {
        updateObject(target[key], source[key])
      } else {
        target[key] = source[key]
      }
    }
  }
}

export async function load_settings() {
  const server_settings = await load_json('settings.json')
  if (server_settings) {
    updateObject(settings, server_settings)

    if (settings.api_type === 'infermaticai') {
      preset.max_length = server_settings.infermaticai.preset.max_length
    } else if (settings.api_type === 'openai') {
      const preset_json = await load_json(server_settings.openai.preset)
      preset.max_length = preset_json.openai_max_context
    }
  }
}

export async function save_settings() {
  await save_json('settings.json', settings)
}
