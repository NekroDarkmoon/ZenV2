#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys
import textwrap
from io import BytesIO

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
path = "./main/cogs/utils/images/"
error_log = []


# --------------------------------------------------------------------------
#                            Adding signature
# --------------------------------------------------------------------------
def add_signature(bg, msg, ctn):
    try:
        # Get size of image
        width, height = bg.size

        # Get singature data
        signature = ImageDraw.Draw(bg)
        fnt = ImageFont.truetype(f'{path}DancingScript.ttf', 30)
        w, h = signature.textsize(msg, font=fnt)

        # Calc location
        place_w = width - (165 + w)
        place_h = 300 + ctn[1] + 20

        # Draw signature
        signature.multiline_text((place_w, place_h), msg, font=fnt, fill='black', align='right')

        error_log.append('Added Signature')
        return (bg)
    except Exception as e:
        print(e)
        error_log.append('Erro Adding Signature')
        return


# --------------------------------------------------------------------------
#                            Adding content
# --------------------------------------------------------------------------
def add_content(bg, msg, ctn):
    try:
        # Get size of image
        width, height = bg.size
        # msg = "\n".join(wrap(msg, width=60))
        wrapper = textwrap.TextWrapper(width=60, replace_whitespace=False, drop_whitespace=False)
        msg = wrapper.fill(text=msg)

        # Get content data
        content = ImageDraw.Draw(bg)
        fnt = ImageFont.truetype(f'{path}DancingScript.ttf', 30)
        w, h = content.textsize(msg, font=fnt)

        # Calc location
        place_w = 160
        if ctn is True:
            place_h = 250
        else:
            place_h = 300

        # Draw content
        content.multiline_text((place_w, place_h), msg, font=fnt, fill='black')

        error_log.append('Added Content')
        return bg, (w, h)
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
        fnt = ImageFont.truetype(f"{path}OldeEnglish.ttf", 70)
        w, h = title.textsize(msg, font=fnt)
        place_w = int((width - w) / 2)

        # Draw title
        title.text((place_w, 200), msg, font=fnt, fill='black')
        error_log.append('Added title')

        return bg, (w, h)

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
def main(title, content, signature, skip=True):
    # Get image from file
    bg = get_bg()

    # Adding a title
    if title:
        bg, skip = add_title(bg, title)

    # Adding content
    bg, content_details = add_content(bg, content, skip)

    # Adding signature
    bg = add_signature(bg, signature, content_details)

    try:
        # bg.save('pil_text_font.png')
        print(error_log)

        final_buffer = BytesIO()

        bg.save(final_buffer, "png")
        final_buffer.seek(0)
        return final_buffer
    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    main()
