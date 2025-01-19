<script lang="ts">
  import { onMount } from 'svelte'

  let { value = $bindable(), class: className = '' }: { value: string; class?: string } = $props()
  let textarea: HTMLTextAreaElement

  function adjust_height() {
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = textarea.scrollHeight + 1 + 'px'
    }
  }

  onMount(() => {
    setTimeout(() => adjust_height(), 0)
  })
</script>

<textarea
  bind:this={textarea}
  bind:value
  class={`p-2 rounded border border-neutral-300 outline-none w-full text-base h-auto focus:border-primary-500 bg-gray-50 ${className}`}
></textarea>
