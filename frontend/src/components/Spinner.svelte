<script lang="ts">
  interface Props {
    angle?: number
    size?: number
  }

  let { angle = 0, size = 32 }: Props = $props()
</script>

<div
  class="spinner_square {angle === 0 ? 'glow' : ''}"
  style="transform: rotate({angle}deg); width: {size}px; height: {size}px;"
></div>

<style>
  .spinner_square {
    border: 4px solid #bfc9eb;
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
