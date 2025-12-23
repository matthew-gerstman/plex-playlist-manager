#!/usr/bin/env python3
"""
Plex Playlist Manager CLI

Create themed playlists from your Plex library.
"""

import click
import os
import sys
from plexapi.server import PlexServer


# Theme definitions with keywords and exclusions
THEMES = {
    "christmas": {
        "keywords": [
            "christmas", "xmas", "santa", "santa's", "scrooge", "nutcracker",
            "krampus", "yuletide", "rudolph", "grinch", "north pole",
            "christmas eve", "christmas tree", "jingle", "frosty the snowman",
            "mistletoe", "eggnog"
        ],
        "exclude": [
            "halloween", "thanksgiving", "easter", "valentine", "hanukkah",
            "kwanzaa", "columbus day", "independence day", "4th of july",
            "new year", "labor day", "memorial day"
        ],
        "description": "Christmas and holiday episodes"
    },
    "halloween": {
        "keywords": [
            "halloween", "spooky", "haunted", "ghost", "witch", "vampire",
            "zombie", "monster", "trick or treat", "costume", "pumpkin",
            "scary", "horror", "nightmare"
        ],
        "exclude": ["christmas", "thanksgiving"],
        "description": "Halloween and spooky episodes"
    },
    "thanksgiving": {
        "keywords": [
            "thanksgiving", "turkey day", "pilgrim", "giving thanks"
        ],
        "exclude": ["christmas"],
        "description": "Thanksgiving episodes"
    },
    "newyears": {
        "keywords": [
            "new year", "new year's", "nye", "december 31", "january 1",
            "midnight countdown", "ball drop", "auld lang syne"
        ],
        "exclude": ["chinese new year", "lunar new year"],
        "description": "New Year's Eve/Day episodes"
    },
    "hanukkah": {
        "keywords": [
            "hanukkah", "chanukah", "hanukah", "channukah", "menorah",
            "dreidel", "latkes", "maccabee", "festival of lights",
            "eight crazy nights"
        ],
        "exclude": [],
        "description": "Hanukkah episodes and movies"
    },
    "valentine": {
        "keywords": [
            "valentine", "valentines", "valentine's day", "cupid",
            "romantic", "love day"
        ],
        "exclude": [],
        "description": "Valentine's Day episodes"
    },
    "july4th": {
        "keywords": [
            "4th of july", "fourth of july", "july fourth", "july 4th",
            "independence day", "fireworks"
        ],
        "exclude": ["christmas", "halloween", "thanksgiving", "alien", "war of the worlds"],
        "description": "4th of July / Independence Day episodes"
    },
}


# Musical episodes - specific episodes by show (not keyword-based)
MUSICAL_EPISODES = {
    # Classic musical episodes
    "Buffy the Vampire Slayer": ["Once More, with Feeling"],
    "Scrubs": ["My Musical"],
    "Community": ["Regional Holiday Music"],
    "Psych": ["Psych: The Musical", "The Musical"],
    "Grey's Anatomy": ["Song Beneath the Song"],
    "The Flash": ["Duet"],
    "Lucifer": ["Bloody Celestial Karaoke Jam"],
    "It's Always Sunny in Philadelphia": ["The Nightman Cometh", "The Gang Turns Black"],
    "How I Met Your Mother": ["Girls Versus Suits", "Girls vs. Suits"],
    "That '70s Show": ["That '70s Musical"],
    "Fringe": ["Brown Betty"],
    "Batman: The Brave and the Bold": ["Mayhem of the Music Meister"],
    "The Simpsons": ["All Singing, All Dancing"],
    "South Park": ["Elementary School Musical"],
    "Bob's Burgers": ["Work Hard or Die Trying", "Glued, Where's My Bob"],
    "Xena: Warrior Princess": ["The Bitter Suite", "Lyre, Lyre"],
    "Riverdale": ["A Night to Remember", "Wicked Little Town", "Next to Normal"],
    "Even Stevens": ["Influenza: The Musical"],
    "7th Heaven": ["Red Socks"],
    "Daria": ["Daria!"],
    "Lexx": ["Brigadoom"],
    "The Drew Carey Show": ["Drew and Kate's Duet"],
    "Hercules: The Legendary Journeys": ["...And Fancy Free"],
    "Oz": ["Variety"],
    "Once Upon a Time": ["The Song in Your Heart"],
    "The Magicians": ["All That Josh", "A Life in the Day"],
    "Supergirl": ["Duet"],
    "Legacies": ["Salvatore: The Musical!"],
    "Supernatural": ["Fan Fiction"],
    "Chicago Hope": ["Brain Salad Surgery"],
}

# Full musical series (every episode counts)
MUSICAL_SERIES = [
    "Zoey's Extraordinary Playlist",
    "Crazy Ex-Girlfriend",
    "Flight of the Conchords",
    "Galavant",
    "Smash",
    "Glee",
    "Schmigadoon!",
    "High School Musical: The Musical: The Series",
    "Julie and the Phantoms",
    "Katy Keene",
]


def get_plex_connection(url, token):
    """Connect to Plex server."""
    try:
        return PlexServer(url, token)
    except Exception as e:
        click.echo(f"❌ Failed to connect to Plex: {e}", err=True)
        sys.exit(1)


def find_themed_content(plex, theme_name, include_movies=True, include_tv=True):
    """Find content matching a theme."""
    if theme_name not in THEMES:
        click.echo(f"❌ Unknown theme: {theme_name}", err=True)
        click.echo(f"Available themes: {', '.join(THEMES.keys())}")
        sys.exit(1)
    
    theme = THEMES[theme_name]
    keywords = theme["keywords"]
    exclude = theme["exclude"]
    
    items = []
    
    def matches_theme(title, summary):
        combined = f"{title} {summary}".lower()
        
        # Check exclusions
        for exc in exclude:
            if exc.lower() in combined:
                return False
        
        # Check keywords
        for kw in keywords:
            if kw.lower() in combined:
                return True
        
        return False
    
    # Search TV shows
    if include_tv:
        for section in plex.library.sections():
            if section.type == 'show':
                click.echo(f"  Scanning {section.title}...")
                for show in section.all():
                    for episode in show.episodes():
                        title = episode.title or ""
                        summary = episode.summary or ""
                        if matches_theme(title, summary):
                            items.append(episode)
    
    # Search movies
    if include_movies:
        for section in plex.library.sections():
            if section.type == 'movie':
                click.echo(f"  Scanning {section.title}...")
                for movie in section.all():
                    title = movie.title or ""
                    summary = movie.summary or ""
                    if matches_theme(title, summary):
                        items.append(movie)
    
    return items


def find_musical_episodes(plex):
    """Find musical episodes in the library."""
    items = []
    
    for section in plex.library.sections():
        if section.type != 'show':
            continue
        
        click.echo(f"  Scanning {section.title}...")
        
        for show in section.all():
            show_title = show.title
            
            # Check if it's a full musical series
            if show_title in MUSICAL_SERIES:
                episodes = show.episodes()
                items.extend(episodes)
                click.echo(f"    ✓ {show_title}: {len(episodes)} episodes (musical series)")
                continue
            
            # Check for specific musical episodes
            if show_title in MUSICAL_EPISODES:
                target_titles = MUSICAL_EPISODES[show_title]
                for episode in show.episodes():
                    ep_title = episode.title or ""
                    for target in target_titles:
                        if target.lower() in ep_title.lower():
                            items.append(episode)
                            click.echo(f"    ✓ {show_title} S{episode.seasonNumber}E{episode.episodeNumber}: {ep_title}")
                            break
    
    return items


def create_or_update_playlist(plex, name, items):
    """Create a new playlist or update existing one."""
    # Check for existing playlist
    existing = None
    for playlist in plex.playlists():
        if playlist.title == name:
            existing = playlist
            break
    
    if existing:
        click.echo(f"  Removing existing playlist '{name}'...")
        existing.delete()
    
    if items:
        playlist = plex.createPlaylist(name, items=items)
        return playlist
    return None


@click.group()
def cli():
    """Plex Playlist Manager - Create themed playlists from your library."""
    pass


@cli.command()
@click.option('--url', envvar='PLEX_URL', required=True, help='Plex server URL')
@click.option('--token', envvar='PLEX_TOKEN', required=True, help='Plex auth token')
@click.option('--theme', required=True, type=click.Choice(list(THEMES.keys()) + ['musical']), 
              help='Theme to create playlist for')
@click.option('--name', default=None, help='Custom playlist name (default: theme name)')
@click.option('--movies/--no-movies', default=True, help='Include movies')
@click.option('--tv/--no-tv', default=True, help='Include TV episodes')
@click.option('--dry-run', is_flag=True, help='Show what would be added without creating')
def create(url, token, theme, name, movies, tv, dry_run):
    """Create a themed playlist."""
    plex = get_plex_connection(url, token)
    
    playlist_name = name or f"{theme.title()} Episodes"
    
    click.echo(f"🔍 Searching for {theme} content...")
    
    if theme == 'musical':
        items = find_musical_episodes(plex)
    else:
        items = find_themed_content(plex, theme, include_movies=movies, include_tv=tv)
    
    if not items:
        click.echo(f"❌ No {theme} content found in your library.")
        return
    
    click.echo(f"\n📋 Found {len(items)} items:")
    for item in items[:20]:  # Show first 20
        if hasattr(item, 'grandparentTitle'):
            click.echo(f"  • {item.grandparentTitle} - {item.title}")
        else:
            click.echo(f"  • {item.title}")
    
    if len(items) > 20:
        click.echo(f"  ... and {len(items) - 20} more")
    
    if dry_run:
        click.echo(f"\n🔍 Dry run - playlist not created")
        return
    
    click.echo(f"\n📝 Creating playlist '{playlist_name}'...")
    playlist = create_or_update_playlist(plex, playlist_name, items)
    
    if playlist:
        click.echo(f"✅ Created playlist '{playlist_name}' with {len(items)} items!")
    else:
        click.echo(f"❌ Failed to create playlist")


@cli.command()
@click.option('--url', envvar='PLEX_URL', required=True, help='Plex server URL')
@click.option('--token', envvar='PLEX_TOKEN', required=True, help='Plex auth token')
def list_themes(url, token):
    """List available themes."""
    click.echo("Available themes:\n")
    for name, theme in THEMES.items():
        click.echo(f"  {name}: {theme['description']}")
    click.echo(f"  musical: Musical episodes (Buffy, Scrubs, Sunny, etc.)")


@cli.command()
@click.option('--url', envvar='PLEX_URL', required=True, help='Plex server URL')
@click.option('--token', envvar='PLEX_TOKEN', required=True, help='Plex auth token')
def list_playlists(url, token):
    """List existing playlists."""
    plex = get_plex_connection(url, token)
    
    playlists = plex.playlists()
    if not playlists:
        click.echo("No playlists found.")
        return
    
    click.echo("Playlists:\n")
    for p in playlists:
        click.echo(f"  • {p.title} ({len(p.items())} items)")


if __name__ == '__main__':
    cli()
