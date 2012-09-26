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
        
        # amount of entities function tries to generrate on tile - conditions
        self.treeAmount = 300
        # min height where trees can appear
        self.treeMinHeight = 2
        # max, beyond this point there will be no trees
        self.treeMaxHeight = 80  
        
    def addStuff(self, w):
        print "Generating trees..."
        #random example trees
        
        for tile, tileName in enumerate(self.terrainSlice):
            entityCount = 0
            #read height data from generated .ntf files
            inputFile = self.folder + tileName + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
                        
            coord = []
            height = []
            #generate random coordinates to array, get height
            for j in range(self.treeAmount):
                x = random.randint(0, self.tileWidth)
                z = random.randint(0, self.tileWidth)
                y = t.getHeight(z,x)
                
                a = [x, z]
                b = [y]
                coord.append(a)
                height.append(b)
            
            # loop though list of coordinates
            for j, e in enumerate(coord):
                x = coord[j][0]
                z = coord[j][1]
                y = height[j][0]
                
                #tree adding logic
                if (y > self.treeMinHeight and y < self.treeMaxHeight) and (y < t.getMaxitem()):
                    #check vegetationmap here with the coordinates 
                    if self.checkVegMap(tileName,x,z) == 1:
                        self.addTree(w, tile, "group", x, y, z)
                        entityCount = entityCount + 1
                    elif self.checkVegMap(tileName,x,z) == 2:
                        self.addTree(w, tile, "birch", x, y, z)
                        entityCount = entityCount + 1
            print "Added " + str(entityCount) + " entities to " + tileName
        '''
            #checkouts
            for j, c in enumerate(coord):
                print tile
                print "x: " + str(coord[j][0]) + " z: " + str(coord[j][1]) 
                print "height at x,z: " + str(height[j][0])
        '''
            
                     
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
        
    def addTree(self, w, tile, type, x, y, z):
        #offset the entity coordinates to match the tile it should be on, adjust to scale
        x, z = self.locationOffset(tile, x, z, self.tileWidth, self.horScale)
        
        if (type == "birch"):
            mesh="birch.mesh"
            material="birch3_branches.material;birch3_bark.material"
            modelAdjustment = 6
        elif (type == "simple"):
            mesh="tree.mesh"
            material="pine.material;"
            modelAdjustment = 0
        elif (type == "group"):
            mesh="tree_group08.mesh"
            material="pine.material;spruce.material"
            modelAdjustment = 0
        elif (type == "treeline"):
            mesh="treeline.mesh"
            material="treeline.material"
            modelAdjustment = 0
            
        #random rotation?
        w.createEntity_Staticmesh(1, type + "Tree"+str(w.TXML.getCurrentEntityID()),
                                      mesh=mesh,
                                      material=material,
                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+modelAdjustment, z))
    
    def dynamicType(self, x, z, offset):
        #if x,z + offset < 50 type = 1, elif 50<x<100 type=2, else type=3?
        #generate treegroup
        #generate treeline
        todo
