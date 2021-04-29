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

'''
***************************
Determine location lists
***************************
'''

if(len(sys.argv) != 3):
    print("Usage: parseData.py <file name in location/> <game string>")
    exit(1)
locations = []
##Add special locations for progression gates
#locations.append("%SURF%")
#locations.append("%OLDROD%")
#locations.append("%GOODROD%")
#locations.append("%SUPERROD%")
#locations.append("%POSTGAME%")#Stop checking after this
#
#
#for f in os.listdir("pkl/trainer"):
#    with open("pkl/trainer/"+f, 'rb') as input:
#        pokeList = pickle.load(input)
#        if(pokeList[0].tRegion.lower() == sys.argv[1].lower()):
#            locations.append(f.replace(".trainer.pkl",""))
#            
#for loc in locations:
#        print(loc)


foundLocation = False
for f in os.listdir("location/"):
    if f == sys.argv[1]:
        foundLocation = True
if not foundLocation:
    print("File not found in location/:", sys.argv[1])
    exit(1)
    

with open ("location/"+sys.argv[1], "r") as f:
    for line in f:
        locations.append(line.strip())
        
        
game = sys.argv[2].lower().strip()

if(game != "rby" and
   game != "gsc" and
   game != "rse" and
   game != "dppt" and
   game != "bw" and
   game != "b2w2" and
   game != "xy" and
   game != "sm" and
   game != "swsh" and
   game != "frlg" and
   game != "hgss" and
   game != "oras" and
   game != "lgpe"):
    print(f"Invalid game string: {game}")
    exit(1)

#Determine whether progression gates have been passed
#Old Rod, Good Rod, Super Rod, Surf
flags = [False, False, False, False]
specialFlags = []
wilds = []
trainers = []
locationsClean = []
for location in locations:
    areaWilds = []
    areaTrainers = []
    skipWilds = False
    skipTrainers = False
    
    if(location[0] == '%'):
        #Flag
        if location == "%OLDROD%":
            flags[0] = True
        if location == "%GOODROD%":
            flags[1] = True
        if location == "%SUPERROD%":
            flags[2] = True
        if location == "%SURF%":
            flags[3] = True
        else:
            specialFlags.append(location)
        continue
    else:
        locationsClean.append(location)
    try:
        with open("pkl/pokemon/"+location+".pokemon.pkl", "rb") as f:
            areaWilds = pickle.load(f)
        if(len(areaWilds) == 0):
            #Nothing in the file, skip it
            wilds.append("0")
            skipWilds = True
    except (FileNotFoundError):
        #No wild pokemon in the area.  Skip it
        wilds.append("0")
        skipWilds = True
    
    try:
        with open("pkl/trainer/"+location+".trainer.pkl","rb") as f:
            areaTrainers = pickle.load(f)
        if(len(areaTrainers) == 0):
            trainers.append("0")
            skipTrainers = True
    except (FileNotFoundError):
        trainers.append("0")
        skipTrainers = True

    '''
    *****************************
    Parse wild Pokemon levels
    *****************************
    '''
    #Find the average of the wild Pokemon levels
    accumulator = 0
    counter = 0
    if not skipWilds:
        for mon in areaWilds:
            #Check rods/surf
            if((mon.pArea.lower() == "fish old" and flags[0])
               or (mon.pArea.lower() == "fish good" and flags[1])
               or (mon.pArea.lower() == "fish super" and flags[2])
               or (mon.pArea.lower() == "surf" and flags[3])
               or (
                   mon.pArea.lower() != "fish old"
                   and mon.pArea.lower() != "fish good"
                   and mon.pArea.lower() != "fish super"
                   and mon.pArea.lower() != "surf"
                   and mon.pArea.lower() != "gift"
                   and mon.pArea.lower() != "only one"
                   and mon.pArea.lower() != "special"
                   and mon.pArea.lower() != "trade"
               )
            ):
                if(game == "rby"):
                    monGame = mon.pGames
                    if(monGame == "R," or
                       monGame == "B," or
                       monGame == "Y," or
                       monGame == "R,B," or
                       monGame == "R,Y," or
                       monGame == "B,Y," or
                       monGame == "R,B,Y,"):
                        #print(mon)
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "gsc"):
                    monGame = mon.pGames
                    if(monGame == "G," or
                       monGame == "S," or
                       monGame == "C," or
                       monGame == "G,S," or
                       monGame == "G,C," or
                       monGame == "S,C," or
                       monGame == "G,S,C,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                
                if(game == "rse"):
                    monGame = mon.pGames
                    if(monGame == "R," or
                       monGame == "S," or
                       monGame == "E," or
                       monGame == "R,E," or
                       monGame == "S,E," or
                       monGame == "R,S," or
                       monGame == "R,S,E,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                
                if(game == "frlg"):
                    monGame = mon.pGames
                    if(monGame == "FR," or
                       monGame == "LG," or
                       monGame == "FR,LG,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "dppt"):
                    monGame = mon.pGames
                    if(monGame == "D," or
                       monGame == "P," or
                       monGame == "Pt," or
                       monGame == "D,P," or
                       monGame == "D,Pt," or
                       monGame == "P,Pt," or
                       monGame == "D,P,Pt,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "hgss"):
                    monGame = mon.pGames
                    if(monGame == "HG," or
                       monGame == "SS," or
                       monGame == "HG,SS,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "bw"):
                    monGame = mon.pGames
                    if(monGame == "B," or
                       monGame == "W," or
                       monGame == "B,W,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "b2w2"):
                    monGame = mon.pGames
                    if(monGame == "B2," or
                       monGame == "W2," or
                       monGame == "B2,W2,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "xy"):
                    monGame = mon.pGames
                    if(monGame == "X," or
                       monGame == "Y," or
                       monGame == "X,Y,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "oras"):
                    monGame = mon.pGames
                    if(monGame == "OR," or
                       monGame == "AS," or
                       monGame == "OR,AS,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                
                if(game == "sm"):
                    monGame = mon.pGames
                    if(monGame == "S," or
                       monGame == "M," or
                       monGame == "S,M,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "usum"):
                    monGame = mon.pGames
                    if(monGame == "US," or
                       monGame == "UM," or
                       monGame == "US,UM,"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
                       
                if(game == "swsh"):
                    monGame = mon.pGames
                    if(monGame == "Sw," or
                       monGame == "Sh," or
                       monGame == "Sw,Sh"):
                        try:
                            accumulator += (int(mon.pMinLevel) + int(mon.pMaxLevel))/2
                            counter += 1
                        except:
                           pass
        if(counter > 0):
            wilds.append(str(accumulator/counter))
        else:
            wilds.append("0")
    
    '''
    *****************************
    Parse Trainer levels
    *****************************
    '''    
    accumulator = 0
    counter = 0
    if not skipTrainers:
        areaLevels = []
        for trainer in areaTrainers:
            if (game == "rby"):
                tGame = trainer.tGame.lower()
                if(tGame == "r" or
                   tGame == "b" or
                   tGame == "y" or
                   tGame == "rb" or
                   tGame == "ry" or
                   tGame == "by" or
                   tGame == "rby" or
                   tGame == "rgb"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    accumulator += (tAcc/tCount) #We only care about the average level
                    counter += 1
            
            if (game == "gsc"):
                tGame = trainer.tGame.lower()
                if(tGame == "g" or
                   tGame == "s" or
                   tGame == "c" or
                   tGame == "gs" or
                   tGame == "gc" or
                   tGame == "sc" or
                   tGame == "gsc"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
            if (game == "rse"):
                tGame = trainer.tGame.lower()
                if(tGame == "r" or
                   tGame == "s" or
                   tGame == "e" or
                   tGame == "rs" or
                   tGame == "re" or
                   tGame == "se" or
                   tGame == "rse"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
            if (game == "frlg"):
                tGame = trainer.tGame.lower()
                if(tGame == "fr" or
                   tGame == "lg" or
                   tGame == "frlg"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    accumulator += (tAcc/tCount) #We only care about the average level
                    counter += 1        
            
            if (game == "dppt"):
                tGame = trainer.tGame.lower()
                if(tGame == "d" or
                   tGame == "p" or
                   tGame == "pt" or
                   tGame == "dp" or
                   tGame == "dpt" or
                   tGame == "ppt" or
                   tGame == "dppt"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
            if (game == "hgss"):
                tGame = trainer.tGame.lower()
                if(tGame == "hg" or
                   tGame == "ss" or
                   tGame == "hgss"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    accumulator += (tAcc/tCount) #We only care about the average level
                    counter += 1
                    
            if (game == "bw"):
                tGame = trainer.tGame.lower()
                if(tGame == "b" or
                   tGame == "w" or
                   tGame == "bw"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
            
            if (game == "b2w2"):
                tGame = trainer.tGame.lower()
                if(tGame == "b2" or
                   tGame == "w2" or
                   tGame == "b2w2"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
            if (game == "xy"):
                tGame = trainer.tGame.lower()
                if(tGame == "x" or
                   tGame == "y" or
                   tGame == "xy" or
                   tGame == "s" or
                   tGame == "m" or
                   tGame == "sm"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
            
            if (game == "oras"):
                tGame = trainer.tGame.lower()
                if(tGame == "or" or
                   tGame == "as" or
                   tGame == "oras" or
                   tGame == "s" or
                   tGame == "m" or
                   tGame == "sm"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
            if (game == "sm"):
                tGame = trainer.tGame.lower()
                if(tGame == "s" or
                   tGame == "m" or
                   tGame == "sm"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
            
            if (game == "swsh"):
                tGame = trainer.tGame.lower()
                if(tGame == "sw" or
                   tGame == "sh" or
                   tGame == "swsh" or
                   tGame == "s" or
                   tGame == "m" or
                   tGame == "sm"):
                    trainerMons = trainer.getPokes()
                    tAcc = 0
                    tCount = 0
                    for mon in trainerMons:
                        try:
                            tAcc += int(mon.pLevel)
                            tCount += 1
                        except:
                            pass
                    try:
                        accumulator += (tAcc/tCount) #We only care about the average level
                        counter += 1
                    except:
                        pass # Problem with the trainer
                    
        if(counter > 0):
            areaLevels.append(str(accumulator/counter))
        else:
            areaLevels.append("0")
            
        accumulator = 0
        counter = 0
        for area in areaLevels:
            accumulator += float(area)
            counter += 1
        avgLevel = accumulator/counter
        
        #Clean the data, remove outlier trainers
        for trainer in areaLevels:
            if float(trainer) == 0 or not (abs( (float(trainer) - float(avgLevel) ) / float(trainer)) <= .20):
                trainer = 0
        
        for area in areaLevels:
            accumulator += float(area)
            counter += 1
        trainers.append(accumulator/counter)
        

print("Area, Wild, Trainer")
for i in range (len(locationsClean)):
    print(f'{locationsClean[i]},{wilds[i]},{trainers[i]}')