<script lang="ts">
  import { settings, load_settings, save_settings } from '../lib/settings.svelte'
  import { onMount } from 'svelte'
  import { Modal, Button, Input, uiHelpers, Breadcrumb, BreadcrumbItem } from 'svelte-5-ui-lib'
  import type { Entry, DirEntries } from '../types/file'
  import { get_dir_entries, get_checkpoints } from '../lib/files.svelte'

  let language_models: string[] = $state([])
  let checkpoints: string[] = $state([])
  const modalExample = uiHelpers()
  let modalStatus = $state(false)
  const closeModal = modalExample.close
  $effect(() => {
    modalStatus = modalExample.isOpen
  })

  let dir_entries: DirEntries = $state({
    entries: [],
    current_directory: '.',
  })

  let path_entries = $state<string[]>([])

  $effect(() => {
    get_language_models(settings.api_type).then((models) => {
      language_models = models
    })
  })

  async function get_language_models(api_type: 'infermaticai' | 'openai') {
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

  const select_path = async () => {
    settings.checkpoints_folder = dir_entries.current_directory
    modalExample.close()
    checkpoints = await get_checkpoints()
  }

  onMount(async () => {
    await load_settings()
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
      checkpoints = await get_checkpoints()
    } catch (error) {
      console.error('Error fetching checkpoints:', error)
    }
    try {
      language_models = await get_language_models(settings.api_type)
    } catch (error) {
      console.error('Error fetching language models:', error)
    }
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
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.infermaticai.preset} />
      <div class="label">Instruct</div>
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.infermaticai.instruct} />
      <div class="label">Context</div>
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.infermaticai.context} />
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
      <Input class="focus:ring-2 ring-sky-500" bind:value={settings.openai.preset} />
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

<style>
  @reference "tailwindcss/theme";

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
