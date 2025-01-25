export interface Entry {
  name: string
  is_dir: boolean
}

export interface DirEntries {
  entries: Entry[]
  current_directory: string
}
