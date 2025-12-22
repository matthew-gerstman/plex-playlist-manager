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
}


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
    
    # Search TV episodes
    if include_tv:
        try:
            tv = plex.library.section('TV Shows')
            for show in tv.all():
                for ep in show.episodes():
                    title = ep.title or ""
                    summary = ep.summary or ""
                    if matches_theme(title, summary):
                        items.append(ep)
        except Exception:
            pass  # TV library might not exist
    
    # Search movies
    if include_movies:
        try:
            movies = plex.library.section('Movies')
            for movie in movies.all():
                title = movie.title or ""
                summary = movie.summary or ""
                if matches_theme(title, summary):
                    items.append(movie)
        except Exception:
            pass  # Movies library might not exist
    
    return items


def find_highly_rated_unwatched(plex, min_rating=8.0):
    """Find highly rated unwatched movies."""
    try:
        movies = plex.library.section('Movies')
    except Exception as e:
        click.echo(f"❌ Could not access Movies library: {e}", err=True)
        return []
    
    all_movies = movies.all()
    unwatched = [m for m in all_movies if not m.isPlayed]
    
    highly_rated = [
        m for m in unwatched
        if (m.rating or 0) >= min_rating or (m.audienceRating or 0) >= min_rating
    ]
    
    # Sort by best rating
    highly_rated.sort(
        key=lambda m: max(m.rating or 0, m.audienceRating or 0),
        reverse=True
    )
    
    return highly_rated


@click.group()
@click.option('--url', envvar='PLEX_URL', help='Plex server URL')
@click.option('--token', envvar='PLEX_TOKEN', help='Plex authentication token')
@click.pass_context
def cli(ctx, url, token):
    """Plex Playlist Manager - Create themed playlists from your library."""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['token'] = token


@cli.command()
@click.pass_context
def themes(ctx):
    """List available playlist themes."""
    click.echo("\n🎬 Available Themes:\n")
    for name, theme in THEMES.items():
        click.echo(f"  {name:12} - {theme['description']}")
    click.echo()


@cli.command()
@click.argument('theme')
@click.option('--name', '-n', help='Playlist name (defaults to theme name)')
@click.option('--tv-only', is_flag=True, help='Only include TV episodes')
@click.option('--movies-only', is_flag=True, help='Only include movies')
@click.option('--dry-run', is_flag=True, help='Show what would be added without creating')
@click.pass_context
def create(ctx, theme, name, tv_only, movies_only, dry_run):
    """Create a themed playlist."""
    url = ctx.obj.get('url')
    token = ctx.obj.get('token')
    
    if not url or not token:
        click.echo("❌ Missing Plex URL or token. Set PLEX_URL and PLEX_TOKEN env vars.", err=True)
        sys.exit(1)
    
    plex = get_plex_connection(url, token)
    
    include_movies = not tv_only
    include_tv = not movies_only
    
    click.echo(f"\n🔍 Searching for {theme} content...")
    items = find_themed_content(plex, theme, include_movies, include_tv)
    
    if not items:
        click.echo(f"❌ No {theme} content found in your library.")
        return
    
    playlist_name = name or f"{theme.title()} Episodes"
    
    click.echo(f"\n✅ Found {len(items)} items:\n")
    for item in items:
        if hasattr(item, 'seasonNumber'):
            click.echo(f"  📺 {item.grandparentTitle} - S{item.seasonNumber:02d}E{item.index:02d}: {item.title}")
        else:
            click.echo(f"  🎬 {item.title} ({item.year})")
    
    if dry_run:
        click.echo(f"\n[Dry run - playlist '{playlist_name}' not created]")
        return
    
    # Check if playlist exists
    existing = None
    for p in plex.playlists():
        if p.title == playlist_name:
            existing = p
            break
    
    if existing:
        click.confirm(f"\nPlaylist '{playlist_name}' exists. Replace it?", abort=True)
        existing.delete()
    
    playlist = plex.createPlaylist(playlist_name, items=items)
    duration_mins = sum(i.duration for i in items if i.duration) // 60000
    
    click.echo(f"\n🎉 Created '{playlist_name}' with {len(items)} items (~{duration_mins} min)")


@cli.command()
@click.option('--name', '-n', default='Highly Rated Unwatched', help='Playlist name')
@click.option('--min-rating', '-r', default=8.0, help='Minimum rating (0-10 scale)')
@click.option('--dry-run', is_flag=True, help='Show what would be added without creating')
@click.pass_context
def highly_rated(ctx, name, min_rating, dry_run):
    """Create a playlist of highly rated unwatched movies."""
    url = ctx.obj.get('url')
    token = ctx.obj.get('token')
    
    if not url or not token:
        click.echo("❌ Missing Plex URL or token. Set PLEX_URL and PLEX_TOKEN env vars.", err=True)
        sys.exit(1)
    
    plex = get_plex_connection(url, token)
    
    click.echo(f"\n🔍 Finding unwatched movies rated {min_rating}+ ...")
    items = find_highly_rated_unwatched(plex, min_rating)
    
    if not items:
        click.echo("❌ No matching movies found.")
        return
    
    click.echo(f"\n✅ Found {len(items)} movies:\n")
    for m in items[:20]:  # Show first 20
        rating = max(m.rating or 0, m.audienceRating or 0)
        click.echo(f"  {rating:.1f} - {m.title} ({m.year})")
    
    if len(items) > 20:
        click.echo(f"  ... and {len(items) - 20} more")
    
    if dry_run:
        click.echo(f"\n[Dry run - playlist '{name}' not created]")
        return
    
    # Check if playlist exists
    existing = None
    for p in plex.playlists():
        if p.title == name:
            existing = p
            break
    
    if existing:
        click.confirm(f"\nPlaylist '{name}' exists. Replace it?", abort=True)
        existing.delete()
    
    playlist = plex.createPlaylist(name, items=items)
    duration_hrs = sum(i.duration for i in items if i.duration) // 3600000
    
    click.echo(f"\n🎉 Created '{name}' with {len(items)} movies (~{duration_hrs} hours)")


@cli.command('list')
@click.pass_context
def list_playlists(ctx):
    """List all playlists on your Plex server."""
    url = ctx.obj.get('url')
    token = ctx.obj.get('token')
    
    if not url or not token:
        click.echo("❌ Missing Plex URL or token. Set PLEX_URL and PLEX_TOKEN env vars.", err=True)
        sys.exit(1)
    
    plex = get_plex_connection(url, token)
    playlists = plex.playlists()
    
    if not playlists:
        click.echo("\nNo playlists found.")
        return
    
    click.echo(f"\n📋 Found {len(playlists)} playlists:\n")
    for p in playlists:
        smart = "⚡" if p.smart else "📝"
        duration = p.duration // 60000 if p.duration else 0
        click.echo(f"  {smart} {p.title} ({len(p.items())} items, ~{duration} min)")


@cli.command()
@click.argument('name')
@click.pass_context
def delete(ctx, name):
    """Delete a playlist."""
    url = ctx.obj.get('url')
    token = ctx.obj.get('token')
    
    if not url or not token:
        click.echo("❌ Missing Plex URL or token. Set PLEX_URL and PLEX_TOKEN env vars.", err=True)
        sys.exit(1)
    
    plex = get_plex_connection(url, token)
    
    try:
        playlist = plex.playlist(name)
    except Exception:
        click.echo(f"❌ Playlist '{name}' not found.", err=True)
        sys.exit(1)
    
    click.confirm(f"Delete playlist '{name}'?", abort=True)
    playlist.delete()
    click.echo(f"✅ Deleted '{name}'")


if __name__ == '__main__':
    cli()
