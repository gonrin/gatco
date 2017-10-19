# Prerequisite
* Python 3.5 and above

# Install virtualenv
```bash
$ python3 -m venv /path_to_venv
$ cd /path_to_venv
$ git clone https://giturl/repo.git repo
$ source bin/activate
$ cd repo
$ pip install -r requirements.txt
```

# Edit database configuration
in application/config.py:
```
SQLALCHEMY_DATABASE_URI = 'postgresql://someuser:pass@dbhost:dbport/somedb'
```
in alembic.ini:
```
sqlalchemy.url = postgresql://someuser:pass@dbhost:dbport/somedb
```

then excute:
```bash
# run alembic to migrate database
$ alembic revision --autogenerate -m "initdb"
$ alembic upgrade head
$ python manage run
```

# Add client script:
```bash
$ cd static/js
$ git clone https://github.com/gonrin/GonrinJS.git lib
$ cd ../vendor/
$ git clone https://github.com/gonrin/GonrinUI.git
```

# Now, service is running:
```
2017-09-22 15:37:13 - (sanic)[DEBUG]:
                 ▄▄▄▄▄
        ▀▀▀██████▄▄▄       _______________
      ▄▄▄▄▄  █████████▄  /                 \
     ▀▀▀▀█████▌ ▀▐▄ ▀▐█ |   Gotta go fast!  |
   ▀▀█████▄▄ ▀██████▄██ | _________________/
   ▀▄▄▄▄▄  ▀▀█▄▀█════█▀ |/
        ▀▀▀▄  ▀▀███ ▀       ▄▄
     ▄███▀▀██▄████████▄ ▄▀▀▀▀▀▀█▌
   ██▀▄▄▄██▀▄███▀ ▀▀████      ▄██
▄▀▀▀▄██▄▀▀▌████▒▒▒▒▒▒███     ▌▄▄▀
▌    ▐▀████▐███▒▒▒▒▒▐██▌
▀▄▄▄▄▀   ▀▀████▒▒▒▒▄██▀
          ▀▀█████████▀
        ▄▄██▀██████▀█
      ▄██▀     ▀▀▀  █
     ▄█             ▐▌
 ▄▄▄▄█▌              ▀█▄▄▄▄▀▀▄
▌     ▐                ▀▀▄▄▄▀
 ▀▀▄▄▀

2017-09-22 15:37:13 - (sanic)[INFO]: Goin' Fast @ http://0.0.0.0:8000
2017-09-22 15:37:13 - (sanic)[INFO]: Starting worker [3115]
2017-09-22 15:37:13 - (sanic)[INFO]: Starting worker [3114]
2017-09-22 15:37:13 - (sanic)[INFO]: Starting worker [3117]
2017-09-22 15:37:13 - (sanic)[INFO]: Starting worker [3116]
```
