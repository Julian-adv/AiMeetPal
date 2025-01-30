<script lang="ts">
  import { Button, Dropdown, DropdownLi, DropdownUl, uiHelpers } from 'svelte-5-ui-lib'
  import { ChevronDown } from 'svelte-heros-v2'
  import { sineIn } from 'svelte/easing'

  interface Props {
    value: string
    options: string[]
  }

  let { value = $bindable(), options }: Props = $props()

  let dropdown = uiHelpers()
  let dropdown_status = $state(false)
  let dropdown_close = dropdown.close
  $effect(() => {
    dropdown_status = dropdown.isOpen
  })

  function select(option: string) {
    return () => {
      value = option
      dropdown_close()
    }
  }
</script>

<Button color="light" class="p-1 flex-none" onclick={dropdown.toggle}>
  <ChevronDown size="20" />
</Button>
<Dropdown
  dropdownStatus={dropdown_status}
  closeDropdown={dropdown_close}
  params={{ y: 0, duration: 200, easing: sineIn }}
  class="absolute right-1 top-7 w-96 text-left rounded border border-neutral-300"
>
  <DropdownUl>
    {#each options as option}
      <DropdownLi
        ><Button
          color="light"
          class="px-2 py-1 w-full border-0 rounded-none justify-start truncate focus:ring-0"
          onclick={select(option)}>{option}</Button
        ></DropdownLi
      >
    {/each}
  </DropdownUl>
</Dropdown>
