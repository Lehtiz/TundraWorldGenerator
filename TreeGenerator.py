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
                        # check if areas(groupwidth) heighdiff => somevalue
                        self.addTree(w, tile, "simplegroup", x, y, z)
                        entityCount = entityCount + 1
                        
                    elif self.checkVegMap(tileName,x,z) == 2:
                        self.addTree(w, tile, "birch", x, y, z)
                        entityCount = entityCount + 1
            
            print "Added " + str(entityCount) + " entities to " + tileName
            
            #generates a mesh based on location and heightdata, still needs to be converted by hand
            self.dynamicMesh(t, tile, tileName, w, 0, 0)
        #tmp
        #self.createStaticGroup()
                     
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
        
    def addTree(self, w, tile, type, x, y, z):
        #offset the entity coordinates to match the tile it should be on, adjust to scale
        x, z = self.locationOffset(tile, x, z)
        
        if (type == "birch"):
            mesh="birch.mesh"
            material="birch3_branches.material;birch3_bark.material"
            modelAdjustment = 6
        elif (type == "simple"):
            mesh="tree.mesh"
            material="pine.material;"
            modelAdjustment = 0
        elif (type == "simplegroup"):
            mesh="treegroup.mesh"
            material="tree.material;"
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

    #tmp
    def createStaticGroup(self):
        import MeshContainer
        import MeshIO
        
        input = "tree.mesh.xml"
        output = "treegroup.mesh.xml"
        groupWidth = 80
        treeAmount = 100
        #starting point, check width
        
        print "Creating a treegroup..."
        
        mesh = MeshContainer.MeshContainer()
        meshio = MeshIO.MeshIO(mesh)
        #get base mesh from file, also adds a tree at 0,0
        meshio.fromFile(input, None)
        
        #dostuff
        for i in range(treeAmount):
            mesh2 = MeshContainer.MeshContainer()
            meshio2 = MeshIO.MeshIO(mesh2)
            
            meshio2.fromFile(input, None)
            _x = random.randint(0, groupWidth)
            _z = random.randint(0, groupWidth)
            mesh2.translate(_x, 0, _z) # move inside mesh
            #mesh.rotate(0,0,0,0) # rotate
            #mesh.scale(2,2,2) # scale

            #add last object to the meshcontainer
            mesh.merge(mesh2, append=False) #append false; dont create new submesh
        
        #output
        meshio.toFile(output, overwrite=True)

    def dynamicMesh(self, t, tile, tileName, w, x, z):
        #square mesh
        groupWidth = 40
        
        coord = []
        height = []
        
        for i in range(groupWidth):
            for j in range (groupWidth):
                if random.randint(0, 10) < 1:
                    _x = i
                    _z = j
                    y = t.getHeight(_z,_x) #z,x - x,z ?teh fak
                    coord.append([_x, _z])
                    height.append([y])
        
        #create mesh
        name = tileName
        self.createDynamicGroup(name, tile, coord, height)
        
        #move mesh to the correct tile
        x, z = self. locationOffset(tile, x, z)
        w.createEntity_Staticmesh(1, name+"square"+str(w.TXML.getCurrentEntityID()),
                                      mesh=name + "square.mesh",
                                      material="tree.material",
                                      transform="%f,%f,%f,0,0,0,1,1,1" % (x, 0, z))
        
    def createDynamicGroup(self, name, tile, coord, height):
        import MeshContainer
        import MeshIO
        
        input = "tree.mesh.xml"
        output = name + "square.mesh.xml"
        
        mesh = MeshContainer.MeshContainer()
        meshio = MeshIO.MeshIO(mesh)
        #get base mesh from file, also adds a tree at 0,0
        meshio.fromFile(input, None)
        
        #dostuff
        for i, e in enumerate(coord):
            mesh2 = MeshContainer.MeshContainer()
            meshio2 = MeshIO.MeshIO(mesh2)
            
            meshio2.fromFile(input, None)
            x = coord[i][0]
            z = coord[i][1]
            y = height[i][0]
            mesh2.translate(x * self.horScale, y, z * self.horScale) # move inside mesh
            #mesh.rotate(0,0,0,0) # rotate
            #mesh.scale(2,2,2) # scale

            #add last object to the meshcontainer
            mesh.merge(mesh2, append=False) #append false; dont create new submesh
        
        #output
        meshio.toFile(output, overwrite=True)