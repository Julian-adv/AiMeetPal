<script lang="ts">
  import CharacterList from './components/CharacterList.svelte'
  import Chat from './components/Chat.svelte'
  import EditChar from './components/EditChar.svelte'
  import Checkpoints from './components/Checkpoints.svelte'
  import Settings from './components/Settings.svelte'
  import EditPreset from './components/EditPreset.svelte'
  import Tabs from './components/Tabs.svelte'
  import {
    Users,
    ChatBubbleLeftRight,
    WrenchScrewdriver,
    UserPlus,
    Squares2x2,
    AdjustmentsHorizontal,
  } from 'svelte-heros-v2'
  import { g_state } from './lib/state.svelte'

  let tab_items = [
    { label: 'Characters', icon: Users, value: 1, component: CharacterList },
    { label: 'Chat', icon: ChatBubbleLeftRight, value: 2, component: Chat },
    { label: 'Edit char', icon: UserPlus, value: 3, component: EditChar },
    { label: 'Checkpoints', icon: Squares2x2, value: 4, component: Checkpoints },
    { label: 'Settings', icon: WrenchScrewdriver, value: 5, component: Settings },
    { label: 'Preset', icon: AdjustmentsHorizontal, value: 6, component: EditPreset },
  ]
  let prompt = ''
  let loading = false
  let generatedImage: string | null = null
  let error: string | null = null

  async function generateImage() {
    if (!prompt.trim()) return

    loading = true
    error = null
    // generatedImage = null

    const guidance_scale = 4.5
    const width = 832 * 1
    const height = 1216 * 1
    const prefix = 'score_9, score_8_up, score_7_up'
    const face_steps = 20

    try {
      const response = await fetch('http://localhost:5000/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `${prefix}, ${prompt}`,
          guidance_scale,
          width,
          height,
          face_steps,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate image')
      }

      generatedImage = data.image
    } catch (e) {
      error = e instanceof Error ? e.message : 'An error occurred'
    } finally {
      loading = false
    }
  }
</script>

<main>
  <h1>Ai Meet Pal</h1>

  <Tabs {tab_items} active_tab={g_state.active_tab} />
</main>

<style>
  @reference "tailwindcss/theme";

  h1 {
    text-align: center;
    color: theme('colors.slate.600');
    margin-bottom: 2rem;
    font-family: 'Edwardian Script ITC', Georgia, 'Times New Roman', Times, serif;
    margin-top: 2rem;
  }
</style>
