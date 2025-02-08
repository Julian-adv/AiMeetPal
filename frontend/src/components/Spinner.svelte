<script lang="ts">
  interface Props {
    tick?: number
    size?: number
  }

  let { tick = 0, size = 32 }: Props = $props()

  let angle_timer: number | undefined = undefined
  let angle = $state(0)
  let border_width = $derived(size < 16 ? 2 : 4)

  $effect(() => {
    tick
    update_angle()
  })

  function clear_angle_timer() {
    if (angle_timer !== undefined) {
      clearTimeout(angle_timer)
      angle_timer = undefined
    }
  }

  function update_angle() {
    clear_angle_timer()

    let amplitude = 360
    let time_constant = 30

    angle_timer = window.setInterval(() => {
      const delta = amplitude / time_constant
      angle += delta
      amplitude -= delta
      if (delta < 0.1) {
        clearInterval(angle_timer)
      }
    }, 1000 / time_constant)
  }
</script>

<div
  class="spinner_square {angle === 0 ? 'glow' : ''}"
  style="transform: rotate({angle}deg); width: {size}px; height: {size}px; --b-width: {border_width}px;"
></div>

<style>
  .spinner_square {
    border: var(--b-width) solid #bfc9eb;
    border-radius: 2px;
    transition: transform 1s linear;
  }

  .glow {
    animation: glow-animation 1.5s infinite alternate;
  }

  @keyframes glow-animation {
    from {
      box-shadow: 0 0 1px #bfc9eb;
      filter: brightness(1);
    }
    to {
      box-shadow: 0 0 10px #fff;
      filter: brightness(1.1);
    }
  }
</style>
