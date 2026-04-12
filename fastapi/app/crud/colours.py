import os
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw
from app import models

def get_colours(db : Session) -> list[models.Colour]:
    return [_ for _ in db.scalars(
        select(models.Colour)
    )]


def get_colours_bar_image(colours_hex: List[str], width: int=300, height: int=40, border_radius: int=20, border_color:str="#e0e0e0", border_width:int=0) -> dict[str, str]:
    
    # for the filename, sort the colours according to their integer value, so that different permutations can still use the same file
    colours_sorted = sorted(colours_hex, key=lambda c: models.Colour.getintvalue(c))
    image_file_name = f"colour_bar_" + "_".join(colours_sorted) + ".png"

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    image_file_path = os.path.join(temp_data_dir, image_file_name)
    
    if not os.path.exists(image_file_path):

        # Create a base image with transparency
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
    
        # Calculate segment width
        segment_width = width / len(colours_hex)
    
        # Draw colour segments
        for i, colour in enumerate(colours_hex):
            x0 = int(i * segment_width)
            x1 = int((i + 1) * segment_width)
    
            draw.rectangle(
                [x0, 0, x1, height],
                fill=f"#{colour}"
            )
    
        # Create rounded mask
        mask = Image.new("L", (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [0, 0, width, height],
            radius=border_radius,
            fill=255
        )
    
        # Apply rounded corners
        rounded = Image.new("RGBA", (width, height))
        rounded.paste(img, (0, 0), mask=mask)
    
        # Add border
        if border_width > 0:
            border_draw = ImageDraw.Draw(rounded)
            border_draw.rounded_rectangle(
                [0, 0, width-1, height-1],
                radius=border_radius,
                outline=border_color,
                width=border_width
            )
            
        with open(image_file_path, "wb") as fout:
            rounded.save(fout)
            
    return {"path": image_file_path, "media_type": "image/png"}
