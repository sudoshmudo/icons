import base64
import difflib
import io
import os
import subprocess
import sys
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import requests
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

load_dotenv()

ICONS8_TOKEN = os.environ['ICONS8_TOKEN']

ICONS8_GET_URL = 'https://api-icons.icons8.com/publicApi/icons/icon'
ICONS8_SEARCH_URL = 'https://search.icons8.com/api/iconsets/v5/search'
OK = 'OK'
OUTPUT_FORMAT = 'PNG'
PLATFORM = 'color'
SVG_PATH = 'svg/'

class Icon(BaseModel):
    name: str
    keyword: Optional[str] = None
    platform: Optional[str] = PLATFORM

app = FastAPI()

def icons8_search(keyword, platform):
    request_model = requests.models.PreparedRequest()
    params = {
        'term': keyword,
        'token': ICONS8_TOKEN,
        'platform': platform,
        'amount':  1
    }
    request_model.prepare_url(ICONS8_SEARCH_URL, params)
    return requests.get(request_model.url).json()['icons'][0]['id']

def icons8_get(id):
    request_model = requests.models.PreparedRequest()
    params = {
        'id': id,
        'token': ICONS8_TOKEN
    }
    request_model.prepare_url(ICONS8_GET_URL, params)
    return requests.get(request_model.url).json()['icon']['svg']

@app.get("/icons/{name}")
async def get_icon(name):
    matching_icons = difflib.get_close_matches(name, [filename.split('.')[0] for filename in os.listdir(SVG_PATH)])
    if len(matching_icons) == 0:
        raise HTTPException(status_code=404, detail="No icons available for this name")
    filepath = os.path.join(SVG_PATH, '{}.svg'.format(matching_icons[0]))

    drawing = svg2rlg(filepath)
    io_file = io.BytesIO()
    renderPM.drawToFile(drawing, io_file, fmt=OUTPUT_FORMAT)
    return base64.b64encode(io_file.getvalue())

@app.post("/icons/")
async def create_icon(icon: Icon):
    keyword = icon.name
    if (icon.keyword is not None):
        keyword = icon.keyword

    icon_id = icons8_search(keyword, icon.platform)
    icon_svg = icons8_get(icon_id)

    with open(os.path.join(SVG_PATH, '{}.svg'.format(icon.name)), 'w') as f:
        f.write(icon_svg)

    return OK