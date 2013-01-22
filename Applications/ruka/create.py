#!/usr/bin/python
import os
import shutil

import TerrainGenerator
import WorldGenerator
import MaterialGenerator
import TextureGenerator
import TreeGenerator

prefix         = ""
env_prefix     = ""

resourcesFolder  = "./resources/"
generatedFolder = "./generated/"
terrainSlice = "S5244H", "T5133G", "T5311A", "S5422B"
terrainSuffix = ".xyz"

patchSize = 0
patchCount = 0

def create_assets():
    if os.path.exists(generatedFolder):
        shutil.rmtree(generatedFolder)
    os.mkdir(generatedFolder)
    global patchSize
    global patchCount
    
    for i in terrainSlice:
        inputFile = resourcesFolder + i + terrainSuffix
        t = TerrainGenerator.TerrainGenerator()
        t.fromFile(inputFile)
        t.adjustHeight(-290.0)
        t.mirror(mirrorX=True, mirrorY=False)
        outputFile = generatedFolder + i + ".ntf" 
        t.toFile(outputFile, overwrite=True)
        
        patchCount = t.width
        patchSize = t.cPatchSize
        
        print "Generating weightmap for the terrain: " + i
        weightFile = generatedFolder + i + "weight.png"
        t.toWeightmap(weightFile, fileformat="PNG", overwrite=True, maxitem=200)
        
        print "Generating material for " + i
        m = MaterialGenerator.Material(i)
        m.createMaterial_4channelTerrain("terrain", "sand.png", "grass.png", "rock.png", "", weightFile)        
        materialFile = generatedFolder + i + ".material"
        m.toFile(materialFile, overwrite=True)
        
    print "Generating terrain textures"
    t = TextureGenerator.TextureGenerator()
    t.createSingleColorTexture(30,100,30,50)
    t.toImage(generatedFolder + "grass.png", "PNG", overwrite=True)
    t.createSingleColorTexture(90,83,73,50)
    t.toImage(generatedFolder + "rock.png", "PNG", overwrite=True)
    t.createSingleColorTexture(160,136,88,70)
    t.toImage(generatedFolder + "sand.png", "PNG", overwrite=True)
        
    
def create_world():
    t_width  = 16*((1500/16)+1)
    t_height = 16*((1500/16)+1)
    w = WorldGenerator.WorldGenerator()
    w.TXML.startScene()
    
    # witdh of the overlap caused by replacing the missing 8 points in the maps
    overlapCorrection = 8 
    
    #scaling
    verScale = 1
    horScale = 10
    
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
                             "avatarapplication.js;"+ \
                             "simpleavatar.js;" + \
                             "exampleavataraddon.js")
    w.createEntity_Waterplane(1, "Waterplane", (tileWidth*2*horScale), (tileWidth*2*horScale), 0.0)
    
    # tree generation
    tree = TreeGenerator.TreeGenerator(generatedFolder, resourcesFolder, terrainSlice, tileWidth, verScale, horScale, 
                                       "spruce.mesh.xml", "pine.mesh.xml", "birch.mesh.xml",
                                       "spruce.material", "pine.material", "birch.material")
    tree.createForest(w)
    
    w.TXML.endScene()
    w.toFile("./Terrain.txml", overwrite=True)

create_assets()
create_world()
