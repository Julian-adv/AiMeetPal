<script lang="ts">
  import { settings, load_settings, save_settings } from '../lib/settings.svelte'
  import { onMount } from 'svelte'
  import { Button, Input, Select, uiHelpers } from 'svelte-5-ui-lib'
  import { get_checkpoints, get_data_dir, get_dir_entries } from '../lib/files.svelte'
  import type { ApiType } from '../lib/settings.svelte'
  import FileDialog from './FileDialog.svelte'
  import type { Entry } from '@/types/file'

  let language_models: string[] = $state([])
  let checkpoints: string[] = $state([])
  let select_dialog = uiHelpers()
  let presets: { value: string; name: string }[] = $state([])

  $effect(() => {
    get_language_models(settings.api_type).then((models) => {
      language_models = models
    })
  })

  async function get_language_models(api_type: ApiType) {
    try {
      const response = await fetch(`http://localhost:5000/api/models?api_type=${api_type}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (response.ok) {
        const result = await response.json()
        return result.models
      }
    } catch (error) {
      console.error('Error fetching model list:', error)
      return []
    }
  }

  const handle_checkpoints_folder = async () => {
    select_dialog.toggle()
  }

  const select_path = async (current_dir: string) => {
    settings.checkpoints_folder = current_dir
    checkpoints = await get_checkpoints()
  }

  onMount(async () => {
    try {
      await load_settings()
    } catch (error) {
      console.error('Error loading settings:', error)
    }
    try {
      checkpoints = await get_checkpoints()
    } catch (error) {
      console.error('Error fetching checkpoints:', error)
    }
    try {
      language_models = await get_language_models(settings.api_type)
    } catch (error) {
      console.error('Error fetching language models:', error)
    }
    const data_dir = await get_data_dir()
    const entries = await get_dir_entries(data_dir + '/presets')
    presets = entries.entries.map((entry: Entry) => ({ value: entry.name, name: entry.name }))
  })
</script>

<h2>Settings</h2>
<div class="settings-container">
  <div class="settings">
    <div class="label">API type</div>
    <div>
      <select bind:value={settings.api_type}>
        <option value="infermaticai">Infermatic.ai</option>
        <option value="openai">OpenAI Compatible</option>
        <option value="googleaistudio">Google AI Studio</option>
      </select>
    </div>
    {#if settings.api_type === 'infermaticai'}
      <div class="label">Infermatic.ai API key</div>
      <Input
        type="password"
        class="focus:ring-2 ring-sky-500"
        bind:value={settings.infermaticai.api_key}
      />
      <div class="label">Preset</div>
      <Select items={presets} bind:value={settings.infermaticai.preset} />
      <div class="label">Instruct</div>
      <Select items={presets} bind:value={settings.infermaticai.instruct} />
      <div class="label">Context</div>
      <Select items={presets} bind:value={settings.infermaticai.context} />
      <div class="label">Language model</div>
      <div>
        <select bind:value={settings.infermaticai.model}>
          {#each language_models as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>
      <div class="label">Max tokens</div>
      <Input
        class="focus:ring-2 ring-sky-500"
        type="number"
        bind:value={settings.infermaticai.max_tokens}
      />
    {/if}
    {#if settings.api_type === 'openai'}
      <div class="label">Custom URL</div>
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.openai.custom_url} />
      <div class="label">API key</div>
      <Input
        type="password"
        class="focus:ring-2 ring-sky-500"
        bind:value={settings.openai.api_key}
      />
      <div class="label">Preset</div>
      <Select items={presets} bind:value={settings.openai.preset} />
      <div class="label">Language model</div>
      <div>
        <select bind:value={settings.openai.model}>
          {#each language_models as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>
      <div class="label">Max tokens</div>
      <Input
        class="focus:ring-2 ring-sky-500"
        type="number"
        bind:value={settings.openai.max_tokens}
      />
    {/if}
    {#if settings.api_type === 'googleaistudio'}
      <div class="label">API key</div>
      <Input
        type="password"
        class="focus:ring-2 ring-sky-500"
        bind:value={settings.googleaistudio.api_key}
      />
      <div class="label">Preset</div>
      <Select items={presets} bind:value={settings.googleaistudio.preset} />
      <div class="label">Module</div>
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.googleaistudio.module} />
      <div class="label">Language model</div>
      <div>
        <select bind:value={settings.googleaistudio.model}>
          {#each language_models as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>
      <div class="label">Max tokens</div>
      <Input
        class="focus:ring-2 ring-sky-500"
        type="number"
        bind:value={settings.googleaistudio.max_tokens}
      />
    {/if}
    <div class="label">Image model folder</div>
    <div class="folder-select">
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.checkpoints_folder} />
      <Button color="light" size="sm" onclick={handle_checkpoints_folder}>Browse...</Button>
    </div>
    <div class="label">Image model</div>
    <div>
      <select bind:value={settings.checkpoint_name}>
        {#each checkpoints as checkpoint}
          <option value={checkpoint}>{checkpoint}</option>
        {/each}
      </select>
    </div>
  </div>
  <Button color="sky" class="m-3 mx-auto" onclick={() => save_settings()}>Save</Button>
</div>

<FileDialog
  title="Select checkpoints folder"
  ok_text="Select"
  init_dir={settings.checkpoints_folder}
  on_init={(modal) => (select_dialog = modal)}
  on_ok={select_path}
/>

<style>
  @reference "tailwindcss/theme";

  .settings-container {
    display: flex;
    flex-direction: column;
    text-align: left;
    width: 100%;
    padding: 0.5rem;
  }

  .settings {
    display: grid;
    align-items: center;
    grid-template-columns: 200px 1fr;
    gap: 1rem;
    margin: 0.5rem 0;
    color: theme('colors.neutral.700');
  }

  .label {
    justify-self: end;
    color: theme('colors.neutral.500');
  }

  .folder-select {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  select {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    width: auto;
  }

  select:focus {
    @apply ring-2 ring-sky-500 outline-none;
  }
</style>
