# TrainerTournament

Please note that the wiki, sprite, pkl, and json folders are intentionally empty.

# Usage

Ensure that the pip packages `mwparserfromhell` and `bs4` are installed
Place Bulbapedia articles (Wikicode only) in the `wiki` folder. (Optional)
Run the script, pointing to the location of a wikicode file containing trainer data.
The script will automatically parse out trainer data, and dump trainer information to the console as well as to a .pkl file in the `pkl` directory.
The script will also download any trainer sprites from the article (Pokemon and item sprites are not downloaded, although the script could be modified to support this fairly easily)