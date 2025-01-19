interface Settings {
  infermaticAiApiKey: string
  preset: string
  instruct: string
  context: string
  model: string
  max_tokens: number
  checkpoints_folder: string
  checkpoint_name: string
}

export const settings: Settings = $state({
  infermaticAiApiKey: 'your api key',
  preset: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json',
  instruct: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json',
  context: 'anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json',
  model: 'anthracite-org-magnum-v4-72b-FP8-Dynamic',
  max_tokens: 1024,
  checkpoints_folder: '.',
  checkpoint_name: '',
})
