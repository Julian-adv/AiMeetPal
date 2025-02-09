<script lang="ts">
  import { get_dir_entries } from '../lib/files.svelte'
  import type { DirEntries, Entry } from '@/types/file'
  import { onMount } from 'svelte'
  import { Breadcrumb, BreadcrumbItem, Button, Input, Modal, uiHelpers } from 'svelte-5-ui-lib'

  interface Props {
    title: string
    ok_text: string
    init_dir: string
    select_file?: boolean
    min_width?: number
    on_init: (modal: any) => void
    on_ok: (current_dir: string) => void
  }

  let {
    title,
    ok_text,
    init_dir,
    select_file = false,
    min_width = 10,
    on_init,
    on_ok,
  }: Props = $props()

  let file_dialog = uiHelpers()
  let modalStatus = $state(false)
  let closeModal = file_dialog.close
  $effect(() => {
    modalStatus = file_dialog.isOpen
  })

  let dir_entries: DirEntries = $state({
    entries: [],
    current_directory: '.',
  })
  let path_entries: string[] = $state([])
  let selected_file = $state('')

  function dir_to_path_entries(path: string) {
    const entries = path.split(/[\/\\]/)
    return ['This PC', ...entries]
  }

  function handle_breadcrumb_click(index: number) {
    return async () => {
      dir_entries.current_directory = dir_entries.current_directory
        .split(/[\/\\]/)
        .slice(0, index)
        .join('/')
      path_entries = dir_to_path_entries(dir_entries.current_directory)
      dir_entries = await get_dir_entries(dir_entries.current_directory + '/')
    }
  }

  function handle_entry_click(entry: Entry) {
    return async () => {
      if (entry.is_dir) {
        let new_path =
          dir_entries.current_directory === '.' || dir_entries.current_directory === '/'
            ? entry.name
            : `${dir_entries.current_directory}/${entry.name}`
        new_path = new_path.replace(/\\/g, '/')
        new_path = new_path.replace(/\/\//g, '/')
        dir_entries = await get_dir_entries(new_path + '/')
        path_entries = dir_to_path_entries(new_path)
        selected_file = ''
      } else if (select_file) {
        selected_file = entry.name
      }
    }
  }

  function on_click_ok() {
    if (!select_file) {
      file_dialog.close()
      on_ok(dir_entries.current_directory)
    } else if (selected_file) {
      file_dialog.close()
      on_ok(dir_entries.current_directory + '/' + selected_file)
    }
  }

  onMount(async () => {
    on_init(file_dialog)
    dir_entries.current_directory = init_dir
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
    path_entries = dir_to_path_entries(dir_entries.current_directory)
  })
</script>

<Modal size="lg" {title} {modalStatus} {closeModal}>
  <div class="overflow-hidden">
    <Breadcrumb>
      {#each path_entries as entry, i}
        <BreadcrumbItem href="#" home={i === 0} onclick={handle_breadcrumb_click(i)}
          >{entry}</BreadcrumbItem
        >
      {/each}
    </Breadcrumb>
  </div>
  <div class="entries" style="--min-width: {min_width}rem;">
    {#each dir_entries.entries as entry}
      <button
        type="button"
        class={(entry.is_dir || select_file ? 'entry' : 'entry-file') +
          (selected_file === entry.name ? ' selected' : '')}
        onclick={handle_entry_click(entry)}
        style="--min-width: {min_width}rem;"
      >
        <div>{entry.is_dir ? '📁' : '📄'}</div>
        <div class="entry-name" style="--min-width: {min_width}rem;">{entry.name}</div>
      </button>
    {/each}
  </div>
  {#snippet footer()}
    <div class="w-full text-left border rounded-sm border-zinc-300 bg-zinc-100 p-2 h-10">
      {selected_file}
    </div>
    <Button type="submit" color="sky" class="me-2" onclick={on_click_ok}>{ok_text}</Button>
    <Button onclick={closeModal} color="alternative">Cancel</Button>
  {/snippet}
</Modal>

<style>
  @reference "tailwindcss/theme";

  .entries {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--min-width, 10rem), 1fr));
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
    max-width: var(--min-width, 10rem);
    gap: 0.2rem;
    background-color: transparent;
  }

  .entry:hover {
    background-color: var(--color-zinc-100);
    cursor: pointer;
    border-radius: 8px;
  }

  .entry-file {
    padding: 0.1rem 0.5rem 0.3rem 0.4rem;
    display: flex;
    align-items: center;
    max-width: var(--min-width, 10rem);
    gap: 0.2rem;
    background-color: transparent;
    border: none;
    cursor: default;
  }

  .selected {
    background-color: var(--color-sky-200);
  }

  .selected:hover {
    @apply bg-sky-400/50;
  }

  .entry-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* hack because svelte-5-ui-lib still uses tailwind 3 */
  :global(.bg-opacity-75) {
    @apply bg-stone-700/50;
  }
</style>
