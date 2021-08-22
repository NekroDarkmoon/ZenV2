# Zen-Public

### New Dev install for Windows
01. `git clone https://github.com/NekroDarkmoon/Zen-Public`
02. `cd Zen-Public`
03. `python -m venv .venv`
04. `.venv\Scripts\activate`
05. `	pip install -r requirements.txt`
06. Create a config.json
07. Populate config.json
08. `cd main`
09. `bot.py`

### Install db
01. Download from https://www.postgresql.org/
02. Create a new user called  `Zen` with `yourpw`
03. Create a new database called `Zen` with owner `Zen`


### Config template

config.py
```py

client_id = ""  
token = ""
db = 'postgresql://user:pass@localhost:5432/database'
prefix = ""
stat_webhook = ('877310740992753714', "JrHoh8FJ9o8lJPITtzuZMjFiRgsWojNONRFk4UglG15SzqV6OHHlt7-O8dQvf2Vvk3mu")

```
