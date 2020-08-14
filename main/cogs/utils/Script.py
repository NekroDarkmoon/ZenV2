import asyncio
import asyncpg
import requests
from bs4 import BeautifulSoup
import datetime


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
        msg_amt = int(user['stat[0]'].replace('.', '').replace('k', '000'))
        total_exp = int(user['stat[1]'].replace('.', '').replace('k', '000'))
        level = int(user['stat[2]'])
        sql = """INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )"""
        await conn.execute(sql, server_id, user_id, last_exp, msg_amt, total_exp, level)


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(run())
