export interface Character {
  file_name: string
  image: string
  info: {
    name: string
    description: string
    first_mes: string
    scenario: string
    personality: string
    mes_example: string
    image_prompt: string
    [key: string]: any
  }
}
