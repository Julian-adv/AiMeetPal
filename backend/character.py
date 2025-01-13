# list character cards
import os
from fastapi import APIRouter, HTTPException
from settings import get_data_path
import base64

router = APIRouter()

@router.get('/api/characters')
async def list_characters():
    """List all character PNG files in the data/characters directory.
    
    Returns:
        List[dict]: List of dictionaries containing character information.
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
                image_path = os.path.join(characters_dir, file)
                
                # Read and encode the image
                with open(image_path, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read()).decode()
                
                characters.append({
                    'id': character_id,
                    'image': f'data:image/png;base64,{image_data}'
                })
        
        return sorted(characters, key=lambda x: x['id'])
    except Exception as e:
        print(f"Error listing characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
