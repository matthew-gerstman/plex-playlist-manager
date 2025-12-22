from setuptools import setup

setup(
    name='plex-playlist-manager',
    version='1.0.0',
    py_modules=['plex_playlist'],
    install_requires=[
        'plexapi>=4.15.0',
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'plex-playlist=plex_playlist:cli',
        ],
    },
    author='Matthew Gerstman',
    description='Create themed playlists from your Plex library',
    python_requires='>=3.8',
)
