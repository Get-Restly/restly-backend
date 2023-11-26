# Setup

## 1. Create and activate virtual environment

```sh
python -m venv venv
source ./venv/bin/activate
```

## 2. Install dependencies

```sh
pip install -r requirements.txt
```

## 3. Run migrations

```
flask db upgrade
```

## 4. Run Flask application

```
flask run
```

NOTE: You can use instance/project.db file for sqlite.
