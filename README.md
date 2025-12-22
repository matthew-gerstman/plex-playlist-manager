# Plex Playlist Manager

A CLI tool to create themed playlists from your Plex library.

## Features

- **Themed Playlists**: Christmas, Halloween, Thanksgiving, New Year's, Hanukkah, Valentine's Day
- **Highly Rated Unwatched**: Auto-generate a playlist of top-rated movies you haven't seen
- **Cross-Library Search**: Finds content in both TV Shows and Movies
- **Smart Keyword Matching**: Searches titles and summaries with exclusion filters

## Installation

```bash
pip install plexapi click
```

Or with the requirements file:

```bash
pip install -r requirements.txt
```

## Setup

Set your Plex credentials as environment variables:

```bash
export PLEX_URL="http://YOUR_PLEX_IP:32400"
export PLEX_TOKEN="your-plex-token"
```

### Finding Your Plex Token

1. Open Plex Web App and play any media
2. Click the `⋮` menu → "Get Info" → "View XML"
3. Look at the URL — your token is the `X-Plex-Token=XXXXX` parameter

## Usage

### List Available Themes

```bash
python plex_playlist.py themes
```

### Create a Themed Playlist

```bash
# Christmas episodes and movies
python plex_playlist.py create christmas

# Halloween, TV only
python plex_playlist.py create halloween --tv-only

# Custom playlist name
python plex_playlist.py create thanksgiving --name "Turkey Day Marathon"

# Dry run (see what would be added)
python plex_playlist.py create hanukkah --dry-run
```

### Create Highly Rated Unwatched Movies Playlist

```bash
# Default: 8.0+ rating
python plex_playlist.py highly-rated

# Custom minimum rating
python plex_playlist.py highly-rated --min-rating 7.5

# Custom name
python plex_playlist.py highly-rated --name "Must Watch"
```

### List All Playlists

```bash
python plex_playlist.py list
```

### Delete a Playlist

```bash
python plex_playlist.py delete "Christmas Episodes"
```

## Available Themes

| Theme | Description |
|-------|-------------|
| `christmas` | Christmas and holiday episodes |
| `halloween` | Halloween and spooky episodes |
| `thanksgiving` | Thanksgiving episodes |
| `newyears` | New Year's Eve/Day episodes |
| `hanukkah` | Hanukkah episodes and movies |
| `valentine` | Valentine's Day episodes |

## Examples

```bash
# Create all holiday playlists
python plex_playlist.py create christmas
python plex_playlist.py create thanksgiving
python plex_playlist.py create halloween
python plex_playlist.py create hanukkah
python plex_playlist.py create newyears

# Create a movie night playlist
python plex_playlist.py highly-rated --min-rating 8.5 --name "Movie Night Picks"
```

## License

MIT
