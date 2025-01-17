<script lang="ts">
  import { settings } from '../lib/settings.svelte'
  import { onMount } from 'svelte'
  import { Modal, Button, Input, uiHelpers, Breadcrumb, BreadcrumbItem } from 'svelte-5-ui-lib'

  let language_models: string[] = $state([])
  let checkpoints: string[] = $state([])
  const modalExample = uiHelpers()
  let modalStatus = $state(false)
  const closeModal = modalExample.close
  $effect(() => {
    modalStatus = modalExample.isOpen
  })

  interface Entry {
    name: string
    is_dir: boolean
  }

  let dir_entries: { entries: Entry[]; current_directory: string } = $state({
    entries: [],
    current_directory: '.',
  })

  let path_entries = $state<string[]>([])

  async function get_checkpoints() {
    try {
      const entries = await get_dir_entries(settings.checkpoints_folder)
      checkpoints = entries.entries.map((entry: Entry) => entry.name)
    } catch (error) {
      console.error('Error fetching checkpoints:', error)
    }
  }

  async function get_language_models() {
    try {
      const response = await fetch('https://api.totalgpt.ai/v1/models', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${settings.infermaticAiApiKey}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        const models = data.data.map((model: any) => model.id)
        return models.sort((a: string, b: string) => a.toLowerCase().localeCompare(b.toLowerCase()))
      }
    } catch (error) {
      console.error('Error fetching model list:', error)
      return []
    }
  }

  async function get_dir_entries(path: string) {
    const response = await fetch('http://localhost:5000/api/files', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path: path }),
    })
    if (response.ok) {
      return await response.json()
    }
    throw new Error('Failed to fetch directory entries')
  }

  function dir_to_path_entries(path: string) {
    const entries = path.split(/[\/\\]/)
    return ['This PC', ...entries]
  }

  const handle_checkpoints_folder = async () => {
    modalExample.toggle()
    dir_entries = await get_dir_entries(dir_entries.current_directory)
    path_entries = dir_to_path_entries(dir_entries.current_directory)
  }

  const handle_breadcrumb_click = (index: number) => async () => {
    dir_entries.current_directory = dir_entries.current_directory
      .split(/[\/\\]/)
      .slice(0, index)
      .join('/')
    path_entries = dir_to_path_entries(dir_entries.current_directory)
    dir_entries = await get_dir_entries(dir_entries.current_directory + '/')
  }

  const handle_entry_click = (entry: Entry) => async () => {
    if (entry.is_dir) {
      let new_path =
        dir_entries.current_directory === '.' || dir_entries.current_directory === '/'
          ? entry.name
          : `${dir_entries.current_directory}/${entry.name}`
      new_path = new_path.replace(/\\/g, '/')
      new_path = new_path.replace(/\/\//g, '/')
      dir_entries = await get_dir_entries(new_path + '/')
      path_entries = dir_to_path_entries(new_path)
    }
  }

  async function save_server_settings(settings: any) {
    try {
      const response = await fetch('http://localhost:5000/api/save_settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      })
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      return []
    }
  }

  const select_path = async () => {
    settings.checkpoints_folder = dir_entries.current_directory
    modalExample.close()
    await get_checkpoints()
  }

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

  onMount(async () => {
    const server_settings = await load_server_settings()
    Object.assign(settings, server_settings)
    dir_entries.current_directory = settings.checkpoints_folder
    try {
      dir_entries = await get_dir_entries(dir_entries.current_directory)
    } catch (error) {
      console.error('Error fetching dir entries:', error)
      dir_entries.current_directory = '.'
      try {
        dir_entries = await get_dir_entries(dir_entries.current_directory)
      } catch (error) {
        console.error('Error fetching dir entries .:', error)
      }
    }
    try {
      await get_checkpoints()
    } catch (error) {
      console.error('Error fetching checkpoints:', error)
    }
    try {
      language_models = await get_language_models()
    } catch (error) {
      console.error('Error fetching language models:', error)
    }
  })
</script>

<h2>Settings</h2>
<div class="settings-container">
  <div class="settings">
    <div class="label">Infermatic.ai API key</div>
    <Input class="focus:ring-2 ring-sky-500" bind:value={settings.infermaticAiApiKey} />
    <div class="label">Preset</div>
    <Input class="focus:ring-2 ring-sky-500" bind:value={settings.preset} />
    <div class="label">Instruct</div>
    <Input class="focus:ring-2 ring-sky-500" bind:value={settings.instruct} />
    <div class="label">Context</div>
    <Input class="focus:ring-2 ring-sky-500" bind:value={settings.context} />
    <div class="label">Language model</div>
    <div>
      <select bind:value={settings.model}>
        {#each language_models as model}
          <option value={model}>{model}</option>
        {/each}
      </select>
    </div>
    <div class="label">Max tokens</div>
    <Input class="focus:ring-2 ring-sky-500" bind:value={settings.max_tokens} />
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
  <Button color="primary" class="m-3 mx-auto" onclick={() => save_server_settings(settings)}
    >Save</Button
  >
</div>

<Modal size="lg" title="Select folder" {modalStatus} {closeModal}>
  <div class="overflow-hidden">
    <Breadcrumb>
      {#each path_entries as entry, i}
        <BreadcrumbItem href="#" home={i === 0} onclick={handle_breadcrumb_click(i)}
          >{entry}</BreadcrumbItem
        >
      {/each}
    </Breadcrumb>
  </div>
  <div class="entries">
    {#each dir_entries.entries as entry}
      <button
        type="button"
        class={entry.is_dir ? 'entry' : 'entry-file'}
        onclick={handle_entry_click(entry)}
      >
        <div>{entry.is_dir ? '📁' : '📄'}</div>
        <div class="entry-name">{entry.name}</div>
      </button>
    {/each}
  </div>
  {#snippet footer()}
    <Button type="submit" color="sky" class="me-2" onclick={select_path}>Select</Button>
    <Button onclick={closeModal} color="alternative">Cancel</Button>
  {/snippet}
</Modal>

<style lang="postcss">
  .settings-container {
    display: flex;
    flex-direction: column;
    text-align: left;
    width: 100%;
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

  .entries {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
    gap: 0.2rem;
    margin: 1rem 0;
    justify-items: start;
    max-height: 40vh;
    overflow-y: auto;
  }

  .entry {
    padding: 0.1rem 0.5rem 0.3rem 0.4rem;
    display: flex;
    align-items: center;
    max-width: 10rem;
    gap: 0.2rem;
    background-color: transparent;
  }

  .entry:hover {
    background-color: theme('colors.sky.300');
    cursor: pointer;
    border-radius: 4px;
  }

  .entry-file {
    padding: 0.1rem 0.5rem 0.3rem 0.4rem;
    display: flex;
    align-items: center;
    max-width: 10rem;
    gap: 0.2rem;
    background-color: transparent;
    border: none;
    cursor: default;
  }

  .entry-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
