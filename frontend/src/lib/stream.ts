import { tick } from 'svelte'

export type ReceivedData =
  | { text: string; reset?: never; start_index?: never }
  | { reset: boolean; text?: never; start_index?: never }
  | { start_index: number; text?: never; reset?: never }

export async function send_stream(
  url: string,
  payload: any,
  received: (data: ReceivedData) => void,
  start_receive?: () => void
): Promise<string> {
  let error = ''
  const response = await fetch('http://localhost:5000/api/' + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    console.log(response)
    return `error: ${response.statusText}`
  }

  const reader = response.body?.getReader()
  if (!reader) {
    return `error: Failed to get response reader`
  }
  const decoder = new TextDecoder()

  if (start_receive) start_receive()

  while (true) {
    const { value, done } = await reader.read()

    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ') && line.trim() !== 'data: ') {
        try {
          const data = JSON.parse(line.slice(6))
          received(data)
          requestAnimationFrame(async () => {
            await tick()
          })
        } catch (e) {
          error = `error: ${e}`
        }
      }
    }
  }
  return error
}
