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
    global asd
    
    for i in terrainSlice:
        inputFile = i + terrainSuffix
        t = TerrainGenerator.TerrainGenerator()
        t.fromFile(inputFile)
        t.adjustHeight(-200.0)
        outputFile = folder + i + ".ntf" 
        t.toFile(outputFile, overwrite=True)
        
        patchCount = t.width
        patchSize = t.cPatchSize
        asd = t
        
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
    
    # position using x, z coordinates and the width of one slice
    #print(patchCount * patchSize)
    side = patchCount * patchSize - overlapCorrection
    spot1 = "%f,0,%f,0,0,0,1,1,1" % (0, 0)
    spot2 = "%f,0,%f,0,0,0,1,1,1" % (-side, 0)
    spot3 = "%f,0,%f,0,0,0,1,1,1" % (-side, -side)
    spot4 = "%f,0,%f,0,0,0,1,1,1" % (0, -side)
    
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
    w.createEntity_Waterplane(1, "Waterplane", (side*2), (side*2), 0.0)
    
    addStuff(w)
    
    w.TXML.endScene()
    w.toFile("./Terrain.txml", overwrite=True)

def addStuff(w):
    
    #example trees
    import random
    width = 32
    height = 32
    
    
    for i in range(100):
        x = random.randint(0, width*w.cPatchSize)
        y = random.randint(0, height*w.cPatchSize)
        z = asd.getHeight(x,y)
        x = x - width*w.cPatchSize/2
        y = y - height*w.cPatchSize/2
        if (z > 2.0) and (z < asd.getMaxitem()/2.0):
            w.createEntity_Staticmesh(1, "Tree"+str(w.TXML.getCurrentEntityID()),
                                          mesh="tree.mesh",
                                          material="",
                                          transform="%f,%f,%f,0,0,0,1,1,1" % (y, z+6, x))


create_assets()
create_world()
