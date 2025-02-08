<script lang="ts">
  import Spinner from './Spinner.svelte'

  interface Props {
    thinking: boolean
    content: string
  }
  let { thinking, content }: Props = $props()
  let collapsed = $state(true)
  let tick = $state(0)
  const size = 14

  $effect(() => {
    content
    setTimeout(() => {
      tick = tick + 1
    }, 0)
  })

  function toggle_collapse() {
    collapsed = !collapsed
  }
</script>

<div class="think {collapsed ? 'collapsed' : ''} {thinking ? 'thinking' : ''}">
  <button class="think-toggle" onclick={toggle_collapse}>▼</button>
  <div class="spinner">
    {thinking ? 'thinking' : 'thought'}
    {#if thinking}
      <Spinner {tick} {size} />
    {/if}
  </div>
  <span class="think-content">{@html content}</span>
</div>

<style>
  .think {
    color: var(--color-gray-400);
  }

  .think-toggle {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0;
    font-size: 0.8em;
    transition: transform 0.2s;
    margin-top: 0.25rem;
  }

  .think .spinner {
    display: none;
  }

  .think.collapsed .spinner {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-style: italic;
    margin-left: 0.5rem;
  }

  .think.collapsed .think-content {
    display: none;
  }

  .think.collapsed .think-toggle {
    transform: rotate(-90deg);
  }
</style>
