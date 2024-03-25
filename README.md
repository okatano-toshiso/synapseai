# synapseai


1. virtual envelopment start

```
conda activate
python -m venv .venv
source django/bin/.venv
python3 -m pip install --upgrade pip
pip install django
pip freeze > requirements.txt
pip install -r requirements.txt
```

2. server start

```
python manage.py runserver
```

3. virtual envelopment stop

```
 deactivate
```

4. create app

```
 python manage.py startapp {myapp}
```

5. venv start

```
 source test/bin/activate
```
