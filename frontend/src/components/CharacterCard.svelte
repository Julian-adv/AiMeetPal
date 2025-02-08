<script lang="ts">
  import { ChatBubbleLeftRight, PencilSquare, Trash } from 'svelte-heros-v2'
  import { Button } from 'svelte-5-ui-lib'
  import type { Character } from '../types/character'

  interface Prop {
    selected: boolean
    onclick: () => void
    character: Character
    chat: () => void
    edit_char: () => void
    delete_char: () => void
  }
  let { selected, onclick, character, chat, edit_char, delete_char }: Prop = $props()
  let hover = $state(false)

  function removeHtmlTags(str: string): string {
    return str.replace(/<[^>]*>/g, '')
  }
</script>

<div
  role="button"
  tabindex="0"
  aria-pressed={selected}
  class="pointer p-0 rounded-md border shadow-mdduration-200 ease-in-out focus:ring {selected
    ? 'ring shadow-lg ring-sky-300 border-sky-300 bg-sky-100'
    : 'border-zinc-300 bg-zinc-50'}"
  {onclick}
  onkeydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onclick()
    }
  }}
  onmouseover={() => (hover = true)}
  onmouseleave={() => (hover = false)}
  onfocus={() => (hover = true)}
>
  <img
    src={character.image}
    alt={character.info.name}
    class="w-full h-64 object-cover object-top rounded-t-md"
  />
  <div class="relative p-2 h-32 overflow-hidden {selected ? 'bg-sky-100' : ''}">
    <h3 class="font-bold">{character.info.name}</h3>
    <p class="text-xs text-left">{removeHtmlTags(character.info.personality)}</p>
    {#if selected}
      <div
        class="{hover
          ? 'visible'
          : 'invisible'} absolute left-0 bottom-2 right-0 flex justify-center gap-2"
      >
        <Button class="text-zinc-500 p-2" color="light" size="sm" onclick={chat}
          ><ChatBubbleLeftRight size="24" /></Button
        >
        <Button class="text-zinc-500 p-2" color="light" size="sm" onclick={edit_char}
          ><PencilSquare size="24" /></Button
        >
        <Button class="text-zinc-500 p-2" color="light" size="sm" onclick={delete_char}
          ><Trash size="24" /></Button
        >
      </div>
    {/if}
  </div>
  <div
    class="flex flex-col items-center justify-center h-12 rounded-b-md p-1 mt-1 {selected
      ? 'bg-sky-500 text-zinc-50'
      : 'bg-zinc-200'}"
  >
    <div class="text-sm overflow-hidden bg-transparent">{character.file_name}</div>
  </div>
</div>
