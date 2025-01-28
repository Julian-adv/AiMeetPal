import { marked } from 'marked'

export function highlightQuotes(content: string) {
  let markedContent = marked(content, { async: false })
  markedContent = markedContent.replace(/"([^"]+)"/g, '<span class="quoted-text">"$1"</span>')
  markedContent = markedContent.replace(/“([^”]+)”/g, '<span class="quoted-text">"$1"</span>')
  return markedContent.replace(/&quot;(.+?)&quot;/g, '<span class="quoted-text">"$1"</span>')
}

let simple_id = 0

export function get_id() {
  return simple_id++
}
