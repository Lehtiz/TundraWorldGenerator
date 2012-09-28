#!/usr/bin/python
import MeshIO
import MeshContainer

# take mesh and multiply it and arrange + save to a group
#
#


if __name__ == "__main__":
    input = "./tree.mesh.xml"
    print "Reading " + input
    
    mesh = MeshContainer.MeshContainer()
    meshio = MeshIO.MeshIO(mesh)
    
    mesh2 = MeshContainer.MeshContainer()
    meshio2 = MeshIO.MeshIO(mesh2)
    
    #input
    meshio.fromFile(input, None)
    meshio2.fromFile(input, None)
    
    #mesh.printStatistics()
    
    #dostuff
    mesh.translate(10,0,-20) # move inside mesh
    #mesh.rotate(0,0,0,0) # rotate
    mesh.scale(2,2,2) # scale
    
    mesh.merge(mesh2, append=True)
    
    
    #output
    meshio.toFile("./1/tree.mesh.xml", overwrite=True)