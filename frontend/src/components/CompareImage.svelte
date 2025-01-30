<script lang="ts">
  import { onMount } from 'svelte'
  import { get_checkpoints } from '../lib/files.svelte'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { StoryEntryState, type StoryEntry } from '../types/story'
  import { image_size, generate_image } from '../lib/generate_image.svelte'
  import { Button } from 'svelte-5-ui-lib'
  import { load_settings } from '../lib/settings.svelte'

  interface Checkpoint {
    name: string
    portrait: StoryEntry
    landscape: StoryEntry
  }

  let checkpoints: Checkpoint[] = $state([])
  let prompt = $state('')
  let stop = $state(false)

  async function add_image(checkpoint_name: string, entry: StoryEntry, portrait: boolean) {
    const { width, height } = image_size(portrait ? 'format: portrait' : 'format: landscape')
    entry.state = StoryEntryState.WaitImage
    let image_entry = {
      image: await generate_image(checkpoint_name, prompt, width, height),
      width: width,
      height: height,
      prompt: '',
      path: '',
    }
    entry.images = [...entry.images, image_entry]
    entry.active_image = entry.images.length - 1
    entry.state = StoryEntryState.Image
  }

  async function start_generate_image() {
    if (prompt.trim() === '') return
    stop = false

    for (let i = 0; i < checkpoints.length; i++) {
      add_image(checkpoints[i].name, checkpoints[i].portrait, true)
      if (stop) return
      add_image(checkpoints[i].name, checkpoints[i].landscape, false)
      if (stop) return
    }
  }

  async function refresh_checkpoints() {
    checkpoints = (await get_checkpoints()).map((checkpoint: string) => {
      const { width, height } = image_size('format: portrait')
      return {
        name: checkpoint,
        portrait: {
          state: StoryEntryState.NoSpinner,
          images: [],
          id: 0,
          speaker: '',
          content: '',
          active_image: undefined,
        },
        landscape: {
          state: StoryEntryState.NoSpinner,
          images: [],
          id: 0,
          speaker: '',
          content: '',
          active_image: undefined,
        },
      }
    })
  }

  onMount(async () => {
    await load_settings()
    await refresh_checkpoints()
  })
</script>

<h2>Compare</h2>
<FlexibleTextarea bind:value={prompt} />
<Button color="light" onclick={start_generate_image}>Generate all</Button>
<Button color="light" onclick={() => (stop = true)}>Stop</Button>
<Button color="light" onclick={refresh_checkpoints}>Refresh</Button>
<div class="mt-5 grid grid-cols-[1fr_2fr] gap-1 justify-items-center">
  {#each checkpoints as checkpoint, i (checkpoint.name)}
    <div class="justify-self-stretch col-span-2 flex items-center">
      {checkpoint.name}
      <div class="ml-2 flex-grow h-px bg-zinc-200"></div>
    </div>
    <div>
      <ImageOrSpinner
        entry={checkpoint.portrait}
        scale={0.7}
        regenerate_image={() => add_image(checkpoint.name, checkpoint.portrait, true)}
      />
    </div>
    <div>
      <ImageOrSpinner
        entry={checkpoint.landscape}
        scale={0.7}
        landscape={true}
        regenerate_image={() => add_image(checkpoint.name, checkpoint.landscape, false)}
      />
    </div>
  {/each}
</div>
