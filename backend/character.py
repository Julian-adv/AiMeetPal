# list character cards
import os
import base64
import json
from fastapi import APIRouter, HTTPException
from settings import get_data_path
import png

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
        for filename in os.listdir(characters_dir):
            if filename.lower().endswith('.png'):
                character_id = os.path.splitext(filename)[0]
                image_path = os.path.join(characters_dir, filename)
                
                # Read and encode the image
                with open(image_path, 'rb') as img_file:
                    png_reader = png.Reader(file=img_file)
                    chunks = list(png_reader.chunks())
                    
                    # Find metadata in tEXt chunks
                    info = {}
                    for chunk_type, chunk_data in chunks:
                        if chunk_type == b'tEXt':
                            # tEXt chunks are separated by null bytes between key and value
                            key, value = chunk_data.split(b'\0', 1)
                            key = key.decode('latin-1')
                            value = value.decode('utf-8')
                            
                            try:
                                if key == 'ccv3':
                                    decoded = base64.b64decode(value).decode('utf-8')
                                    info = json.loads(decoded)
                                    break
                                if key == 'chara':
                                    decoded = base64.b64decode(value).decode('utf-8')
                                    info = json.loads(decoded)
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                            except Exception as e:
                                print(f"Error decoding {key}: {e}")
                    
                    # Reset the file pointer to the beginning
                    img_file.seek(0)
                    image_data = base64.b64encode(img_file.read()).decode()
                
                    if info.get('name') is not None:
                        characters.append({
                            'id': character_id,
                            'image': f'data:image/png;base64,{image_data}',
                            'info': info
                        })
        
        return sorted(characters, key=lambda x: x['id'])
    except Exception as e:
        print(f"Error listing characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
