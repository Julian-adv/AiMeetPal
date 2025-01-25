<script lang="ts">
  import { get_id } from '../lib/util'
  import { StoryEntryState } from '../types/story'
  import { Popover, Button, Modal, uiHelpers } from 'svelte-5-ui-lib'

  interface Prop {
    width: number
    height: number
    image_state: StoryEntryState
    image: string | null
    image_prompt?: string
    scale?: number
  }
  let { width, height, image_state, image, image_prompt, scale = 0.45 }: Prop = $props()
  let popover_id = `scene-image${get_id()}`
  const imageModal = uiHelpers()
  let modalStatus = $state(false)
  const closeModal = imageModal.close
  $effect(() => {
    modalStatus = imageModal.isOpen
  })
</script>

<div
  id={popover_id}
  class={width > height ? 'scene-image-wide' : 'scene-image'}
  style="--image-width: {width}px; --image-height: {height}px; --image-scale: {scale}"
>
  <button type="button" class="image-placeholder" onclick={imageModal.toggle}>
    {#if image_state === StoryEntryState.WaitPrompt || image_state === StoryEntryState.WaitContent}
      <div class="spinner_square"></div>
    {:else if image_state === StoryEntryState.WaitImage}
      <div class="spinner_circle"></div>
    {/if}
  </button>
  {#if image}
    <img src={image} alt="Scene visualization" />
  {/if}
</div>
{#if image_prompt}
  <Popover class="text-sm p-2 w-[50%] z-20" triggeredBy="#{popover_id}" position="bottom"
    >{image_prompt}</Popover
  >
{/if}
<Modal size="lg" {modalStatus} {closeModal}>
  <div class="flex flex-col items-center justify-center">
    <img src={image} alt="Scene visualization" />
  </div>
</Modal>

<style>
  .scene-image {
    position: relative;
    float: left;
    width: calc(var(--image-width) * var(--image-scale));
    height: calc(var(--image-height) * var(--image-scale));
    margin: 0 1rem 0.5rem 0;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
  }

  .scene-image-wide {
    position: relative;
    width: calc(var(--image-width) * var(--image-scale));
    height: calc(var(--image-height) * var(--image-scale));
    float: none;
    margin: 0 auto 0.5rem auto;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
  }

  .scene-image img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .scene-image-wide img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .image-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    padding: 1rem;
    justify-content: end;
    align-items: end;
    z-index: 1;
    background: transparent;
  }

  .spinner_square {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border-radius: 0;
    border: 4px solid #bfc9eb;
  }

  .spinner_circle {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #bfc9eb;
    border-radius: 50%;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
