#!/usr/bin/python
import WorldGenerator
import TerrainGenerator
import random

class TreeGenerator():
    
    def __init__(self, outputFolder, inputFolder, terrainSlice, tileWidth, horScale):
        self.outputFolder = outputFolder
        self.inputFolder = inputFolder
        self.terrainSlice = terrainSlice
        self.tileWidth = tileWidth
        self.horScale = horScale
        
        # amount of entities function tries to generate per tile - conditions
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
            inputFile = self.outputFolder + tileName + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
                        
            coord = []
            height = []
            #generate random coordinates to array, get height
            for j in range(self.treeAmount):
                x = random.randint(0, self.tileWidth)
                z = random.randint(0, self.tileWidth)
                y = t.getHeight(x,z)
                
                coord.append([x, z])
                height.append([y])
            
            # loop though list of coordinates
            for j, e in enumerate(coord):
                x = coord[j][0]
                z = coord[j][1]
                y = height[j][0]
                
                #tree adding logic
                if (y > self.treeMinHeight and y < self.treeMaxHeight) and (y < t.getMaxitem()):
                
                    #check vegetationmap here with the coordinates
                    if self.checkVegMap(tileName,x,z) == 1:
                        # check if areas(groupwidth) heighdiff => somevalue
                        self.dynamicMesh(t, tileName, z, x, j) # z,x ?
                        # y = 0 because meshgen alings itself with 0 + height currently
                        self.addTree(w, tile, "dynamicMesh", x, 0, z, tileName+str(j))
                        entityCount = entityCount + 1
                        
                    elif self.checkVegMap(tileName,x,z) == 2:
                        self.addTree(w, tile, "single", z, y, x)
                        entityCount = entityCount + 1
                        
            print "Added " + str(entityCount) + " entities to " + tileName
                     
    def checkVegMap(self, tileName, x, z): # return mode
        from PIL import Image
        #print "reading vegetation map: " + tileName
        im = Image.open(self.inputFolder + tileName + "vegetationMap.png") #use this after dynamic veg maps available
        #im = Image.open(tileName + "vegetationMap.png")
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
        
    def locationOffset(self, tile, x, z):
        #placement correction, generated trees to their own slice
        if tile == 0:
            x = x
            z = z
        elif tile == 1:
            x = x - self.tileWidth
            z = z
        elif tile == 2:
            x = x - self.tileWidth
            z = z - self.tileWidth
        elif tile == 3:
            x = x
            z = z - self.tileWidth
        x = x * self.horScale
        z = z * self.horScale 
        return x, z
        
    def addTree(self, w, tile, type, x, y, z, meshName=""):
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
        w.createEntity_Staticmesh(1, type + meshName + "_Tree"+str(w.TXML.getCurrentEntityID()),
                                      mesh=mesh,
                                      material=self.inputFolder + material,
                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+modelAdjustment, z))


    def dynamicMesh(self, t, tileName, x, z, groupId):
        #square mesh
        groupWidth = 40
        
        coord = []
        height = []
        print(tileName + str(groupId))
        for j in range(40):
            _x = random.randint(-groupWidth, groupWidth)
            _z = random.randint(-groupWidth, groupWidth)
            adjustedX = _x+x
            adjustedZ = _z+z
            
            #make sure created object fits inside a tiles parameters, (otherwise we'll have floating trees)
            if ( 0 <= adjustedX <= self.tileWidth and 0 <= adjustedZ <= self.tileWidth):
                y = t.getHeight(adjustedX,adjustedZ)
                #add to coord to be generated later
                coord.append([_x, _z])
                height.append([y])
        
        #create mesh
        name = tileName + str(groupId)
        self.createDynamicGroup(name, coord, height)
    
    def createDynamicGroup(self, name, coord, height):
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
            z = coord[i][1] * self.horScale
            y = height[i][0]
            mesh2.translate(z, y, x) # no output on x,z
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