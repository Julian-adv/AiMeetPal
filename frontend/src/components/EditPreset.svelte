<script lang="ts">
  import { Input, Button, uiHelpers } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import { load_settings, settings } from '../lib/settings.svelte'
  import { load_risupreset } from '../lib/risu'
  import FileDialog from './FileDialog.svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'

  let preset = $state({
    name: '',
    aiModel: '',
    subModel: '',
    temperature: 0,
    maxContext: 0,
    maxResponse: 0,
    customPromptTemplateToggle: '',
  })
  let preset_dialog = uiHelpers()

  async function import_preset(file_path: string) {
    const raw_preset = await load_risupreset(file_path)
    if (raw_preset) {
      console.log(raw_preset)
      preset.name = raw_preset.name
      preset.aiModel = raw_preset.aiModel
      preset.subModel = raw_preset.subModel
      preset.temperature = raw_preset.temperature / 100
      preset.maxContext = raw_preset.maxContext
      preset.maxResponse = raw_preset.maxResponse
      preset.customPromptTemplateToggle = raw_preset.customPromptTemplateToggle
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
  <div class="text-right">Name</div>
  <div>
    <Input type="text" bind:value={preset.name} />
  </div>

  <div class="text-right">AI model</div>
  <div>
    <Input type="text" bind:value={preset.aiModel} />
  </div>

  <div class="text-right">Sub model</div>
  <div>
    <Input type="text" bind:value={preset.subModel} />
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

  <div class="text-right">Custom prompt template toggle</div>
  <div>
    <FlexibleTextarea bind:value={preset.customPromptTemplateToggle} />
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
