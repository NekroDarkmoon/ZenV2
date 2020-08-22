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


# --------------------------------------------------------------------------
#                            Adding signature
# --------------------------------------------------------------------------
def add_signature(bg, msg, ctn):
    try:
        # Get size of image
        width, height = bg.size

        # Get singature data
        signature = ImageDraw.Draw(bg)
        fnt = ImageFont.truetype(f'{path}DancingScript.ttf', 35)
        w, h = signature.textsize(msg, font=fnt)

        # Calc location
        place_w = width - (165 + w)
        place_h = ctn[1] + 20

        # Draw signature
        signature.multiline_text((place_w, place_h), msg, font=fnt, fill='black', align='right')

        return (bg)
    except Exception as e:
        print(e)
        return


# --------------------------------------------------------------------------
#                            Adding content
# --------------------------------------------------------------------------
def add_content(bg, msg, ctn):
    try:
        # Get size of image
        width, height = bg.size
        # msg = "\n".join(wrap(msg, width=60))
        lines = msg.splitlines()

        # Calc locations
        place_w = 160
        if ctn is True:
            place_h = 250
        else:
            place_h = 300

        for line in lines:
            wrapper = textwrap.TextWrapper(width=50, replace_whitespace=False, drop_whitespace=False)
            line = wrapper.fill(text=line)

            # Get Content data
            content = ImageDraw.Draw(bg)
            fnt = ImageFont.truetype(f'{path}DancingScript.ttf', 35)
            w, h = content.textsize(text=line, font=fnt)

            # Draw content
            if len(line) > 50:
                content.multiline_text((place_w, place_h), line, font=fnt, fill='black')
            else:
                content.text((place_w, place_h), line, font=fnt, fill='black')

            # Calc new position
            if line == '':
                place_h += 15 + h
            else:
                place_h += 35 + h

        return bg, (w, (place_h))
    except Exception as e:
        print(e)
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

        return bg, (w, h)

    except Exception as e:
        print(e)
        return


# --------------------------------------------------------------------------
#                             Get parchment
# --------------------------------------------------------------------------
def get_bg():
    # Get background
    try:
        bg = Image.open(f"{path}Scroll.png")
        return bg
    except Exception as e:
        print(e)
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
    if signature:
        bg = add_signature(bg, signature, content_details)

    try:
        # bg.save('pil_text_font.png')
        final_buffer = BytesIO()
        bg.save(final_buffer, "png")
        final_buffer.seek(0)
        return final_buffer
    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    main()
