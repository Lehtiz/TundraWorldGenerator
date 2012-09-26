#!/usr/bin/python
import os
import shutil

import TerrainGenerator
import WorldGenerator
import MaterialGenerator
import TextureGenerator
import TreeGenerator

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
    
    # witdh of the overlap caused by replacing the missing 8 points in the maps
    overlapCorrection = 8 
    
    #scaling 1:5 height width
    verScale = 1
    horScale = 5
    
    # position using x, z coordinates and the width of one terrain tile
    tileWidth = patchCount * patchSize - overlapCorrection
    tileOffset = tileWidth * horScale
    
    #loc xyz, rot xyz, scale xyz 
    spot1 = "%f,0,%f,0,0,0,%f,%f,%f" % (0, 0, horScale,verScale,horScale)
    spot2 = "%f,0,%f,0,0,0,%f,%f,%f" % (-tileOffset, 0, horScale,verScale,horScale)
    spot3 = "%f,0,%f,0,0,0,%f,%f,%f" % (-tileOffset, -tileOffset, horScale,verScale,horScale)
    spot4 = "%f,0,%f,0,0,0,%f,%f,%f" % (0, -tileOffset, horScale,verScale,horScale)
    
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
    
    # tree generation
    tree = TreeGenerator.TreeGenerator(folder, terrainSlice, tileWidth, horScale)
    tree.addStuff(w)
    
    w.TXML.endScene()
    w.toFile("./Terrain.txml", overwrite=True)

create_assets()
create_world()
