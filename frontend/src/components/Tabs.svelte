<script lang="ts">
  import { Icon } from '@steeze-ui/svelte-icon'
  import CharacterList from './CharacterList.svelte'
  import type { TabItem } from '../types/tab'

  interface Props {
    tab_items: TabItem[]
    active_tab_value: number
  }

  let { tab_items, active_tab_value }: Props = $props()

  const handle_click = (tab_value: number, callback: (() => void) | undefined) => () => {
    active_tab_value = tab_value
    callback?.()
  }

  const handle_keydown = (tab_value: number) => (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      active_tab_value = tab_value
    }
  }

  function active_class(tab: number) {
    return active_tab_value === tab ? 'active' : ''
  }
</script>

<div class="tabs" role="tablist">
  {#each tab_items as item}
    <button
      role="tab"
      aria-selected={active_tab_value === item.value}
      aria-controls="panel-{item.value}"
      class={active_class(item.value)}
      onclick={handle_click(item.value, item.callback)}
      onkeydown={handle_keydown(item.value)}
    >
      <Icon src={item.icon} width="24" height="24" class={active_class(item.value)} />
      {item.label}
    </button>
  {/each}
</div>

{#each tab_items as item}
  {#if active_tab_value === item.value}
    <div id="panel-{item.value}" role="tabpanel" class="box" tabindex="0">
      <item.component />
    </div>
  {/if}
{/each}

<style>
  .box {
    margin-bottom: 10px;
    padding: 40px;
  }

  .tabs {
    display: flex;
    flex-wrap: wrap;
    padding-left: 0;
    margin-bottom: 0;
  }

  button {
    margin-bottom: -1px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.25rem 0.75rem;
    cursor: pointer;
    color: theme('colors.slate.400');
    background-color: transparent;
    font-size: 10pt;
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
  }

  button:hover {
    border-color: theme('colors.sky.100');
    border-bottom: 3px solid theme('colors.sky.100');
  }

  button.active {
    color: theme('colors.sky.500');
    border-bottom: 3px solid theme('colors.sky.300');
  }
</style>
