# Guppy

### Prerequisites

```bash
brew install ffmpeg
```

You should also install the `guppy_web` deps:

```bash
cd guppy_web
npm install
```

...and the Python deps:

```bash
cd guppy_py
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Building

You have to move a dist directory of the web app to `pb_public` for it to be rendered by pocketbase. See the README.md in guppy_web for more details.

### Running

```bash
./pocketbase serve --debug --http 0.0.0.0:8090
```

You also need to periodically run the show generator (which someday will be done with a long-running service or cron job). Right now it lives in `guppy_py`:

```bash
cd guppy_py
python ./guppy_worker.py
```

## Features

### Create a new podcast from a prompt

![image](https://github.com/j6k4m8/guppy/assets/693511/46e56eca-bb57-4e5f-a5c5-6a3cbfb0f97b)

### Listen to a show

![image](https://github.com/j6k4m8/guppy/assets/693511/0d375c69-83e9-47fa-b3e3-1c1f98ee9e3a)

### Podcast compatibility

Each show has a fully functional RSS feed, so you can subscribe to it in your favorite podcast app. Furthermore, each user has a master RSS feed that contains all of their shows' episodes, so you can subscribe to a rolling feed of all of your shows.
