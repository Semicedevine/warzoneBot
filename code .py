from quickGrab import x_pad
from quickGrab import y_pad
import time
import win32api, win32con, win32clipboard
import numpy as np
import os
import json
import pyperclip

from PIL import ImageGrab
import cv2.cv2 as cv2
import pyautogui as control

from maps import MME

#from PIL import ImageEnhance
#from PIL import ImageOps
import pytesseract as tes
tes.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'


# -----DEBUG-----
def mousePos(cord):
    win32api.SetCursorPos((cord[0], cord[1]))
     
def get_cords():
    x,y = win32api.GetCursorPos()
    print(x,y)

def startGame():
    click(131, 200)
    time.sleep(.1)

def screenGrab():
    b1 = (x_pad + 1,y_pad+1,x_pad+1710,y_pad+903)
    im = ImageGrab.grab(b1)
 
    # debug: im.save(os.getcwd() + '\\Snap__' + str(int(time.time())) +'.png', 'PNG')
    return im

def colorGrabLoop():
    image = ImageGrab.grab()
    print(image.getpixel(win32api.GetCursorPos()))
    time.sleep(2)

    """
    NOTES:
    Yellow (255, 255, 0)
    Blue (0, 0, 255)
    Black (0, 0, 0)
    Neutral Gray (200, 200, 200)
    """


# -----CLASSES-----
class Buttons:

    deploy = (72, 256)
    attack = (72, 280)
    confirm = (72, 304)

    chat = (90, 985)
    menu = (80, 1013)

    # Menu Commands
    cards = (90, 706)
    history = (90, 730)
    settings = (90, 755)
    players = (90, 777)
    surrender = (90, 803)
    vte = (90, 828)
    analyze = (90, 849)
    statistics = (90, 877)
    boot = (90, 898)
    full_screen = (90, 924)
    auto_pilot = (90, 946)
    refresh = (90, 976)

    # History Commands
    forwardMove = (111, 297)
    forwardTurn = (153, 297)
    backwardMove = (70, 297)
    backwardTurn = (27, 297)
    beginning = (44, 324)
    end = (103, 324)
    exitHistory = (130, 200)

class PossibleOwners:
    NEUTRAL = ('neutral')
    OPPONENT = ('opponent')
    PLAYER = ('player')
    FOGGED = ('fogged')
    AVAILABLE = ('available')

class SuperRegion:
    def __init__(self, id, bonus):
        self.id = id
        self.bonus = bonus
        self.regionIds = []

class Region:
    def __init__(self, id, superRegion, x, y, colorX, colorY):
        self.id = id
        self.superRegion = superRegion
        self.owner = PossibleOwners.NEUTRAL
        self.neighbors = []
        self.troopCount = 2
        self.isOnEmpireBorder = False
        self.isOnSuperRegionBorder = False

        # fog of war OP OP but we gotta be optimistic
        self.isVisible = True

        # coordinates for bot to click for this region
        self.x = x
        self.y = y
        self.colorX = colorX
        self.colorY = colorY
    def __repr__(self):
        # returns object properties for debug
        return "{0}, {1}, {2}, {3}, {4}".format(self.id, self.superRegion, self.x, self.y, self.owner)

class Map:
    regions = {}
    superRegions = []
    playerIncome = 5

    def getRegionById(self, id):
        return self.regions[id]

    def getSuperRegionById(self, id):
        return self.superRegions[id]

    def getOwnedRegions(self, owner):
        ownedRegions = []
        for i in self.regions: #keep watch on this line write here... if it doesn't work, use range()...
            region = self.regions[i]
            if region.owner == owner:
                ownedRegions.append(region)
                
        return ownedRegions

class Suggestion:
    def __init__(self, action, targetId, viability):
        self.action = action
        self.targetId = targetId
        self.viability = viability
     def __repr__(self):
        # returns object properties for debug
        return "{0}, {1}, {2}".format(self.action, self.targetId, self.viability)

class Game:
    def __init__(self):
        self.mapStates = {}

    def getMapStateByTurn(self, turn):
        return self.mapStates

# -----FUNCTIONS-----
def setupSuperRegions(data):
    for i in range(0, len(data), 2):
        continentId = data[i]
        continentBonus = data[i + 1]
        map.superRegions.append(SuperRegion(continentId, continentBonus))

def setupRegions(data):
    for i in range(0, len(data), 6):
        regionId = data[i]
        continentId = data[i + 1]
        x = data[i + 2]
        y = data[i + 3]
        colorX = data[i + 4]
        colorY = data[i + 5]
        map.regions[regionId] = Region(regionId, continentId, x, y, colorX, colorY)
        map.getSuperRegionById(continentId).regionIds.append(regionId)

def setupNeighbors(data):
    for i in range(0, len(data), 2):
        regionId = data[i]
        region = map.getRegionById(regionId)
        neighborIds = data[i + 1].split(" ")
        for j in range(0, len(neighborIds)):
            neighborId = int(neighborIds[j])
            neighbor = map.getRegionById(neighborId)

            # connect region with neighbor so this way data doesn't have to be repeated twice
            neighbor.neighbors.append(region)
            region.neighbors.append(neighbor)

def setupWastelands(data):
    for i in range(0, len(data)):
        regionId = int(data[i])
        region = map.getRegionById(regionId)

        # "this really shouldn't be hard coded" - i agree !!!
        region.troopCount = 10

def getGameId():
    # so the program doesn't intercept anything that was copied into the clipboard beforehand
    originalData = pyperclip.paste()


    control.click(294, 47, 3)
    control.hotkey('ctrl', 'c')
    retrievedData = pyperclip.paste()

    # back to how things were originally
    pyperclip.copy(originalData)

    # since in 'https://www.warzone.com/MultiPlayer?GameID=16142744' the game numbers come right after the '='
    retrievedList = retrievedData.split("=")
    gameId = retrievedList[1]

    return gameId

def getTurnNumber():
    imgBox = (57, 153, 128, 180)
    imgScanRGB = ImageGrab.grab(imgBox)
    imgScanBGR = cv2.cvtColor(np.asarray(imgScanRGB), cv2.COLOR_RGB2BGR)
    hsvImg = cv2.cvtColor(imgScanBGR, cv2.COLOR_RGB2HSV)

    lower_limit = np.array([10, 220, 240])
    upper_limit = np.array([230, 255, 255])

    imgMask = cv2.inRange(hsvImg, lower_limit, upper_limit)

    detectedNumbers = []
    finalNumber = ""

    for digit in range(0, 10):
        # get the original sample images of 0-9 and use them for matching
        imgTemplate = cv2.imread('a' + str(digit) + '.png', 0)
        w, h = imgTemplate.shape[::-1]

        res = cv2.matchTemplate(imgMask, imgTemplate, cv2.TM_CCOEFF_NORMED)
        if digit == 1:
            threshold = 0.80
        else:
            threshold = 0.69
        loc = np.where(res > threshold)

        for pt in zip(*loc[::-1]):
            centerX = pt[0] + w
            centerY = pt[1] + h
            
            detectedNumbers.append((centerX, digit))

    detectedNumbers.sort(key=lambda tup: tup[0])

    for item in detectedNumbers:
        finalNumber += str(item[1])

    return int(finalNumber)

def getRegionDistance(homeRegionId, targetRegionId):
    return 4

def getPlayerColors():
    global playerColor
    global opponentColor
    global neutralColor
    playerColor = (255, 255, 0)
    opponentColor = (0, 0, 255)
    neutralColor = (200, 200, 200)
    # who knows

# what do you think this is for
def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print("Click")

def updateMap():
    armyNumbers = {}

    # imgScanRGB is for PIL
    # imgScanBGR is for cv2
    # hsvImg is for cv2 filtering to mask

    imgScanRGB = ImageGrab.grab()
    imgScanBGR = cv2.cvtColor(np.asarray(imgScanRGB), cv2.COLOR_RGB2BGR)
    hsvImg = cv2.cvtColor(imgScanBGR, cv2.COLOR_RGB2HSV)

    for doubleScan in range(0, 2):
        
        if doubleScan == 0:
            # get black digits!
            lower_limit = np.array([0, 0, 0])
            upper_limit = np.array([255, 255, 10])
        else:
            # get white digits!
            lower_limit = np.array([0, 0, 130])
            upper_limit = np.array([0, 0, 255])

        imgMask = cv2.inRange(hsvImg, lower_limit, upper_limit)

        for digit in range(0, 10):
            # get the original sample images of 0-9 and use them for matching
            imgTemplate = cv2.imread('b' + str(digit) + '.png', 0)
            w, h = imgTemplate.shape[::-1]

            res = cv2.matchTemplate(imgMask, imgTemplate, cv2.TM_CCOEFF_NORMED)
            if digit == 1:
                threshold = 0.80
            else:
                threshold = 0.69
            loc = np.where(res > threshold)

            for pt in zip(*loc[::-1]):
                centerX = pt[0] + w
                centerY = pt[1] + h
                if centerY not in armyNumbers:
                    armyNumbers[centerY] = []
                
                armyNumbers[centerY].append((centerX, digit))

    for i in range(0, len(map.regions)):
        global yPixelOffset
        centerX = map.regions[i].x
        centerY = map.regions[i].y
        
        # get the color of the territory based on how much lower or higher than the territory digits that the YPixelOffset wants the getpixel coordinates to go
        color = imgScanRGB.getpixel((map.regions[i].colorX, map.regions[i].colorY))
        if color == playerColor:
            map.regions[i].owner = PossibleOwners.PLAYER
        elif color == opponentColor:
            map.regions[i].owner = PossibleOwners.OPPONENT
        elif color == neutralColor:
            map.regions[i].owner = PossibleOwners.NEUTRAL
        else:
            #god danggit!
            map.regions[i].isVisible = False

        print(i)
        # only do this if the territory is visible, duh (should save a lotta resources)
        if map.regions[i].isVisible:
            # there's a chance that the digits scanned with this y coordinate may not actually belong to the territory in question, so the list is merely considered as 'possibleDigits'
            possibleDigits = armyNumbers[centerY]
            possibleDigits.sort(key=lambda tup: tup[0])
            print(possibleDigits)
            print(centerX)
            builtNumber = ""
            coreDigit = 0

            # find the digit closest to the center of the territory and use as core
            for c in range(0, len(possibleDigits)):
                if abs(possibleDigits[c][0] - centerX) <= 8:
                    coreDigit = c
                    builtNumber = str(possibleDigits[c][1])
                    break
            
            referenceX = possibleDigits[coreDigit][0]

            for l in range(coreDigit - 1, -1, -1):
                leftDigit = possibleDigits[l]
                if referenceX - leftDigit[0] >= 3:
                    if referenceX - leftDigit[0] <= 14:
                        builtNumber = str(leftDigit[1]) + builtNumber
                        referenceX = leftDigit[0]
                    else:
                        break

            referenceX = possibleDigits[coreDigit][0]

            for r in range(coreDigit + 1, len(possibleDigits)):
                rightDigit = possibleDigits[r]
                if rightDigit[0] - referenceX >= 3:
                    if rightDigit[0] - referenceX <= 14:
                        builtNumber = builtNumber + str(rightDigit[1])
                        referenceX = rightDigit[0]
                    else:
                        break
            
            map.regions[i].troopCount = int(builtNumber)

def getMapState(turnType):
    mapState = []
    if turnType == 'picking phase':
        armyNumbers = {}

        # imgScanRGB is for PIL
        # imgScanBGR is for cv2
        # hsvImg is for cv2 filtering to mask

        imgScanRGB = ImageGrab.grab()
        imgScanBGR = cv2.cvtColor(np.asarray(imgScanRGB), cv2.COLOR_RGB2BGR)
        hsvImg = cv2.cvtColor(imgScanBGR, cv2.COLOR_RGB2HSV)
        
        # get black digits!
        lower_limit = np.array([0, 0, 0])
        upper_limit = np.array([255, 255, 10])

        imgMask = cv2.inRange(hsvImg, lower_limit, upper_limit)

        for digit in range(0, 10):
            # get the original sample images of 0-9 and use them for matching
            imgTemplate = cv2.imread('b' + str(digit) + '.png', 0)
            w, h = imgTemplate.shape[::-1]

            res = cv2.matchTemplate(imgMask, imgTemplate, cv2.TM_CCOEFF_NORMED)
            if digit == 1:
                threshold = 0.80
            else:
                threshold = 0.69
            loc = np.where(res > threshold)

            for pt in zip(*loc[::-1]):
                centerX = pt[0] + w
                centerY = pt[1] + h
                if centerY not in armyNumbers:
                    armyNumbers[centerY] = []
                
                armyNumbers[centerY].append((centerX, digit))

        for i in range(0, len(map.regions)):
            centerX = map.regions[i].x
            centerY = map.regions[i].y
            owner = ""
            troopCount = 2

            # get the color of the territory based on how much lower or higher than the territory digits that the YPixelOffset wants the getpixel coordinates to go
            color = imgScanRGB.getpixel((map.regions[i].colorX, map.regions[i].colorY))
            if color == neutralColor:
                owner = PossibleOwners.NEUTRAL
            else:
                # must be a territory that can be picked
                owner = PossibleOwners.AVAILABLE
            
            # only do this if the territory is visible, duh (should save a lotta resources)
            if owner != 'available':
                # there's a chance that the digits scanned with this y coordinate may not actually belong to the territory in question, so the list is merely considered as 'possibleDigits'
                possibleDigits = armyNumbers[centerY]
                possibleDigits.sort(key=lambda tup: tup[0])
                builtNumber = ""
                coreDigit = 0

                # find the digit closest to the center of the territory and use as core
                for c in range(0, len(possibleDigits)):
                    if abs(possibleDigits[c][0] - centerX) <= 8:
                        coreDigit = c
                        builtNumber = str(possibleDigits[c][1])
                        break
                
                referenceX = possibleDigits[coreDigit][0]

                for l in range(coreDigit - 1, -1, -1):
                    leftDigit = possibleDigits[l]
                    if referenceX - leftDigit[0] >= 3:
                        if referenceX - leftDigit[0] <= 14:
                            builtNumber = str(leftDigit[1]) + builtNumber
                            referenceX = leftDigit[0]
                        else:
                            break

                referenceX = possibleDigits[coreDigit][0]

                for r in range(coreDigit + 1, len(possibleDigits)):
                    rightDigit = possibleDigits[r]
                    if rightDigit[0] - referenceX >= 3:
                        if rightDigit[0] - referenceX <= 14:
                            builtNumber = builtNumber + str(rightDigit[1])
                            referenceX = rightDigit[0]
                        else:
                            break
                
                troopCount = int(builtNumber)
            else:
                # CHANGE THIS IF THE AMOUNT OF ARMIES AN UNPICKED TERRITORY WILL HAVE CHANGES; IT'S 4 BY DEFAULT FOR MME
                troopCount = 4

            mapState.append((i, owner, troopCount))
    else:
        armyNumbers = {}

        # imgScanRGB is for PIL
        # imgScanBGR is for cv2
        # hsvImg is for cv2 filtering to mask

        imgScanRGB = ImageGrab.grab()
        imgScanBGR = cv2.cvtColor(np.asarray(imgScanRGB), cv2.COLOR_RGB2BGR)
        hsvImg = cv2.cvtColor(imgScanBGR, cv2.COLOR_RGB2HSV)

        for doubleScan in range(0, 2):
            
            if doubleScan == 0:
                # get black digits!
                lower_limit = np.array([0, 0, 0])
                upper_limit = np.array([255, 255, 10])
            else:
                # get white digits!
                lower_limit = np.array([0, 0, 130])
                upper_limit = np.array([0, 0, 255])

            imgMask = cv2.inRange(hsvImg, lower_limit, upper_limit)

            for digit in range(0, 10):
                # get the original sample images of 0-9 and use them for matching
                imgTemplate = cv2.imread('b' + str(digit) + '.png', 0)
                w, h = imgTemplate.shape[::-1]

                res = cv2.matchTemplate(imgMask, imgTemplate, cv2.TM_CCOEFF_NORMED)
                if digit == 1:
                    threshold = 0.80
                else:
                    threshold = 0.69
                loc = np.where(res > threshold)

                for pt in zip(*loc[::-1]):
                    centerX = pt[0] + w
                    centerY = pt[1] + h
                    if centerY not in armyNumbers:
                        armyNumbers[centerY] = []
                    
                    armyNumbers[centerY].append((centerX, digit))

        for i in range(0, len(map.regions)):
            centerX = map.regions[i].x
            centerY = map.regions[i].y
            owner = ""
            troopCount = 2

            # get the color of the territory based on how much lower or higher than the territory digits that the YPixelOffset wants the getpixel coordinates to go
            color = imgScanRGB.getpixel((map.regions[i].colorX, map.regions[i].colorY))
            if color == playerColor:
                owner = PossibleOwners.PLAYER
            elif color == opponentColor:
                owner = PossibleOwners.OPPONENT
            elif color == neutralColor:
                owner = PossibleOwners.NEUTRAL
            else:
                #god danggit!
                owner = PossibleOwners.FOGGED
            
            # only do this if the territory is visible, duh (should save a lotta resources)
            if owner != 'fogged':
                # there's a chance that the digits scanned with this y coordinate may not actually belong to the territory in question, so the list is merely considered as 'possibleDigits'
                possibleDigits = armyNumbers[centerY]
                possibleDigits.sort(key=lambda tup: tup[0])
                builtNumber = ""
                coreDigit = 0

                # find the digit closest to the center of the territory and use as core
                for c in range(0, len(possibleDigits)):
                    if abs(possibleDigits[c][0] - centerX) <= 8:
                        coreDigit = c
                        builtNumber = str(possibleDigits[c][1])
                        break
                
                referenceX = possibleDigits[coreDigit][0]

                for l in range(coreDigit - 1, -1, -1):
                    leftDigit = possibleDigits[l]
                    if referenceX - leftDigit[0] >= 3:
                        if referenceX - leftDigit[0] <= 14:
                            builtNumber = str(leftDigit[1]) + builtNumber
                            referenceX = leftDigit[0]
                        else:
                            break

                referenceX = possibleDigits[coreDigit][0]

                for r in range(coreDigit + 1, len(possibleDigits)):
                    rightDigit = possibleDigits[r]
                    if rightDigit[0] - referenceX >= 3:
                        if rightDigit[0] - referenceX <= 14:
                            builtNumber = builtNumber + str(rightDigit[1])
                            referenceX = rightDigit[0]
                        else:
                            break
                
                troopCount = int(builtNumber)

            mapState.append((i, owner, troopCount))

    return mapState

def placeArmies(placements):
    # placements = [(id of region, amount of armies)]
    control.click(Buttons.deploy)
    for item in placements:
        region = map.getRegionById(item[0])
        armies = item[1]

        if map.playerIncome < 15:
            control.click(region.x, region.y, armies)
        else:
            control.click(region.x, region.y)
            control.typewrite(str(armies))
            if region.y > 218:
                control.click(region.x + 59, region.y - 24)
            else:
                control.click(region.x + 59, 194)

def moveArmies(moves):
    # moves = [(id of region to use for attack, id of region to attack, amount of armies)]
    control.click(Buttons.attack)
    for item in moves:
        homeRegion = map.getRegionById(item[0])
        targetRegion = map.getRegionById(item[1])
        armies = item[2]

        control.click(homeRegion.x, homeRegion.y)
        control.click(targetRegion.x, targetRegion.y)
        control.typewrite(str(armies))
        control.press('enter')

def makeOrders(mapStates, turnNumber):
    # THE FUNCTION YOU'VE ALL BEEN WAITING FOR
    armiesLeft = map.playerIncome

    # CALCULATING BONUS EFFICIENCIES... -looks at all the superRegions at the start of the game
    bonusEfficiencies = []
    for superRegion in map.superRegions:
        totalArmies = 0
        bonusValue = superRegion.bonus
        for regionId in superRegion.regionIds:
            totalArmies += mapStates["0"][regionId][2]
        
        efficiency = bonusValue / totalArmies
        bonusEfficiencies.append((superRegion.id, efficiency))
    
    bonusesByEfficiency = sorted(bonusEfficiencies, key=lambda tup: tup[1], reverse=True)

    possibleOpponentRegions = mapStates

    for region in mapStates["0"]:
        if region[1] == 'available':
            possibleOpponentRegions.append(region)


    # SORTING OUT REGIONS BY CHARACTERISTICS... -looks at the conditions of every region on the current turn
    playerRegions = []
    opponentRegions = []
    visibleRegions = []
    for region in mapStates[str(turnNumber)]:
        if region[1] != 'fogged':
            if region[1] == 'player':
                playerRegions.append(region)
            elif region[1] == 'opponent':
                opponentRegions.append(region)
            
            visibleRegions.append(region)
    
    # COMPILE A LIST OF SUGGESTED MOVES THAT THE BOT WILL WEIGH AGAINST ONE ANOTHER IN ORDER TO MAKE THE BEST MOVE IN ANY GIVEN SITUATION
    suggestionsMatrix = []
    checkedBonuses = []
    for playerRegion in playerRegions:
        superRegionId = map.getRegionById(playerRegion[0]).superRegion
        if superRegionId not in checkedBonuses:
            viability = bonusEfficiencies[superRegionId][1] * 100

            suggestionsMatrix.append(Suggestion("take bonus", superRegionId, viability))
            
            print(playerRegion[0])
            print(viability)
            checkedBonuses.append(superRegionId)
    
    suggestionsMatrix = suggestionsMatrix.sorted(suggestionsMatrix, key=lambda x: x.viability, reverse=True)

    #decisionMatrix / 1 selects top 100% viable decisions
    for i in range(0, len(suggestionsMatrix) / 1):
        suggestion = suggestionsMatrix[i]
        if suggestion.viability > 10:
            counterViability = 0
            if suggestion.action = "take bonus":
                outsideRegions = []
                for subRegionId in map.getSuperRegionById(suggestion.targetId).regionIds:
                    subRegion = map.getRegionById(subRegionId)
                    for subRegionNeighbor in subRegion.neighbors:
                        if subRegionNeighbor.superRegion != subRegion.superRegion:
                            if subRegionNeighbor.id in outsideRegions:
                                #[item for item in outsideRegions if item[0] == 1][1] += 1
                                [item for item in outsideRegions if item[0] == subRegionNeighbor.id][1] += 1
                            else:
                                outsideRegions.append((subRegionNeighbor.id, 1))
                    for outsideRegion in outsideRegions:
                        for possibleOpponentRegion in possibleOpponentRegions:
                            getRegionDistance(outsideRegion[0], possibleOpponentRegion)
                            #its going to get the distance between every outside double border and the possibleOpponentRegion, what now?









    print(bonusEfficiencies)


    #for item in mapStates:

    return None
        


"""
for i in range(1,1000):
    get_cords()
    time.sleep(2)
"""

# global variables, I don't care what anyone says... desperate data calls for desperate measures
# screen = (x_pad + 1, y_pad+1, x_pad + 1710, y_pad + 903)

playerColor = ""
opponentColor = ""
neutralColor = ""

# how much higher or lower to scan for the territory's color
yPixelOffset = 16
#the diameter of the box screenshot that will be used to capture the region
# boxSize = 34

#click(1183, 280)
getPlayerColors()

map = Map()
currentMap = MME()

'''
#updateMap()

#placeArmies([(24, 5)])

print(getTurnNumber())
'''
'''
data = "what's up"
secondary = ""
try:
    with open('dataew.txt', 'r') as f:
        secondary = json.load(f)
        #json.dump(data, f, ensure_ascii=False)
except:
    with open('dataew.txt', 'w') as f:
        json.dump(data, f)

#print(secondary)
'''
setupSuperRegions(currentMap.superRegions_data)
setupRegions(currentMap.regions_data)
setupNeighbors(currentMap.neighbors_data)

gameId = str(getGameId())
turnNumber = getTurnNumber()
mapStates = {}
try:
    with open(gameId + '.txt', 'r') as f:
        mapStates = json.load(f)
except:
    with open(gameId + '.txt', 'w') as f:
        json.dump("", f)

if turnNumber + 1 > len(mapStates):
    control.click(Buttons.menu)
    control.press('g')
    time.sleep(0.3) # tell the bot to slow down a little because WZ's processing speed takes hours

    for i in range(0, turnNumber + 1):
        if i > len(mapStates) - 1:
            if i == 0:
                time.sleep(0.1)
                mapStates[i] = getMapState('picking phase')
            else:
                time.sleep(0.1)
                mapStates[i] = getMapState('regular turn')
            #control.click(Buttons.forwardTurn[0], Buttons.forwardTurn[1])
            #control.click(Buttons.forwardMove[0], Buttons.forwardMove[1])
        
        if i < turnNumber:
            control.press('right')
            control.press('down')
    
    with open(gameId + '.txt', 'w') as f:
        json.dump(mapStates, f, indent=2)
    
    control.click(Buttons.exitHistory)

makeOrders(mapStates, turnNumber)




'''
width = win32api.GetSystemMetrics(0)
height = win32api.GetSystemMetrics(1)
midWidth = int((width + 1) / 2)
midHeight = int((height + 1) / 2)

territoryNumber = 117

imgScanRGB = ImageGrab.grab()

state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
while True:
    a = win32api.GetKeyState(0x01)
    if a != state_left:  # Button state changed
        state_left = a
        if a < 0:
            print(territoryNumber)
            print(get_cords())
            print(imgScanRGB.getpixel(win32api.GetCursorPos()))
            territoryNumber = territoryNumber + 1

    time.sleep(0.001)
'''

'''
for i in range(0,1000):
    x = get_cords[0]
    y = get_cords[1]
    click(x, y)
    time.sleep(1.9)
'''
"""
print(MME().superRegions_data)

setupSuperRegions(currentMap.superRegions_data)
"""




#im = screenGrab()
#im.getpixel(371)
#setupRegions(MME.regions_data)
#setupNeighbors(MME.neighbors_data)
#florida = Region(1, 1, 213, 213) "0","3


'''
# TIME TEST
def sortby(somelist, n):
    nlist = [(x[n], x) for x in somelist]
    nlist.sort()
    return [val for (key, val) in nlist]


yo = []
yo.extend([(2, "what is love"), (3, "how is love"), (1, "what is life"), (4, "who cares"), (5, "dig deep"), (6, "madeon and porter robinson")])
t0 = time.time()
for i in range(0, 10000):
    k = sorted(yo, key=lambda tup: tup[0])
t1 = time.time()
print(yo)
print(t1-t0)

to = []
to.extend([(2, "what is love"), (3, "how is love"), (1, "what is life"), (4, "who cares"), (5, "dig deep"), (6, "madeon and porter robinson")])
t2 = time.time()
for i in range(0, 10000):
    r = sortby(to, 0)
t3 = time.time()
print(to)
print(t3-t2)
'''




pass

