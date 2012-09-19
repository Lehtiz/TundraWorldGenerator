#!/usr/bin/python
import os
import shutil

import TerrainGenerator
import WorldGenerator
import MaterialGenerator
import TextureGenerator

prefix         = ""
avatar_prefix  = ""
env_prefix     = ""

folder = "./generated/"
terrainSlice = "S5123D", "S5124C", "S5124A", "S5123B"
terrainSuffix = ".xyz"

patchSize = 0
patchCount = 0

def create_assets():
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    global patchSize
    global patchCount
    
    for i in terrainSlice:
        inputFile = i + terrainSuffix
        t = TerrainGenerator.TerrainGenerator()
        t.fromFile(inputFile)
        t.adjustHeight(-200.0)
        outputFile = folder + i + ".ntf" 
        t.toFile(outputFile, overwrite=True)
        
        patchCount = t.width
        patchSize = t.cPatchSize
        
        print "Generating weightmap for the terrain: " + i
        weightFile = folder + i + "weight.png"
        t.toWeightmap(weightFile, fileformat="PNG", overwrite=True)
        
        print "Generating material for " + i
        m = MaterialGenerator.Material(i)
        m.createMaterial_4channelTerrain("terrain", "sand.png", "grass.png", "rock.png", "", weightFile)        
        materialFile = folder + i + ".material"
        m.toFile(materialFile, overwrite=True)
        
    print "Generating terrain textures"
    t = TextureGenerator.TextureGenerator()
    t.createSingleColorTexture(30,100,30,50)
    t.toImage(folder + "grass.png", "PNG", overwrite=True)
    t.createSingleColorTexture(90,83,73,50)
    t.toImage(folder + "rock.png", "PNG", overwrite=True)
    t.createSingleColorTexture(160,136,88,70)
    t.toImage(folder + "sand.png", "PNG", overwrite=True)
        
    

def create_world():
    t_width  = 16*((1500/16)+1)
    t_height = 16*((1500/16)+1)
    w = WorldGenerator.WorldGenerator()
    w.TXML.startScene()
    
    overlapCorrection = 8
    
    # position using x, z coordinates and the width of one terrain tile
    tileWidth = patchCount * patchSize - overlapCorrection
    spot1 = "%f,0,%f,0,0,0,1,1,1" % (0, 0)
    spot2 = "%f,0,%f,0,0,0,1,1,1" % (-tileWidth, 0)
    spot3 = "%f,0,%f,0,0,0,1,1,1" % (-tileWidth, -tileWidth)
    spot4 = "%f,0,%f,0,0,0,1,1,1" % (0, -tileWidth)
    
    spot = spot1, spot2, spot3, spot4
    
    for i, e in enumerate(terrainSlice):
        w.createEntity_Terrain(1, e, transform=spot[i],
                                  width=t_width, height=t_height,
                                  material=prefix + e + ".material",
                                  heightmap=prefix + e + ".ntf")
							  
    w.createEntity_SimpleSky(1, "SimpleSky",
                                texture = env_prefix+"rex_sky_front.dds;" + env_prefix+"rex_sky_back.dds;" + \
                                          env_prefix+"rex_sky_left.dds;" + env_prefix+"rex_sky_right.dds;" + \
                                          env_prefix+"rex_sky_top.dds;" + env_prefix+"rex_sky_bottom.dds")
    w.createEntity_Avatar(1, "AvatarApp",
                             avatar_prefix+"avatarapplication.js;"+ \
                             avatar_prefix+"simpleavatar.js;" + \
                             avatar_prefix+"exampleavataraddon.js")
    w.createEntity_Waterplane(1, "Waterplane", (tileWidth*2), (tileWidth*2), 0.0)
    
    addStuff(w, tileWidth)
    
    w.TXML.endScene()
    w.toFile("./Terrain.txml", overwrite=True)

def addStuff(w, tileWidth):
    print "Generating trees..."
    #random example trees
    import random
    
    for i, e in enumerate(terrainSlice):
        treeAmount = 50 # amount function tries to generate, atm per tile
        treeAdjustment = 6 # acount for difference in the surface and models center
        treeMinHeight = 5 # min height where trees can appear
        treeMaxHeight = 40 # max, beyond this point there will be no trees
        
        #read height data from generated .ntf files
        inputFile = folder + e + ".ntf"
        t = TerrainGenerator.TerrainGenerator()
        t.fromFile(inputFile)

        #for j in range(treeAmount):
        loop = 0
        maxLoop = 500
        # try to generate the amount of trees specified above, stop after 500 tries to prevent infi loops
        while treeAmount > 0 and loop < maxLoop:
            loop = loop + 1
            x = random.randint(0, tileWidth)
            z = random.randint(0, tileWidth)
            y = t.getHeight(z,x) # z,x like x,y with z being x, coord on its side
            
            #decide wether to create a tree here
            if (y > treeMinHeight and y < treeMaxHeight) and (y < t.getMaxitem()):
                
                #check vegetationmap here with the coordinates 
                # tile, x-coord, y-coord
                if checkVegMap(e,z,x) == 1: # mode1 tree, red in vegmap
                
                    x, z = locationOffset(i, x, z, tileWidth)
                    
                    w.createEntity_Staticmesh(1, "redTree"+str(w.TXML.getCurrentEntityID()),
                                                  mesh="tree.mesh",
                                                  material="",
                                                  transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+treeAdjustment, z))
                    treeAmount = treeAmount - 1 # tree added, reduce counter
                
                elif checkVegMap(e,z,x) == 2: # mode2 tree, blue in vegmap
                
                    x, z = locationOffset(i, x, z, tileWidth)
                    
                    w.createEntity_Staticmesh(1, "blueTree"+str(w.TXML.getCurrentEntityID()),
                                                  mesh="tree.mesh",
                                                  material="",
                                                  transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+treeAdjustment, z))
                    treeAmount = treeAmount - 1 # tree added, reduce counter
                
                 
def checkVegMap(tileName, x, y): # return true if allowed
    from PIL import Image
    #print "reading vegetation map: " + tileName
    #im = Image.open(folder + tileName + "vegetationMap.png") #use this after dynamic veg maps available
    im = Image.open(tileName + "vegetationMap.png")
    pix = im.load()
    
    pixel = pix[x,y] # returns tuple rgb
    
    #red do something
    if pixel[0] == 255:
        #print str(x) + "," + str(y) + " red"
        return 1
        
    #green do nothing
    elif pixel[1] == 255:
        #print str(x) + "," + str(y) + " green"
        return 0
        
    #blue do something
    elif pixel[2] == 255:
        #print str(x) + "," + str(y) + " blue"
        return 2
        
def locationOffset(tile, x, z, tileWidth):
#placement correction, generated trees to their own slice
    if tile == 0:
        x = x
        z = z
    elif tile == 1:
        x = x - tileWidth
        z = z
    elif tile == 2:
        x = x - tileWidth
        z = z - tileWidth
    elif tile == 3:
        x = x
        z = z - tileWidth    
    return x, z


create_assets()
create_world()
