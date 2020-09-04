# -------------------------------------------------------------------------
#                              Imports
# -------------------------------------------------------------------------
import logging
import random
import sys
import os
import textwrap
import pandas as pd
from io import BytesIO

import discord # noqa
from PIL import Image, ImageDraw, ImageFont

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
log = logging.getLogger(__name__)
path = "./main/cogs/utils/"


# --------------------------------------------------------------------------
#                            Generate Scroll
# --------------------------------------------------------------------------
def getSpell(spell):
    spells = './main/data/Spells.csv'
    num = 0
    s = None

    df = pd.read_csv(spells, encoding="utf-8")

    try:
        if spell is None:
            num = random.randint(0, 437)
            s = df.iloc[num]
        else:
            df['Name'] = df['Name'].str.lower()
            idx = df.index[df['Name'] == spell.lower().strip()].tolist()
            if s == []:
                return None
            s = df.iloc[idx[0]]

        return(s)

    except Exception as e:
        print(e)
        return


def getBg(school):
    # Get background
    try:
        bg = Image.open(f"{path}images/{school}.png")
        return bg
    except Exception as e:
        print(e)
        return


def addCircle(bg, school):
    try:
        circle = Image.open(f"{path}images/{school}.png")
        bg.paste(circle, (0, 50), mask=circle)
        return bg
    except Exception as e:
        print(e)
        return


def addText(bg, spell):
    # ("Name","Source","Level","Casting Time","Duration","School","Range","Components","Classes","Text","At Higher Levels")
    try:
        width, height = bg.size

        d = ImageDraw.Draw(bg)

        addTitle(d, spell)
        addMeta(d, spell)
        addDesc(d, spell)

        return bg
    except Exception as e:
        print(e)
        return


def addTitle(d, spell):
    try:
        loc_w = 90
        loc_h = 100

        wrapper = textwrap.TextWrapper(width=20, replace_whitespace=False)
        name = wrapper.fill(text=str(spell[0]))
        print(spell[0])
        fnt = ImageFont.truetype(f'{path}fonts/IokharicBold.ttf', 75)
        w, h = d.textsize(text=name, font=fnt)

        d.text((loc_w, loc_h), name, font=fnt, fill=(88, 73, 58))

    except Exception as e:
        print(e)
        return


def addMeta(d, spell):
    try:
        loc_w = 90
        loc_h = 280

        level = "level " + str(spell[2])
        cast = str(spell[3])
        duration = str(spell[4])
        range = str(spell[6])

        wrapper = textwrap.TextWrapper(width=13, replace_whitespace=False)
        line = wrapper.fill(text=f"{level}\n{cast}\n{duration}\n{range}")

        fnt = ImageFont.truetype(f'{path}fonts/IokharicBold.ttf', 50)
        w, h = d.textsize(text=line, font=fnt)
        d.text((loc_w, loc_h), line, font=fnt, fill=(88, 73, 58))
    except Exception as e:
        print(e)
        return


def addDesc(d, spell):
    try:
        loc_w = 90
        loc_h = 630

        text = str(spell[9]) + "\n\n" + str(spell[10])
        s = text[:850] if len(text) > 850 else text
        print(s)
        wrapper = textwrap.TextWrapper(width=55, drop_whitespace=False, replace_whitespace=False)
        line = wrapper.fill(text=s)

        fnt = ImageFont.truetype(f'{path}fonts/IokharicBold.ttf', 28)
        w, h = d.textsize(text=line, font=fnt)
        d.text((loc_w, loc_h), line, font=fnt, fill=(26, 21, 17))
    except Exception as e:
        print(e)
        return


def resize(scroll):
    basewidth = 900
    wpercent = (basewidth/float(scroll.size[0]))
    hsize = int((float(scroll.size[1])*float(wpercent)))
    img = scroll.resize((basewidth, hsize), Image.ANTIALIAS)
    return img


def main(spellname=None):
    try:
        spell = getSpell(spellname)
        if spell is None:
            return
        bg = getBg(str(spell[5]).strip())
        scroll = addText(bg, spell)

    # scroll.save(f"{path}images/sc.png")

        buffer = BytesIO()
        scroll.save(buffer, format="png")
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(e)


# -------------------------------------------------------------------------
#                                  Init
# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
