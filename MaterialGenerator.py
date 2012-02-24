#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import os
import sys

##########################################################################
# Class Material
#
class Material():
    def __init__(self, name):
        self.reset(name)

    def reset(self, name):
        self.name = name
        self.techniques = []
        self.currenttechnique = None
        self.indent = 0

    ##########################################################################
    # Subclasses for the material definition
    # - Technique
    # - Pass
    # - TextureUnit
    #
    class Technique():
        def __init__(self, parentmaterial, name=""):
            self.parentmaterial = parentmaterial
            self.passes = []
            self.currentpass = None
            self.name = name

        def addPass(self, p):
            self.passes.append(p)
            self.currentpass = p

        def addPassParameters(self, d):
            self.currentpass.addPassParameters(d)

        def addTextureunit(self, t):
            self.currentpass.addTextureunit(t)

        def addTextureunitParameters(self, d):
            self.currentpass.addTextureunitParameters(d)

        def addVertexprogram(self, vp):
            self.currentpass.addVertexprogram(vp)

        def addFragmentprogram(self, fp):
            self.currentpass.addFragmentprogram(fp)

        ##########################################################################
        # Technique output methods
        #
        def startTechnique(self):
            self.parentmaterial.writeMaterialString("technique %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTechnique(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTechnique(self):
            for p in self.passes:
                p.startPass()
                p.outputPass()
                p.endPass()

    ##########################################################################
    # Pass Subclass
    #
    class Pass():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.textureunits = []
            self.vertexprograms = []
            self.fragmentprograms = []
            self.currentparams = {}
            self.currenttextureunit = None
            self.currentvertexprogram = None
            self.currentfragmentprogram = None

        def addPassParameters(self, d):
            valid = [ "ambient", "diffuse" ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Pass, but it is not a valid parameter" % key

        def addTextureunit(self, t_unit):
            self.textureunits.append(t_unit)
            self.currenttextureunit = t_unit

        def addTextureunitParameters(self, d):
            self.currenttextureunit.addTextureunitParameters(d)

        def addVertexprogram(self, vp):
            self.vertexprograms.append(vp)
            self.currentvertexprogram = vp

        def addFragmentprogram(self, fp):
            self.fragmentprograms.append(fp)
            self.currentfragmentprogram = fp

        def startPass(self):
            self.parentmaterial.writeMaterialString("pass %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endPass(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputPass(self):
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))
            for vp in self.vertexprograms:
                vp.startVertexprogram()
                vp.outputVertexprogram()
                vp.endVertexprogram()
            for fp in self.fragmentprograms:
                fp.startFragmentprogram()
                fp.outputFragmentprogram()
                fp.endFragmentprogram()
            for t in self.textureunits:
                t.startTextureunit()
                t.outputTextureunit()
                t.endTextureunit()

    ##########################################################################
    # Vertexprogram Subclass
    #
    class Vertexprogram():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.currentparams = {}

        def addVertexprogramParameters(self, d):
            valid = [ ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Vertexprogram, but it is not a valid parameter" % key

        def startVertexprogram(self):
            self.parentmaterial.writeMaterialString("vertex_program_ref %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endVertexprogram(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputVertexprogram(self):
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Fragmentprogram Subclass
    #
    class Fragmentprogram():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.currentparams = {}

        def addFragmentprogramParameters(self, d):
            valid = [ ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Fragmentprogram, but it is not a valid parameter" % key

        def startFragmentprogram(self):
            self.parentmaterial.writeMaterialString("fragment_program_ref %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endFragmentprogram(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputFragmentprogram(self):
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Textureunit Subclass
    #
    class Textureunit():
        def __init__(self, parentmaterial, name=""):
            self.parentmaterial = parentmaterial
            self.name = name
            self.currentparams = {}

        def addTextureunitParameters(self, d):
            valid = [ "texture", "wave_xform", "scroll_anim", "rotate_anim", "colour_op",
                      "texture_alias", "tex_address_mode", "content_type" ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Texture_unit, but it is not a valid parameter" % key

        def startTextureunit(self):
            self.parentmaterial.writeMaterialString("texture_unit %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTextureunit(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTextureunit(self):
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Material class private methods
    #
    def __startMaterial(self):
        self.writeMaterialString("material %s" % self.name)
        self.writeMaterialString("{")
        self.increaseIndent()

    def __endMaterial(self):
        self.decreaseIndent()
        self.writeMaterialString("}")

    def writeMaterialString(self, string):
        s = ""
        for i in range(self.indent): s += "   "
        self.file.write(s + string + "\n")

    def increaseIndent(self):
        self.indent += 1

    def decreaseIndent(self):
        self.indent -= 1

    ##########################################################################
    # Material generator API
    #
    def toFile(self, filename, overwrite=False):
        if os.path.exists(filename):
            if overwrite == False:
                sys.stderr.write("MaterialGenerator: ERROR: output file '%s' already exists!\n" % filename)
                return
            else:
                os.remove(filename)
        try: self.file = open(filename, "w")
        except IOError:
            sys.stderr.write("MaterialGenerator: ERROR: Unable to open file '%s' for writing!" % filename)
            return
        self.__startMaterial()
        for t in self.techniques:
            t.startTechnique()
            t.outputTechnique()
            t.endTechnique()
        self.__endMaterial()
        self.file.close()

    def addTechnique(self, name=""):
        t = Material.Technique(self, name=name)
        self.techniques.append(t)
        self.currenttechnique = t

    def addPass(self, name=""):
        p = Material.Pass(self)
        self.currenttechnique.addPass(p)

    def addPassParameters(self, d={}):
        self.currenttechnique.addPassParameters(d)

    def addTextureunit(self, name=""):
        t = Material.Textureunit(self, name=name)
        self.currenttechnique.addTextureunit(t)

    def addTextureunitParameters(self, d={}):
        self.currenttechnique.addTextureunitParameters(d)

    def addVertexprogram(self, name=""):
        vp = Material.Vertexprogram(self, name=name)
        self.currenttechnique.addVertexprogram(vp)

    def addFragmentprogram(self, name=""):
        fp = Material.Fragmentprogram(self, name=name)
        self.currenttechnique.addFragmentprogram(fp)

    ##########################################################################
    # Material generator pre-defined macros for simple generation of certain
    # types of materials. Parameters in these macros are limited. If it seems
    # too restricting for you, then use the above API to generate more custom
    # materials
    #
    def createMaterial_Diffuseonly(self, name, diffusecolor="1.0 1.0 1.0"):
        self.reset(name)
        m.addTechnique()
        m.addPass()
        m.addPassParameters({"diffuse":diffusecolor})

    def createMaterial_Textureonly(self, name, texture, diffusecolor="1.0 1.0 1.0", ambientcolor="0.5 0.5 0.5"):
        self.reset(name)
        m.addTechnique()
        m.addPass()
        m.addPassParameters({"diffuse":diffusecolor, "ambient":ambientcolor})
        m.addTextureunit(texture)

    def createMaterial_4channelTerrain(self, name, t1, t2, t3, t4, weightmap):
        self.reset(name)
        self.name = name
        m.addTechnique("TerrainPCF")
        m.addPass()
        m.addPassParameters({"ambient":"0.0 0.0 0.0 1.0"})
        m.addVertexprogram("Rex/TerrainPCFVS_weighted")
        m.addFragmentprogram("Rex/TerrainPCFFS_weighted")
        m.addTextureunit("weights")
        m.addTextureunitParameters({"texture_alias":"weights", "texture":weightmap})
        m.addTextureunit("detail0")
        m.addTextureunitParameters({"texture_alias":"detail0", "texture":t1})
        m.addTextureunit("detail1")
        m.addTextureunitParameters({"texture_alias":"detail1", "texture":t2})
        m.addTextureunit("detail2")
        m.addTextureunitParameters({"texture_alias":"detail2", "texture":t3})
        m.addTextureunit("detail3")
        m.addTextureunitParameters({"texture_alias":"detail3", "texture":t4})
        m.addTextureunit("shadowMap0")
        m.addTextureunitParameters({"texture_alias":"shadowMap0", "tex_address_mode":"clamp", "content_type":"shadow"})
        m.addTextureunit("shadowMap1")
        m.addTextureunitParameters({"texture_alias":"shadowMap1", "tex_address_mode":"clamp", "content_type":"shadow"})
        m.addTextureunit("shadowMap2")

##########################################################################
# Matrial unit testacse
#
if __name__ == "__main__":
    m = Material("testmaterial")
    m.addTechnique()
    m.addPass()
    m.addPassParameters({"ambient":"0.5 0.5 0.5", "diffuse":"1.0 1.0 1.0"})
    m.addTextureunit()
    m.addTextureunitParameters({"texture":"image.png", "scroll_anim":"0.1 0.0", "wave_xform":"scale sine 0.0 0.7 0.0 1.0"})
    m.addTextureunit()
    m.addTextureunitParameters({"texture":"wobbly.png", "rotate_anim":"0.25", "colour_op":"add"})
    m.toFile("./resources/testmaterial.material", overwrite=True)

    m.createMaterial_4channelTerrain("terrainsample", "weight.png", "t1.png", "t2.png", "t3.png", "t4.png")
    m.toFile("./resources/4channelterrainsample.material", overwrite=True)
    m.createMaterial_Diffuseonly("diffuse")
    m.toFile("./resources/diffuseonly.material", overwrite=True)
    m.createMaterial_Textureonly("textureonly", "tex.png")
    m.toFile("./resources/textureonly.material")
    print "Done"
