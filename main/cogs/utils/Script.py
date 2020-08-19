import asyncio
import asyncpg
from bs4 import BeautifulSoup
import datetime
import sqlite3

print('Starting connection')
URL = "https://mee6.xyz/leaderboard/719063399148814418"
print(f'Connecting to {URL}')

# try:
#     page = requests.get(URL)
#     print('Connected')
# except Exception as e:
#     print(e)

with open("data.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
    print('Made a soup')

with open("names.txt", 'r') as fp:
    users = fp.readlines()


# soup = BeautifulSoup(page.content, 'html.parser')

data = []
rank_elems = soup.find_all('div', class_='leaderboardPlayer')
for rank_elem in rank_elems:
    user = {}
    user_name = rank_elem.find('div', class_='leaderboardPlayerUsername')
    stats = rank_elem.find_all('div', class_='leaderboardPlayerStatValue')

    for x in users:
        if user_name.text in x:
            id = int(x.split(':')[1].rstrip())
            user.update({'id': id})
            user.update({'name': user_name.text})
            break
        else:
            user.update({'id': None})

    for elem, stat in enumerate(stats):
        user.update({f'stat[{elem}]': stat.text})

    if user['id'] is not None:
        data.append(user)


async def run():
    conn = await asyncpg.connect(user='Zen', password='nothing_is_free',
                                 database='Zen')
    await send(data, conn)
    return (conn)


async def send(data, conn):
    for user in data:
        server_id = 719063399148814418
        user_id = int(user['id'])
        last_exp = datetime.datetime.now()
        # data maniputation
        msg_amt = user['stat[0]']
        if 'k' in msg_amt:
            msg_amt = int(float(msg_amt.replace('k', '')) * 1000)
        else:
            msg_amt = int(msg_amt)

        total_exp = user['stat[1]']
        if 'k' in total_exp:
            total_exp = int(float(total_exp.replace('k', '')) * 1000)
        else:
            total_exp = int(total_exp)

        level = int(user['stat[2]'])
        sql = """INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )"""
        try:
            print(user)
            await conn.execute(sql, server_id, user_id, last_exp, msg_amt, total_exp, level)
        except Exception as e:
            print(e)

    # Getting data from sqlite and putting it in this ish
    try:
        sqconn = sqlite3.connect('cogs.db')
        sqcursor = sqconn.cursor()

        sqcursor.execute('''SELECT * FROM lfg''')
        records = sqcursor.fetchall()
        for record in records:
            print(record)
            sql = """ INSERT INTO quest VALUES ( $1, $2, $3, $4, $5 )"""
            await conn.execute(sql, record[0], record[1], record[2], record[3], record[4])
    except Exception as e:
        print(e)

    records = await conn.fetch('SELECT * FROM quest')
    print(records)

loop = asyncio.get_event_loop()
conn = loop.run_until_complete(run())
