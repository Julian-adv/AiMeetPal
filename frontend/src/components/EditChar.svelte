<script lang="ts">
  import { state } from '../lib/state.svelte'
  import { Input, Button } from 'svelte-5-ui-lib'
  import { onMount } from 'svelte'
  import FlexibleTextarea from './FlexibleTextarea.svelte'
  import { highlightQuotes } from '../lib/util'

  let info = {
    name: '',
    description: '',
    personality: '',
    scenario: '',
    first_mes: '',
    mes_example: '',
  }
  let file_name = ''

  const save_char = async () => {
    if (!state.selected_char) return

    try {
      if (!file_name.endsWith('.card')) {
        file_name = file_name + '.card'
      }
      const response = await fetch('http://localhost:5000/api/save-char', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_name: file_name,
          image: state.selected_char.image.split(',')[1], // Remove data:image/png;base64, prefix
          name: info.name,
          description: info.description,
          first_mes: info.first_mes,
          scenario: info.scenario,
          personality: info.personality,
          mes_example: info.mes_example,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save character')
      }

      // Update local state
      state.selected_char.info = info
    } catch (error) {
      console.error('Error saving character:', error)
      alert('Failed to save character')
    }
  }

  onMount(() => {
    if (state.selected_char) {
      info = state.selected_char.info
      file_name = state.selected_char.id
    }
  })
</script>

<h2>Edit Character</h2>
<div class="edit-char-container">
  <div class="label">Image</div>
  <div>
    <img src={state.selected_char?.image} alt={info.name} />
  </div>
  <div class="label">Name</div>
  <div><Input bind:value={info.name} /></div>
  <div class="label">Description</div>
  <div><FlexibleTextarea bind:value={info.description} /></div>
  <div class="label">Personality</div>
  <div>
    <FlexibleTextarea bind:value={info.personality} />
    <h3>Preview</h3>
    <div class="preview">
      {@html info.personality}
    </div>
  </div>
  <div class="label">Scenario</div>
  <div><FlexibleTextarea bind:value={info.scenario} /></div>
  <div class="label">Message example</div>
  <div><FlexibleTextarea bind:value={info.mes_example} /></div>
  <div class="label">First message</div>
  <div>
    <FlexibleTextarea bind:value={info.first_mes} />
    <h3>Preview</h3>
    <div class="preview">
      {@html highlightQuotes(info.first_mes)}
    </div>
  </div>
  <div class="label">File name</div>
  <div><Input bind:value={file_name} /></div>
</div>
<Button color="primary" class="m-3 mx-auto" onclick={save_char}>Save</Button>

<style lang="postcss">
  .edit-char-container {
    display: grid;
    grid-template-columns: 200px 1fr;
    padding: 0rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 1rem;
    gap: 1rem;
    text-align: left;
    font-family: 'Segoe UI', Inter, Georgia, 'Times New Roman', Times, serif;
    font-size: 1.1rem;
    color: theme('colors.neutral.600');
  }

  .label {
    justify-self: end;
    color: theme('colors.neutral.500');
    margin-top: 0.45rem;
  }

  .edit-char-container img {
    width: 300px;
    height: auto;
    border-radius: 8px;
  }

  .edit-char-container h3 {
    font-weight: bold;
  }

  .edit-char-container :global p {
    margin-block-end: 0.7rem;
  }

  .edit-char-container :global .quoted-text {
    color: theme('colors.blue.800');
  }

  .preview {
    padding: 0.5rem;
    border: 1px solid theme('colors.zinc.300');
    border-radius: 8px;
    height: 500px;
    overflow: auto;
  }
</style>
