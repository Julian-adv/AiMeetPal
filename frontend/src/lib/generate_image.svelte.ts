async function scene_to_prompt(text: string, prev_image_prompt: string) {
  const response = await fetch('http://localhost:5000/api/scene-to-prompt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content: text, prev_image_prompt: prev_image_prompt }),
  })
  const data = await response.json()
  return data.prompt
}

export function image_size(prompt: string) {
  const portrait = !!prompt.match(/format:\s*portrait/i)
  if (portrait) {
    return { width: 832, height: 1216 }
  } else {
    return { width: 1216, height: 832 }
  }
}

async function generate_prompt(content: string, prev_prompt: string) {
  let prompt = await scene_to_prompt(content, prev_prompt)
  if (!prompt) {
    prompt = content
  }
  const { width, height } = image_size(prompt)
  return { prompt, width, height }
}

async function generate_image(
  checkpoint_name: string,
  prompt: string,
  width: number,
  height: number
) {
  const prefix = 'score_9, score_8_up, score_7_up'
  const response = await fetch('http://localhost:5000/api/generate-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      checkpoint_name: checkpoint_name,
      prompt: `${prefix}, ${prompt}`,
      guidance_scale: 4.5,
      width: width * 1,
      height: height * 1,
      face_steps: 20,
    }),
  })
  const data = await response.json()
  const image = data.image
  return image
}

export { generate_image, generate_prompt }
