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
  import { Button, Dropdown, DropdownLi, DropdownUl, Label, uiHelpers } from 'svelte-5-ui-lib'
  import { load_settings } from '../lib/settings.svelte'
  import { ChevronDown } from 'svelte-heros-v2'
  import { sineIn } from 'svelte/easing'

  interface Checkpoint {
    name: string
    portrait: StoryEntry
    landscape: StoryEntry
  }

  let checkpoints: Checkpoint[] = $state([])
  let prefix = $state('')
  let prompt = $state('')
  let stop = $state(false)
  let prefix_dropdown = uiHelpers()
  let prefix_dropdown_status = $state(false)
  let prefix_dropdown_close = prefix_dropdown.close
  $effect(() => {
    prefix_dropdown_status = prefix_dropdown.isOpen
  })
  let prefix_dropdown_options = $state([
    'score_9, score_8_up, score_7_up, score_6_up',
    'masterpiece, 8k, hd',
  ])

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

    let index = prefix_dropdown_options.indexOf(prefix)
    if (index === -1) {
      prefix_dropdown_options = [...prefix_dropdown_options, prefix]
      index = prefix_dropdown_options.length - 1
    }

    await save_json('compare/compare.json', {
      prefixes: prefix_dropdown_options,
      selected_prefix: index,
      prompt: prompt,
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
    if (data && data.prompt) {
      prompt = data.prompt
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

  function select_prefix(option: string) {
    return () => {
      prefix = option
      prefix_dropdown_close()
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
  <div class="flex gap-2 w-full p-2 relative items-start">
    <FlexibleTextarea id="prefix" class="flex-grow" bind:value={prefix} />
    <Button color="light" class="p-1 flex-none" onclick={prefix_dropdown.toggle}>
      <ChevronDown size="20" />
    </Button>
    <Dropdown
      dropdownStatus={prefix_dropdown_status}
      closeDropdown={prefix_dropdown_close}
      params={{ y: 0, duration: 200, easing: sineIn }}
      class="absolute right-1 top-9 w-96 text-left rounded border border-neutral-300"
    >
      <DropdownUl>
        {#each prefix_dropdown_options as option}
          <DropdownLi
            ><Button
              color="light"
              class="px-2 py-1 w-full border-0 rounded-none justify-start truncate focus:ring-0"
              onclick={select_prefix(option)}>{option}</Button
            ></DropdownLi
          >
        {/each}
      </DropdownUl>
    </Dropdown>
  </div>
  <Label for="prompt">Prompt</Label>
  <FlexibleTextarea id="prompt" bind:value={prompt} />
  <div class="flex flex-row gap-1">
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
