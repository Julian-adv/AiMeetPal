<script lang="ts">
  import { settings } from '../lib/settings.svelte'
</script>

<h2>Settings</h2>
<div class="settings-container">
  <div class="settings">
    <div>Model:</div>
    <div>
      <input bind:value={settings.model} />
    </div>
  </div>
</div>

<style>
  h2 {
    margin: 0 0 1rem 0;
    font-size: 1.2rem;
    font-weight: bold;
    color: theme('colors.gray.700');
    text-align: left;
  }

  .settings-container {
    display: block;
    text-align: left;
    width: 100%;
  }

  .settings {
    display: grid;
    max-width: 902px;
    width: 100%;
    gap: 0.5rem;
    grid-template-columns: auto 1fr;
    align-items: center;
  }

  .settings input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid theme('colors.gray.300');
    border-radius: 4px;
  }
</style>
