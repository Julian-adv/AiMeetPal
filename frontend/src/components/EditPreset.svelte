<script lang="ts">
  import { Input, Button, uiHelpers, Select, Checkbox } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import { load_settings, settings } from '../lib/settings.svelte'
  import { load_risupreset } from '../lib/risu'
  import FileDialog from './FileDialog.svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { save_json } from '../lib/files.svelte'

  interface PromptEntry {
    name?: string
    role: 'system' | 'user' | 'bot'
    text: string
    innerFormat?: string
    type:
      | 'plain'
      | 'persona'
      | 'description'
      | 'lorebook'
      | 'memory'
      | 'chat'
      | 'authornote'
      | 'postEverything'
    type2: 'normal' | 'main' | 'globalNote'
    rangeStart?: number
    rangeEnd?: number | 'end'
    chatAsOriginalOnSystem?: boolean
  }

  let preset = $state({
    name: '',
    aiModel: '',
    subModel: '',
    temperature: 0,
    maxContext: 0,
    maxResponse: 0,
    customPromptTemplateToggle: '',
    promptTemplate: [] as PromptEntry[],
  })

  let preset_dialog = uiHelpers()

  const types = [
    { value: 'plain', name: 'Plain' },
    { value: 'persona', name: 'Persona' },
    { value: 'description', name: 'Description' },
    { value: 'lorebook', name: 'Lorebook' },
    { value: 'memory', name: 'Memory' },
    { value: 'chat', name: 'Chat' },
    { value: 'authornote', name: 'Author Note' },
    { value: 'postEverything', name: 'Post Everything' },
  ]

  const types2 = [
    { value: 'normal', name: 'Normal' },
    { value: 'main', name: 'Main' },
    { value: 'globalNote', name: 'Global Note' },
  ]

  const roles = [
    { value: 'system', name: 'System' },
    { value: 'user', name: 'User' },
    { value: 'bot', name: 'Bot' },
  ]

  let converted_preset: any = $state({})

  async function import_preset(file_path: string) {
    converted_preset = await load_risupreset(file_path)
    if (converted_preset) {
      console.log(converted_preset)
      preset.name = converted_preset.name
      preset.aiModel = converted_preset.aiModel
      preset.subModel = converted_preset.subModel
      preset.temperature = converted_preset.temperature / 100
      preset.maxContext = converted_preset.maxContext
      preset.maxResponse = converted_preset.maxResponse
      preset.customPromptTemplateToggle = converted_preset.customPromptTemplateToggle
      preset.promptTemplate = converted_preset.promptTemplate
    }
  }

  async function show_import_preset() {
    preset_dialog.toggle()
  }

  async function save_preset() {
    save_json(`${converted_preset.name}.json`, converted_preset)
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
<Button color="light" class="p-2" onclick={save_preset}>Save</Button>
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

  {#if preset.promptTemplate.length > 0}
    <div class="text-left text-lg font-bold col-span-2">Prompt template</div>
  {/if}
  {#each preset.promptTemplate as entry}
    <div class="text-right">Type</div>
    <div class="text-left">
      <Select items={types} bind:value={entry.type} size="sm" class="p-1 w-auto" />
    </div>
    {#if entry.type === 'chat'}
      {#if entry.name}
        <div class="text-right">Name</div>
        <div class="text-left"><Input bind:value={entry.name} /></div>
      {/if}
      <div class="text-right">Range start</div>
      <div class="text-left"><Input bind:value={entry.rangeStart} /></div>
      <div class="text-right">Range end</div>
      <div class="text-left"><Input bind:value={entry.rangeEnd} /></div>
      {#if entry.chatAsOriginalOnSystem}
        <div class="text-right"></div>
        <div class="text-left">
          <Checkbox bind:checked={entry.chatAsOriginalOnSystem}>Chat as original on system</Checkbox
          >
        </div>
      {/if}
    {:else if entry.type !== 'lorebook' && entry.type !== 'memory' && entry.type !== 'authornote' && entry.type !== 'postEverything'}
      {#if entry.name}
        <div class="text-right">Name</div>
        <div class="text-left"><Input bind:value={entry.name} /></div>
      {/if}
      <div class="text-right">Type 2</div>
      <div class="text-left">
        <Select items={types2} bind:value={entry.type2} size="sm" class="p-1 w-auto" />
      </div>
      {#if entry.innerFormat}
        <div class="text-right">Inner format</div>
        <div class="text-left">
          <FlexibleTextarea bind:value={entry.innerFormat} />
        </div>
      {:else}
        <div class="text-right">Text</div>
        <div class="text-left">
          <FlexibleTextarea bind:value={entry.text} />
        </div>
      {/if}
      <div class="text-right">Role</div>
      <div class="text-left">
        <Select items={roles} bind:value={entry.role} size="sm" class="p-1 w-auto" />
      </div>
    {/if}
    <hr class="border-zinc-300 border-dashed col-span-2" />
  {/each}
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
