import sys
import os
digodb_version = "[% version %]"
digodb_date = "[% date %]"

# 0.02    Version bei BMW
# 0.03    25.05.2011    Wenn das Ergebnis ein Array mit genau 3 kommagetrennten Werten enthaelt, so werden die Werte ohne Klammern etc ausgegeben 
# 0.04    30.11.2011    Zusaetzlicher Parameter 'coordsys' implementiert
# 0.05    17.01.2012    Zusaetzlicher Parameter 'postfunction' implementiert
# 0.06    18.01.2012    Fehlverhalten bei --coordsys behoben
# 0.07    19.01.2012    Liste der angezeigten Field-Output-Variablen wird reduziert um die, die keine values enthalten
# 0.08    20.01.2012    Fuer elset und nset duerfen fuer die Namen auch Pattern-Matching-Muster verwendet werden
# 0.08a    09.02.2012    klassennamen und sonstige Bezeichnungen geaendert
# 0.09    27.03.2012    Korrektur der Koordinatensystemabfrage
#                       Wenn Koordinatensystem ein \s oder ; im Namen tragen, werden sie im Informationsprint der interaktiven Ausgabe in Anfuehrungszeichen gesetzt 
# 0.10    02.04.2012    Absturz bei nicht vorhandenen Instance-Namen behoben
# 0.11    24.07.2012    postfunctions zerteilen vektoren jetzt auch wenn kein ',' als trennzeichen vorhanden ist. (ab abaqus v6.11)
# 0.2.0   27.06.2014    postfunctions zerteilen vektoren update (fehler bei vektor mit muster /0. 0. 0./ behoben)

#print "Script dir: ", os.path.realpath(os.path.dirname(sys.argv[0]))

external_lib = os.path.realpath(os.path.dirname(sys.argv[0])) + "/../lib"
sys.path.append(external_lib)
#print sys.path
import argparse
from field import *

# Definieren der Kommandozeilenparameter
parser = argparse.ArgumentParser(description='a tool for obtaining information (field output) from an abaqus output database file (odb).',
                                 epilog='author: alexander.vogel@prozesskraft.de | version: '+digodb_version+' | date: '+digodb_date)
parser.add_argument('--odb', metavar='ODBFILE', type=str, required=True,
                   help='abaqus output database file')
parser.add_argument('--framenr', metavar='FRAMENR', action='store',
                   help='number of frame (increment)')
parser.add_argument('--instance', metavar='INSTANCE', action='store', default='PART-1-1',
                   help='part of the model e.g. PART-1-1')
parser.add_argument('--field', metavar='FIELD', action='store',
                   help='name of field variable. e.G. U, RF, CF etc.')
parser.add_argument('--output', metavar='OUTPUT', action='store',
                   help='name of output variable. e.G. data, mises')
parser.add_argument('--coordsys', metavar='COORDINATESYSTEM', action='store',
                   help='name of coordinate system.')
parser.add_argument('--postfunction', metavar='POSTFUNCTION', action='store',
                   help='name of function to manipulate retrieved values.')
parser.add_argument('--interactive', "-i", action='store_true', default=False,
                   help='interactive mode.')
#parser.add_argument('--batch', "-b", action='store_true', default=False,
#                   help='non-interactive mode.')

# Exklusivgruppen der Parameter
group = parser.add_mutually_exclusive_group()
group.add_argument('--stepname', metavar='STEPNAME', action='store',
                   help='name of step')
#group.add_argument('--stepnr', metavar='STEPNR', action='store',
#                   help='number of step containing the information')

# Exklusivgruppen der Parameter
group_2 = parser.add_mutually_exclusive_group()
group_2.add_argument('--elset', metavar='ELSETNAME', action='store',
                   help='name of element set. regular expressions may be used. opening and closing anchors are set implicitly')
group_2.add_argument('--nset', metavar='NSETNAME', action='store',
                   help='name of node set. regular expressions may be used. opening and closing anchors are set implicitly')
group_2.add_argument('--nid', metavar='NID', action='store',
                   help='node id')
group_2.add_argument('--eid', metavar='EID', action='store',
                   help='element id')

args = parser.parse_args()
#print args

#print(args.accumulate(args.integers))
#print str(args)
ergebniswert = field(args)
