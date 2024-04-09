#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, star, diamond

windowSize = 600
helpWindow = False
helpWin = 0
mainWin = 0
centered = False

beginTime = 0
countTime = 0
score = 0
finalScore = 0
canStart = False
overReason = ""
speed = 1.0

#for wheel spinning
tickTime = 0

#creating objects
objectArray = []
jeep1Obj = jeep.jeep('p')
jeep2Obj = jeep.jeep('g')
jeep3Obj = jeep.jeep('r')

allJeeps = [jeep1Obj, jeep2Obj, jeep3Obj]
jeepNum = 0
jeepObj = allJeeps[jeepNum]
#personObj = person.person(10.0,10.0)

#concerned with camera
eyeX = 0.0
eyeY = 2.0
eyeZ = 10.0
midDown = False
topView = False
behindView = False

#concerned with panning
nowX = 0.0
nowY = 0.0

angle = 0.0
radius = 10.0
phi = 0.0

#concerned with scene development
land = 20
gameEnlarge = 10

#concerned with obstacles (cones) & rewards (stars)
coneAmount = 15
starAmount = 5 #val = -10 pts
diamondAmount = 1 #val = deducts entire by 1/2
diamondObj = diamond.diamond(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))
usedDiamond = False

allcones = []
allstars = []
obstacleCoord = []
rewardCoord = []
ckSense = 5.0

#concerned with lighting#########################!!!!!!!!!!!!!!!!##########
applyLighting = True

fov = 30.0
attenuation = 1.0

light0_Position = [0.0, 1.0, 1.0, 1.0]
light0_Intensity = [0.75, 0.75, 0.75, 0.25]

light1_Position = [0.0, 0.0, 0.0, 0.0]
light1_Intensity = [0.25, 0.25, 0.25, 0.25]

matAmbient = [1.0, 1.0, 1.0, 1.0]
matDiffuse = [0.5, 0.5, 0.5, 1.0]
matSpecular = [0.5, 0.5, 0.5, 1.0]
matShininess  = 100.0



#--------------------------------------developing scene---------------
class Scene:
    axisColor = (0.5, 0.5, 0.5, 0.5)
    axisLength = 50   # Extends to positive and negative on all axes
    landColor = (.47, .53, .6, 0.5) #Light Slate Grey
    landLength = land  # Extends to positive and negative on x and y axis
    landW = 1.0
    landH = 0.0
    cont = gameEnlarge
    ribbonW = 1.0
    ribbonH = 0.0
    
    def draw(self):
        self.drawAxis()
        self.drawLand()

    def drawAxis(self):
        glColor4f(self.axisColor[0], self.axisColor[1], self.axisColor[2], self.axisColor[3])
        glBegin(GL_LINES)
        glVertex(-self.axisLength, 0, 0)
        glVertex(self.axisLength, 0, 0)
        glVertex(0, -self.axisLength, 0)
        glVertex(0, self.axisLength, 0)
        glVertex(0, 0, -self.axisLength)
        glVertex(0, 0, self.axisLength)
        glEnd()

    def drawLand(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, roadTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # accelerating ribbon
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, ribbonTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength / 2, 0.1, self.cont * self.landLength / 2 + 3)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength / 2, 0.1, self.landLength * self.cont / 2 - 3)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(0, 0.1, self.landLength * self.cont / 2 - 3)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(0, 0.1, self.cont * self.landLength / 2 + 3)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # adding grass
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, grassTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength * 10, -0.1, 2 * self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength * 10, -0.1, 2 * (-self.landLength))

        glTexCoord2f(self.landW, self.landW)
        glVertex3f((-self.landLength) * 10, -0.1, 2 * (-self.landLength))

        glTexCoord2f(self.landW, self.landH)
        glVertex3f((-self.landLength) * 10, -0.1, 2 * self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # add finish line
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, finishLineTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, self.cont * self.landLength + 3)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength + 3)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)


#--------------------------------------populating scene----------------
def staticObjects():
    global objectArray
    objectArray.append(Scene())
    print ('append')


def display():
    global jeepObj, canStart, score, beginTime, countTime
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if (applyLighting == True):
        myLights()
        glPushMatrix()
        glLoadIdentity()
        gluLookAt(0.0, 3.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        glLightfv(GL_LIGHT0, GL_POSITION, light0_Position)
        pointPosition = [0.0,-10.0,0.0]

        glDisable(GL_LIGHTING)

        glColor3f(light0_Intensity[0], light0_Intensity[1], light0_Intensity[2])

        glTranslatef(light0_Position[0], light0_Position[1], light0_Position[2])

        glutSolidSphere(0.025, 36, 24)

        glTranslatef(-light0_Position[0], -light0_Position[1], -light0_Position[2])
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbient)
        for x in range(1,4):
            for z in range(1,4):
                 matDiffuse = [float(x) * 0.3, float(x) * 0.3, float(x) * 0.3, 1.0] 
                 matSpecular = [float(z) * 0.3, float(z) * 0.3, float(z) * 0.3, 1.0]  
                 matShininess = float(z * z) * 10.0
                 ## Set the material diffuse values for the polygon front faces. 
                 glMaterialfv(GL_FRONT, GL_DIFFUSE, matDiffuse)

                 ## Set the material specular values for the polygon front faces. 
                 glMaterialfv(GL_FRONT, GL_SPECULAR, matSpecular)

                 ## Set the material shininess value for the polygon front faces. 
                 glMaterialfv(GL_FRONT, GL_SHININESS, matShininess)

                 ## Draw a glut solid sphere with inputs radius, slices, and stacks
                 glutSolidSphere(0.25, 72, 64)
                 glTranslatef(1.0, 0.0, 0.0)

            glTranslatef(-3.0, 0.0, 1.0)
        glPopMatrix()
   
    beginTime = 6-score
    countTime = score-6
    if (score <= 5):
        canStart = False
        glColor3f(1.0,0.0,1.0)
        text3d("Begins in: "+str(beginTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    elif (score == 6):
        canStart = True
        glColor(1.0,0.0,1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    else:
        canStart = True
        glColor3f(0.0,1.0,1.0)
        text3d("Scoring: "+str(countTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)

    for obj in objectArray:
        obj.draw()
    for cone in allcones:
        cone.draw()
    for star in allstars:
        star.draw()

    if (usedDiamond == False):
        diamondObj.draw()
    
    jeepObj.draw()
    jeepObj.drawW1()
    jeepObj.drawW2()
    jeepObj.drawLight()
    #personObj.draw()
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score
    jeepObj.rotateWheel(-0.1 * tickTime)    
    glutPostRedisplay()
    
    curTime = glutGet(GLUT_ELAPSED_TIME)
    tickTime =  curTime - prevTime
    prevTime = curTime
    score = int(curTime/1000)

    # if the game has not concluded
    if overReason == '' and finalScore == 0:
        collisionCheck()

#---------------------------------setting camera----------------------------
def setView():
    global eyeX, eyeY, eyeZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)
    if (topView == True):
        gluLookAt(0, 10, land*gameEnlarge/2, 0, jeepObj.posY, land*gameEnlarge/2, 0, 1, 0)
    elif (behindView ==True):
        gluLookAt(jeepObj.posX, jeepObj.posY + 1.0, jeepObj.posZ - 2.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1, 0) 
    else:
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    
    glutPostRedisplay()    

def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)

    if behindView == True:
        gluLookAt(jeepObj.posX, jeepObj.posY + 5.0, jeepObj.posZ - 10.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1,
                  0)

    if topView == True:
        gluLookAt(jeepObj.posX, jeepObj.posY + 5.0, jeepObj.posZ + 10.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1,
                  0)

    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()

#-------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown, eyeX, eyeY, eyeZ
    if (button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN):
        midDown = True
    else:
        midDown = False    

    if button == 3 and state == GLUT_DOWN:
        eyeX *= 0.9
        eyeY *= 0.9
        eyeZ *= 0.9
    elif button == 4 and state == GLUT_DOWN:
        eyeX *= 1.1
        eyeY *= 1.1
        eyeZ *= 1.1
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
        

def motionHandle(x,y):
    global nowX, nowY, angle, eyeX, eyeY, eyeZ, phi
    if (midDown == True):
        pastX = nowX
        pastY = nowY 
        nowX = x
        nowY = y
        if (nowX - pastX > 0):
            angle -= 0.25
        elif (nowX - pastX < 0):
            angle += 0.25
        elif (nowY - pastY > 0): #look into looking over and under object...
            phi += 0.25
        elif (nowX - pastY <0):
            phi -= 0.25
        eyeX = radius * math.sin(angle) 
        eyeZ = radius * math.cos(angle)
        eyeY = radius * math.sin(phi)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
    #print eyeX, eyeY, eyeZ, nowX, nowY, radius, angle
    #print "getting handled"



def specialKeys(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    global jeepObj, centered, speed

    # move the car only if score begin time <= 0 (or score >= 6)
    if score >= 6 and keypress == GLUT_KEY_UP:
        jeepObj.move(False, speed)

    elif score >= 6 and keypress == GLUT_KEY_DOWN:
        jeepObj.move(False, -speed)

    if score >= 6 and keypress == GLUT_KEY_LEFT:
        jeepObj.move(True, speed)

    elif score >= 6 and keypress == GLUT_KEY_RIGHT:
        jeepObj.move(True, -speed)

    # update object view after each movement
    if centered == True:
        setObjView()

def myKeyboard(key, mX, mY):
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered, helpWin, overReason, topView, behindView
    if key == b"h":
        print ("h pushed"+ str(helpWindow))
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow(b'Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(myKeyboard)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print (glutGetWindow())
            glutHideWindow()
            #glutDestroyWindow(helpWin)
            glutMainLoop()
    # things can do
    # this is the part to set special functions, such as help window.

    elif key == b'>':
        jeepObj.sizeX *= 1.05
        jeepObj.sizeY *= 1.05
        jeepObj.sizeZ *= 1.05

    elif key == b'<':
        jeepObj.sizeX /= 1.05
        jeepObj.sizeY /= 1.05
        jeepObj.sizeZ /= 1.05

    elif key == b'b':
        centered = not centered
        behindView = centered
        topView = False

        # update object view after chaning viewing option
        if centered == True:
            setObjView()

    elif key == b'c':
        centered = not centered
        topView = centered
        behindView = False

        # update object view after chaning viewing option
        if centered == True:
            setObjView()

    elif key == b'l':
        jeepObj.lightOn = not jeepObj.lightOn

    elif key == b'q':
        glutLeaveMainLoop()

#-------------------------------------------------tools----------------------       
def drawTextBitmap(string, x, y): #for writing text to display
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def text3d(string, x, y, z):
    glRasterPos3f(x,y,z)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def dist(pt1, pt2):
    a = pt1[0]
    b = pt1[1]
    x = pt2[0]
    y = pt2[1]
    return math.sqrt((a-x)**2 + (b-y)**2)

def noReshape(newX, newY): #used to ensure program works correctly when resized
    glutReshapeWindow(windowSize,windowSize)

#--------------------------------------------making game more complex--------
def addCone(x,z):
    allcones.append(cone.cone(x,z))
    obstacleCoord.append((x,z))

def addStar(x, z):
    print(allstars)
    allstars.append(star.star(x, z))
    rewardCoord.append((x, z))

def collisionCheck():
    global overReason, score, usedDiamond, countTime, speed
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()

    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()

    for reward in rewardCoord:
        if dist((jeepObj.posX, jeepObj.posZ), reward) <= ckSense:
            print("Star bonus!")
            allstars.pop(rewardCoord.index(reward))
            rewardCoord.remove(reward)
            countTime -= 10

    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print ("Diamond bonus!")
        countTime /= 2
        usedDiamond = True

    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()

    if land * gameEnlarge / 2 + 3 >= jeepObj.posZ >= land * gameEnlarge / 2 - 3 and land / 2 > jeepObj.posX > 0:
        speed = 5.0

#----------------------------------multiplayer dev (using tracker)-----------
def recordGame():
    with open('results.csv', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)
        spamwriter.writerow([st] + [finalScore])
    
#-------------------------------------developing additional windows/options----
def gameOver():
    global finalScore
    print ("Game completed!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow(b'Game Over!')
    glutDisplayFunc(overScreen)
    glutMainLoop()
    
def gameSuccess():
    global finalScore
    print ("Game success!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow(b'Complete!')
    glutDisplayFunc(winScreen)
    glutMainLoop()

def winScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Completed Trial!" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score is: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def overScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,1.0)
    drawTextBitmap("Incomplete Trial" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Because you..." , -1.0, 0.5)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(overReason, -1.0, 0.35)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score stopped at: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()

def showHelp():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,0.0)
    drawTextBitmap("Help Guide" , -0.2, 0.85)
    glColor3f(0.0,0.0,1.0)
    drawTextBitmap("describe your control strategy." , -1.0, 0.7)
    glutSwapBuffers()

#----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    try:
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGBX",0,-1)#tostring("raw", "RGBX", 0, -1)
    except Exception:
        print ("Error:")
        print ("Switching to RGBA mode.")
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGB",0,-1)#tostring("raw", "RGBA", 0, -1)

    tempID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tempID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return tempID

def loadSceneTextures():
    global roadTextureID
    roadTextureID = loadTexture("../img/road2.png")

    global ribbonTextureID
    ribbonTextureID = loadTexture("../img/arrows.jpg")

    global grassTextureID
    grassTextureID = loadTexture("../img/grass.png")

    global finishLineTextureID
    finishLineTextureID = loadTexture("../img/blackWhiteSquare.jpg")
    
#-----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)                
    glEnable(GL_LIGHT0)                 
    glEnable(GL_DEPTH_TEST)              
    glEnable(GL_NORMALIZE)               
    glClearColor(0.2, 0.3, 0.4, 1.0)

applyAmbient = True
applyDiffuse = True
applySpecular = True

def myLights():
    global applyAmbient
    global applyDiffuse
    global applySpecular

    if applyAmbient:
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 0.2])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [1, 1, 1, 1])
    else:
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0, 0, 0, 0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0, 0, 0, 0])

    if applyDiffuse:
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(GL_LIGHT1, GL_DIFFUSE, [1, 1, 1, 1])
    else:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0, 0, 0, 0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0, 0, 0, 0])

    if applySpecular:
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [1, 1, 1, 1])
    else:
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0, 0, 0, 0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0, 0, 0, 0])

def myMenu(value):
    global applyAmbient, applyDiffuse, applySpecular, mainWin, windowSize

    if value == 1:
        applyAmbient = not applyAmbient

    elif value == 2:
        applyDiffuse = not applyDiffuse

    elif value == 3:
        applySpecular= not applySpecular

    elif value > 3:

        if value == 4:
            windowSize = 300

        elif value == 5:
            windowSize = 600

        elif value == 6:
            windowSize = 900

        glutDestroyWindow(mainWin)
        main()

    return 0

#~~~~~~~~~~~~~~~~~~~~~~~~~the finale!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    glutInit()

    global prevTime, mainWin
    prevTime = glutGet(GLUT_ELAPSED_TIME)
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    # things to do
    # change the window resolution in the game
    glutInitWindowSize(windowSize, windowSize)
    
    glutInitWindowPosition(0, 0)
    mainWin = glutCreateWindow(b'CS4182')
    glutDisplayFunc(display)
    glutIdleFunc(idle)#wheel turn

    setView()
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)   

    glutMouseFunc(mouseHandle)
    glutMotionFunc(motionHandle)
    glutSpecialFunc(specialKeys)
    glutKeyboardFunc(myKeyboard)
    
    glutReshapeFunc(noReshape)
    # things to do
    # add a menu
    glutCreateMenu(myMenu)

    glutAddMenuEntry("Ambient", 1)
    glutAddMenuEntry("Diffuse", 2)
    glutAddMenuEntry("Specular & Position", 3)
    glutAddMenuEntry("Small Window", 4)
    glutAddMenuEntry("Medium Window", 5)
    glutAddMenuEntry("Large Window", 6)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    loadSceneTextures()

    jeep1Obj.makeDisplayLists()
    jeep2Obj.makeDisplayLists()
    jeep3Obj.makeDisplayLists()
    #personObj.makeDisplayLists()

    # things to do
    # add a automatic object
    for i in range(coneAmount):#create cones randomly for obstacles, making sure to give a little lag time in beginning by adding 10.0 buffer
        addCone(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))

    # things to do
    # add stars
    for i in range(starAmount):
        addStar(random.randint(-land, land), random.randint(10.0, land * gameEnlarge))

    for cone in allcones:
        cone.makeDisplayLists()

    for star in allstars:
        star.makeDisplayLists()
    
    diamondObj.makeDisplayLists()
    
    staticObjects()
    if (applyLighting == True):
        initializeLight()
    glutMainLoop()



    
main()

