<script lang="ts">
  import { onMount } from 'svelte'

  interface Props {
    id?: string
    value?: string
    class?: string
    textarea?: HTMLTextAreaElement
    onkeydown?: (e: KeyboardEvent) => void
    oninit?: (textarea: HTMLTextAreaElement) => void
  }

  let {
    id,
    value = $bindable(),
    class: className = '',
    textarea = $bindable(),
    onkeydown = () => {},
  }: Props = $props()

  $effect(() => {
    value
    adjust_height()
  })

  function adjust_height() {
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight + 1, 500) + 'px'
    }
  }

  onMount(() => {
    setTimeout(() => adjust_height(), 0)
  })
</script>

<textarea
  {id}
  bind:this={textarea}
  bind:value
  rows={1}
  class={`p-2 rounded border border-neutral-300 outline-none w-full text-base h-auto bg-gray-50 ${className}`}
  {onkeydown}
  oninput={adjust_height}
></textarea>
