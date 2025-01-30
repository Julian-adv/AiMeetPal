<script lang="ts">
  import { Modal, uiHelpers } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import { get_session_entries, get_session_json } from '../lib/files.svelte'
  import { g_state } from '../lib/state.svelte'
  import StoryScene from './StoryScene.svelte'
  import type { StoryEntry } from '../types/story'
  import { Button } from 'svelte-5-ui-lib'
  import type { Session } from '../types/session'

  let { on_init, on_load } = $props()
  const load_session_modal = uiHelpers()
  let modalStatus = $state(false)
  const closeModal = load_session_modal.close
  let sessions = $state<string[]>([])
  let entries: StoryEntry[] = $state([])
  let selected = $state<string | null>(null)
  let more_entries = $state(false)
  let session: Session | null = $state(null)

  async function get_sessions() {
    if (!g_state.selected_char) return
    sessions = await get_session_entries(g_state.selected_char.file_name.replace('.card', ''))
  }

  $effect(() => {
    modalStatus = load_session_modal.isOpen
    if (modalStatus) {
      get_sessions()
    }
  })

  const handle_session_click = (session_name: string) => async () => {
    if (!g_state.selected_char) return
    const char_name = g_state.selected_char.file_name.replace('.card', '')
    session = await get_session_json(char_name, session_name)
    if (!session) return
    entries = session.story_entries.slice(-3)
    selected = session_name
    more_entries = session.story_entries.length > 3
  }

  const regenerate_content = () => {}
  const image_generated = async (entry: StoryEntry) => {}

  const load_session = async () => {
    load_session_modal.toggle()
    on_load(session)
  }

  onMount(() => {
    on_init(load_session_modal)
  })
</script>

<Modal size="lg" title="Load session" {modalStatus} {closeModal}>
  <div class="flex flex-row gap-3">
    <div class="flex flex-col shrink-0 gap-2">
      {#each sessions as session}
        <Button
          color="light"
          class="p-2 focus:ring-sky-300 {selected === session ? 'bg-sky-300 border-sky-300' : ''}"
          onclick={handle_session_click(session)}
        >
          {session}
        </Button>
      {/each}
    </div>
    <div class="grow h-[50vh] overflow-y-auto overflow-x-hidden">
      {#if more_entries}
        <h2><span class="text-3xl tracking-widest">...</span></h2>
      {/if}
      <div class="w-full scale-[0.8] origin-top-left transform-gpu" style="width: 125%;">
        {#each entries as entry}
          <StoryScene {entry} {regenerate_content} index={0} {image_generated} disabled={true} />
        {/each}
      </div>
    </div>
  </div>
  <Button onclick={load_session}>Load</Button>
</Modal>
