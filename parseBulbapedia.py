'''
TODO:
* Download sprites based on the filename
** This will need to parse HTML

* Convert basic Pokes into finished Pokes based on PokeAPI (Find moves, pick random ability)
* Dump trainers to JSON file
'''




import os
import sys
import re
import mwparserfromhell
from bs4 import BeautifulSoup
import requests


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
        getTrainerSprite(self.tSprite)
        self.findGameFromSprite()
    def __str__(self):
        list = self.getList()
        output = ""
        for line in list:
            output += str(line)
            output += '\n'
        return output
    def findGameFromSprite(self):
        sprName = self.tSprite.replace("_"," ")
        if " RG " in sprName or " RB " in sprName:
            self.tGame = "RGB"
        elif " Y " in sprName:
            self.tGame = "Y"
        elif " GS " in sprName or " GSC " in sprName:
            self.tGame = "GS"
        elif " C " in sprName:
            self.tGame = "C"
        elif " RS " in sprName or " RSE " in sprName:
            self.tGame = "RS"
        elif " E " in sprName:
            self.tGame = "E"
        elif " FRLG " in sprName:
            self.tGame = "FRLG"
        elif " DP " in sprName or " DPPt " in sprName:
            self.tGame = "DP"
        elif " Pt " in sprName:
            self.tGame = "Pt"
        elif " HGSS " in sprName:
            self.tGame = "HGSS"
        elif " BW " in sprName:
            self.tGame = "BW"
        elif " B2W2 " in sprName:
            self.tGame = "B2W2"
        elif " XY " in sprName:
            self.tGame = "XY"
        elif " ORAS " in sprName:
            self.tGame = "ORAS"
        elif " SM " in sprName or " USUM " in sprName:
            self.tGame = "SM"
        elif " LGPE " in sprName:
            self.tGame = "LGPE"
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
            if not found:
                print("Game undetermined")
                print("Sprite Name: " + sprName)
                print("Enter game acronym:")
                self.tGame = input().upper()
                lookupTable.append(manualSpriteLookup(sprName, self.tGame))


    def printName(self):
        print(self.tName)
    def printSelf(self):
        list = self.getList()
        for line in list:
            print(line)
        print('\n')
    def getList(self):
        return [self.tSprite, self.tClass, self.tName, self.tMoney, self.tPokeCount, self.tLocation, self.tRegion, self.tGame, self.tPokes]
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
    def __init__(self, pDexNo, pSpecies, pGender, pLevel):
        self.pDexNo = pDexNo
        self.pSpecies = pSpecies
        #Determine gender
        if(pGender == ''):
            self.pGender = 'U'
        if(pGender == '♀'):
            self.pGender = 'F'
        if(pGender == '♂'):
            self.pGender = 'M'
        #For B2W2 trainers, do extra work to parse level info
        if(pLevel[0] == '{'):
            levelCode = mwparserfromhell.parse(pLevel)
            levelTemplates = levelCode.filter_templates()
            levelTemplate = levelTemplates[0]
            parsedLevel = levelTemplate.get(1).value
            self.pLevel = parsedLevel
        else:
            self.pLevel = pLevel

    def __str__(self):
        return str(self.pDexNo) + "," + str(self.pSpecies) + "," + str(self.pGender) + "," + str(self.pLevel)
    def __repr__(self):
        return str(self)

    def makeFinishedPoke(self):
        print("Not implemented!")

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


def findTrainerList():
    foundTrainers = False
    bossTrainer = False
    bossLine = ""
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
            else:
                if(line[0] == '='):
                    line = line.strip()
                    line.replace(' ', '')
                    if(endHeader.match(line)):
                        foundTrainers = False
                        break
                if line.strip(): #https://stackoverflow.com/questions/7896495/python-how-to-check-if-a-line-is-an-empty-line
                    if(line.strip() == "{{Party/Single"):
                        print("Found boss trainer")
                        bossTrainer = True
                        bossLine += (line.strip())
                        #trainerLines.append(line.strip())
                    else:
                        trainerLines.append(line.strip())
        else:
            line = line.rstrip()
            line.replace(' ','') #Remove any extra spaces
            if(line == "==Trainers=="):
                print("Trainer list found")
                foundTrainers = True
    return trainerLines
def findRegularTrainers(trainerList):
    for line in trainerList:
        if(line[0] == '='):
            #Header
            game = line
            continue
        #print(line)
        
        if("Trainerentry" in line):
            wikicode = mwparserfromhell.parse(line)
            templates = wikicode.filter_templates()
            template = templates[0]
            #Found trainer, parse them out
            trainerSprite = str(template.get(1).value)
            trainerClass = str(template.get(2).value)
            trainerName = str(template.get(3).value)
            trainerMoney = str(template.get(4).value)
            trainerPokeCount = str(template.get(5).value)
            #TODO: Iterate through Pokemon list, parse Pokes and create objects
            tempTrainer = Trainer(trainerSprite, trainerClass, trainerName, trainerMoney, trainerPokeCount, location, region, game)
            offset = 6
            for i in range(0,int(trainerPokeCount[0])):
                pokeDexNo = str(template.get(offset + 0).value)
                pokeSpecies = str(template.get(offset + 1).value)
                pokeGender = str(template.get(offset + 2).value)
                pokeLevel = str(template.get(offset + 3).value)
                tempTrainer.addPoke(BasicPokemon(pokeDexNo,pokeSpecies,pokeGender,pokeLevel))
                offset += 5 # 4 fields make up Pokemon data
            #tempTrainer.printSelf()
            parsedTrainers.append(tempTrainer)
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
        if "Party/Single" in line:
            tempTrainer = ""
            wikicode = mwparserfromhell.parse(line)
            templates = wikicode.filter_templates()
            for template in templates:
                #print(template)
                if template.name == "Party/Single":
                    tSprite = str(template.get("sprite").value)
                    tClass = str(template.get("class").value)
                    tMoney = str(template.get("prize").value) # Will require further parsing later, contains special character, plus B2W2 weirdness
                    tName = str(template.get("name").value) # More parsing required to get proper name
                    tPokeCount = int(str(template.get("pokemon").value))
                    tGame = str(template.get("game").value)
                    
                    #Additional formatting
                    tMoney = tMoney.replace("{{PDollar}}","")
                    ##Name
                    nameCode = mwparserfromhell.parse(tName)
                    nameTemps = nameCode.filter_templates()
                    nameTemp = nameTemps[0]
                    tName = str(nameTemp.get(2).value)
                    ##{{PK}}{{MN}}
                    tClass = tClass.replace("{{PK}}{{MN}}","Pokemon")

                    tempTrainer = Trainer(tSprite, tClass, tName, tMoney, tPokeCount, tLocation, tRegion, tGame)
                    #tempTrainer.printSelf()
                if "Pokémon" in template.name:
                    #print(template)
                    #Parse Pokemon
                    pDexNo = int(str(template.get("ndex").value))
                    pSpecies = str(template.get("pokemon").value)
                    pGender = str(template.get("gender").value)
                    pLevel = str(template.get("level").value)
                    pMoves = []
                    try:
                        pHold = str(template.get("held").value)
                    except ValueError:
                        pHold = "" 
                    pAbility = str(template.get("ability").value)
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
            parsedTrainers.append(tempTrainer)


def getTrainerSprite(spriteName):
    if not spriteName in foundSprites:
        URL = "https://bulbapedia.bulbagarden.net/wiki/File:"+spriteName.replace(" ","_")
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
            print(href)
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
            print(splitLine)
            if(len(splitLine) == 2):
                lookupTable.append(manualSpriteLookup(splitLine[0], splitLine[1]))
        lookupFile.close()
    except FileNotFoundError:
        print("Lookup file not found!")

def saveData():
    lookupOut = ""
    for entry in lookupTable:
        lookupOut += str(entry)
    #Write CSV file for manual lookup
    lookupFile = open("manualLookup.csv", 'w')
    lookupFile.write(lookupOut)
    lookupFile.close()

foundSprites = []
lookupTable = []
parsedTrainers = []




init()
endHeader = re.compile("^==[A-Z][a-z]+")
wikiPage = open(sys.argv[1], "r", encoding="utf8")
location = sys.argv[1]
region = ""
game = ""
for line in wikiPage:
    if "region=" in line:
        region=line[-6:-1] #Sinnoh will just be "innoh".  All other region names are 5 letters long
        if region == "innoh":
            region = "Sinnoh"
        break
trainerList = findTrainerList()
wikiPage.close()
#print(trainerList)
#for line in trainerList:
#    print(line)
#    print(",")
findRegularTrainers(trainerList)
findBossTrainers(trainerList)
for trainer in parsedTrainers:
    print(trainer)
saveData()

