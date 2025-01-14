export interface Character {
  id: string
  image: string
  info: {
    name: string
    description: string
    first_mes: string
    scenario: string
    personality: string
    mes_example: string
    [key: string]: any
  }
}
