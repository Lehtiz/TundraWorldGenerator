#!/usr/bin/python
import WorldGenerator
import TerrainGenerator
import random

class TreeGenerator():
    def addStuff(self, folder, terrainSlice, w, tileWidth, horScale):
        print "Generating trees..."
        #random example trees
        
        for i, e in enumerate(terrainSlice):
            #read height data from generated .ntf files
            inputFile = folder + e + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
            
            treeAmount = 200 # amount of entities function tries to generate, atm per tile
            treeAdjustment = 6 # acount for difference in the surface and models center
            treeMinHeight = 2 # min height where trees can appear
            treeMaxHeight = 80 # max, beyond this point there will be no trees

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
                    if self.checkVegMap(e,z,x) == 1: # mode1 tree, red in vegmap
                    
                        #offset the entity coordinates to match the tile it should be on
                        x, z = self.locationOffset(i, x, z, tileWidth, horScale)
                        
                        w.createEntity_Staticmesh(1, "redTree"+str(w.TXML.getCurrentEntityID()),
                                                      mesh="tree_group08.mesh",
                                                      material="pine.material;spruce.material",
                                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y, z))
                        '''
                        w.createEntity_Staticmesh(1, "redTree"+str(w.TXML.getCurrentEntityID()),
                                                      mesh="Cube.mesh",
                                                      material="Material.material",
                                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y, z))
                        '''
                        treeAmount = treeAmount - 1 # tree added, reduce counter
                    
                    elif self.checkVegMap(e,z,x) == 2: # mode2 tree, blue in vegmap
                    
                        x, z = self.locationOffset(i, x, z, tileWidth, horScale)
                        '''
                        w.createEntity_Staticmesh(1, "blueTree"+str(w.TXML.getCurrentEntityID()),
                                                      mesh="tree.mesh",
                                                      material="birch3_branches.material;birch3_bark.material",
                                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+treeAdjustment, z))
                        '''
                        w.createEntity_Staticmesh(1, "blueTree"+str(w.TXML.getCurrentEntityID()),
                                                      mesh="Cube.mesh",
                                                      material="Material.material",
                                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y, z))
                        treeAmount = treeAmount - 1 # tree added, reduce counter
                    
                     
    def checkVegMap(self, tileName, x, y): # return mode
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
            
    def locationOffset(self, tile, x, z, tileWidth, horScale):
    #placement correction, generated trees to their own slice
        var = tileWidth * horScale
        if tile == 0:
            x = x * horScale
            z = z * horScale
        elif tile == 1:
            x = x - var
            z = z * horScale
        elif tile == 2:
            x = x - var
            z = z - var
        elif tile == 3:
            x = x * horScale
            z = z - var    
        return x, z

