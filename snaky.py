import random, pygame, sys, operator, os, time
from pygame.locals import *
F = 70
WIDTH = 1800
HEIGHT = 1200
SIZE = 60
assert WIDTH% SIZE== 0 
assert HEIGHT% SIZE== 0
CELLWIDTH = int(WIDTH / SIZE)
CELLHEIGHT = int(HEIGHT / SIZE)
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
YELLOW  = ( 40,  40,  40)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HEAD = 0 

def main():
    global A, DISPLAY, FONT
    global window,softwindow
    window = []
    softwindow = []
    softwindow = findSoftWall()
    window = findWall()
    pygame.init()
    A = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
    FONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('SNAKE GAME')
    showStartScreen()


    while True:
        runGame()
        showGameOverScreen()


def runGame():
    global status
    status = False
    statusCount = -1
    xaxis = 5
    yaxis = 0 
    snake = [{'x': xaxis+ 6, 'y': yaxis},
                  {'x': xaxis + 5, 'y': yaxis},
                  {'x': xaxis+ 4, 'y': yaxis},
                  ]
                  
    direction = RIGHT
    directionList = [RIGHT]
    PATH = []

    apple = {'x': xaxis+8,     'y': yaxis}
    lastApple = {'x':xaxis-1,   'y': yaxis -1}
    PATH = calculatePath(snake,apple,True)
    directionList = calcDirection(PATH)
    lastWall = 0

    while True: 
        for event in pygame.event.get(): 
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                  if event.key == K_ESCAPE:
                      terminate()
       
        if snake[HEAD]['x'] == -1 or snake[HEAD]['x'] == CELLWIDTH or snake[HEAD]['y'] == -1 or snake[HEAD]['y'] == CELLHEIGHT:
            terminate()
            return 
        
        for snakeBody in snake[1:]:
            if snakeBody['x'] == snake[HEAD]['x'] and snakeBody['y'] == snake[HEAD]['y']:
                terminate()
                return 
        if snake[HEAD]['x'] == apple['x'] and snake[HEAD]['y'] == apple['y']:
           
            lastApple = apple
            apple = getRandomLocation(snake) 
            drawApple(apple,lastApple)                        
            PATH = calculatePath(snake,apple,True)  
            if not PATH:
              status = True
              statusCount = 10000
            elif PATH == 'stall':
              status = True
              statusCount = int(len(snake)/2)
            else:
              directionList = calcDirection(PATH)
        else:
            del snake[-1] # remove worm's tail segment


        lastDirection = direction

       
        if status and not directionList:
          onlyDirection = calcOnlyDirection(snake)
          if onlyDirection and onlyDirection == lastDirection:
            directionList.append(onlyDirection)
            print('only direction:', direction)
          else:
            if safeToGo(snake,direction,lastWall):       
             
              directionList.append(direction)      
            elif (not findNewHead(direction,snake) in snake) or (findNewHead(direction,snake) in window):
              directionList.append(direction)
            else:
              lastDirection = direction

              PATH = calculatePath(snake,apple,False)
              if PATH != [] and PATH != 'stall':
                status = False
                statusCount = -1
                directionList = calcDirection(PATH)
              else:
                if checkLastWall(snake):
                  lastWall = checkLastWall(snake)
                directionList.extend(findBetterDirection(snake,direction,lastWall))
                if calcArea(findNewHead(directionList[0],snake), snake, lastWall)<3:
                  directionList = [lastDirection]
                
            statusCount = statusCount - 1
           
            if statusCount < 1:
        
              status = False
              prevLastWall = lastWall
              lastWall = 0
              directionList.append(lastDirection)
              PATH = calculatePath(snake,apple,True)
              if not PATH:
                status = True
                statusCount = 10000
                lastWall = prevLastWall
              elif PATH == 'stall':
                status = True
                statusCount = int(len(snake)/2)
                lastWall = prevLastWall
              else:
                directionList = calcDirection(PATH)
        nextHead = findNewHead(directionList[0],snake)
        
        if status:
          if AreaIsTooSmall(CELLWIDTH,nextHead, snake, lastWall):      
            lastWall = 0
            directionList = findNextDirection(snake, directionList[0],0)
            print('almost died, recalcualting...',snake[0],directionList)          
        

        direction = directionList.pop(0)
        newHead = findNewHead(direction, snake)
        snake.insert(0, newHead)
        DISPLAY.fill(BGCOLOR)
        drawGrid()
        drawWorm(snake)
        drawApple(apple,lastApple)
        drawScore(len(snake) - 3)
        pygame.display.update()
        A.tick(F)

def calcOnlyDirection(worm):
    count = 4 
    ways = getNeighborhood(worm[0])
    theWay = 0
    for each in ways:
      if each in worm:
        count = count - 1
      else:
        theWay = each
    if count == 1:
      return calcDirection([worm[0],theWay])
    else:
      return 0

def getNextwindow(lastWall):
    walls = []

    loopcount = 0 
    for _ in range(CELLHEIGHT):
      if lastWall == RIGHT:
        walls.append({'x':0, 'y':loopcount})
      if lastWall == LEFT:
        walls.append({'x':CELLWIDTH-1, 'y':loopcount})
      loopcount = loopcount + 1
   
    loopcount = 0 
    for _ in range(CELLWIDTH):
      if lastWall == DOWN:
        walls.append({'x':loopcount, 'y':0})
      if lastWall == UP:
        walls.append({'x':loopcount, 'y':CELLHEIGHT-1})
      loopcount = loopcount + 1
    return walls

def safeToGo(worm,direction,lastWall):
    listOfNo = window + worm
    listOfNo.extend(getNextwindow(lastWall))
    head = worm[0]
    forward = worm[0]
    forwardLeft = worm[0]
    forwardRight = worm[0]
    left = worm[0]
    right = worm[0]
    if direction == UP:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1}
        forward = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 2}
        forwardLeft = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y'] - 1}
        forwardRight = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y'] - 1}
        left = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']}
        right = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']}
    elif direction == DOWN:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1}
        forward = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 2}
        forwardLeft = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y'] + 1}
        forwardRight = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y'] + 1}
        left = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']}
        right = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']}
    elif direction == LEFT:
        newHead = {'x': worm[HEAD]['x'] - 1, 'y': worm[HEAD]['y']}
        forward = {'x': worm[HEAD]['x'] - 2, 'y': worm[HEAD]['y']}
        forwardLeft = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y'] + 1}
        forwardRight = {'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y'] - 1}
        left = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']+1}
        right = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']-1}
    elif direction == RIGHT:
        newHead = {'x': worm[HEAD]['x'] + 1, 'y': worm[HEAD]['y']}
        forward = {'x': worm[HEAD]['x'] + 2, 'y': worm[HEAD]['y']}
        forwardLeft = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y'] - 1}
        forwardRight = {'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y'] + 1}
        left = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']-1}
        right = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']+1}

   
    if (forwardLeft in listOfNo and not left in listOfNo) or (forwardRight in listOfNo and not right in listOfNo):

      return False
    if newHead in listOfNo:
      return False
    waysToGo = []
    waysToGo = getNeighborhood(newHead)
    count = len(waysToGo)
    for each in waysToGo:
      if each in listOfNo:
        count = count - 1
    if count < 1:
      return False
    elif count < 2 and not (forward in listOfNo):
      return False
    else:
      return True

def checkLastWall(worm):
    x = worm[0]['x']
    y = worm[0]['y']
    if x == 0:
      return LEFT
    elif x == CELLWIDTH - 1:
      return RIGHT
    elif y == 0:
      return UP
    elif y == CELLHEIGHT -1:
      return DOWN
    else:
      return 0

def checkSmartTurn(worm,listOfNo,direction1,direction2):
    if direction1 == UP or direction1 == DOWN:
      if direction2 == RIGHT:
        if {'x': worm[HEAD]['x']+3, 'y': worm[HEAD]['y']} in listOfNo and (not {'x': worm[HEAD]['x']+2, 'y': worm[HEAD]['y']} in listOfNo):
          return True
        else:
          return False
      if direction2 == LEFT:
        if {'x': worm[HEAD]['x']-3, 'y': worm[HEAD]['y']} in listOfNo and (not {'x': worm[HEAD]['x']-2, 'y': worm[HEAD]['y']} in listOfNo):
          return True
        else:
          return False
    if direction1 == LEFT or direction1 == RIGHT:
      if direction2 == UP:
        if {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']-3} in listOfNo and (not {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']-2} in listOfNo):
          return True
        else:
          return False
      if direction2 == DOWN:
        if {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']+3} in listOfNo and (not {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']+2} in listOfNo):
          return True
        else:
          return False    

def findBetterDirection(worm, direction,lastWall):
    listOfNo = list(worm)
    smartTurn = False   #dont kill yourself in the corner 
    if direction == UP:
        areaLeft = calcArea({'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']},worm,lastWall)
        areaRight = calcArea({'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']},worm,lastWall)
        if areaLeft == 0 and areaRight == 0:
          return [direction]
        areaStraight = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']-1},worm,lastWall)
        maxArea = max(areaLeft,areaRight,areaStraight)
        print ('Options:', 'left:',areaLeft,'right:',areaRight,'straight:',areaStraight)
        if maxArea == areaStraight:
          return [direction]
        elif maxArea == areaLeft:
          if checkSmartTurn(worm,listOfNo,direction,LEFT):
            print('Smart Turn Enabled')
            return [LEFT, LEFT]
          else:
            return [LEFT, DOWN]
        else:
          if checkSmartTurn(worm,listOfNo,direction,RIGHT):
            print('Smart Turn Enabled')
            return [RIGHT, RIGHT]
          else:
            return [RIGHT,DOWN]

    if direction == DOWN:
        areaLeft = calcArea({'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']},worm,lastWall)
        areaRight = calcArea({'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']},worm,lastWall)
        if areaLeft == 0 and areaRight == 0:
          return [direction]
        areaStraight = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']+1},worm,lastWall)
        maxArea = max(areaLeft,areaRight,areaStraight)
        print ('Options:','left:',areaLeft,'right:',areaRight,'straight:',areaStraight)
        if maxArea == areaStraight:
          return [direction]
        elif areaLeft == maxArea:
          if checkSmartTurn(worm,listOfNo,direction,LEFT):
            print('Smart Turn Enabled')
            return [LEFT, LEFT]
          else:
            return [LEFT, UP]
        else:
          if checkSmartTurn(worm,listOfNo,direction,RIGHT):
            print('Smart Turn Enabled')
            return [RIGHT, RIGHT]
          else:
            return [RIGHT,UP]

    elif direction == LEFT:
        areaUp = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1},worm,lastWall)
        areaDown = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1},worm,lastWall)
        if areaUp == 0 and areaDown == 0:
          return [direction]
        areaStraight = calcArea({'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']},worm,lastWall)
        maxArea = max(areaStraight,areaUp,areaDown)
        print ('Options:','up:',areaUp,'down:',areaDown,'straight:',areaStraight)
        if maxArea == areaStraight:
          return [direction]       
        elif maxArea == areaUp:
          if checkSmartTurn(worm,listOfNo,direction,UP):
            print('Smart Turn Enabled')
            return [UP, UP]
          else:
            return [UP,RIGHT]
        else:
          if checkSmartTurn(worm,listOfNo,direction,DOWN):
            print('Smart Turn Enabled')
            return [DOWN, DOWN]
          else:
            return [DOWN,RIGHT]

    elif direction == RIGHT:
        areaUp = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1},worm,lastWall)
        areaDown = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1},worm,lastWall)
        if areaUp == 0 and areaDown == 0:
          return [direction]
        areaStraight = calcArea({'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']},worm,lastWall)
        maxArea = max(areaStraight,areaUp,areaDown)
        print ('Options:','up:',areaUp,'down:',areaDown,'straight:',areaStraight)
        if maxArea == areaStraight:
          return [direction]              
        elif areaUp ==maxArea:
          if checkSmartTurn(worm,listOfNo,direction,UP):
            print('Smart Turn Enabled')
            return [UP, UP]
          else:
            return [UP,LEFT]
        else:
          if checkSmartTurn(worm,listOfNo,direction,DOWN):
            print('Smart Turn Enabled')
            return [DOWN, DOWN]
          else:
            return [DOWN,LEFT]

def findNextDirection(worm, direction,lastWall):
    listOfNo = list(worm)
    areaLeft = calcArea({'x': worm[HEAD]['x']-1, 'y': worm[HEAD]['y']},worm,lastWall)
    areaRight = calcArea({'x': worm[HEAD]['x']+1, 'y': worm[HEAD]['y']},worm,lastWall)
    areaUp = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1},worm,lastWall)
    areaDown = calcArea({'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1},worm,lastWall)
    maxArea = max(areaLeft,areaRight,areaUp,areaDown)
    if maxArea == areaUp:
      return [UP]
    elif maxArea == areaDown:
      return [DOWN]
    elif maxArea == areaLeft:
      return [LEFT]
    else:
      return [RIGHT]

def calcArea(point, worm, lastWall):
    nextWall = getNextwindow(lastWall)
    if point in worm or point in window or point in nextWall:
      return 0
    tailBonus = 0
    q = []
    searchPoints = []
    searchPoints.append(point)
    while (searchPoints):
      i = searchPoints.pop()
      for each in getNeighborhood(i):
        if not each in q:
          if not (each in worm or each in window or point in nextWall):
            searchPoints.append(each)
        if each == worm[-1]:
          tailBonus = 200
      q.append(i)
    return len(q)+tailBonus

def AreaIsTooSmall(bound,point, worm, lastWall):
    nextWall = getNextwindow(lastWall)
    if point in worm or point in window or point in nextWall:
      return True
    tailBonus = 0
    q = []
    searchPoints = []
    searchPoints.append(point)
    while (searchPoints):
      i = searchPoints.pop()
      for each in getNeighborhood(i):
        if not each in q:
          if not (each in worm or each in window or point in nextWall):
            searchPoints.append(each)
        if each == worm[-1]:
          tailBonus = 200
      q.append(i)
      if (len(q) + tailBonus) > bound:
        return False
    return True

def calcCost(point,worm):
    print ('calculating cost of point', point)
    neibors = getNeighborhood(point)
    for each in neibors:
      if each in worm[1:]:
        return worm.index(each)
    return 999

def calcDirection(path):
    '''Converting point-path to step by step direction'''
    lastPoint = path[0]
    directions = []
    nextDirection = ''
    for currentPoint in path:
      if (currentPoint['x'] > lastPoint['x']):
        nextDirection = RIGHT
      elif (currentPoint['x'] < lastPoint['x']):
        nextDirection = LEFT
      else:
        if (currentPoint['y'] > lastPoint['y']):
          nextDirection = DOWN
        elif (currentPoint['y'] < lastPoint['y']):
          nextDirection = UP
        else:
        
          continue
    
      lastPoint = currentPoint
      directions.append(nextDirection)
    
    return directions

def calculatePath(worm,apple,softCalculation):
  oldWorm = list(worm)

  path = mainCalculation(worm,apple,softCalculation)
  if not path:
    return []
  else:
    pathCopy = list(path)
    pathCopy.reverse()
    newWorm = pathCopy + oldWorm
    pathOut = mainCalculation(newWorm,newWorm[-1],False)
    if not pathOut:
      print('No path out, dont go for apple')
      return 'stall'
    else:
      return path

def mainCalculation(worm,apple,softCalculation):
  pointsToPath= []
  discoverEdge = []
  newPoints = []
  exhaustedPoints = []
  numberOfPoints = 1         #if all point tested go back one point
  findingPath = True  #false
  listOfNo = getListOfNo(worm)
  softListOfNo = getSoftListOfNo(worm)
  softListOfNo.extend(softwindow)
  discoverEdge.append(worm[0])
  exhaustedPoints.append(worm[0])
  lastPoint = discoverEdge[-1]
  pointsToPath.append(lastPoint)

  if (apple in softwindow) or (apple in softListOfNo):
    softCalculation = False

  
  while(findingPath and softCalculation):
    lastPoint = discoverEdge[-1]
    newPoints = getNeighborhood(lastPoint)
    newPoints = sorted(newPoints, key = lambda k: calcDistance(k,apple), reverse = True)  #sort newPoints
    numberOfPoints = len(newPoints)
    for point in newPoints:
      if point in softListOfNo:
        
        numberOfPoints = numberOfPoints -1
      elif point in exhaustedPoints:
        
        numberOfPoints = numberOfPoints -1
      else:                                
        discoverEdge.append(point)      
        pointsToPath.append(lastPoint) 
        exhaustedPoints.append(lastPoint)
        #print (point)
      #exhaustedPoints.append(point)
    if numberOfPoints == 0:
      #backtrack
      exhaustedPoints.append(discoverEdge.pop())
      exhaustedPoints.append(pointsToPath.pop())
    if apple in discoverEdge:
      findingPath = 0
    if not discoverEdge:
      softCalculation = False 
      break


  if not softCalculation:
    pointsToPath= []
    discoverEdge = []
    newPoints = []
    exhaustedPoints = []
    numberOfPoints = 1       
    findingPath = True  
    listOfNo = getListOfNo(worm)
    discoverEdge.append(worm[0])
    exhaustedPoints.append(worm[0])
    lastPoint = discoverEdge[-1]
    pointsToPath.append(lastPoint)

  
    while(findingPath):
      lastPoint = discoverEdge[-1]
      newPoints = getNeighborhood(lastPoint)
      newPoints = sorted(newPoints, key = lambda k: calcDistance(k,apple), reverse = True) 
      numberOfPoints = len(newPoints)
      for point in newPoints:
        if point in listOfNo:
    
          numberOfPoints = numberOfPoints -1
        elif point in exhaustedPoints:
          
          numberOfPoints = numberOfPoints -1
        else:                                
          discoverEdge.append(point)        
          pointsToPath.append(lastPoint) 
          exhaustedPoints.append(lastPoint)
          #print (point)
        #exhaustedPoints.append(point)
      if numberOfPoints == 0:
        #backtrack
        exhaustedPoints.append(discoverEdge.pop())
        exhaustedPoints.append(pointsToPath.pop())
      if apple in discoverEdge:
        findingPath = 0
      if not discoverEdge:
        
        return []
    


  ##WHEN DISCOVER EDGE IS EMPTY, TRY FIND TAIL
  pointsToPath.append(apple)       #adding in the last point 
  return pointsToPath

def getNeighborhood(point):      ### NOT NEGATIVE
  neighborhood = []
  if point['x'] < CELLWIDTH:
    neighborhood.append({'x':point['x']+1,'y':point['y']})
  if point['x'] > 0:
    neighborhood.append({'x':point['x']-1,'y':point['y']})
  if point['y'] < CELLHEIGHT:
    neighborhood.append({'x':point['x'],'y':point['y']+1})
  if point['y'] >0:
    neighborhood.append({'x':point['x'],'y':point['y']-1})
  return neighborhood

def calcDistance(point, apple):
  distance = abs(point['x'] - apple['x']) + abs(point['y'] - apple['y'])
  return distance

def getSoftListOfNo(worm):
  listOfNo = []
  listOfNo.extend(getWormSurroundings(worm))
  #listOfNo.extend(softwindow)
  #remove duplicates
  return listOfNo 


def getWormSurroundings(worm):
  listOfNo = []
  headx = worm[0]['x']
  heady = worm[0]['y']
  count = 0
  for each in worm:
    if count == 0:
      listOfNo.append(each)
    else:
      dist = abs (each['x'] - headx) + abs(each['y']-heady)
      countFromBehind = len(worm) - count
      if dist < (countFromBehind+1):
        listOfNo.append(each)
        listOfNo.append({'x':each['x']+1,'y':each['y']})
        listOfNo.append({'x':each['x']-1,'y':each['y']})
        listOfNo.append({'x':each['x'],'y':each['y']+1})
        listOfNo.append({'x':each['x'],'y':each['y']-1})
        listOfNo.append({'x':each['x']+1,'y':each['y']+1})
        listOfNo.append({'x':each['x']-1,'y':each['y']-1})
        listOfNo.append({'x':each['x']-1,'y':each['y']+1})
        listOfNo.append({'x':each['x']+1,'y':each['y']-1})
    count = count + 1
  seen = set()
  newList = []
  for d in listOfNo:
    t = tuple(d.items())
    if t not in seen:
        seen.add(t)
        newList.append(d)
  return newList



def getListOfNo(worm):
  listOfNo = []
  headx = worm[0]['x']
  heady = worm[0]['y']
  count = 0
  for each in worm:
    dist = abs (each['x'] - headx) + abs(each['y']-heady)
    countFromBehind = len(worm) - count
    count = count + 1 
    if dist < (countFromBehind+1):
      listOfNo.append(each)
  listOfNo.extend(window)
  #print ('List of No Go:')
  #print (listOfNo)
  return listOfNo


def findWall():
  walls = []
  #append LEFT RIGHT walls
  loopcount = 0 
  for _ in range(CELLHEIGHT):
    walls.append({'x':-1       , 'y':loopcount})
    walls.append({'x':CELLWIDTH, 'y':loopcount})
    loopcount = loopcount + 1
  #append TOP BOTTOM walls
  loopcount = 0 
  for _ in range(CELLWIDTH):
    walls.append({'x':loopcount, 'y':-1})
    walls.append({'x':loopcount, 'y':CELLHEIGHT})
    loopcount = loopcount + 1
  #print (walls)
  return walls

def findSoftWall():
  walls = []
  #append LEFT RIGHT walls
  loopcount = 0 
  for _ in range(CELLHEIGHT):
    walls.append({'x':0       , 'y':loopcount})
    walls.append({'x':CELLWIDTH-1, 'y':loopcount})
    loopcount = loopcount + 1
  #append TOP BOTTOM walls
  loopcount = 0 
  for _ in range(CELLWIDTH):
    walls.append({'x':loopcount, 'y':0})
    walls.append({'x':loopcount, 'y':CELLHEIGHT-1})
    loopcount = loopcount + 1
  #print (walls)
  return walls


def drawEdgeOfDiscovery(points):
    for point in points:
        x = point['x'] * SIZE
        y = point['y'] * SIZE
        wormSegmentRect = pygame.Rect(x, y, SIZE, SIZE)
        pygame.draw.rect(DISPLAY, ORANGE, wormSegmentRect)
    lastPointRect = pygame.Rect(points[-1]['x']*SIZE, points[-1]['y']*SIZE, SIZE, SIZE)
    pygame.draw.rect(DISPLAY, (255,255,255), wormSegmentRect)
    


def sectionBreak():
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')
  print('AAAAAAAAAAAAAAAAAAAA')


def pauseGame():
  pauseGame = True
  while (pauseGame):
    for event in pygame.event.get():
      if event.type == KEYDOWN:
        if event.key == K_SPACE:
          pauseGame = False

def oppositeDirection(direction):
    if direction == UP:
        return DOWN
    elif direction == DOWN:
        return UP
    elif direction == LEFT:
        return RIGHT
    elif direction == RIGHT:
        return LEFT

def findNewHead(direction,snake):
    if direction == UP:
        newHead = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] - 1}
    elif direction == DOWN:
        newHead = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1}
    elif direction == LEFT:
        newHead = {'x': snake[HEAD]['x'] - 1, 'y': snake[HEAD]['y']}
    elif direction == RIGHT:
        newHead = {'x': snake[HEAD]['x'] + 1, 'y': snake[HEAD]['y']}
    return newHead




def drawPressKeyMsg():
    pressKeySurf = FONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WIDTH - 200, HEIGHT - 30)
    DISPLAY.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('SNAKE GAME!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('SNAKE GAME!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAY.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WIDTH / 2, HEIGHT / 2)
        DISPLAY.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WIDTH / 2, HEIGHT / 2)
        DISPLAY.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()
            return
        pygame.display.update()
        A.tick(F)
        degrees1 += 3
        degrees2 += 7


def terminate():
    print('YOU DIED!')
    pauseGame()
    pygame.quit()
    sys.exit()


def getRandomLocation(worm):
    location = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while(location in worm):
        location = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return location


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WIDTH / 2, 10)
    overRect.midtop = (WIDTH / 2, gameRect.height + 10 + 25)

    DISPLAY.blit(gameSurf, gameRect)
    DISPLAY.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = FONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WIDTH - 120, 10)
    DISPLAY.blit(scoreSurf, scoreRect)

def drawWorm(snake):
    for coord in snake:
        x = coord['x'] * SIZE
        y = coord['y'] * SIZE
        wormSegmentRect = pygame.Rect(x, y, SIZE, SIZE)
        pygame.draw.rect(DISPLAY, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, SIZE - 8, SIZE - 8)
        pygame.draw.rect(DISPLAY, GREEN, wormInnerSegmentRect)

    


def drawApple(coord,lastApple):
    x = coord['x'] * SIZE
    y = coord['y'] * SIZE
    appleRect = pygame.Rect(x, y, SIZE, SIZE)
    pygame.draw.rect(DISPLAY, RED, appleRect)



def drawGrid():
    for x in range(0, WIDTH, SIZE): # draw vertical lines
        pygame.draw.line(DISPLAY, YELLOW, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SIZE): # draw horizontal lines
        pygame.draw.line(DISPLAY, YELLOW, (0, y), (WIDTH, y))

pygame.quit()
if __name__ == '__main__':
    main()
