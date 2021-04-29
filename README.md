# Usage
0. Install the Python library "mwparserfromhell".  This is required to parse the wikicode
1. Create empty folders in the root of the project called "pkl", "wiki", "json", "sprites", "out" and "location"
2. Put wikicode for Bulbapedia articles in the "wiki" directory
3. Use `parseBulbapedia.py` inside a bash for loop to parse all files in the "wiki" directory
4. Create the directories "trainer" and "pokemon" inside the `pkl` directory
5. Move `*.trainer.pkl` to the `trainer` directory, and `*.pokemon.pkl` to the `pokemon` directory


Once articles are parsed, use
`{ while read region game; do python parseData.py $region $game > out/$region-$game; done } < locationList`
to generate CSV files in the `out` directory