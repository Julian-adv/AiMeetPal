<script lang="ts">
  import { Input, Button, uiHelpers } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import { load_settings, settings } from '../lib/settings.svelte'
  import { load_risupreset } from '../lib/risu'
  import FileDialog from './FileDialog.svelte'

  let preset = $state({
    name: '',
    temperature: 0,
    maxContext: 0,
    maxResponse: 0,
  })
  let preset_dialog = uiHelpers()

  async function import_preset(file_path: string) {
    const preset = await load_risupreset(file_path)
    if (preset) {
      preset.temperature = preset.temperature / 100
    }
  }

  async function show_import_preset() {
    preset_dialog.toggle()
  }

  function init_preset_dialog(dialog: any) {
    preset_dialog = dialog
  }

  onMount(() => {
    load_settings()
  })
</script>

<h2>Edit Preset</h2>
<Button color="primary" class="p-2" onclick={show_import_preset}>Import</Button>
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

<FileDialog
  title="Import Preset"
  ok_text="Import"
  init_dir="../data"
  select_file={true}
  min_width={25}
  on_init={init_preset_dialog}
  on_ok={import_preset}
/>
