#!/usr/bin/python
####
# 
# 
# 
####
import WorldGenerator
import TerrainGenerator
import random
from PIL import Image
import MeshContainer
import MeshIO
import subprocess
import datetime
from threading import Thread


class TreeGenerator():

    def __init__(self, outputFolder, inputFolder, terrainSlice, tileWidth, verScale, horScale, 
                     treeMinHeight=None, treeMaxHeight=None, groupWidth = None, treesInGroup = None):
        
        self.outputFolder = outputFolder
        self.inputFolder = inputFolder
        
        # string tuple containing the names of the tiles
        self.terrainSlice = terrainSlice
        # int containing the width and lenght of a tile
        self.tileWidth = tileWidth
        #scaling factors
        self.verScale = verScale
        self.horScale = horScale
        
        # min height where trees can appear
        self.treeMinHeight = treeMinHeight
        # max, beyond this point there will be no trees
        self.treeMaxHeight = treeMaxHeight
        self.groupWidth = groupWidth
        self.treesInGroup = treesInGroup
        
        #default values
        if treeMinHeight == None:
            self.treeMinHeight = 2
        if treeMaxHeight == None:
            self.treeMaxHeight = 200
        if groupWidth == None:
            self.groupWidth = 50
        if treesInGroup == None:
            self.treesInGroup = 300
        self.subSlice = tileWidth / self.groupWidth
    
    
    def addStuff(self, w):
        start = datetime.datetime.now()
        print "Started: " + str(start)
        print "Generating trees..."
        
        for tile, tileName in enumerate(self.terrainSlice):
            #read height data from generated .ntf files
            inputFile = self.outputFolder + tileName + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
            
            coordGeneral = self.generateCoordGrid(t, tile)
            vegCoord = []
            vegCoord = self.vegMapToCoord(tileName)
            
            self.addEntity(t, w, coordGeneral, tile, tileName, vegCoord)
            
        stop = datetime.datetime.now()
        print "Stopped: " + str(stop)
        print "Runtime: " + str(stop - start)
    
    
    #generate a grid of coordinates
    def generateCoordGrid(self, t, tile):
        coord = []
        sliceWidth = self.tileWidth / self.subSlice
        
        for i in range(self.subSlice): #x
            for j in range(self.subSlice): #y
                x = i * sliceWidth
                z = j * sliceWidth
                #offset coordinates to tile vegmap, designated zone in a different location
                x, z = self.locationOffset(tile, x, z, 1)
                
                # coordinates flipped from 3d to 2d x,y,z -> z,x  
                y = t.getHeight(z,x)
                coord.append([x, y*self.verScale, z])
        
        coord.sort()
        return coord
    
    
    #vegmap to coord
    def vegMapToCoord(self, tileName):
        coord = []
        im = Image.open(self.inputFolder + tileName + "vegetationMap.png")
        pix = im.load()
        # +8 for overlap until fixed
        for y in range(self.tileWidth+8):
            for x in range(self.tileWidth+8):
                pixel = pix[x,y]
                coord.append([[x,y],pixel])
        return coord
    
    
    def addEntity(self, t, w, coord, tile, tileName, vegCoord):
        entityCount = 0
        for j, e in enumerate(coord):
            x = coord[j][0]
            y = coord[j][1]
            z = coord[j][2]
            
            if (y > self.treeMinHeight and y < self.treeMaxHeight):
                #creates forest like treegroup tiles, if group has more than 1 tree
                name = self.createDynamicGroup(t, tileName, x, z, j, self.groupWidth, self.treesInGroup, vegCoord)
                
                if name != "single": 
                    # y = 0 because createdynmesh alings itself with 0 + height currently
                    self.addTree(w, tile, tileName, "dynamicMesh", x, 0, z, name)
                    entityCount = entityCount + 1
                    
                else:
                    self.addTree(w, tile, tileName, "single", x, y, z)
                    entityCount = entityCount + 1
                    
        print "Added " + str(entityCount) + " entities to " + tileName

        
    def locationOffset(self, tile, x, y, mode = 0):
        #placement correction, generated trees to their own slice
        if mode == 0:
            if tile == 0:
                x = x
                y = y
            elif tile == 1:
                x = x - self.tileWidth
                y = y
            elif tile == 2:
                x = x - self.tileWidth
                y = y - self.tileWidth
            elif tile == 3:
                x = x
                y = y - self.tileWidth
            x = x * self.horScale
            y = y * self.horScale 
        #offset for heightcheck
        if mode == 1:
            if tile == 0:
                x = x
                y = y
            elif tile == 1:
                x = self.tileWidth - x
                y = y
            elif tile == 2:
                x = self.tileWidth - x
                y = self.tileWidth - y
            elif tile == 3:
                x = x
                y = self.tileWidth - y
        return x, y
    
    
    def addTree(self, w, tile, tileName, type, x, y, z, meshName=""):
        #offset the entity coordinates to match the tile it should be on, adjust to scale
        x, z = self.locationOffset(tile, x, z)
        
        #preconfigured entity types
        if (type == "birch"):
            mesh = "birch.mesh"
            material = "birch3_branches.material;birch3_bark.material"
            #adjustment in y axel incase the model does not start at zero height
            modelAdjustment = 6
            
        elif (type == "single"):
            mesh = "tree.mesh"
            material = "tree.material"
            modelAdjustment = 0

        elif (type == "dynamicMesh"):
            mesh = self.outputFolder + meshName + "dynamicGroup.mesh"
            material = "tree.material"
            modelAdjustment = 0
            
        #random rotation?
        w.createEntity_Staticmesh(1, type  + tileName + meshName + "_Tree"+str(w.TXML.getCurrentEntityID()),
                                      mesh=mesh,
                                      material=self.inputFolder + material,
                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+modelAdjustment, z))


    def createDynamicGroup(self, t, tileName, x, z, groupId, groupWidth, entityAmount, vegCoord):
        name = tileName + str(groupId)
        print "Generating treegroup: " + name
        coord = []
        
        for j in range(entityAmount):
            _x = random.randint(-groupWidth/2, groupWidth/2)
            _z = random.randint(-groupWidth/2, groupWidth/2)
            adjustedX = _x+x
            adjustedZ = _z+z
            
            #make sure created object fits inside a tiles parameters, (otherwise we'll have floating trees)
            if ( 0 <= adjustedX <= self.tileWidth and 0 <= adjustedZ <= self.tileWidth):
                
                # only add trees if over red in vegmap
                # figure out the index where we want to check for trees
                i = adjustedX + adjustedZ * (self.tileWidth+8)
                
                # [index][x,y](R, G, B)
                if vegCoord[i][0] == [adjustedX, adjustedZ]:
                    #if red
                    if vegCoord[i][1][0] == 255:
                        y = t.getHeight(adjustedZ,adjustedX)
                        #check list incase coords were generated below the minimum height for trees
                        if y >= self.treeMinHeight and y <= self.treeMaxHeight:
                            #add to coord to be generated later
                            coord.append([_x, y*self.verScale, _z])
        
        if len(coord) > 1:
            #create mesh
            self.createDynamicMesh(name, coord)
            return name
        else:
            print "... No group needed for " + name + ", skipping"
            return "single"
    
    
    def createDynamicMesh(self, name, coord):
        start = datetime.datetime.now()
        input = self.inputFolder + "tree.mesh.xml"
        output = self.outputFolder + name + "dynamicGroup.mesh.xml"
        
        mesh = MeshContainer.MeshContainer()
        meshio = MeshIO.MeshIO(mesh)
        #get base mesh from file, also adds a tree at 0,0
        meshio.fromFile(input, None)
        
        #dostuff
        for i, e in enumerate(coord):
            mesh2 = MeshContainer.MeshContainer()
            meshio2 = MeshIO.MeshIO(mesh2)
            
            meshio2.fromFile(input, None)
            x = coord[i][0] * self.horScale
            y = coord[i][1]
            z = coord[i][2] * self.horScale
            
            mesh2.translate(x, y, z) # no output on x,z
            #mesh.rotate(0,0,0,0) # rotate
            #mesh.scale(2,2,2) # scale

            #add last object to the meshcontainer
            mesh.merge(mesh2, append=False) #append True, gray crossboxes
        
        #output
        meshio.toFile(output, overwrite=True)
        # from .mesh.xml to .mesh
        self.compileDynamicMesh(output)
        
        stop = datetime.datetime.now()
        print "createDynamicMesh " + name + " Runtime: " + str(stop - start)
    
    
    def compileDynamicMesh(self, input):
        compiler = "OgreXMLConverter.exe  -q "
        subprocess.Popen(compiler +  input, shell=True)
        
        