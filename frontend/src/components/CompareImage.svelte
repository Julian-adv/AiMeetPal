<script lang="ts">
  import { onMount } from 'svelte'
  import { get_checkpoints } from '../lib/files.svelte'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { StoryEntryState } from '../types/story'
  import { image_size, generate_image } from '../lib/generate_image.svelte'
  import { Button } from 'svelte-5-ui-lib'

  interface CheckpointImage {
    state: StoryEntryState
    image: string | null
    width: number
    height: number
  }

  interface Checkpoint {
    name: string
    portrait: CheckpointImage
    landscape: CheckpointImage
  }

  let checkpoints: Checkpoint[] = $state([])
  let prompt = $state('')
  let stop = $state(false)

  async function start_generate_image() {
    if (prompt.trim() === '') return
    stop = false

    for (let i = 0; i < checkpoints.length; i++) {
      checkpoints[i].portrait.state = StoryEntryState.WaitImage
      checkpoints[i].portrait.image = await generate_image(
        checkpoints[i].name,
        prompt + ', format: portrait',
        checkpoints[i].portrait.width,
        checkpoints[i].portrait.height
      )
      checkpoints[i].portrait.state = StoryEntryState.Image
      if (stop) return
      checkpoints[i].landscape.state = StoryEntryState.WaitImage
      checkpoints[i].landscape.image = await generate_image(
        checkpoints[i].name,
        prompt,
        checkpoints[i].landscape.width,
        checkpoints[i].landscape.height
      )
      checkpoints[i].landscape.state = StoryEntryState.Image
    }
  }

  async function refresh_checkpoints() {
    checkpoints = (await get_checkpoints()).map((checkpoint: string) => {
      const { width, height } = image_size('format: portrait')
      return {
        name: checkpoint,
        portrait: {
          state: StoryEntryState.WaitPrompt,
          image: null,
          width: width,
          height: height,
        },
        landscape: {
          state: StoryEntryState.WaitPrompt,
          image: null,
          width: height,
          height: width,
        },
      }
    })
  }

  onMount(async () => {
    await refresh_checkpoints()
  })
</script>

<h2>Compare</h2>
<FlexibleTextarea bind:value={prompt} />
<Button color="light" onclick={start_generate_image}>Generate</Button>
<Button color="light" onclick={() => (stop = true)}>Stop</Button>
<Button color="light" onclick={refresh_checkpoints}>Refresh</Button>
<div class="mt-5 grid grid-cols-[1fr_2fr] gap-4">
  {#each checkpoints as checkpoint, i (checkpoint.name)}
    <div>
      {checkpoint.name}
    </div>
    <div></div>
    <div>
      <ImageOrSpinner
        image={checkpoint.portrait.image}
        state={checkpoint.portrait.state}
        width={checkpoint.portrait.width}
        height={checkpoint.portrait.height}
        scale={0.4}
      />
    </div>
    <div>
      <ImageOrSpinner
        image={checkpoint.landscape.image}
        state={checkpoint.landscape.state}
        width={checkpoint.landscape.width}
        height={checkpoint.landscape.height}
        scale={0.4}
      />
    </div>
  {/each}
</div>
