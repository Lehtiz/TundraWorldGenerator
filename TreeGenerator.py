#!/usr/bin/python
####
# - trees could be grouped more like group groups in your groups so your groups can group
# - 
# - 
####
import WorldGenerator
import TerrainGenerator
import random

class TreeGenerator():
    def __init__(self, outputFolder, inputFolder, terrainSlice, tileWidth, horScale, 
                    treeAmount=300, treeMinHeight=2, treeMaxHeight=800):
        
        self.outputFolder = outputFolder
        self.inputFolder = inputFolder
        
        # string tuple containing the names of the tiles
        self.terrainSlice = terrainSlice
        # int containing the width and lenght of a tile
        self.tileWidth = tileWidth
        # horisontal scaling factor
        self.horScale = horScale
        
        # amount of entities function tries to generate per tile - conditions
        self.treeAmount = treeAmount
        # min height where trees can appear
        self.treeMinHeight = treeMinHeight
        # max, beyond this point there will be no trees
        self.treeMaxHeight = treeMaxHeight
        
    def addStuff(self, w):
        print "Generating trees..."
        
        pointOfInterestX = 0
        pointOfInterestZ = 0
        interestWidth = 40
        interestHeight = 40
        
        for tile, tileName in enumerate(self.terrainSlice):
            #read height data from generated .ntf files
            inputFile = self.outputFolder + tileName + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
            
            #generate random coordinates to array, get height
            coordInterest = self.generateCoord(t, tile, 30, pointOfInterestX, pointOfInterestZ, interestWidth, interestHeight)
            #another set of coordinates for area beyond focus
            coordGeneral = self.generateCoord(t, tile, 300, interestWidth, interestHeight, mode = 1)
            
            #add entities, 1 for interest area 2 for general
            self.addEntity(1, t, w, coordInterest, tile, tileName)
            self.addEntity(2, t, w, coordGeneral, tile, tileName)
        
        
    def generateCoord(self, t, tile, amount, minX = 0, minZ = 0, xWidth = 600, zWidth = 600, mode = 0):
        coord = []
        for j in range(amount):
            x = random.randint(0, xWidth)
            z = random.randint(0, zWidth)
            #offset coordinates to tile vegmap, designated zone in a different location
            x, z = self.locationOffset(tile, x, z, 1)
            
            # coordinates flipped from 3d to 2d x,y,z -> z,x  
            y = t.getHeight(z,x)
            coord.append([x, y, z])
            coord.sort()
            
            #exclude interest area from general coords
            if mode == 1:
                for i, e in enumerate(coord):
                    if coord[i][0] < minX and coord[i][2] < minZ:
                        coord.pop(i)
        #print coord
        return coord
        
    def addEntity(self, area, t, w, coord, tile, tileName):
        # loop though list of coordinates
        entityCount = 0
        for j, e in enumerate(coord):
            x = coord[j][0]
            y = coord[j][1]
            z = coord[j][2]
            
            #tree adding logic
            if (y > self.treeMinHeight and y < self.treeMaxHeight):
                #check vegetationmap here with the coordinates
                mode = self.checkVegMap(tileName, x, z)
                if(area==1):
                    if mode == 1:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
                    if mode == 2:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
                if(area==2):
                    # coordinates flipped from 3d to 2d x,y,z -> z,x
                    if mode == 1:
                        self.dynamicMesh(t, tileName, x, z, j)
                        # y = 0 because meshgen alings itself with 0 + height currently
                        self.addTree(w, tile, tileName, "dynamicMesh", x, 0, z, tileName + str(j))
                        entityCount = entityCount + 1
                    elif mode == 2:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
            
        print "Added " + str(entityCount) + " entities to " + tileName
    
        
    def checkVegMap(self, tileName, x, y): # return mode
        from PIL import Image
        #print "=====reading vegetation map: " + tileName
        im = Image.open(self.inputFolder + tileName + "vegetationMap.png")
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
        else:
            print str(x) + "," + str(y) + " something else:" + str(pixel) 
        
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
        
        if (type == "birch"):
            mesh = "birch.mesh"
            material = "birch3_branches.material;birch3_bark.material"
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


    def dynamicMesh(self, t, tileName, x, z, groupId):
        #square mesh
        groupWidth = 100
        entityAmount = 60
        
        coord = []
        print(tileName + str(groupId))
        for j in range(entityAmount):
            _x = random.randint(-groupWidth/2, groupWidth/2)
            _z = random.randint(-groupWidth/2, groupWidth/2)
            adjustedX = _x+x
            adjustedZ = _z+z
            
            #make sure created object fits inside a tiles parameters, (otherwise we'll have floating trees)
            if ( 0 <= adjustedX <= self.tileWidth and 0 <= adjustedZ <= self.tileWidth):
                y = t.getHeight(adjustedZ,adjustedX)
                #add to coord to be generated later
                coord.append([_x, y, _z])
        
        #create mesh
        name = tileName + str(groupId)
        self.createDynamicGroup(name, coord)
    
    def createDynamicGroup(self, name, coord):
        import MeshContainer
        import MeshIO
        
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
        
        self.compileDynamicGroup(output)
        
    def compileDynamicGroup(self, input):
        import subprocess
        folder = "./../"
        compiler = folder + "OgreXMLConverter.exe  -q"
        
        subprocess.Popen(compiler + " " +  input, shell=True)