# NFGame, a simple FNC game

## Installation

### Requirements
The next software is needed to run this game:

- Python 2.6 or higher OR
- Python 3.3 or higher
- Flask  0.11 or higher

You can install this as root by doing the following:

- Debian: apt-get install python-flask
- FreeBSD: pkg install py27-Flask
- pip: pip install Flask

Watch out! Raspbian has an old version of flask! (0.10) A raspberry is perfect
for running this game, but install pip and use pip to install Flask.

    apt-get install python-pip
    pip install Flask

### Getting the software
Just clone the software from github:

    git clone https://github.com/sciuro/nfgame.git

### Updating the software
You can always update the software by running:

    git pull

### Configure the software
Copy the file nfgame.cfg-example to nfgame.cfg and edit to your preferences.

    cp nfgame.cfg-example nfgame.cfg

## Running the game
    ./run.sh

The site is running on http://1.2.3.4:5000

## Debug mode
You can enable the debug mode by running:

    ./run.sh debug
