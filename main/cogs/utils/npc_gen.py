# -------------------------------------------------------------------------
#                              Imports
# -------------------------------------------------------------------------
import logging
import random
import re
import sys
import os
import traceback


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


log = logging.getLogger(__name__)


# -------------------------------------------------------------------------
#                                  Name gen
# -------------------------------------------------------------------------
def get_name(sex):
    # Variables
    f_names = './main/data/name_dict2.txt'
    fsex = ""

    # Fix sex for data extraction
    if sex == 'Neutral':
        sex = '?'

    # Generate a seed
    while(sex[0] != fsex):
        gen_num = random.randint(1, 48530)
        try:
            with open(f_names, 'r', encoding='utf-8') as f:
                # line = linecache.getline(f_names, gen_num)
                line = f.readlines()[gen_num]

                fsex = (line[0:1])
        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())
            return

    ret_val = re.sub(r'[^\w]', '', (line[3:-1]))
    return ret_val


# -------------------------------------------------------------------------
#                                  Sex Gen
# -------------------------------------------------------------------------
def get_sex(sex):
    if sex is None:
        seed = random.randint(1, 100)
        if seed % 2 == 0:
            return 'Male'
        else:
            return 'Female'

    else:
        if sex.lower() == 'm':
            return "Male"
        elif sex.lower() == 'f':
            return "Female"
        elif sex.lower() == 't':
            return "Neutral"
        else:
            return None


# -------------------------------------------------------------------------
#                            Age, Height, Weight
# -------------------------------------------------------------------------
def get_awh(race, norm_races):
    # Variables
    unpack = norm_races[race]

    # Generate Age
    age = random.randint(10, unpack[0])

    # Generate Height
    base = unpack[1]
    mod = unpack[2]
    roller = unpack[3]

    height = base + (2.54 * (mod * (random.randint(0, roller))))

    # Generate Weight
    base = unpack[1]
    mod = unpack[2]
    roller = unpack[3]

    weight = base + (mod * (random.randint(0, roller)))
    weight = weight * 0.45

    return age, round(height, 2), round(weight, 1)


# -------------------------------------------------------------------------
#                                  Main
# -------------------------------------------------------------------------
def main(gender=None, chosen_race=None):
    # Variables
    npc = {
        'First Name': '',
        'Last Name': '',
        'Sex': '',
        'Race': '',
        'Age': '',
        'Height': '',
        'Weight': '',
    }

    norm_races = {
        'Human': (90, 142, 2, 10, 110, 2, 4),
        'Dwarf': (350, 91, 2, 4, 130, 2, 6),
        'Elf': (750, 121, 2, 12, 90, 1, 4),
        'Halfling': (250, 61, 2, 4, 35, 1, 1),
        'Dragonborn': (80, 152, 2, 8, 175, 2, 6),
        'Gnome': (500, 60, 2, 4, 35, 1, 1),
        'Half-Elf': (180, 121, 2, 8, 110, 2, 4),
        'Half-Orc': (75, 130, 2, 10, 140, 2, 6),
        'Tiefling': (100, 130, 2, 8, 110, 2, 4)
    }

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Getting or generating a gender
    sex = gender
    npc['Sex'] = get_sex(sex)
    if npc['Sex'] is None:
        return ("Supported options for sex: m/f/t")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Generating Names
    npc['First Name'] = get_name(npc['Sex'])
    npc['Last Name'] = get_name('Male')

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Generating Race
    choice_exists = False
    if chosen_race is None:
        npc['Race'] = random.choice(list(norm_races))
        choice_exists = True

    for race in norm_races:
        if (chosen_race == race):
            npc['Race'] = race
            choice_exists = True
            break

    if choice_exists is False:
        return(f"Chosen race doesn't exist.\n Choices: {list(norm_races.keys())}")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Getting Age, weight and height
    npc['Age'], npc['Height'], npc['Weight'] = get_awh(npc['Race'], norm_races)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Printing
    return(f"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Name:       {npc['First Name']} {npc['Last Name']}
Gender:     {npc['Sex']}
Race:       {npc['Race']}
Age:        {npc['Age']}
Height:     {npc['Height']}cm
Weight:     {npc['Weight']}kg
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """)


# -------------------------------------------------------------------------
#                                  Init
# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
