<script lang="ts">
  import { Input, Button } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import { load_settings, settings } from '../lib/settings.svelte'

  let preset = $state({
    name: '',
    temperature: 0,
    maxContext: 0,
    maxResponse: 0,
  })

  onMount(() => {
    load_settings()
  })
</script>

<h2>Edit Preset</h2>
<Button color="primary" class="p-2">Import</Button>
<div class="grid grid-cols-[9rem_1fr] gap-2 items-center mt-2">
  <div class="text-right">Preset name</div>
  <div>
    <Input type="text" bind:value={preset.name} />
  </div>

  <div class="text-right">Temperature</div>
  <div>
    <Input type="number" bind:value={preset.temperature} />
  </div>

  <div class="text-right">Max context</div>
  <div>
    <Input type="number" bind:value={preset.maxContext} />
  </div>

  <div class="text-right">Max response</div>
  <div>
    <Input type="number" bind:value={preset.maxResponse} />
  </div>
</div>
