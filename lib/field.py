from odbAccess import *
import sys
import re
class field(object):
    "all die auspraegungen"

    
    def __init__(self, argument):
#        self.batch    = argument.batch
        self.interactive = argument.interactive
        if (self.interactive):
            self.batch = False
        else:
            self.batch = True

        self.arg_odb  = str(argument.odb)
        self.odb      = self._getodb(self.arg_odb)

        
        self.arg_stepname, self.step     = self._getstep(str(argument.stepname))
        self.arg_framenr,  self.frame    = self._getframe(str(argument.framenr))
        self.arg_instance, self.instance = self._getinstance(str(argument.instance))

        self.arg_regiontype, self.regiontype = self._getregiontype(str(argument.nid), str(argument.eid), str(argument.nset), str(argument.elset))
        self.arg_region, self.region         = self._getregion(self.regiontype, str(argument.nid), str(argument.eid), str(argument.nset), str(argument.elset))

# feststellen des koordinatensystems
#        if ((str(argument.coordsys) != "_global_") and (argument.coordsys != None)):   # wenn nicht _global_, dann muss das Koordinatensystem-Objekt festgestellt werden...
        self.arg_coordsys, self.coordsys = self._getcoordsys(str(argument.coordsys))
            
# self.field enthaelt nur die fields fuer die ermittelte region
        self.arg_field, self.field           = self._getfield(str(argument.field))
        self.arg_output, self.output         = self._getoutput(str(argument.output))

        self.arg_postfunction, self.postfunction = self._getpostfunction(str(argument.postfunction))

        self.result = self._getresult()

        if ((argument.elset is not "None") and (argument.nset is "None")):
            self.settype = "elset"
            self.elset    = argument.elset
        elif ((argument.elset is "None") and (argument.nset is not "None")):
            self.settype = "nset"
            self.nset     = argument.nset


#    def gencall(self, batch, ):
#        if (batch is False):
#            print "to achieve the same information in batch mode call me:"
#            print "abaqus python --odb sel"

    def print_args(self):
        for attribute, value in self.__dict__.iteritems():
            print attribute, value
            
    def check_odb_update_required(self):
        if isUpgradeRequiredForOdb(self.odbfile):
            print "The database is from a previous release of Abaqus."
            print "Run abaqus -upgrade -job <newFileName> -odb <oldOdbFileName> to upgrade it."
            sys.exit()
        else:
            print "no update is required for odb-File "+self.odbfile

# =============================
# Method: ermittlung des odb-objektes
# =============================
    def _getodb(self, odbfile):
        if isUpgradeRequiredForOdb(odbfile):
            print "The database is from a previous release of Abaqus."
            print "Run abaqus -upgrade -job <newFileName> -odb <oldOdbFileName> to upgrade it."
            sys.exit()
        else:
            if (self.batch == False):
                print "no update is required for odb-File "+odbfile
            
            odb=openOdb(odbfile)
            return(odb)

# =============================
# Method: ermittlung des step-objektes
# =============================
    def _getstep(self, stepname):
        # feststellen ob stepname in odb vorhanden ist
        # wenn nicht, dann im --batch-Modus aussteigen und qualifizierte Meldung machen
        # wenn nicht, dann im interaktiv-Modus den Step abfragen
        odb = self.odb
        try:
            odb.steps[stepname]
        except KeyError:
            if (self.batch):
                print "stepname '"+stepname+"' does not exist in odb '"+odb.name+"'"
                sys.exit()
            else:
                print "======="
                print "These steps are available in " + odb.name# + str(odb.sectionCategories)
                print "-------"
                stepNames = odb.steps.keys()

                stepNr = 0
                for stepName in stepNames:
                    print "(" + str(stepNr) + ") " + stepName
                    stepNr+=1
                print "-------"

                # User Abfrage
                desired_step_nr = raw_input("Please specify step: ")
                while ((re.search('\D', str(desired_step_nr))) or ((len(stepNames)-1) < int(desired_step_nr)) or (int(desired_step_nr)) < 0):
                    desired_step_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                stepname = str(stepNames[int(desired_step_nr)])
                print "You've chosen step '" + stepname + "'"
                return (stepname, odb.steps[stepname])

        return (stepname, odb.steps[stepname])

# =============================
# Method: ermittlung des frame-objektes
# =============================
    def _getframe(self, framenr):

        odb = self.odb
        step = self.step
        try:
            frame = step.frames[int(framenr)]
#        except KeyError or TypeError:
        except:
            if (self.batch):
                print "framenr '"+str(framenr)+"' does not exist in step '"+step.name+"'"
                sys.exit()
            else:
                print "======="
                print "These frames are available in " + step.name# + str(odb.sectionCategories)
                print "-------"

                frameNr = 0
                frames = step.frames
                for frame in frames:
                    print "(" + str(frameNr) + ") " + frame.description
                    frameNr+=1
                print "-------"

                # User Abfrage
                desired_frame_nr = raw_input("Please specify frame: ")
                while ((re.search('\D', str(desired_frame_nr))) or ((len(frames)-1) < int(desired_frame_nr)) or (int(desired_frame_nr)) < 0):
#                    print desired_frame_nr
                    desired_frame_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                frame = frames[int(desired_frame_nr)]
                print "You've chosen frame '" + frame.description + "'"
#                print "Return: "+desired_frame_nr+", "+str(frame)
                return (desired_frame_nr, frame)
            

        return (framenr, frame)

# =============================
# Method: ermittlung des field-objektes
# Falls es ein coordinatensystem gibt, wird eine transformation vorgenommen
# =============================
    def _getfield(self, fieldvariable):

        frame = self.frame
#        print "FIELDIN = "+ fieldvariable
        
        try:
#            field = frame.fieldOutputs[fieldvariable].getSubset(region=self.region)
            field = frame.fieldOutputs[fieldvariable]

# wenn es ein koordionatensystem gibt, wird eine transformation vorgenommen
            if self.coordsys:
                field = field.getTransformedField(self.coordsys)

            field = field.getSubset(region=self.region)

            values = field.values
            if (len(values) == 0):
                print "there are no values for the field "+fieldvariable
                raise Exception("there are no values for this field")
#        except KeyError or TypeError:
        except:
            if (self.batch):
                print "no value does exist in field '"+fieldvariable+"' OR field '"+fieldvariable+"' does not exist in framenr '"+str(self.frame.incrementNumber)+"' ("+self.frame.description+") of stepname "+self.arg_stepname
                sys.exit()
            else:
                print "======="

                fieldNr = 0
                fieldKeys = frame.fieldOutputs.keys()

# es werden die field-variablen, die keine values enthalten aus der liste entfernt                
                fieldKeys_bereinigt = []
                fieldKeys_cleared_anzahl = 0
                
                for fieldKey in fieldKeys:
                    if (len(frame.fieldOutputs[fieldKey].getSubset(region=self.region).values) > 0):
                        fieldKeys_bereinigt.append(fieldKey)
                    else:
                        fieldKeys_cleared_anzahl += 1
                
                print "These fields are available in '" +frame.description+"'"
                print "listing "+str(fieldKeys_cleared_anzahl)+" empty fields have been suppressed"
                print "-------"
                for fieldKey in fieldKeys_bereinigt:
                    print "(" + str(fieldNr) + ") " + fieldKey + " ["+ frame.fieldOutputs[fieldKey].description+"]"
                    fieldNr+=1
                print "-------"

                # User Abfrage
                desired_field_nr = raw_input("Please specify field: ")
#                field
                
                fault = 1
                while (fault > 0):
                    fault = 0

# ist der eingegebene index im Bereich der vergebenen zahlen?
                    if ((re.search('\D', str(desired_field_nr))) or ((len(fieldKeys_bereinigt)-1) < int(desired_field_nr)) or ((int(desired_field_nr)) < 0) ):
                        fault = 1

# der field-output wird abgefragt, falls es keine Eintraege gibt, wird sofort nach einem anderen field-output gefragt
                    elif (len(frame.fieldOutputs[fieldKeys_bereinigt[int(desired_field_nr)]].values) == 0):
                        fault = 2
                
#                    print desired_field_nr
                    
                    if (fault == 1):
                        desired_field_nr = raw_input("impermissible choice - please use an index mentioned above: ")
                    elif (fault == 2):
                        desired_field_nr = raw_input("there are no values for this field in your region - please try something else: ")
                    
# an dieser stelle ist bereits sichergestellt, dass es variablen in diesem field-output gibt
#                    field = frame.fieldOutputs[fieldKeys[int(desired_field_nr)]].getSubset(region=self.region)
                field = frame.fieldOutputs[fieldKeys_bereinigt[int(desired_field_nr)]]
                    # den fieldnamen sicher, da sich dieser aendert sobald ein field.getTransformed(lokales Koordinatensystemnamen) durchgefuehrt wird
                fieldvariable = field.name

# wenn es ein koordionatensystem gibt, wird eine transformation vorgenommen
                if self.coordsys:
                    field = field.getTransformedField(self.coordsys)
                
                field = field.getSubset(region=self.region)


#                field = frame.fieldOutputs[fieldKeys[int(desired_field_nr)]].getSubset(region=self.region)
                print "You've chosen field '" +fieldvariable+ "'"

#        print "FIELDOUT= "+ fieldvariable
        return (fieldvariable, field)


# =============================
# Method: ermittlung des output-objektes
# =============================
    def _getoutput(self, outputname):

        field = self.field
        values = field.values
        try:
#            print "WOOOOP"
#            odb.steps[str(self.stepname)].frames
            output_array = []

            if (outputname == "None"):
                raise
            for value in values:

                output_array.append(getattr(value, outputname))
#            odb.steps[self.stepname].frames
#            odb.steps[str(stepNames[desired_step_nr])].frames
#        except KeyError or TypeError:
        except:
            if (self.batch):
                print "output '"+outputname+"' does not exist in field '"+field.name+"'"
                sys.exit()
            else:
                print "======="
                print "These outputs are available: "
                print "(example result) is from the first value of actual region: "
                print "-------"

                attrs = dir(values[0])
                selected_attrs = []                              #eine gefilterte liste erstellen (ohne __blabla__ etc)
                for attr in attrs:
                    if (re.match('[^_]', str(attr)) and str(attr) != "instance" and str(attr) != "dataDouble"):
                        selected_attrs.append(attr)
                
                outputNr = 0
                for selected_attr in selected_attrs:
                    try:
                        result = getattr(values[0], selected_attr)
                    except:
                        pass
#                        print "(" + str(outputNr) + ") " + selected_attr + " = "+str(result)
                    print "(" + str(outputNr) + ") " + selected_attr + " ("+str(result)+")"
                    outputNr+=1
                print "-------"

                # User Abfrage
                desired_output_nr = raw_input("Please specify output: ")
                while ((re.search('\D', str(desired_output_nr))) or ((len(selected_attrs)-1) < int(desired_output_nr)) or (int(desired_output_nr)) < 0):
#                    print desired_output_nr
                    desired_output_nr = raw_input("impermissible choice - please use an index mentioned above: ")

#                field = frame.fieldOutputs[fieldKeys[int(desired_output_nr)]].getSubset(region=self.region)
                outputname = str(selected_attrs[int(desired_output_nr)])
                print "You've chosen output '" +outputname+ "'"
                
                # bei nodeSets und elementSets gibt es mehrere Ergebnisdaten, deshalb ein array
                output_array = []
                for value in values:
                    output_array.append(getattr(value, outputname))

        return (outputname, output_array)


# =============================
# Method: ermittlung der postfunction
# =============================
    def _getpostfunction(self, postfunction):

        postfunctions = ("none", "value_1", "value_2", "value_3", "vector")
        
        try: # feststellen, ob es die postfunction ueberhaupt gibt
            if (postfunction not in postfunctions):
                raise ('unknown postfunction '+ postfunction)
            else:
                return (postfunction, postfunction) 
            
        except:
            if (self.batch):
                print "error: unknown postfunction "+postfunction
                sys.exit()
            else:
                print "======="
                print "These postfunctions are available "
                print "If you don't know - try 'none' first"
                print "-------"

                postfunctionNr = 0
                
                for postfunction in postfunctions:
                    print "(" + str(postfunctionNr) + ") " + postfunction
                    postfunctionNr +=1
                print "-------"

                # User Abfrage
                desired_postfunction_nr = raw_input("Please specify postfunction: ")
                while ((re.search('\D', str(desired_postfunction_nr))) or ((len(postfunctions)-1) < int(desired_postfunction_nr)) or (int(desired_postfunction_nr)) < 0):
#                    print desired_coordsys_nr
                    desired_postfunction_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                postfunction = postfunctions[int(desired_postfunction_nr)]
                print "You've chosen postfunction '" +postfunction+ "'"
                
                return (postfunction, postfunction)

# =============================
# Method: ermittlung des results
# =============================
    def _getresult(self):

        output_array = self.output
        
#        for output in output_array:
#            search = re.search('[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*,\s*[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*,\s*[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', str(output))
##           search = re.search('\(.+\)', str(output))
##            search2 = re.search('[^\[\]]', search.group())
#            if (search):
#                array = search.group()
#                output = array
##                print str(array)
#            print str(output)
        ergebnis = self.output

        for output in output_array:

            if self.postfunction == "none":
                ergebnis = str(output)
            
            if self.postfunction == "value_1":
                search = re.search('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', str(output))
                if (search):
                    ergebnis = str(search.group(1))
                else:
                    ergebnis = "output '"+str(output)+"' doesn't match pattern used in postfunction 'value_1'"

            elif self.postfunction == "value_2":
                search = re.search('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', str(output))
                if (search):
                    ergebnis = str(search.group(3))
                else:
                    ergebnis = "output '"+str(output)+"' doesn't match pattern used in postfunction 'value_2'"

            elif self.postfunction == "value_3":
                search = re.search('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', str(output))
                if (search):
                    ergebnis = str(search.group(5))
                else:
                    ergebnis = "output '"+str(output)+"' doesn't match pattern used in postfunction 'value_3'"

            elif self.postfunction == "vector":
                search = re.search('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\s*)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*,?*\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', str(output))
                if (search):
                    ergebnis = str(search.group())
                else:
                    ergebnis = "output '"+str(output)+"' doesn't match pattern used in postfunction 'vector'"

# ausgabe des ergebniswertes            
            print ergebnis

#        print self.output

        if (self.batch == False):
# falls in den einzelnen parametern blanks vorkommen, werden diese maskiert mit anfuehrungszeichen
            arg_coordsys_evtl_mit_anfuehrungszeichen = self.arg_coordsys
            search = re.search('[\s;]+', str(self.arg_coordsys))
            if (search):
                arg_coordsys_evtl_mit_anfuehrungszeichen = "\""+self.arg_coordsys+"\""
            
            arg_field_evtl_mit_anfuehrungszeichen = self.arg_field
            search = re.search('[\s;]+', str(self.arg_field))
            if (search):
                arg_field_evtl_mit_anfuehrungszeichen = "\""+self.arg_field+"\""

            print "To get the same information in batch mode, call:"
            command = "abaqus python "+sys.argv[0]+" --odb "+self.arg_odb+" --stepname "+self.arg_stepname+" --framenr "+str(self.arg_framenr)+" --instance "+self.arg_instance+" --"+self.arg_regiontype+" "+str(self.arg_region)+" --field "+arg_field_evtl_mit_anfuehrungszeichen+" --output "+self.arg_output+" --coordsys "+arg_coordsys_evtl_mit_anfuehrungszeichen+" --postfunction "+self.arg_postfunction
            print command
        

# =============================
# Method: ermittlung der regiontypes
# =============================
    def _getregiontype(self, nid, eid, nset, elset):
        odb = self.odb
        arg_regiontype = ""
        
        if (nid != "None"):
            regiontype = "nodes"
            arg_regiontype = "nid"
        elif (eid != "None"):
            regiontype = "elements"
            arg_regiontype = "eid"
        elif (nset != "None"):
            regiontype = "nodeSets"
            arg_regiontype = "nset"
        elif (elset != "None"):
            regiontype = "elementSets"
            arg_regiontype = "elset"
        else:
            if (self.batch):
                print "no region (nid, eid, nset or elset) specified."
                sys.exit()
                

            print "======="
            print "This kind of output regions are available:"
            print "-------"
            
            regiontypeNr = 0
            regionTypes = ["nodes", "elements", "nodeSets", "elementSets"]
            arg_regionTypes = ["nid", "eid", "nset", "elset"]
            for regionType in regionTypes:
                print "(" + str(regiontypeNr) + ") " + regionType
                regiontypeNr+=1
            print "-------"
            
            # User Abfrage
            desired_regiontype_nr = raw_input("Please specify regionType: ")
            while ((re.search('\D', str(desired_regiontype_nr))) or ((len(regionTypes)-1) < int(desired_regiontype_nr)) or (int(desired_regiontype_nr)) < 0):
                print desired_regiontype_nr
                desired_regiontype_nr = raw_input("impermissible choice - please use an index mentioned above: ")

            regiontype = regionTypes[int(desired_regiontype_nr)]
            arg_regiontype = arg_regionTypes[int(desired_regiontype_nr)]
            print "You've chosen type '" +regiontype+ "'"
            
#        print "regiontype="+regiontype
#        print "RETURN: "+arg_regiontype+str(regiontype)
        return (arg_regiontype, regiontype)


# =============================
# Method: ermittlung der region
# =============================
    def _getregion(self, regiontype, nid, eid, nset, elset):
#        odb = self.odb
        instance = self.instance

# ermittlung der knotennummer, falls nicht bekannt
        if (regiontype == "nodes"):

            nodes = instance.nodes
            nid_existent = False
            for node in nodes:
                try:                # falls nid='None' ist, soll exception abgefangen werden
                    if (node.label == int(nid)):
                        nid_existent = True
                        return (node.label, node)
                except:
                    pass
            if ((nid_existent == False) and (self.batch)):
                print "nid '"+nid+"' does not exist in regiontype '"+regiontype+"'"
                sys.exit()
            
            else:
                nodes = instance.nodes
                amount_nodes = len(nodes)
                print "======="
                print str(amount_nodes)+" nodes are available in instance '"+instance.name+"'"
                print "-------"
            
            # User Abfrage
                desired_nid = input("Please specify nid: ")

                searching_nid = True;
            
                while(searching_nid):
                    for node in nodes:
                        try:
                            if (node.label == desired_nid):
#                            print "nid "+str(desired_nid)+" found"
                                print "You've chosen node '" +str(node.label)+ "'"
                                return (node.label, node)
                                searching_nid = False;
                        except:
                            pass
                    if (searching_nid):
                        desired_nid = input("node nid="+str(desired_nid)+" not found - please try again: ")

        elif (regiontype == "elements"):

            elements = instance.elements
            eid_existent = False
            for element in elements:
                try:                # falls eid='None' ist, soll exception abgefangen werden
                    if (element.label == int(eid)):
                        eid_existent = True
                        return (element.label, element)
                except:
                    pass
            if ((eid_existent == False) and (self.batch)):
                print "eid '"+eid+"' does not exist in regiontype '"+regiontype+"'"
                sys.exit()
            
            else:
                elements = instance.elements
                amount_elements = len(elements)
                print "======="
                print str(amount_elements)+" elements are available in instance '"+instance.name+"'"
                print "-------"
            
            # User Abfrage
                desired_eid = input("Please specify eid: ")

                searching_eid = True;
            
                while(searching_eid):
                    for element in elements:
                        try:
                            if (element.label == desired_eid):
#                            print "nid "+str(desired_nid)+" found"
                                print "You've chosen element '" +str(element.label)+ "'"
                                return (element.label, element)
                                searching_eid = False;
                        except:
                            pass
                    if (searching_eid):
                        desired_eid = input("element eid="+str(desired_eid)+" not found - please try again: ")

        elif (regiontype == "nodeSets"):

#            nset_existent = False
            nodeset = "unbekannt"
            
            try:                # ist gewuenschtes nset nicht vorhanden, greift exception..
                nodesetKeys = instance.nodeSets.keys()
                matched = []    # die nsets, deren namen auf das pattern matched werden hier gesammelt
#                print str(nodesetKeys)
                for nodesetKey in nodesetKeys:
#                    print "trying "+nset+" with "+str(nodesetKey)
                    search = re.search("^"+str(nset)+"$", str(nodesetKey))

                    if (search):
#                        print "erfolgreich"
                        matched.append(str(nodesetKey))
                    else:
#                        print "nicht erfolgreich"
                        pass

                if (len(matched)==1):
                    nodeset = instance.nodeSets[matched[0]]
                else:
                    raise
            except:
                if ((self.batch) and (len(matched)==0)):
                    print "nset with pattern '"+nset+"' does not exist in regiontype '"+regiontype+"'"
                    sys.exit()
            
                elif ((self.batch) and (len(matched)>1)):
                    print "more than one nset with pattern '"+nset+"' does exist in regiontype '"+regiontype+"'. please be more precise. found nsets: "+str(matched)
                    sys.exit()
            
                else:
                    print "======="
                    print "This nodeSets are available:"
                    print "-------"
            
                    nodesetKeys = instance.nodeSets.keys()
                    nodesetNr = 0
                    for nodesetKey in nodesetKeys:
                        print "(" + str(nodesetNr) + ") " + nodesetKey
                        nodesetNr+=1
                    print "-------"
            
            # User Abfrage
                    desired_nodeset_nr = raw_input("Please specify nodeSet: ")
                    while ((re.search('\D', str(desired_nodeset_nr))) or ((len(nodesetKeys)-1) < int(desired_nodeset_nr)) or (int(desired_nodeset_nr)) < 0):
                        print desired_nodeset_nr
                        desired_nodeset_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                    nodeset = instance.nodeSets[nodesetKeys[int(desired_nodeset_nr)]]
                    print "You've chosen nodeSet '" +nodeset.name+ "'"
                
            return (nodeset.name, nodeset)

        elif (regiontype == "elementSets"):

            elementset = "unbekannt"
            
            try:                # ist gewuenschtes nset nicht vorhanden, greift exception..
                elementsetKeys = instance.elementSets.keys()
                matched = []    # die nsets, deren namen auf das pattern matched werden hier gesammelt
#                print str(nodesetKeys)
                for elementsetKey in elementsetKeys:
#                    print "trying "+nset+" with "+str(nodesetKey)
                    search = re.search("^"+str(elset)+"$", str(elementsetKey))

                    if (search):
#                        print "erfolgreich"
                        matched.append(str(elementsetKey))
                    else:
#                        print "nicht erfolgreich"
                        pass

                if (len(matched)==1):
                    elementset = instance.elementSets[matched[0]]
                else:
                    raise
            except:
                if (self.batch) and (len(matched)==0):
                    print "elset '"+elset+"' does not exist in regiontype '"+regiontype+"'"
                    sys.exit()
            
                elif ((self.batch) and (len(matched)>1)):
                    print "more than one elset with pattern '"+elset+"' does exist in regiontype '"+regiontype+"'. please be more precise. found elsets: "+str(matched)
                    sys.exit()
            
                else:
                    print "======="
                    print "This elementSets are available:"
                    print "-------"
            
                    elementsetKeys = instance.elementSets.keys()
                    elementsetNr = 0
                    for elementsetKey in elementsetKeys:
                        print "(" + str(elementsetNr) + ") " + elementsetKey
                        elementsetNr+=1
                    print "-------"
            
            # User Abfrage
                    desired_elementset_nr = raw_input("Please specify elementSet: ")
                    while ((re.search('\D', str(desired_elementset_nr))) or ((len(elementsetKeys)-1) < int(desired_elementset_nr)) or (int(desired_elementset_nr)) < 0):
                        print desired_elementset_nr
                        desired_elementset_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                    elementset = instance.elementSets[elementsetKeys[int(desired_elementset_nr)]]
                    print "You've chosen elementSet '" +elementset.name+ "'"
                
            return (elementset.name, elementset)

# =============================
# Method: ermittlung des instance-objektes
# =============================
    def _getinstance(self, instance_name):

        odb = self.odb
        try:
            instance = odb.rootAssembly.instances[instance_name]
#        except KeyError or TypeError:
        except KeyError:
            if (self.batch):
                print "instance '"+instance_name+"' not found in odb '"+odb.name+"'"
                sys.exit()
            else:
                print "======="
                print "These instances are available in " + odb.name# + str(odb.sectionCategories)
                print "-------"

                instanceNr = 0
                instanceKeys = odb.rootAssembly.instances.keys()
                for instanceKey in instanceKeys:
                    print "(" + str(instanceNr) + ") " + instanceKey
                    instanceNr+=1
                print "-------"

                # User Abfrage
                desired_instance_nr = raw_input("Please specify instance: ")
                while ((re.search('\D', str(desired_instance_nr))) or ((len(instanceKeys)-1) < int(desired_instance_nr)) or (int(desired_instance_nr)) < 0):
                    print desired_instance_nr
                    desired_instance_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                instance = odb.rootAssembly.instances[instanceKeys[int(desired_instance_nr)]]
                print "You've chosen instance '" +instance.name+ "'"
                return (instance.name, instance)
        
        return (instance_name, instance)

# =============================
# Method: ermittlung des koordinatensystem-objektes
# =============================
    def _getcoordsys(self, coordsys_name_asked):

        odb = self.odb
        try:# feststellen ob sich ein object coordinatensystem mit dem namen 'coordsys_name' im odb befindet, wenn nicht->exception
            # ist das system ermittelt, soll das field-output transformiert werden
            # eine exception wird auch geworfen, wenn vom letzten array-eintrag versucht wird der name zu ermitteln
#            if (cordsys_name is  "none"):
#                raise
#            coordsyss = odb.rootAssembly.connectorOrientations
            coordsys_names = odb.rootAssembly.datumCsyses.keys()
            for coordsys_name in coordsys_names:
#                print "ASKED: "+coordsys_name_asked+" PRESENT: "+coordsys_name
                if coordsys_name == coordsys_name_asked:
                    return (coordsys_name, odb.rootAssembly.datumCsyses[coordsys_name_asked])
            
            if coordsys_name_asked == "_global_":
                return ("_global_", None)
            
            else:
                raise

        except:
            if (self.batch):
                print "coordinate system '"+coordsys_name_asked+"' not found in odb '"+odb.name+"'"
                sys.exit()
            else:
                print "======="
                print "These coordinate systems are available in " + odb.name# + str(odb.sectionCategories)
                print "-------"

                coordsysNr = 0
                coordsys = odb.rootAssembly.datumCsyses
                coordsys_names = odb.rootAssembly.datumCsyses.keys()
#                coordsys_keys = coordsyss.keys()
#                print coordsyss
#                print coordsyss_keys
#                print "Laenge des arrays: " + str(len(coordsyss))
                
#                coordsyss_gereinigt = []
#                for coordsys in coordsyss:
#                    print coordsys
#                    if (coordsys.localCsys1):
#                        coordsyss_gereinigt.append(coordsys)
#                print "Laenge des arrays nach reinigung: " + str(len(coordsyss_gereinigt))
                
#                for coordsys in coordsyss_gereinigt:
                for coordsys_name in coordsys_names:
#                    if (coordsys.localCsys1):
                        print "(" + str(coordsysNr) + ") " + coordsys_name
                        coordsysNr+=1
                print "(" + str(coordsysNr) + ") " + "_global_"
                print "-------"

                # User Abfrage
                desired_coordsys_nr = raw_input("Please specify coordinate system: ")
                
#                print "string desired_coordsys_nr:  "+str(desired_coordsys_nr)
#                print "length coordsys:             "+str(len(coordsyss))
#                print "integer desired_soordsys_nr: "+str(int(desired_coordsys_nr))
                
                while ((re.search('\D', str(desired_coordsys_nr))) or ((len(coordsys_names)) < int(desired_coordsys_nr)) or (int(desired_coordsys_nr)) < 0):
#                    print desired_coordsys_nr
                    desired_coordsys_nr = raw_input("impermissible choice - please use an index mentioned above: ")

                try:
                    if coordsys_names[int(desired_coordsys_nr)]:
                        coordsys_name = coordsys_names[int(desired_coordsys_nr)]
                        print "You've chosen coordinate system '" +coordsys_name+ "'"
                        return (coordsys_name, odb.rootAssembly.datumCsyses[coordsys_name])
#                    self.field = self.field.getTransformedField(odb.rootAssembly.connectorOrientations[int(desired_coordsys_nr)].localCsys1)
                except:
                    print "You've chosen coordinate system '_global_'"
                    coordsys_name = "_global_";
                    return (coordsys_name, None)
