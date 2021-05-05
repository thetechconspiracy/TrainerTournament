import os
import sys
import re
import mwparserfromhell
from bs4 import BeautifulSoup
import requests
import pickle
import json
import random
import os.path
import traceback

if(len(sys.argv) < 2):
    print("Usage: parseBulbapedia.py <wiki page from local drive>\n--force-parse: Parse the entire file, don't check for the Trainers section of the article")
    exit()

class Trainer:
    def __init__(self, tSprite, tClass, tName, tMoney, tPokeCount, tLocation="", tRegion="", tGame=""):
        self.tSprite = tSprite
        self.tClass = tClass
        self.tName = tName
        #For B2W2 trainers, do extra work to parse money info
        try:
            if(tMoney[0] == '{'):
                #print(tMoney[0])
                levelCode = mwparserfromhell.parse(tMoney)
                levelTemplates = levelCode.filter_templates()
                levelTemplate = levelTemplates[0]
                parsedLevel = levelTemplate.get(1).value
                self.tMoney = parsedLevel
            else:
                self.tMoney = tMoney
        except:
            self.tMoney = 0
        self.tPokeCount = tPokeCount
        self.tLocation = tLocation
        self.tRegion = tRegion
        self.tGame = tGame
        self.tPokes = []

        self.tSprite = self.tSprite.replace("{{!}}70px","")
        self.tSprite = self.tSprite.replace("{{!}}90px","")
        self.tSprite = self.tSprite.replace("{{!}}100px","")
        self.tSprite = self.tSprite.replace("{{!}}150px","")
        self.tSprite = self.tSprite.replace("{{!}}170px","")

        self.bossFlag = False
        
        getTrainerSprite(self.tSprite)
        self.findGameFromSprite()
    def __str__(self):
        list = self.getList()
        output = ""
        for line in list:
            output += str(line)
            output += '\n'
        return output

    def makeShowdown(self):
        outStr = ""
        for poke in self.tPokes:
            if(type(poke) == FinishedPokemon):
                outStr += poke.makeShowdown() + "\r\n"
            else:
                print("Not a finished Pokemon!")
        return outStr

    def findGameFromSprite(self):
        sprName = self.tSprite.replace("_"," ")
        if " RG " in sprName or " RB " in sprName:
            self.tGame = "RGB"
            self.tLongGame = "red-blue"
        elif " Y " in sprName:
            self.tGame = "Y"
            self.tLongGame = "yellow"
        elif " GS " in sprName or " GSC " in sprName:
            self.tGame = "GS"
            self.tLongGame = "gold-silver"
        elif " C " in sprName:
            self.tGame = "C"
            self.tLongGame = "crystal"
        elif " RS " in sprName or " RSE " in sprName:
            self.tGame = "RS"
            self.tLongGame = "ruby-sapphire"
        elif " E " in sprName:
            self.tGame = "E"
            self.tLongGame = "emerald"
        elif " FRLG " in sprName:
            self.tGame = "FRLG"
            self.tLongGame = "firered-leafgreen"
        elif " DP " in sprName or " DPPt " in sprName:
            self.tGame = "DP"
            self.tLongGame = "diamond-pearl"
        elif " Pt " in sprName:
            self.tGame = "Pt"
            self.tLongGame = "platinum"
        elif " HGSS " in sprName:
            self.tGame = "HGSS"
            self.tLongGame = "heartgold-soulsilver"
        elif " BW " in sprName:
            self.tGame = "BW"
            self.tLongGame = "black-white"
        elif " B2W2 " in sprName:
            self.tGame = "B2W2"
            self.tLongGame = "black-2-white-2"
        elif " XY " in sprName:
            self.tGame = "XY"
            self.tLongGame = "x-y"
        elif " ORAS " in sprName:
            self.tGame = "ORAS"
            self.tLongGame = "omega-ruby-alpha-sapphire"
        elif " SM " in sprName or " USUM " in sprName:
            self.tGame = "SM"
            self.tLongGame = "sun-moon"
        elif " LGPE " in sprName or " PE "  in sprName or " PE." in sprName:
            self.tGame = "LGPE"
            self.tLongGame = "sun-moon"
        elif " SwSh " in sprName:
            self.tGame = "SwSh"
        else:
            #Manually determine game
            found = False
            for sprite in lookupTable:
                result = sprite.lookup(sprName)
                if(result != False):
                    found = True
                    self.tGame = result
                    self.tLongGame = self.getLongGame(self.tGame)
            if not found:
                print("Game undetermined")
                print("Sprite Name: " + sprName)
                print("Enter game acronym:")
                self.tGame = "SM"
                lookupTable.append(manualSpriteLookup(sprName, self.tGame))
                self.tLongGame = self.getLongGame(self.tGame)
    def getLongGame(self, short):
            sprName = short
            if "RG" in sprName or "RB" in sprName:
                # self.tGame = "RGB"
                return "red-blue"
            elif "Y" in sprName:
                # self.tGame = "Y"
                return "yellow"
            elif "GS" in sprName or "GSC" in sprName:
                # self.tGame = "GS"
                return "gold-silver"
            elif "C" in sprName:
                # self.tGame = "C"
                return "crystal"
            elif "RS" in sprName or "RSE" in sprName:
                # self.tGame = "RS"
                return "ruby-sapphire"
            elif "E" in sprName and "P" not in sprName:
                # self.tGame = "E"
                return "emerald"
            elif "FRLG" in sprName:
                # self.tGame = "FRLG"
                return "firered-leafgreen"
            elif "DP" in sprName or "DPPt" in sprName:
                # self.tGame = "DP"
                return "diamond-pearl"
            elif "Pt" in sprName:
                # self.tGame = "Pt"
                return "platinum"
            elif "HGSS" in sprName:
                # self.tGame = "HGSS"
                return "heartgold-soulsilver"
            elif "BW" in sprName:
                # self.tGame = "BW"
                return "black-white"
            elif "B2W2" in sprName:
                # self.tGame = "B2W2"
                return "black-2-white-2"
            elif "XY" in sprName:
                # self.tGame = "XY"
                return "x-y"
            elif "ORAS" in sprName:
                # self.tGame = "ORAS"
                return "omega-ruby-alpha-sapphire"
            elif "SM" in sprName or "USUM" in sprName or "LGPE"  in sprName or "PE"  in sprName or "PE." in sprName:
                # self.tGame = "SM"
                return "sun-moon"

    def printName(self):
        print(self.tName)
    def printSelf(self):
        list = self.getList()
        for line in list:
            print(line)
        print('\n')
    def getList(self):
        return [self.tSprite, self.tClass, self.tName, self.tMoney, self.tPokeCount, self.tLocation, self.tRegion, self.tGame, self.tLongGame, self.tPokes]
    def getPokes(self):
        return self.tPokes
    def addPoke(self, poke):
        self.tPokes.append(poke)
        #if(len(int(self.tPokes[0]) > 6)):
        #    print("***************************************************")
        #    print("*            POKEMON COUNT EXCEEDS 6!             *")
        #    print("***************************************************")
    def isBoss(self):
        self.bossFlag = True

class manualSpriteLookup:
    def __init__(self, sprName, originGame):
        self.sprName = sprName
        self.originGame = originGame
    def lookup(self, sprName):
        if self.sprName == sprName:
            return self.originGame
        else:
            return False
    def __str__(self):
        #Returns a CSV line
        return self.sprName + "," + self.originGame + "\n"

class BasicPokemon:
    def __init__(self, pDexNo, pSpecies, pGender, pLevel, pHold = ""):
        self.pDexNo = pDexNo
        self.pSpecies = pSpecies
        #Determine gender
        self.pGender = ''
        if(pGender == ''):
            self.pGender = 'U'
        if(pGender == '♀' or pGender.upper() == 'F'):
            self.pGender = 'F'
        if(pGender == '♂' or pGender.upper() == 'M'):
            self.pGender = 'M'
        #For B2W2 trainers, do extra work to parse level info
        if(pLevel[0] == '{'):
            levelCode = mwparserfromhell.parse(pLevel)
            levelTemplates = levelCode.filter_templates()
            levelTemplate = levelTemplates[0]
            parsedLevel = levelTemplate.get(1).value
            self.pLevel = str(parsedLevel)
        else:
            self.pLevel = pLevel
        self.pHold = pHold

    def __str__(self):
        return str(self.pDexNo) + "," + str(self.pSpecies) + "," + str(self.pGender) + "," + str(self.pLevel) + "," + str(self.pHold)
    def __repr__(self):
        return str(self)

    def makeFinishedPoke(self, gameID):
        jsonCode = ""
        try:
            jsonCode = getJSON(self.pSpecies)
        except:
            #JSON error.  Put error handling info on, and move on.  Probably don't need this anymore, since the project changed.
            pMoves = []
            pMoves.append("Splash")
            pAbility = ("Run Away")
            return FinishedPokemon(self.pDexNo, self.pSpecies, self.pGender, self.pLevel, pMoves, self.pHold, pAbility)
        #print(self.pSpecies)
        #lastPoke += self.pSpecies

        if self.pSpecies == "Mr. Mime": #Mr. Mime causes issues once again.  Hardcode a solution.
            jsonCode = getJSON("mr-mime")
        if self.pSpecies == "Nidoran♂":
            jsonCode = getJSON("nidoran-m")
        if self.pSpecies == "Nidoran♀":
            jsonCode = getJSON("nidoran-f")
        if self.pSpecies == "Farfetch'd":
            jsonCode = getJSON("farfetchd")
        #print(jsonCode)
        parsed = json.loads(jsonCode)
        abilityChoices = []
        for ability in parsed["abilities"]:
            #parsedAbility = json.loads(ability)
            #print(ability)
            if not ability['is_hidden']:
                #Don't want to give hidden abilities
                abilityChoices.append(ability["ability"]["name"])
        #Randomly choose an ability
        pAbility = random.choice(abilityChoices)

        #Find moves
        #Assume PokeAPI is already sorted
        pMoves = []
        for move in parsed["moves"]:
            #if move["version_group_details"]["version_group"] == gameID:
                #print(move)
            for moveVer in (move["version_group_details"]):
                if moveVer["level_learned_at"] != 0:
                    if moveVer["version_group"]["name"] == gameID:
                        pMoves.append(move["move"]["name"])
        pMoves = pMoves[-4:]
        #print(pMoves)

        return FinishedPokemon(self.pDexNo, self.pSpecies, self.pGender, self.pLevel, pMoves, self.pHold, pAbility)

class FinishedPokemon:
    def __init__(self, pDexNo, pSpecies, pGender, pLevel, pMoves = [], pHold = "", pAbility = ""):
        self.pDexNo = pDexNo
        self.pSpecies = pSpecies
        #Determine gender
        #print(pGender)
        if(pGender == ''):
            self.pGender = 'U'
        elif(pGender == '♀'):
            self.pGender = 'F'
        elif(pGender == '♂'):
            self.pGender = 'M'
        else:
            self.pGender = ''

        if(pGender == 'M' or pGender == 'F' or pGender == 'U'):
            #Gender is already set normally
            self.pGender = pGender
        #For B2W2 trainers, do extra work to parse level info
        if(pLevel[0] == '{'):
            levelCode = mwparserfromhell.parse(pLevel)
            levelTemplates = levelCode.filter_templates()
            levelTemplate = levelTemplates[0]
            parsedLevel = levelTemplate.get(1).value
            self.pLevel = parsedLevel
        else:
            self.pLevel = pLevel
        self.pMoves = pMoves
        self.pHold = pHold
        self.pAbility = pAbility

    def __str__(self):
        return str(self.pDexNo) + "," + str(self.pSpecies) + "," + str(self.pGender) + "," + str(self.pLevel) + "," + str(self.pMoves) + "," + str(self.pHold) + "," + str(self.pAbility)
    def __repr__(self):
        return str(self)
    
    def makeShowdown(self):
        outStr = ""
        if(self.pGender == 'U'):
            outStr += self.pSpecies + " @ " + self.pHold + "\r\n"
        else:
            outStr += self.pSpecies +" (" + self.pGender + ")"
            if(self.pHold == ""):
                outStr += "\r\n"
            else:
                outStr += " @ " + self.pHold + "\r\n"
        outStr += "Ability: " + self.pAbility + "\r\n"
        outStr += "Level: " + self.pLevel + "\r\n"
        outStr += "EVs: 1 HP / 1 Atk / 1 Def / 1 SpA / 1 SpD / 1 Spe  \r\n"
        for move in self.pMoves:
            outStr += "- " + move + "\r\n"
        return outStr
class WildPokemon:
    def __init__(self, pDexNo, pSpecies, pGames, pArea, pMinLevel, pMaxLevel, pRate):
        self.pDexNo = pDexNo
        self.pSpecies = pSpecies
        self.pGames = pGames
        self.pArea = pArea
        self.pMinLevel = pMinLevel
        self.pMaxLevel = pMaxLevel
        self.pRate = pRate
    
    def __str__(self):
        return (self.pDexNo + " " + self.pSpecies + " " + self.pGames +  " " + self.pArea + " " + self.pMinLevel + " " + self.pMaxLevel + " " + self.pRate)


def getJSON(pokeName):
    pokeName = pokeName.lower()
    #Search local cache
    for file in os.listdir("json"):
        if(file == (pokeName + ".json")):
            retFile = open("json/" + file, "r")
            retStr = ""
            for line in retFile:
                retStr += line
            retFile.close()
            return retStr
    #Not found, download the JSON file from PokeAPI
    URL = "https://pokeapi.co/api/v2/pokemon/"+pokeName
    jsonCode=requests.get(URL).content
    with open("json/" + pokeName + ".json", 'wb') as file:
        file.write(jsonCode)
    return jsonCode.decode("utf-8")

def findPokeList():
    foundPokes = False
    pokeLines = []
    for line in wikiPage:
        #print(line)
        pokeLines.append(line.strip())

        #if(foundPokes):
        #    if(line.strip() == "==Trainers==" or line.strip() == "===Trainers==="):
        #        foundPokes = False
        #        break
        #    if(endHeader.match(line)):
        #       foundPokes = False
        #       break
        #    else:
        #        pokeLines.append(line.strip())
        #else:
        #   if(line.replace(' ','').rstrip() == "==Pokémon=="):
        #       foundPokes = True
        
    return pokeLines

def parsePokemon(pokeList):
    #Use Catch/entryx to determine how to parse game list (some have 2, some 3, some only 1)
    for entry in pokeList:
        wikicode = mwparserfromhell.parse(entry)
        templates = wikicode.filter_templates()
        template = ""
        try:
            template = templates[0]
        except:
            #Nothing on this line that we can work with.  Do nothing.
            continue
        #Figure out what generation we are dealing with
            #entry1: RBY
                #Don't worry about Japanese Blue, it seems Bulbapedia doesn't mention it in encounter data.  wiki.ポケモン.com does, but we aren't scraping them, are we?
            #entry2: GSC
            #entry3: RSE
            #entryfl: FRLG
            #entry4: DPPt
            #entryhg: HGSS
            #entry5: BWG?  Third entry likely is supposed to reflect Gray, which never happened.
            #entry5-2: B2W2
            #entry6: XY
            #entryoras: ORAS
            #entry7: SM
            #entryusum: USUM
            #entrype: LGPE
            #entry8: SwSh
        if not "entry" in str(template.name):
            continue
        splitHeader = str(template.name).split("/")
        header = ""
        if len(splitHeader) > 1 and "entry" in splitHeader[1]:
            header = splitHeader[1].replace("entry","")
        else:
            #Not a Pokemon line, skip it
            continue
        
        #Extract Pokemon info.  Changes depending on the generation.
        if(header == "1"):
            #Parse Gen 1
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(6))
            levels = str(template.get(7))
            rate = str(template.get(8)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("R,")
            if(template.get(4).lower() == "yes"):
                games += ("B,")
            if(template.get(5).lower() == "yes"):
                games += ("Y,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "2"):
            #Parse Gen 2
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(6))
            levels = str(template.get(7))
            rate = ""

            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Day, evening, and night
                #Don't know what to do here, honestly.  Just take the highest
                day = int(str(template.get(8)).replace("%",""))
                eve = int(str(template.get(9)).replace("%",""))
                night = int(str(template.get(10)).replace("%",""))

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.
                if largest < night:
                    largest = night
                rate = str(largest) 
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("G,")
            if(template.get(4).lower() == "yes"):
                games += ("S,")
            if(template.get(5).lower() == "yes"):
                games += ("C,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]
                    
            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "3"):
            #Parse Gen 3
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(6))
            levels = str(template.get(7))
            rate = str(template.get(8)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("Ru,")
            if(template.get(4).lower() == "yes"):
                games += ("S,")
            if(template.get(5).lower() == "yes"):
                games += ("E,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "fl"):
            #Parse FRLG
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = str(template.get(7)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("FR,")
            if(template.get(4).lower() == "yes"):
                games += ("LG,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "4"):
            #Parse Gen 4
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(6))
            levels = str(template.get(7))
            rate = ""

            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Day, evening, and night
                #Don't know what to do here, honestly.  Just take the highest
                day = int(str(template.get(8)).replace("%",""))
                eve = int(str(template.get(9)).replace("%",""))
                night = int(str(template.get(10)).replace("%",""))

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.
                if largest < night:
                    largest = night
                rate = str(largest) 
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("D,")
            if(template.get(4).lower() == "yes"):
                games += ("P,")
            if(template.get(5).lower() == "yes"):
                games += ("Pt,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]
                    
            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "hs"):
            #Parse HGSS (the worst games)
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = ""

            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Day, evening, and night
                #Don't know what to do here, honestly.  Just take the highest
                day = int(str(template.get(7)).replace("%",""))
                eve = int(str(template.get(8)).replace("%",""))
                night = int(str(template.get(9)).replace("%",""))

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.
                if largest < night:
                    largest = night
                rate = str(largest) 
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("HG,")
            if(template.get(4).lower() == "yes"):
                games += ("SS,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]
                    
            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "5"):
            #Parse Gen 5
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(6))
            levels = str(template.get(7))
            rate = ""

            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Seasons.  Ignore the names, the names lie.
                #Don't know what to do here, honestly.  Just take the highest
                if(template.get(8).replace("%","").isdecimal()):
                    day = int(str(template.get(8)).replace("%",""))
                else:
                    day = 0
                if(template.get(9).replace("%","").isdecimal()):
                    eve = int(str(template.get(9)).replace("%",""))
                else:
                    eve = 0
                if(template.get(10).replace("%","").isdecimal()):
                    night = int(str(template.get(10)).replace("%",""))
                else:
                    night = 0
                if(template.get(11).replace("%","").isdecimal()):
                    winter = int(str(template.get(11)).replace("%",""))
                else:
                    winter = 0

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                largest2 = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.
                if(night > winter):
                    largest2 = night
                else:
                    largest2 = winter
                
                if(largest < largest2):
                    largest = largest2
                #No need for an else, we use largest as the winner
                rate = str(largest)
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("B,")
            if(template.get(4).lower() == "yes"):
                games += ("W,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]
                    
            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "5-2"):
            #Parse Gen 5
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = ""

            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Seasons.  Ignore the names, the names lie.
                #Don't know what to do here, honestly.  Just take the highest
                if(template.get(8).replace("%","").isdecimal()):
                    day = int(str(template.get(8)).replace("%",""))
                else:
                    day = 0
                if(template.get(9).replace("%","").isdecimal()):
                    eve = int(str(template.get(9)).replace("%",""))
                else:
                    eve = 0
                if(template.get(10).replace("%","").isdecimal()):
                    night = int(str(template.get(10)).replace("%",""))
                else:
                    night = 0
                if(template.get(7).replace("%","").isdecimal()):
                    winter = int(str(template.get(7)).replace("%",""))
                else:
                    winter = 0

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                largest2 = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.
                if(night > winter):
                    largest2 = night
                else:
                    largest2 = winter
                
                if(largest < largest2):
                    largest = largest2
                #No need for an else, we use largest as the winner
                rate = str(largest)
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("B2,")
            if(template.get(4).lower() == "yes"):
                games += ("W2,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]
                    
            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "6"):
            #Parse XY
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = str(template.get(7)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("X,")
            if(template.get(4).lower() == "yes"):
                games += ("Y,")
            




            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "oras"):
            #Parse ORAS
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = str(template.get(7)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("OR,")
            if(template.get(4).lower() == "yes"):
                games += ("AS,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "7"):
            #Parse SM
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = ""
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("Su,")
            if(template.get(4).lower() == "yes"):
                games += ("M,")
            
            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Day, evening, and night
                #Don't know what to do here, honestly.  Just take the highest
                if(str(template.get(7)).replace("%","").isdecimal()):
                    day = int(str(template.get(7)).replace("%",""))
                else:
                    day = 0
                if(str(template.get(8)).replace("%","").isdecimal()):
                    eve = int(str(template.get(8)).replace("%",""))
                else:
                    night = 0

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.

                rate = str(largest) 

            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "usum"):
            #Parse SM
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = ""
            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("US,")
            if(template.get(4).lower() == "yes"):
                games += ("UM,")
            
            try:
                rate = str(template.get("all")).replace("%","").replace("all=","")
            except ValueError:
                #Day, evening, and night
                #Don't know what to do here, honestly.  Just take the highest
                if(str(template.get(7)).replace("%","").isdecimal()):
                    day = int(str(template.get(7)).replace("%",""))
                else:
                    day = 0
                if(str(template.get(8)).replace("%","").isdecimal()):
                    eve = int(str(template.get(8)).replace("%",""))
                else:
                    night = 0

                #Find the largest of the 3.  Sounds like a fun problem to solve
                largest = 0
                if (day > eve):
                    largest = day
                else:
                    largest = eve #This also triggers in the event of a tie.

                rate = str(largest) 

            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

        if(header == "pe"):
            #Parse Lets Go Pikachu/Eevee
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            rate = str(template.get(7)).replace("%","")

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("Pi,")
            if(template.get(4).lower() == "yes"):
                games += ("Ev,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))
        
        if(header == "8"):
            #Parse SwSh
            dexNo = str(template.get(1))
            species = str(template.get(2))
            games = ""
            area = str(template.get(5))
            levels = str(template.get(6))
            try:
                rate = str(template.get(7)).replace("%","")
            except:
                rate = "0"#Weather.  Don't bother, just ignore.  Probably won't use this anyway

            #Parse games
            if(template.get(3).lower() == "yes"):
                games += ("Sw,")
            if(template.get(4).lower() == "yes"):
                games += ("Sh,")
            
            minRate = ""
            maxRate = ""
            #Parse levels
            levelRange = levels.split(", ")
            if(len(levelRange) == 1):
                if not "-" in levelRange[0]:
                    minRate = maxRate = levelRange[0]
                else:
                    levelRange = levelRange[0].split("-")
                    minRate = levelRange[0]
                    maxRate = levelRange[1]
            else:
                #Look at start to find minimum level
                if not "-" in levelRange[0]:
                    minRate  = levelRange[0]
                else:
                    levelRangeSub = levelRange[0].split("-")
                    minRate = levelRangeSub[0]

                #Look at end to find max level
                index = len(levelRange) - 1
                if not "-" in levelRange[index]:
                    maxRate  = levelRange[index]
                else:
                    levelRangeSub = levelRange[index].split("-")
                    maxRate = levelRangeSub[index]

            parsedWilds.append(WildPokemon(dexNo, species, games, area, minRate, maxRate, rate))

    for poke in parsedWilds:
        if not poke.pRate.isdecimal():
            poke.pRate = str(0) #Encouter rate is weird.  Probably a special encounter, so just set to 0%
            #I believe roaming legendaries have a 100% encounter rate when on a route
        while not poke.pDexNo.isdecimal():
            #Alternate forms specify a letter after the dex no.  Remove it, so we can work as an int.  Form changes are purely cosmetic.  In a while loop so we can handle multiple letters.
            poke.pDexNo = poke.pDexNo[:-1]

            


def findTrainerList():
    forceParse = True
    foundTrainers = True # We know where trainers are, but the header is likely missing.
    bossTrainer = False
    bossLine = ""
    splitLine = False
    trainerLines = []
    for line in wikiPage:
        if(foundTrainers):
            if(bossTrainer):
                if(line.strip() == "{{Party/Footer}}"):
                    bossTrainer = False
                    bossLine += line.strip()
                    trainerLines.append(bossLine)
                    bossLine = ""
                cleanLine = line.strip()
                cleanLine = line.strip("\r")
                cleanLine = line.strip("\n")
                #print(repr(cleanLine))
                if(bossTrainer):
                    #Verify that we aren't at the end of the trainer
                    bossLine += (cleanLine)
                #trainerLines.append(line)
            #elif splitLine and not bossTrainer:
            #    print("Not boss, but split")
            #    bossLine += line.strip()
            #    bossLine = bossLine.strip("\r")
            #    bossLine = bossLine.strip("\n")
            #    if(bossLine[-1] == '}'):
            #        print("found end")
            #        trainerLines.append(bossLine)
            #        bossLine = ""
            #        splitLine = False
            else:
                if(line[0] == '='):
                    line = line.strip()
                    line.replace(' ', '')
                    if(endHeader.match(line) and not forceParse):
                        foundTrainers = False
                        break
                    if("side series" in line.lower()):
                        foundTrainers = False
                        break
                if line.strip(): #https://stackoverflow.com/questions/7896495/python-how-to-check-if-a-line-is-an-empty-line
                    if "{{Party/Single" in line:
                        bossTrainer = True
                        bossLine += (line.strip())
                        #trainerLines.append(line.strip())
                    else:
                        cleanLine = line.strip()
                        cleanLine = cleanLine.strip("\r")
                        cleanline = cleanLine.strip("\n")
                        #if cleanLine[-1] != '}':
                        #    #Split line
                        #    splitLine = True
                        #    bossLine = cleanLine
                        cleanLine = cleanLine.replace("\r", "")
                        cleanLine = cleanLine.replace("\n", "")
                        if not splitLine:
                            trainerLines.append(cleanLine)
        else:
            #print(line)
            line = line.rstrip()
            line.replace(' ','') #Remove any extra spaces
            if(line == "==Trainers==" or line == "===Trainers==="):
                print("Trainer list found")
                foundTrainers = True
    return trainerLines

def findRegularTrainers(trainerList):
    game = ""
    for line in trainerList:
        try:
            if(line[0] == '='):
                #Header
                game = line
                continue
            #print(line)

            if("Trainerentry" in line or "trainerentry" in line.lower()):
                wikicode = mwparserfromhell.parse(line)
                templates = wikicode.filter_templates()
                template = templates[0]
                #Found trainer, parse them out
                trainerSprite = str(template.get(1).value)
                trainerClass = str(template.get(2).value)
                trainerName = str(template.get(3).value)
                trainerMoney = str(template.get(4).value)
                trainerPokeCount = str(template.get(5).value)
                #Iterate through Pokemon list, parse Pokes and create objects
                tempTrainer = Trainer(trainerSprite, trainerClass, trainerName, trainerMoney, trainerPokeCount, location, region, game)
                offset = 6

                try:
                    int(trainerPokeCount[0])
                except:
                    return

                for i in range(0,int(trainerPokeCount[0])):
                    #print(template)
                    #print("Offset "+str(offset))
                    pokeDexNo = str(template.get(offset + 0).value)
                    pokeSpecies = str(template.get(offset + 1).value)
                    pokeGender = str(template.get(offset + 2).value)
                    pokeLevel = str(template.get(offset + 3).value)
                    try:
                        pokeItem = str(template.get(offset + 4))
                    except ValueError:
                        pokeItem = ""
                    if(pokeItem.lower() == "none"):
                        pokeItem = ""
                    #print(tempTrainer.tGame)
                    #print(pokeSpecies)
                    try:
                        tempTrainer.addPoke(BasicPokemon(pokeDexNo,pokeSpecies,pokeGender,pokeLevel).makeFinishedPoke(tempTrainer.tLongGame))
                    except:
                        print("Failure parsing trainer " + trainerClass + " " + trainerName + " in " + sys.argv[1])
                        traceback.print_exc
                        break
                    offset += 5 # 5 fields make up Pokemon data
                #tempTrainer.printSelf()
                parsedTrainers.append(tempTrainer)
            if("Rematch" in line):
                break
        except:
            pass


def findBossTrainers(trainerList):
    foundTrainer = False

    tSprite = ""
    tClass = ""
    tMoney = 0
    tName = ""
    tPokeCount = 0
    tRegion = region
    tGame = ""
    tLocation = location
    tPokes = []
    '''for line in trainerList:
        #print(line)
        if(line[0] == '='):
            continue
        if "{{Party/Single" in line:
            #Boss Trainer
            print("Found boss")
            foundTrainer = True
        if(foundTrainer):
            #print(line)
            if(line.strip() == "{{Party/Footer}}"):
                foundTrainer = False
                print("Sprite: " + tSprite)
                print(tClass)
                print(tMoney)
                #Finalize boss
            if "sprite=" in line:
                tSprite = line[8:].strip()
            if "|prize={{PDollar}}" in line:
                tMoney = line[18:].strip()
            if "|class=" in line:
                if"{{PK}}{{MN}}" in line:
                    line = line.replace("{{PK}}{{MN}}", "Pokemon")
                tClass = line[7:].strip()
            if "|game=" in line:
                tGame = line[6:].strip()
        #print(",")'''
    for line in trainerList:
        try:
            if "Party/Single" in line:
                tempTrainer = ""
                wikicode = mwparserfromhell.parse(line)
                templates = wikicode.filter_templates()
                for template in templates:
                    #print(template)
                    if template.name == "Party/Single":
                        tSprite = str(template.get("sprite").value)
                        try:
                            tClass = str(template.get("class").value)
                        except:
                            tClass = "Leader"
                        tMoney = str(template.get("prize").value) # Will require further parsing later, contains special character, plus B2W2 weirdness
                        tName = str(template.get("name").value) # More parsing required to get proper name
                        tPokeCount = int(str(template.get("pokemon").value))
                        tGame = str(template.get("game").value)

                        #Additional formatting
                        tMoney = tMoney.lower()
                        tMoney = tMoney.replace("{{pdollar}}","")
                        ##Name
                        try:
                            nameCode = mwparserfromhell.parse(tName)
                            nameTemps = nameCode.filter_templates()
                            nameTemp = nameTemps[0]
                            tName = str(nameTemp.get(2).value)
                        except:
                            str(template.get("name"))
                        ##{{PK}}{{MN}}
                        tClass = tClass.replace("{{PK}}{{MN}}","Pokemon")

                        tempTrainer = Trainer(tSprite, tClass, tName, tMoney, tPokeCount, tLocation, tRegion, tGame)
                        #tempTrainer.printSelf()
                    if "Pokémon" in template.name:
                        #print(template)
                        #Parse Pokemon
                        try:
                            pDexNo = int(str(template.get("ndex").value))
                        except:
                            try:
                                pDexNo = int(str(template.get("ndex").value)[:-2])
                            except:
                                pDexNo = 0 #Couldn't parse, so now it's a MissingNo.  Are you proud?
                        pSpecies = str(template.get("pokemon").value)
                        try:
                            pGender = str(template.get("gender").value)
                        except:
                            pGender = "Unknown"
                        pLevel = str(template.get("level").value)
                        pMoves = []
                        try:
                            pHold = str(template.get("held").value)
                        except ValueError:
                            pHold = "" 
                        try:
                            pAbility = str(template.get("ability").value)
                        except:
                            #Gen 1 or 2, so give a random ability
                            jsonCode = getJSON(pSpecies)
                            #print(pSpecies)
                            if pSpecies == "Mr. Mime": #Mr. Mime causes issues once again.  Hardcode a solution.
                                jsonCode = getJSON("mr-mime")
                            if pSpecies == "Nidoran♂":
                                jsonCode = getJSON("nidoran-m")
                            if pSpecies == "Nidoran♀":
                                jsonCode = getJSON("nidoran-f")
                            parsed = json.loads(jsonCode)
                            abilityChoices = []
                            for ability in parsed["abilities"]:
                                #parsedAbility = json.loads(ability)
                                #print(ability)
                                if not ability['is_hidden']:
                                    #Don't want to give hidden abilities
                                    abilityChoices.append(ability["ability"]["name"])
                            #Randomly choose an ability
                            pAbility = random.choice(abilityChoices)
                        #Parse Gender
                        if(pGender == "male"):
                            pGender = 'M'
                        elif(pGender == "female"):
                            pGender = 'F'
                        else:
                            pGender = 'U'
                        #Parse moves
                        pMoves.append(str(template.get("move1").value))
                        try:
                            pMoves.append(str(template.get("move2").value))
                        except ValueError:
                            1+1 #Do nothing, filler line to stop Python from fussing
                        try:
                            pMoves.append(str(template.get("move3").value))
                        except ValueError:
                            1+1 #Do nothing, filler line to stop Python from fussing
                        try:
                            pMoves.append(str(template.get("move4").value))
                        except ValueError:
                            1+1 #Do nothing, filler line to stop Python from fussing
                        tempTrainer.addPoke(FinishedPokemon(pDexNo, pSpecies, pGender, pLevel, pMoves, pHold, pAbility))
                #print(tempTrainer)
                #Set the boss trainer flag
                tempTrainer.isBoss()
                parsedTrainers.append(tempTrainer)
        except:
            pass


def getTrainerSprite(spriteName):
    spriteName = spriteName.replace("{{!}}70px","")
    spriteName = spriteName.replace("{{!}}90px","")
    spriteName = spriteName.replace("{{!}}100px","")
    spriteName = spriteName.replace("{{!}}150px","")
    spriteName = spriteName.replace("{{!}}170px","")
    if not spriteName in foundSprites:
        URL = "https://bulbapedia.bulbagarden.net/wiki/File:"+spriteName.replace(" ","_")

        URL = URL.replace("{{!}}70px","")
        URL = URL.replace("{{!}}90px","")
        URL = URL.replace("{{!}}100px","")
        URL = URL.replace("{{!}}150px","")
        URL = URL.replace("{{!}}170px","")
        #print(URL)
        #webbrowser.open(URL)
        imgPageCode=requests.get(URL)
        imgPage = imgPageCode.content
        #Get link by class and title: https://stackoverflow.com/a/32542575
        soup = BeautifulSoup(imgPage, "html.parser")
        links = soup.findAll('a', {"class": "internal"})
        for link in links:
            href = link.get('href')
            title = link.get('title')
            href = "https:"+href
            #print(href)
            img = requests.get(href)
            with open("sprites/" + title, 'wb') as f:
                f.write(img.content)
        foundSprites.append(spriteName)

def init():
    for file in os.listdir("sprites"):
        foundSprites.append(file)
    #Import lookup table
    try:
        lookupFile = open("manualLookup.csv", "r")
        for line in lookupFile:
            cleanLine = line.replace("\n", "")
            splitLine = cleanLine.split(",")
            #print(splitLine)
            if(len(splitLine) == 2):
                lookupTable.append(manualSpriteLookup(splitLine[0], splitLine[1]))
        lookupFile.close()
    except FileNotFoundError:
        print("Lookup file not found!")


pokeList = ""
foundSprites = []
lookupTable = []
parsedTrainers = []
parsedWilds = []

init()

#Check if PKL already exists

if(os.path.exists("pkl/"+str(sys.argv[1]).replace("wiki/","")+".pkl")):
    print("PKL already exists.  Exiting")
    exit()

endHeader = re.compile("^==[A-Z][a-z]+")
wikiPage = open(sys.argv[1], "r", encoding="utf8")
location = sys.argv[1]
region = ""
game = "a"
for line in wikiPage:
    if "region=" in line:
        region=line[-6:-1] #Sinnoh will just be "innoh".  All other region names are 5 letters long
        if region == "innoh":
            region = "Sinnoh"
        break
wikiPage.seek(0)
pokeList = findPokeList()
wikiPage.seek(0)
trainerList = findTrainerList()
#if not pokeList:
#    print("No pokemon found")
#if not trainerList:
#    print("No trainers found")
wikiPage.close()

#for line in pokeList:
#    print(line)
#    print(",")


#print(trainerList)
#for line in trainerList:
#    print(line)
#    print(",")

parsePokemon(pokeList)

#for pokemon in parsedWilds:
#    print(pokemon)


try:
    findRegularTrainers(trainerList)
    findBossTrainers(trainerList)
except Exception as e:
    print("Parse error")
    print(e)
    traceback.print_exc()
    outFile = sys.argv[1].replace("wiki/","")
    pickleFile = "pkl/" + outFile + ".err"
    with open(pickleFile, 'w') as output:
        output.writelines("Error parsing")
else:
    #Dump trainer list
#    print("!!!!!File output disabled!!!!!")
    outFile = sys.argv[1].replace("wiki/","")
    pickleFile = "pkl/" + outFile + ".trainer.pkl"
    with open(pickleFile, 'wb') as output:
        pickle.dump(parsedTrainers, output, 0)

#for trainer in parsedTrainers:
#    print(trainer)
lookupOut = ""
for entry in lookupTable:
    lookupOut += str(entry)
#Write CSV file for manual lookup
lookupFile = open("manualLookup.csv", 'w')
try:
    lookupFile.write(lookupOut)
except:
    pass
lookupFile.close()
pickleFile = "pkl/" + outFile + ".pokemon.pkl"
with open(pickleFile, 'wb') as output:
    pickle.dump(parsedWilds, output, 0)


for trainer in parsedTrainers:
    print(trainer)