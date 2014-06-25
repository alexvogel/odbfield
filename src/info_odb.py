#!/usr/bin/python

import sys

if len(sys.argv)!=2:
    print "call: abaqus python $scriptname $odbfile"
    sys.exit()

from odbAccess import *
from textRepr import *

odbfile = sys.argv[1]
if isUpgradeRequiredForOdb(odbfile):
    print "The database is from a previous release of Abaqus."
    print "Run abaqus -upgrade -job <newFileName> -odb <oldOdbFileName> to upgrade it."
    sys.exit()

odb=openOdb(odbfile)

#prettyPrint(odb,2)

#print "odbfile"

#from odbAccess import *
#from textRepr import *
#odb=openOdb('odbfile')

###############################
#
# Stepabfrage
#
###############################
print "======="
print "These steps are available in " + odb.name# + str(odb.sectionCategories)
print "-------"
stepNames = odb.steps.keys()

stepNr = 0
for stepName in stepNames:
    print "(" + str(stepNr) + ") " + stepName
    stepNr+=1
print "-------"

desired_step_nr = input("Please specify the step of desire: ")

while (((len(stepNames)-1) < desired_step_nr ) or (desired_step_nr < 0)):
    desired_step_nr = input("unknown choice - please use an index mentioned above: ")

step = str(stepNames[desired_step_nr])
print "You've chosen step '" + step + "'"

###############################
#
# Frameabfrage
#
###############################
print "======="
print "These frames are available in " + step
print "-------"

frameNr = 0
frames = odb.steps[str(stepNames[desired_step_nr])].frames
for frame in frames:
    print "(" + str(frameNr) + ") " + frame.description
    frameNr+=1
print "-------"

desired_frame_nr = input("Please specify the frame of desire: ")

#print "Unveraendert: " + str(desired_frame_nr)
#print "als int: " + str(int(desired_frame_nr))

while (((len(frames)-1) < int(desired_frame_nr) ) or ( int(desired_frame_nr) < 0)):
    desired_frame_nr = input("unknown choice - please use an index mentioned above: ")

frame = frames[desired_frame_nr]
print "You've chosen frame '" + frame.description + "'"

###############################
#
# Partabfrage
#
###############################
print "======="
print "These parts are available in " + odb.name
print "-------"

partNr = 0
#parts = odb.parts.keys()
parts = odb.rootAssembly.instances.keys()

for part in parts:
    print "(" + str(partNr) + ") " + part
    partNr+=1
print "-------"

desired_part_nr = input("Please specify the part of desire: ")

while (((len(parts)-1) < desired_part_nr ) or (desired_part_nr < 0)):
    desired_part_nr = input("unknown choice - please use an index mentioned above: ")

part = parts[desired_part_nr]
print "You've chosen part '" + part + "'"

###############################
#
# Elset Abfrage
#
###############################
print "======="
print "These elsets are available in " + part
print "-------"

setNr = 0
#parts = odb.parts.keys()
nodesets = odb.rootAssembly.instances[part].nodeSets.keys()
print odb.rootAssembly.instances[part]
elsets = odb.rootAssembly.instances[part].elementSets.keys()
#print odb.rootAssembly.instances[part].elementSets
#blub = odb.rootAssembly.instances[part].nodeSets
#blab = odb.rootAssembly.instances[part]
#print blub
#print blab

for elset in elsets:
    print "(" + str(setNr) + ") " + elset
    setNr+=1
print "-------"

desired_elset_nr = input("Please specify the elset of desire: ")

while (((len(elsets)-1) < desired_elset_nr ) or (desired_elset_nr < 0)):
    desired_elset_nr = input("unknown choice - please use an index mentioned above: ")

elset = elsets[desired_elset_nr]
print "You've chosen elset '" + elset + "'"

###############################
#
# fieldOutput Abfrage
#
###############################

fieldOutputNr = 0
fieldOutputs = frame.fieldOutputs.keys()

for fieldOutput in fieldOutputs:
    print "(" + str(fieldOutputNr) + ") " + fieldOutput
    fieldOutputNr+=1
print "-------"

desired_fieldOutput_nr = input("Please specify the fieldOutput of desire: ")

while (((len(fieldOutputs)-1) < desired_fieldOutput_nr ) or (desired_fieldOutput_nr < 0)):
    desired_fieldOutput_nr = input("unknown choice - please use an index mentioned above: ")

fieldOutput = fieldOutputs[desired_fieldOutput_nr]
print "You've chosen fieldOutput '" + fieldOutput + "'"

###############################
#
# Den End-field-Output-Aufruf generieren
#
###############################

#fo = fieldOutput.keys()

#ergebnisse = frame.fieldOutputs[fieldOutput]
#ergebnisse = frame.fieldOutputs.values()
#ergebnisse = frame.fieldOutputs[fieldOutput].componentLabels
#ergebnisse = frame.fieldOutputs[fieldOutput].name
#ergebnisse = frame.fieldOutputs[fieldOutput].data
ergebnisse = frame.fieldOutputs[fieldOutput]

#prettyPrint (frame.fieldOutputs[fieldOutput], 1)


#for ergebnisse in frame.fieldOutputs[fieldOutput].values:
    
print "OUTPUT: "
print ergebnisse


#    print "elementLabel: " + str(ergebnisse.elementLabel)
#    print "position: " + ergebnisse.locations







print "value = 0"
ergebnisse = frame.fieldOutputs[fieldOutput].values[0]
print ergebnisse

print "value = 1"
ergebnisse = frame.fieldOutputs[fieldOutput].values[1]
print ergebnisse

print "value = 2"
ergebnisse = frame.fieldOutputs[fieldOutput].values[2]
print ergebnisse

print "value = 3"
ergebnisse = frame.fieldOutputs[fieldOutput].values[3]
print ergebnisse

print "value = 4"
ergebnisse = frame.fieldOutputs[fieldOutput].values[4]
print ergebnisse

#for v in ergebnisse.values():
#    print v

#print "These are the values stored under your specifications"
#print ergebnisse





#variables = frame.historyOutputs.keys()

#for variable in variables:
#    print variable


#instances = odb.rootAssembly.instances.keys()
#instances = odb.parts.keys()

#print instances


