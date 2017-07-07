# NFGame, a simple FNC game

## Installation

### Requirements
The next software is needed to run this game:

- Python 2.6 or higher OR
- Python 3.3 or higher
- Flask  0.11 or higher
- Twisted

You can install this as root by doing the following:

- Debian: apt-get install python-flask python-twisted
- FreeBSD: pkg install py27-Flask py27-twisted
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
Please change the password!

    cp nfgame.cfg-example nfgame.cfg

## Running the game
    ./run.sh start

## URL's in the game
The site is running on http://1.2.3.4:5000

These are all the URL's used in the game:
| URL                | Description                                           |
|--------------------|-------------------------------------------------------|
| /                  | Switch between the scoreboard and the highscores page |
| /scoreboard        | Show the scoreboard                                   |
| /highscores        | Show the highscores                                   |
| /newuser           | Make a new user                                       |
| /newuser/<hash>    | Make a new user. A hash is needed                     |
| /tag/<hash>        | Find a tag and register it on your name               |
| /admin/<password>  | Admin page                                            |

## Debug mode
You can enable the debug mode by running:

    ./run.sh start debug

## Ending the game

    ./run.sh stop
