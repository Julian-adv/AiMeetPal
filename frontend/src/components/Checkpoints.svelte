<script lang="ts">
  import { onMount } from 'svelte'
  import {
    get_checkpoints,
    save_json,
    load_json,
    save_image_story_entry,
  } from '../lib/files.svelte'
  import ImageOrSpinner from './ImageOrSpinner.svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { StoryEntryState, type ImageEntry, type StoryEntry } from '../types/story'
  import { image_size, generate_image } from '../lib/generate_image.svelte'
  import { Button, Label } from 'svelte-5-ui-lib'
  import { load_settings } from '../lib/settings.svelte'
  import DropdownButton from './DropdownButton.svelte'

  interface Checkpoint {
    name: string
    portrait: StoryEntry
    landscape: StoryEntry
  }

  let checkpoints: Checkpoint[] = $state([])
  let prefix = $state('')
  let prompt = $state('')
  let stop = $state(false)
  let prefix_dropdown_options = $state([
    'score_9, score_8_up, score_7_up, score_6_up',
    'masterpiece, 8k, hd',
  ])
  let prompt_dropdown_options = $state(['1girl'])

  async function add_image(checkpoint_name: string, entry: StoryEntry, portrait: boolean) {
    const { width, height } = image_size(portrait ? 'format: portrait' : 'format: landscape')
    entry.state = StoryEntryState.WaitImage
    let image_entry: ImageEntry = {
      image: await generate_image(checkpoint_name, `${prefix},${prompt}`, width, height),
      width: width,
      height: height,
      prompt: '',
    }
    entry.images = [...entry.images, image_entry]
    entry.active_image = entry.images.length - 1
    entry.state = StoryEntryState.Image
    await save_compare()
  }

  async function save_compare() {
    for (let i = 0; i < checkpoints.length; i++) {
      await save_image_story_entry(
        'compare',
        checkpoints[i].name.substring(0, checkpoints[i].name.lastIndexOf('.')) + '_p',
        checkpoints[i].portrait
      )
      await save_image_story_entry(
        'compare',
        checkpoints[i].name.substring(0, checkpoints[i].name.lastIndexOf('.')) + '_l',
        checkpoints[i].landscape
      )
    }

    let prefix_index = prefix_dropdown_options.indexOf(prefix)
    if (prefix_index === -1) {
      prefix_dropdown_options = [...prefix_dropdown_options, prefix]
      prefix_index = prefix_dropdown_options.length - 1
    }

    let prompt_index = prompt_dropdown_options.indexOf(prompt)
    if (prompt_index === -1) {
      prompt_dropdown_options = [...prompt_dropdown_options, prompt]
      prompt_index = prompt_dropdown_options.length - 1
    }

    await save_json('compare/compare.json', {
      prefixes: prefix_dropdown_options,
      selected_prefix: prefix_index,
      prompts: prompt_dropdown_options,
      selected_prompt: prompt_index,
      checkpoints: checkpoints,
    })
  }

  async function start_generate_image() {
    if (prompt.trim() === '') return
    stop = false

    for (let i = 0; i < checkpoints.length; i++) {
      await add_image(checkpoints[i].name, checkpoints[i].portrait, true)
      if (stop) return
      await add_image(checkpoints[i].name, checkpoints[i].landscape, false)
      if (stop) return
    }
  }

  async function refresh_checkpoints() {
    const newCheckpoints = await get_checkpoints()

    // Add only new checkpoints that don't exist in current checkpoints array
    for (const checkpoint of newCheckpoints) {
      if (!checkpoints.some((c) => c.name === checkpoint)) {
        checkpoints = [
          ...checkpoints,
          {
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
          },
        ]
      }
    }
  }

  async function load_compare() {
    const data = await load_json('compare/compare.json')
    if (data) {
      if (data.prefixes && data.prefixes.length > 0) {
        prefix_dropdown_options = data.prefixes
        if (
          data.selected_prefix !== undefined &&
          data.selected_prefix >= 0 &&
          data.selected_prefix < data.prefixes.length
        ) {
          prefix = data.prefixes[data.selected_prefix]
        }
      }
      if (data.prompts && data.prompts.length > 0) {
        prompt_dropdown_options = data.prompts
        if (
          data.selected_prompt !== undefined &&
          data.selected_prompt >= 0 &&
          data.selected_prompt < data.prompts.length
        ) {
          prompt = data.prompts[data.selected_prompt]
        }
      }

      // Restore saved checkpoint data
      if (data.checkpoints) {
        for (const savedCheckpoint of data.checkpoints) {
          // Find matching checkpoint in current checkpoints array
          const checkpoint = checkpoints.find((c) => c.name === savedCheckpoint.name)
          if (checkpoint) {
            // Restore portrait and landscape data
            checkpoint.portrait = {
              ...checkpoint.portrait,
              ...savedCheckpoint.portrait,
            }
            checkpoint.landscape = {
              ...checkpoint.landscape,
              ...savedCheckpoint.landscape,
            }
          }
        }
      }
    }
  }

  onMount(async () => {
    await load_settings()
    await refresh_checkpoints()
    await load_compare()
  })
</script>

<h2>Checkpoints</h2>
<form class="flex flex-col gap-1 items-start">
  <Label for="prefix">Prefix</Label>
  <div class="flex gap-2 w-full px-2 relative items-start">
    <FlexibleTextarea id="prefix" class="flex-grow" bind:value={prefix} />
    <DropdownButton bind:value={prefix} options={prefix_dropdown_options} />
  </div>
  <Label for="prompt" class="mt-2">Prompt</Label>
  <div class="flex gap-2 w-full px-2 relative items-start">
    <FlexibleTextarea id="prompt" bind:value={prompt} />
    <DropdownButton bind:value={prompt} options={prompt_dropdown_options} />
  </div>
  <div class="flex flex-row gap-1 p-2">
    <Button color="primary" onclick={start_generate_image}>Generate all</Button>
    <Button color="light" onclick={() => (stop = true)}>Stop</Button>
    <Button color="light" onclick={refresh_checkpoints}>Refresh</Button>
    <Button color="light" onclick={save_compare}>Save</Button>
  </div>
  <div class="mt-5 grid grid-cols-[1fr_2fr] gap-1 justify-items-center">
    {#each checkpoints as checkpoint, i (checkpoint.name)}
      <div class="justify-self-stretch col-span-2 flex items-center">
        {checkpoint.name}
        <div class="ml-2 flex-grow h-px bg-zinc-200"></div>
      </div>
      <div>
        <ImageOrSpinner
          bind:entry={checkpoint.portrait}
          scale={0.7}
          regenerate_image={() => add_image(checkpoint.name, checkpoint.portrait, true)}
        />
      </div>
      <div>
        <ImageOrSpinner
          bind:entry={checkpoint.landscape}
          scale={0.7}
          landscape={true}
          regenerate_image={() => add_image(checkpoint.name, checkpoint.landscape, false)}
        />
      </div>
    {/each}
  </div>
</form>
