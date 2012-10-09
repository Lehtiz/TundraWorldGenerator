#!/usr/bin/python
####
# ? trees could be grouped more like group groups in your groups so your groups can group
# ? read vegmap first, then draw coords and generate
# 
####
import WorldGenerator
import TerrainGenerator
import random

class TreeGenerator():
    def __init__(self, outputFolder, inputFolder, terrainSlice, tileWidth, verScale, horScale, 
                    treeAmount=300, treeMinHeight=2, treeMaxHeight=200):
        
        self.outputFolder = outputFolder
        self.inputFolder = inputFolder
        
        # string tuple containing the names of the tiles
        self.terrainSlice = terrainSlice
        # int containing the width and lenght of a tile
        self.tileWidth = tileWidth
        #scaling factors
        self.verScale = verScale
        self.horScale = horScale
        
        # amount of entities function tries to generate per tile - conditions
        self.treeAmount = treeAmount
        # min height where trees can appear
        self.treeMinHeight = treeMinHeight
        # max, beyond this point there will be no trees
        self.treeMaxHeight = treeMaxHeight
        
        self.groupWidth = 50
        self.treesInGroup = 400
        self.subSlice = tileWidth / self.groupWidth
        
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
            #coordInterest = self.generateCoord(t, tile, 30, pointOfInterestX, pointOfInterestZ, interestWidth, interestHeight)
            #another set of coordinates for area beyond focus
            #coordGeneral = self.generateCoord(t, tile, 300, interestWidth, interestHeight, mode = 1)
            
            coordGeneral = self.generateCoordGrid(t, tile)
            
            #add entities, 1 for interest area 2 for general
            #self.addEntity(1, t, w, coordInterest, tile, tileName)
            self.addEntity(t, w, coordGeneral, tile, tileName, 2)
        
        
    def generateRandomCoord(self, t, tile, amount, minX = 0, minZ = 0, xWidth = 600, zWidth = 600, mode = 0):
        coord = []
        for j in range(amount):
            x = random.randint(0, xWidth) #+ random.random()
            z = random.randint(0, zWidth) #+ random.random()
            #offset coordinates to tile vegmap, designated zone in a different location
            x, z = self.locationOffset(tile, x, z, 1)
            
            # coordinates flipped from 3d to 2d x,y,z -> z,x  
            y = t.getHeight(z,x)
            coord.append([x, y*self.verScale, z])
            coord.sort()
            
            #exclude interest area from general coords
            if mode == 1:
                for i, e in enumerate(coord):
                    if coord[i][0] < minX and coord[i][2] < minZ:
                        coord.pop(i)
        #print coord
        return coord
    
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
            
        #exclude interest area from general coords
        if 0 == 1:
            for i, e in enumerate(coord):
                if coord[i][0] < minX and coord[i][2] < minZ:
                    coord.pop(i)
        #print coord
        return coord
    
    
    def addEntity(self, t, w, coord, tile, tileName, area = 2):
        # loop though list of coordinates
        entityCount = 0
        for j, e in enumerate(coord):
            x = coord[j][0]
            y = coord[j][1]
            z = coord[j][2]
            
            #tree adding logic
            if (y > self.treeMinHeight and y < self.treeMaxHeight):
                #check vegetationmap here with the coordinates
                mode = self.checkVegMap(tileName, x, z) # tuple rgb+alpha "(0,0,0,255)"
                if(area==1): # interest test
                    if mode[0] == 255:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
                    if mode[2] == 255:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
                if(area==2): #default
                    if mode[0] == 255:
                        name = self.createDynamicGroup(t, tileName, x, z, j, self.groupWidth, self.treesInGroup)
                        # y = 0 because meshgen alings itself with 0 + height currently
                        self.addTree(w, tile, tileName, "dynamicMesh", x, 0, z, name)
                        entityCount = entityCount + 1
                    elif mode[2] == 255:
                        self.addTree(w, tile, tileName, "single", x, y, z)
                        entityCount = entityCount + 1
            
        print "Added " + str(entityCount) + " entities to " + tileName
    
        
    def checkVegMap(self, tileName, x, y): # return mode
        from PIL import Image
        #print "=====reading vegetation map: " + tileName
        im = Image.open(self.inputFolder + tileName + "vegetationMap.png")
        pix = im.load()
        pixel = pix[x,y] # returns tuple rgb
        return pixel    
    
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


    def createDynamicGroup(self, t, tileName, x, z, groupId, groupWidth, entityAmount):
        coord = []
        
        for j in range(entityAmount):
            _x = random.randint(-groupWidth/2, groupWidth/2)
            _z = random.randint(-groupWidth/2, groupWidth/2)
            adjustedX = _x+x
            adjustedZ = _z+z
            
            #make sure created object fits inside a tiles parameters, (otherwise we'll have floating trees)
            if ( 0 <= adjustedX <= self.tileWidth and 0 <= adjustedZ <= self.tileWidth):
                y = t.getHeight(adjustedZ,adjustedX)
                
                # only add trees if over red in vegmap
                pixel = self.checkVegMap(tileName, adjustedX, adjustedZ)
                if  pixel[0] == 255:
                    #check list incase coords were generetted below the minimum height for trees
                    if y >= self.treeMinHeight:
                        #add to coord to be generated later
                        coord.append([_x, y*self.verScale, _z])
                
        
        #create mesh
        name = tileName + str(groupId)
        self.createDynamicMesh(name, coord)
        return name
    
    def createDynamicMesh(self, name, coord):
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
        
        self.compileDynamicMesh(output)
        
    def compileDynamicMesh(self, input):
        import subprocess
        
        compiler = "OgreXMLConverter.exe  -q "
        
        subprocess.Popen(compiler +  input, shell=True)