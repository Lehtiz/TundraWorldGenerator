#!/usr/bin/python
import WorldGenerator
import TerrainGenerator
import random

class TreeGenerator():
    
    def __init__(self, folder, terrainSlice, tileWidth, horScale):
        self.folder = folder
        self.terrainSlice = terrainSlice
        self.tileWidth = tileWidth
        self.horScale = horScale
        
    def addStuff(self, w):
        print "Generating trees..."
        #random example trees
        
        for i, e in enumerate(self.terrainSlice):
            #read height data from generated .ntf files
            inputFile = self.folder + e + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
            
            treeAmount = 200 # amount of entities function tries to generate, atm per tile
            treeMinHeight = 2 # min height where trees can appear
            treeMaxHeight = 80 # max, beyond this point there will be no trees

            #for j in range(treeAmount):
            loop = 0
            maxLoop = 500
            # try to generate the amount of trees specified above, stop after 500 tries to prevent infi loops
            while treeAmount > 0 and loop < maxLoop:
                loop = loop + 1
                x = random.randint(0, self.tileWidth)
                z = random.randint(0, self.tileWidth)
                y = t.getHeight(z,x) # z,x like x,y with z being x, coord on its side
                
                #decide wether to create a tree here
                if (y > treeMinHeight and y < treeMaxHeight) and (y < t.getMaxitem()):
                    
                    #check vegetationmap here with the coordinates 
                    if self.checkVegMap(e,x,z) == 1: # mode1 tree, red in vegmap
                        #offset the entity coordinates to match the tile it should be on, adjust to scale
                        x, z = self.locationOffset(i, x, z, self.tileWidth, self.horScale)
                        #add tree entity
                        self.addTree(w, "group", x, y, z)
                        treeAmount = treeAmount - 1
                    
                    elif self.checkVegMap(e,x,z) == 2: # mode2 tree, blue in vegmap
                        x, z = self.locationOffset(i, x, z, self.tileWidth, self.horScale)
                        self.addTree(w, "birch", x, y, z)
                        treeAmount = treeAmount - 1
                    
                     
    def checkVegMap(self, tileName, x, z): # return mode
        from PIL import Image
        #print "reading vegetation map: " + tileName
        #im = Image.open(folder + tileName + "vegetationMap.png") #use this after dynamic veg maps available
        im = Image.open(tileName + "vegetationMap.png")
        pix = im.load()
        
        pixel = pix[x,z] # returns tuple rgb
        
        #red do something
        if pixel[0] == 255:
            #print str(x) + "," + str(z) + " red"
            return 1
            
        #green do nothing
        elif pixel[1] == 255:
            #print str(x) + "," + str(z) + " green"
            return 0
            
        #blue do something
        elif pixel[2] == 255:
            #print str(x) + "," + str(z) + " blue"
            return 2
            
    def locationOffset(self, tile, x, z, tileWidth, horScale):
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
        x = x * horScale
        z = z * horScale 
        return x, z
        
    def addTree(self, w, type, x, y, z):
        if (type == "birch"):
            mesh="birch.mesh"
            material="birch3_branches.material;birch3_bark.material"
            treeAdjustment = 6
        elif (type == "simple"):
            mesh="tree.mesh"
            material="pine.material;"
            treeAdjustment = 0
        elif (type == "group"):
            mesh="tree_group08.mesh"
            material="pine.material;spruce.material"
            treeAdjustment = 0
            
        w.createEntity_Staticmesh(1, type + "Tree"+str(w.TXML.getCurrentEntityID()),
                                      mesh=mesh,
                                      material=material,
                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+treeAdjustment, z))
