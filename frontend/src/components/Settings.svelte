<script lang="ts">
  import { settings } from '../lib/settings.svelte'
  import { onMount } from 'svelte'
  import { Modal, Button, Input, uiHelpers, Breadcrumb, BreadcrumbItem } from 'svelte-5-ui-lib'

  let models: string[] = []
  let checkpoints_folder: HTMLInputElement
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

  async function checkpoint_list() {
    try {
      const response = await fetch('http://localhost:5000/api/checkpoints')
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error fetching model list:', error)
      return []
    }
  }

  async function get_dir_entries(path: string) {
    try {
      const response = await fetch('http://localhost:5000/api/files', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: path }),
      })
      const data = await response.json()
      return data
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

  const select_path = () => {
    settings.checkpoints_folder = dir_entries.current_directory
    modalExample.close()
  }

  onMount(async () => {
    dir_entries = await get_dir_entries(dir_entries.current_directory)
  })
</script>

<h2>Settings</h2>
<div class="settings-container">
  <div class="settings">
    <div class="label">Image model folder</div>
    <div class="folder-select">
      <div>{settings.checkpoints_folder}</div>
      <Button color="light" size="sm" onclick={handle_checkpoints_folder}>Browse...</Button>
    </div>
    <div class="label">Image model</div>
    <div>
      <select bind:value={settings.model}>
        {#each models as model}
          <option value={model}>{model}</option>
        {/each}
      </select>
    </div>
  </div>
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
    display: block;
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
