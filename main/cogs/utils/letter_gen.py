#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys

# Third party imports
import discord # noqa
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# Local application imports
# Enabling local imports
# BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_PATH)
# from settings import embeds as emb # noqa

log = logging.getLogger(__name__)
path = "images/"
error_log = []


# --------------------------------------------------------------------------
#                            Adding content
# --------------------------------------------------------------------------
def add_content(bg, msg):
    try:
        # Get size of image
        width, height = bg.size

        # Get content data
        content = ImageDraw.Draw(bg)
        fnt = ImageFont.truetype(f'{path}DancingScript.ttf', 40)
        w, h = content.textsize(msg, font=fnt)

        # Draw content

        error_log.append('Added Content')
        return bg
    except Exception as e:
        print(e)
        error_log.append('Error adding content')
        return


# --------------------------------------------------------------------------
#                            Adding a title
# --------------------------------------------------------------------------
def add_title(bg, msg):
    try:
        # Get size of image
        width, height = bg.size

        # Get title data
        title = ImageDraw.Draw(bg)
        fnt = ImageFont.truetype(f"{path}OldeEnglish.ttf", 80)
        w, h = title.textsize(msg, font=fnt)
        place_w = int((width - w) / 2)

        # Draw title
        title.text((place_w, 200), msg, font=fnt, fill='black')
        error_log.append('Added title')

        return bg

    except Exception as e:
        print(e)
        error_log.append('Error Adding title')
        return


# --------------------------------------------------------------------------
#                             Get parchment
# --------------------------------------------------------------------------
def get_bg():
    # Get background
    try:
        bg = Image.open(f"{path}Scroll.png")
        error_log.append('Loaded background')
        return bg
    except Exception as e:
        print(e)
        error_log.append('Error Loading bg')
        return


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
def main():
    # sort out vars
    title = "Help Wanted"
    content = """
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the
industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type
and scrambled it to make a type specimen book. It has survived not only five centuries, but also
the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the
1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with
desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
    """

    # Get image from file
    bg = get_bg()

    # Adding a title
    if title:
        bg = add_title(bg, title)

    # Adding content
    bg = add_content(bg, content)

    # Adding signature
    bg = add_signature(bg, signature)

    try:
        bg.save('pil_text_font.png')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
