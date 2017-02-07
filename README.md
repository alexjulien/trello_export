# trello_export
Export Trello JSON files to Markdown

This simple script converts a Trello board JSON export to:

1. A folder for the board with
2. A subfolder for each list with
3. A subfolder per card with
4. An index.md file per card, containing its description and comments and links to
5. Each attachment for the card. Images appear as embedded images in the markdown file.

My Python version is 3.5.2. No external modules used. If anyone needs Python 2, the conversion shouldn't be that hard, I guess.

MIT license here, so use it as you please, but a little credit would be nice.

## Usage:

Export your board to json (board > menu > more > print and export > export to JSON), saving it in the same folder as this script and then

`$ python trello_export.py <filename.json>`

Nothing to configure, no argument validation; quick and dirty.

## Motivation

Evernote, OneNote, Simplenote, and of course, Trello. And then some. My organization/note-taking/productivity system has been there, done that, tried those... My current endeavor involves Markdown because, well, it's cool and all the rage. Well, of course there's more to it, and I'm tempted to write some blog posts about it, or something. But right now, I just want to release this.

Anyhow, I wanted to export all of my Trello boards into Markdown. This is the result of my efforts. It does the trick for my needs. Maybe you'll find it useful too. I'll be glad to receive comments, forks, bug reports, ideas and whatnot.

Welcome.
