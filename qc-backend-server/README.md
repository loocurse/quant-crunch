# Python Backend for Web Interface

## TODO

- [ ] Provide API for frontend
- [ ] Logging

## Setup

To setup the environment, you may want to use
[pipenv](https://pypi.org/project/pipenv/) as it might be easier to specify the
python version and to activate the environment:

```bash
pipenv install
pipenv shell
```

Alternatively, installing through `pip` would work as well. You are strongly
recommended to use python `3.9` and above if you're installing with `pip`.

```bash
pip install -r requirements.txt
```

To run the server:

```bash
pipenv run start
```

or

```bash
python main.py
```

## Docs

```
localhost:5050/docs
```

## Docker Setup

```sh
git clone https://github.com/loocurse/quant-crunch.git
cd quant-crunch/qc-backend-server
vim .env
sudo docker-compose up -d
```

Things to set in `.env`

```
POLYGON_API_KEY=
MONGO_ATLAS_URI=
```

If you're using a reverse proxy like `nginx`, you might need to set the
`ROOT_PATH` variable to the appropriate url prefix.

If you're not running the application via `docker-compose`, you might want to set `REDIS_HOST` to the
appropriate url like `localhost`.
