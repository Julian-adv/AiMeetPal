export function image_size(prompt: string) {
  const portrait = !!prompt.match(/format:\s*portrait/i)
  if (portrait) {
    return { width: 832, height: 1216 }
  } else {
    return { width: 1216, height: 832 }
  }
}

async function generate_image(
  checkpoint_name: string,
  prompt: string,
  width: number,
  height: number
) {
  const response = await fetch('http://localhost:5000/api/generate-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      checkpoint_name: checkpoint_name,
      prompt: prompt,
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

export { generate_image }
