
import os
import sys
import re
import mwparserfromhell
from bs4 import BeautifulSoup
import requests
import pickle
import json
import random

if(len(sys.argv) != 2):
    print("Usage: parseBulbapedia.py <wiki page from local drive>")
    exit()

class Trainer:
    def __init__(self, tSprite, tClass, tName, tMoney, tPokeCount, tLocation="", tRegion="", tGame=""):
        self.tSprite = tSprite
        self.tClass = tClass
        self.tName = tName
        #For B2W2 trainers, do extra work to parse money info
        if(tMoney[0] == '{'):
            levelCode = mwparserfromhell.parse(tMoney)
            levelTemplates = levelCode.filter_templates()
            levelTemplate = levelTemplates[0]
            parsedLevel = levelTemplate.get(1).value
            self.tMoney = parsedLevel
        else:
            self.tMoney = tMoney
        self.tPokeCount = tPokeCount
        self.tLocation = tLocation
        self.tRegion = tRegion
        self.tGame = tGame
        self.tPokes = []
        getTrainerSprite(self.tSprite.replace("{{!}}90px",""))
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
                self.tGame = input().upper()
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
        jsonCode = getJSON(self.pSpecies)
        #print(self.pSpecies)
        if self.pSpecies == "Mr. Mime": #Mr. Mime causes issues once again.  Hardcode a solution.
            jsonCode = getJSON("mr-mime")
        if self.pSpecies == "Nidoran♂":
            jsonCode = getJSON("nidoran-m")
        if self.pSpecies == "Nidoran♀":
            jsonCode = getJSON("nidoran-f")
        if self.pSpecies == "Farfetch'd":
            jsonCode = getJSON("farfetchd")
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
        if(pGender == ''):
            self.pGender = 'U'
        if(pGender == '♀'):
            self.pGender = 'F'
        if(pGender == '♂'):
            self.pGender = 'M'
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






trainers = []
with open(sys.argv[1], 'rb') as input:
    print(sys.argv[1])
    trainers = pickle.load(input)
for trainer in trainers:
    print(trainer)
