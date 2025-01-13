# list character cards
import os
from fastapi import APIRouter
from settings import get_data_path

router = APIRouter()

@router.get('/api/characters')
async def list_characters():
    """List all character PNG files in the data/characters directory.
    
    Returns:
        list: List of dictionaries containing character information
              Each dictionary has 'id' and 'image' keys
    """
    characters_dir = get_data_path('characters')
    
    try:
        # Ensure the directory exists
        if not os.path.exists(characters_dir):
            os.makedirs(characters_dir)
        
        # Get all PNG files
        characters = []
        for file in os.listdir(characters_dir):
            if file.lower().endswith('.png'):
                character_id = os.path.splitext(file)[0]
                characters.append({
                    'id': character_id,
                    'image': f'/characters/{file}'
                })
        
        return sorted(characters, key=lambda x: x['id'])
    except Exception as e:
        print(f"Error listing characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
