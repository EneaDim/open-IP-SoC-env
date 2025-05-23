
# Copyright 2023 AUC Open Source Hardware Lab
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import getopt
import os
import re
import copy
import sys
import json
import time
import xml.etree.ElementTree as ET

##########################################################################################

pathCellsDelays = []
criticalPaths = []
blackboxCells = []
pathNames = []
netDelays = []

##########################################################################################


class Pin:
    def __init__(self, name, net, type):
        self.name = name
        self.net = net
        self.type = type


##############################


class StandardCell:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.pins = []

    def addPin(self, pin):
        self.pins.append(pin)


##########################################################################################


def get_offset(line):
    offset = re.search(r"\b(Delay)\b", line)
    return offset.start()


##############################


def add_cell_to_path(_standardCell, tempCriticalPath):
    flag = False
    for iterationCell in tempCriticalPath:
        if _standardCell.id == iterationCell.id:
            flag == True
            pinFlag = False
            for pin in iterationCell.pins:
                if pin.name == _standardCell.pins[0].name:
                    pinFlag = True
                    return pin.net
            if pinFlag == False:
                iterationCell.pins.append(copy.deepcopy(_standardCell.pins[0]))
            return copy.copy(_standardCell.pins[0].net)

    if flag == False:
        tempCriticalPath.append(copy.deepcopy(_standardCell))
    return copy.copy(_standardCell.pins[0].net)


##############################


def add_pin_to_blackbox_cell(pin, cell):
    flag = False
    for iterationPin in cell.pins:
        if pin.name == iterationPin.name:
            flag == True
            return

    if flag == False:
        tempPin = Pin(copy.deepcopy(pin.name), "", copy.deepcopy(pin.type))
        cell.pins.append(copy.deepcopy(tempPin))
    return


def add_blackbox_cell(_standardCell):
    flag = False
    for iterationCell in blackboxCells:
        if _standardCell.name == iterationCell.name:
            flag == True
            # take care of deep copy
            for pin in _standardCell.pins:
                add_pin_to_blackbox_cell(pin, iterationCell)
            return

    if flag == False:
        blackboxCells.append(copy.deepcopy(_standardCell))
    return


##############################


def checkArgs(argv):
    staReportFile = ""
    skinFile = ""
    numberOfPaths = -1
    sortType = "none"
    STAtool = ""

    try:
        opts, args = getopt.getopt(
            argv, "i:s:h:n:t:", ["input=", "skin=", "help", "npaths=", "sort=", "tool="]
        )
    except getopt.GetoptError:
        print("invalid arguments!")
        print(
            """
Syntax:
    run: python3 interactiveReport.py -i <STA_Report_File_Path> -s <Skin_File_Path> -t <STA_tool>

Options:
    --tool=<primetime/opensta> or -t <"primetime" or "opensta">
                        This option is used to specify the STA tool used to generate. 
                        Use "primetime" for PrimeTime and "opensta" for OpenSTA.
    
    --npaths=<numberOfPaths> or -n <numberOfPaths>
                        This option is used to specify the number of paths to be
                        generated. If this option is not specified, all paths are
                        generated.
                        
    --sort=<"asc" or "desc">   
                        This option is used to sort the paths in ascending 
                        or descending order based on slack. 
                        "asc" for ascending and "desc" for descending order.
                        
"""
        )
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                """
Syntax:
    run: python3 interactiveReport.py -i <STA_Report_File_Path> -s <Skin_File_Path> -t <STA_tool>

Options:
    --tool=<primetime/opensta> or -t <"primetime" or "opensta">
                        This option is used to specify the STA tool used to generate. 
                        Use "primetime" for PrimeTime and "opensta" for OpenSTA.
    
    --npaths=<numberOfPaths> or -n <numberOfPaths>
                        This option is used to specify the number of paths to be
                        generated. If this option is not specified, all paths are
                        generated.
                        
    --sort=<"asc" or "desc">   
                        This option is used to sort the paths in ascending 
                        or descending order based on slack. 
                        "asc" for ascending and "desc" for descending order.
                        
"""
            )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            staReportFile = arg
        elif opt in ("-s", "--sfile"):
            skinFile = arg
        elif opt in ("-n", "--npaths"):
            numberOfPaths = int(arg)
        elif opt in ("--sort="):
            sortType = arg
        elif opt in ("-t", "--tool"):
            STAtool = arg

    return staReportFile, skinFile, numberOfPaths, sortType, STAtool


#################################


def generate_dirs(designName):

    if not os.path.exists("signoff/path_view"):
        os.makedirs("signoff/path_view")

    if not os.path.exists("signoff/path_view/" + designName):
        os.makedirs("signoff/path_view/" + designName)

    if not os.path.exists("signoff/path_view/" + designName + "/schematics"):
        os.makedirs("signoff/path_view/" + designName + "/schematics")

    if not os.path.exists("signoff/path_view/" + designName + "/json"):
        os.makedirs("signoff/path_view/" + designName + "/json")

    if not os.path.exists("signoff/path_view/" + designName + "/website"):
        os.makedirs("signoff/path_view/" + designName + "/website")


#################################


def generateNetInteractions(path):
    filename = "signoff/path_view/" + designName + "/schematics/" + path + ".svg"
    tree = ET.parse(filename)
    root = tree.getroot()

    # Find all line elements
    lines = root.findall(".//{http://www.w3.org/2000/svg}line")
    netInteractions = "\n"
    for line in lines:
        classline = line.get("class")
        if "net_" in classline:
            # Get XML code for line element
            classline = classline.split(" ")
            classline = classline[0]
            classline = classline.split("_")
            classline = classline[1]
            temp = ""
            index = int(classline)
            if index == -2:
                temp = 'onClick="net_click(this.id)" id="' + str(0) + '" class="net'
            elif index == -1:
                continue
            else:
                temp = (
                    'onClick="net_click(this.id)" id="'
                    + str(index + 1)
                    + '" class="net'
                )
            newstyle = "stroke: white; opacity: 0 ; stroke-width: 18;"
            lineheader = "line  "

            line_xml = ET.tostring(line, encoding="unicode")
            temp_string = line_xml.replace("stroke-width: 1", newstyle)
            temp_string = temp_string.replace('class="net_', temp)
            temp_string = temp_string.replace(
                'ns0:line xmlns:ns0="http://www.w3.org/2000/svg"', lineheader
            )
            netInteractions += temp_string + "\n"
    return netInteractions

##############################

def extractValuesFromstring(line):
    line = line.strip()                         # Remove leading/trailing spaces and tabs
    line = re.sub(r'\s+', ' ', line)            # Remove consecutive spaces or tabs
    texts = line.split(' ')                     # Extract texts separated by spaces
    texts = [text for text in texts if text]    # Remove empty texts
    return texts

def buildFullPath(logicGroups, clockGroups, no_nets):          # takes both the logic and clock paths and builds the full path
    
    tempPathDelays = []                    # tempPathDelays contains the path delays in an iteration
    tempNetDelays = []                     # tempNetDelays contains the net delays in an iteration
    tempCriticalPath = []                  # tempCriticalPath contains a local copy of a critical path in an iteration
    
    wire = 0                 # wire is the number of nets in a path, propagated through logic and clock paths
    wire = buildPath(logicGroups, tempPathDelays, tempNetDelays,tempCriticalPath, wire, "logic")
    wire = buildPath(clockGroups, tempPathDelays, tempNetDelays,tempCriticalPath, wire, "clock")
    no_nets.append(wire+2)
    
    for cell in tempCriticalPath:           # add the new cells discovered in this path to the set of blackbox cells
        add_blackbox_cell(cell)
                                                            # Add the newly created path to the criticalPaths, the path contains both logic and clock
    pathCellsDelays.append(copy.deepcopy(tempPathDelays))   # add the path delays to the pathCellsDelays array
    netDelays.append(copy.deepcopy(tempNetDelays))          # add the net delays to the netDelays array
    criticalPaths.append(copy.deepcopy(tempCriticalPath))   # add the critical path to the criticalPaths array
    pass


def buildPath(groups, tempPathDelays, tempNetDelays,tempCriticalPath, wire = 0, type = "logic"):

    i = -1
    _net = "clk "

    for criticalPathCell in groups:
            i += 1
            
            cellName = re.search(r'\((.*?)\)', criticalPathCell[0]).group(1)                    # extract the cell name "standard cell name"
            cellId = re.search(r'^(.*)/', criticalPathCell[0]).group(1)                         # extract the cell id "local naming"
            cellIdAndInputPin =  re.search(r'\s*(.*?)\s*\(', criticalPathCell[0]).group(0)      # extract the cell id and input pin name
            inputPinName =  re.search(r'/([^/]+)\s*\(', criticalPathCell[0]).group(1)           # extract the input pin name
            inputPinName = inputPinName.strip()                                                 # remove leading and trailing spaces
            inputPinNumbers = re.findall(r'\d+\.\d+', criticalPathCell[0])                      # extract all the input report numbers
            inputPinTime   = inputPinNumbers [-1]                                               # assign the input pin time
            inputPinDelay  = inputPinNumbers [-2]                                               # assign the input pin delay
            _InputStandardCell = StandardCell(cellName, cellId)
            _InputPin = Pin(inputPinName, _net, "input")
            _InputCell = [cellId,"input",inputPinDelay,inputPinTime,inputPinName]
            tempPathDelays.append(_InputCell)
            _InputStandardCell.addPin(copy.deepcopy(_InputPin))
            _net_report = [inputPinDelay, inputPinTime]
            tempNetDelays.append(_net_report)
            if (i == len(groups)-1):
                #if type == "logic":
                #    _InputStandardCell.pins.append(Pin("out", "net_out", "output"))
                _net = add_cell_to_path(_InputStandardCell, tempCriticalPath)
                continue
            _net = add_cell_to_path(_InputStandardCell, tempCriticalPath)
            
            
            cellIdAndOutputPin = re.search(r'\s*(.*?)\s*\(', criticalPathCell[1]).group(1)
            outputPinName =  re.search(r'/([^/]+)\s*\(', criticalPathCell[1]).group(1)
            outputPinName = outputPinName.strip()
            outputPinNumbers = re.findall(r'\d+\.\d+', criticalPathCell[1])
            outputPinTime  = outputPinNumbers[-1]
            outputPinDelay = outputPinNumbers[-2]
            _OutputStandardCell = StandardCell(cellName, cellId)
            _net = "net" + str(wire)
            _OutputPin = Pin(outputPinName, _net, "output")
            wire += 1
            _OutputCell = [cellId,"output",outputPinDelay,outputPinTime,outputPinName]
            tempPathDelays.append(_OutputCell)
            _OutputStandardCell.addPin(copy.deepcopy(_OutputPin))
            _net = add_cell_to_path(_OutputStandardCell, tempCriticalPath)
            repeatednet = copy.copy(_net)
            repeatednet = _net.split("net")
            repeatednet = repeatednet[1]
            repeatednetid = int(repeatednet)
            if repeatednetid != wire-1:
                tempNetDelays[repeatednetid].append(outputPinDelay)
                tempNetDelays[repeatednetid].append(outputPinTime)

    return wire
    

def getGroupsPrimeTime(staReportFile, no_nets):
    processingPath = False              # processingPath is true when the parser is processing a path
    reportString = open(staReportFile, "r+")
    groups=[]                           # groups contains the groups of data
    logicPathGroups = []
    clockPathGroups =[]

    groupString = ["","",""]            # groupString contains the 3 lines of a group, input, output and net
    arr = [7,5,2]                       # arr contains the number of reported data per line, 7 for input, 5 for output, 2 for net
    idx = 0                             # idx is the index of the groupString  
    startPoint = "None"
    endPoint = "None"
    slack = "None"
    counter = -1
    for line in reportString:
        line = line.strip()
        if "Startpoint" in line:
            counter += 1                    # counter is the number of paths
            startPoint = "None"             # startPoint is the start point of a path
            endPoint = "None"               # endPoint is the end point of a path
            slack = "None"                  # slack is the slack of a path
            startPoint = copy.copy(line)
            processingPath = True           # process the upcoming lines as a path
            pass
        elif "Endpoint" in line:
            endPoint = copy.copy(line)
            pass
        elif "slack (MET)" in line:
            # Todo: extract the slack and names
            slack = re.findall(r'\d+\.\d+', line)[-1]                    # extract all the input report numbers
            pathNames.append([startPoint, endPoint, slack, counter])
            pass
        elif processingPath:
            if "data arrival time" in line:
                groups.append(groupString)                          # add the group to the list of groups
                logicPathGroups = copy.deepcopy(groups)
                groupString = ["","",""]                            # reset the group
                idx = 0
                groups.clear()
                pass
            elif "data required time" in line:
                groups.append(groupString)                          # add the group to the list of groups
                clockPathGroups = copy.deepcopy(groups)
                groupString = ["","",""]                            # reset the group
                idx = 0
                buildFullPath(logicPathGroups, clockPathGroups, no_nets)
                logicPathGroups.clear()
                clockPathGroups.clear()
                groups.clear()
                processingPath = False
                pass
            else:
                if ")" not in line:             # check if this is the final line of the group
                    continue
                
                splitLineOnBracket = line.split(")") 
                rightSubString = splitLineOnBracket[1]
                # the right sub string contains the reporting data, extract theses data as a list
                rightSubString = extractValuesFromstring(rightSubString)
                
                # get the number of reported data per line
                textlen = len(rightSubString)   
                
                if (textlen == arr[idx]) or (textlen == arr[idx]+1):        # check if the number of reported data is correct
                    groupString[idx] = line                                 # add the line to the group
                    idx = idx + 1                                           # increment the index
                    if idx == 3:                                            # check if the group is complete
                        
                        groups.append(groupString)                          # add the group to the list of groups
                        groupString = ["","",""]                            # reset the group
                        idx = 0
                else:
                    groupString = ["","",""]
                    idx = 0
        
        
def parsePrimeTime(staReportFile, no_nets):
    getGroupsPrimeTime(staReportFile, no_nets)
    print(len(criticalPaths))
    return no_nets
    
def parseOpenSta(staReportFile, no_nets):
    f = open(staReportFile, "r+")
    processingPath = False                          # processingPath is true when the parser is processing a path
    tempPathDelays = []                             # tempPathDelays contains the path delays in an iteration
    tempNetDelays = []                              # tempNetDelays contains the net delays in an iteration
    tempCriticalPath = []                           # tempCriticalPath contains a local copy of a critical path in an iteration
    offset = 0                                      # offset is the offset of the delay in the report, how many spaces needed to be removed
    counter = -1                                    # counter is the number of paths
    wire = 0                                        
    net_index = -1
    _net = ""
    startPoint = "None"
    endPoint = "None"
    slack = "None"
    _pinType = "input"

    for line in f:
        line = line[offset:]
        line = line.strip()

        if "Delay" in line:
            offset = get_offset(line)

        elif "Startpoint" in line:
            counter += 1
            no_nets.append(2)
            startPoint = "None"
            endPoint = "None"
            slack = "None"
            startPoint = copy.copy(line)

            processingPath = True                       # process the upcoming lines as a path
            tempPathDelays.clear()                      # restore the temp arrays
            tempNetDelays.clear()
            tempCriticalPath.clear()
            _pinType = "input"                          # reset the pin type to input, path starts with input after clock

        elif "Endpoint" in line:
            endPoint = copy.copy(line)

        elif "slack" in line:
            if startPoint != "None":
                slack = copy.copy(line)
                slack = slack.split(" ")
                slack = slack[0]
                pathNames.append([startPoint, endPoint, slack, counter])        # add the names of this path to the pathNames array

        elif processingPath:
            if "data arrival time" in line:
                #tempCriticalPath[-1].pins.append(Pin("out", "net_out", "output"))    # add the output pin to the last cell in the path
                wire += 1                                # increment the wire number
                net_index = -1                           # reset the net index to -1, to start from 0 in the clock path
                _pinType = "input"                       # reset the pin type to input, for the clock path

            elif "data required time" in line: 
                for cell in tempCriticalPath:           # add the new cells discovered in this path to the set of blackbox cells
                    add_blackbox_cell(cell)
                                                                        # Add the newly created path to the criticalPaths, the path contains both logic and clock
                pathCellsDelays.append(copy.deepcopy(tempPathDelays))   # add the path delays to the pathCellsDelays array
                netDelays.append(copy.deepcopy(tempNetDelays))          # add the net delays to the netDelays array
                criticalPaths.append(copy.deepcopy(tempCriticalPath))   # add the critical path to the criticalPaths array
                
                processingPath = False                  # stop processing the upcoming lines as a path
                offset = 0                              # reset the offset to 0
                wire = 0                                # reset the wire number to 0, for a new path
                _pinType = "input"                      # reset the pin type to input, for a new path
                net_index = -1                          
                pass

            elif "(net)" in line:
                pass
            elif "/" in line:

                line = line.split("(")

                cellName = line[1]
                cellName = cellName.split(")")
                cellName = cellName[0]

                line = line[0]
                line = line.split(" ")
                line = list(filter(None, line))
                delay = line[0]
                time = line[1]

                cellNameAndPin = line.pop()
                cellInfo = cellNameAndPin.split("/")
                pinName = cellInfo[-1]
                cellInfo.pop()
                cellId = "_".join(cellInfo)
                cellId = cellId.replace(".", "_")
                cellId = cellId.replace("[", "_")
                cellId = cellId.replace("]", "_")

                _standardCell = StandardCell(cellName, cellId)
                wirecopy = copy.copy(wire)

                if net_index == -1:
                    _net = "clk "
                    net_index += 1
                else:
                    if net_index == 0:
                        _net = "net" + str(wire)
                        net_index += 1
                    elif net_index == 1:

                        net_index = 0
                        wire += 1

                _pin = Pin(pinName, _net, _pinType)

                _cell = []
                _cell.append(cellId)
                _cell.append(_pinType)
                _cell.append(delay)
                _cell.append(time)
                _cell.append(pinName)
                tempPathDelays.append(_cell)
                _standardCell.addPin(copy.deepcopy(_pin))

                if _pinType == "input":
                    no_nets[counter] += 1
                    _net_report = []
                    _net_report.append(delay)
                    _net_report.append(time)
                    tempNetDelays.append(_net_report)
                    _pinType = "output"
                else:
                    _pinType = "input"

                _net = add_cell_to_path(_standardCell, tempCriticalPath)

                if _pinType == "input":
                    repeatednet = copy.copy(_net)
                    repeatednet = _net.split("net")
                    repeatednet = repeatednet[1]
                    repeatednetid = int(repeatednet)
                    if repeatednetid != wirecopy:
                        tempNetDelays[repeatednetid].append(delay)
                        tempNetDelays[repeatednetid].append(time)

    return no_nets


##########################################################################################


def generate_SVG_from_JSON(path, skinfile):
    os.system(
        "netlistsvg signoff/path_view/"
        + designName
        + "/json/"
        + path
        + ".json -o signoff/path_view/"
        + designName
        + "/schematics/"
        + path
        + ".svg --skin "
        + skinfile
    )
    return


##########################################################################################


def compareConsecutivePaths(index):

    if index < 1:
        return False

    if len(criticalPaths[index]) != len(criticalPaths[index - 1]):
        return False

    for i in range(len(criticalPaths[index])):

        if criticalPaths[index][i].name != criticalPaths[index - 1][i].name:
            return False

        if len(criticalPaths[index][i].pins) != len(criticalPaths[index - 1][i].pins):
            return False

        for j in range(len(criticalPaths[index][i].pins)):
            if (
                criticalPaths[index][i].pins[j].name
                != criticalPaths[index - 1][i].pins[j].name
            ):
                return False

    return True


def addInteraction(path, i, index, hrefs):

    html = (
        """
<!DOCTYPE html>
<html>
<head>
 
<style>
body {
  font-family: "Lato", sans-serif;
  margin: 0;
  background-color: #f5f5f5;
  width: 100%; 
}
header {
  background-image: url('../../../../util/path_view_images/background.jpg');
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  color: #fff;
  padding: 55px;
  text-align: center;
  overflow-x: auto;
}

nav {
  height: 100%;
  overflow-y: auto; 
  width: 130px;
  position: absolute;
  background-color: #eee; 
  padding: 10px 16px;
  color: #000000;
}

nav a {
  display: block;
  padding: 10px 10px;
  text-decoration: none;
  font-size: 18px;
  color: #000000;
}

nav a:hover {
  background-color: #555;
  color: #fff;
}

main {
  margin-left: 160px;
  font-size: 18px;
  padding: 20px;
  background-color: #fff;
  overflow-x: auto;
  height: 100vh; 
}

@media screen and (max-height: 450px) {

  nav a {font-size: 14px;}
}
</style>

</head>
<body>
<header>
  <h1 style="font-size: 55px;">Path View</h1>
  <a href="https://github.com/kanndil/PathView"><img src = "../../../../util/path_view_images/github.svg" alt="github"style="width:42px;height:42px;"/></a>

</header>

"""
        + hrefs
        + """


<main>
   
<h4> Path: """
        + str(i + 1)
        + """</h4>

<h5>"""
        + pathNames[i][0]
        + """</h5>
        
<h5>"""
        + pathNames[i][1]
        + """</h5>

<h5>Slack: """
        + pathNames[i][2]
        + """</h5>
    """
    )
    jsScript = (
        """ 
    
</main>
   
</body>
</html> 


        <script type="text/javascript">
            function reply_click(id)
            {
                const cells = """
        + str(pathCellsDelays[index])
        + """ ;
        
                var cellName = "";
                var logicpath= "";
                var clkpath= "";
                var count=0;
                var data = "";
                var flag = 0;
                var parent = document.getElementById(id);
                var child = parent.querySelector("#flipflop");
                if (child !== null) {
                    flag =1;
                    for (let i = 0; i < cells.length; i++) { 
                        if (("cell_" + cells[i][0]) == id ){
                            cellName = "Cell name: " + cells[i][0]+"\\n\\n";
                            if (cells[i][1] == "input"){
                                data += "\\tPin (" + cells[i][4] + ") arrival time = " + cells[i][3]+"\\n\\n";
                            } else {
                                data += "\\tDelay = " + cells[i][2] + "\\n";
                                data += "\\tPin (" + cells[i][4] +  ") time = " + cells[i][3] + "\\n";
                            }
                            count = count+1;
                        }
                    }
                  } else {
                    for (let i = 0; i < cells.length; i++) { 
                        if (("cell_" + cells[i][0]) == id ){
                            flag = 1
                            cellName = "Cell name: " + cells[i][0]+"\\n";
                            if (count < 2){
                                if (cells[i][1] == "input"){
                                    logicpath += "\\tPin (" + cells[i][4] + ") arrival time = " + cells[i][3]+"\\n\\n";
                                } else {
                                    logicpath += "\\tDelay = " + cells[i][2] + "\\n";
                                    logicpath += "\\tPin (" + cells[i][4] +  ") time = " + cells[i][3] + "\\n";
                                }
                            } else {
                                if (count == 3 ){
                                    logicpath = "\\nLogic Path: \\n" + logicpath ;
                                    clkpath = "\\nClock Path: \\n";
                                }
                                if (cells[i][1] == "input"){
                                    clkpath += "\\tPin (" + cells[i][4] + ") arrival time = " + cells[i][3]+"\\n\\n";
                                } else {
                                    clkpath += "\\tDelay = " + cells[i][2] + "\\n";
                                    clkpath += "\\tPin (" + cells[i][4] +  ") time = " + cells[i][3] + "\\n";
                                }
                                
                            }
                            data = logicpath + clkpath;
                            count = count+1;
                        }
                    }
                  }

                if (flag){
                    alert(cellName + data);
                }
            }
            
            function net_click(id)
            {
                const nets = """
        + str(netDelays[index])
        + """ ;
                var data = "net_" + id;
                var i = parseInt(id);
                if (nets[i].length == 2){
                    data += "\\n\\tdelay = " + nets[i][0];
                    data += "\\n\\ttime = " + nets[i][1] + "\\n";
                } else if (nets[i].length == 4){
                    data+= "\\n\\nLogic Path:"
                    data+= "\\n\\tdelay = " + nets[i][0];
                    data+= "\\n\\ttime = " + nets[i][1];
                    data+= "\\n\\nClock Path:"
                    data+= "\\n\\tdelay = " + nets[i][2];
                    data+= "\\n\\ttime = " + nets[i][3];
                }
                alert(data);
            }
            
        </script>
    """
    )

    netInteractions = generateNetInteractions(path)

    body = ""
    with open("signoff/path_view/" + designName + "/schematics/" + path + ".svg", "r") as f:
        body = f.read()

    body = body.replace("</svg>", " ")
    with open("signoff/path_view/" + designName + "/schematics/" + path + ".svg", "w") as f:
        f.write(html + body + netInteractions + "</svg>" + jsScript)

    os.system(
        "mv signoff/path_view/"
        + designName
        + "/schematics/"
        + path
        + ".svg signoff/path_view/"
        + designName
        + "/schematics/"
        + path
        + ".html"
    )
    return


##########################################################################################


def get_json_blackbox_cells():
    json_blackbox_modules = {}
    for i in range(len(blackboxCells)):
        sub_module = {}
        ports = {}

        sub_module["attributes"] = {
            "blackbox": "00000000000000000000000000000001",
        }

        for pin in blackboxCells[i].pins:
            ports[pin.name] = {"direction": pin.type, "bits": [0]}
        sub_module["ports"] = ports
        json_blackbox_modules[blackboxCells[i].name] = sub_module

    return json_blackbox_modules


def json_from_report(critica_path, path, json_blackbox_modules, index):

    modules = {"modules": {}}
    modules["modules"].update(json_blackbox_modules)

    top_module = {
        "top": {
            "attributes": {"top": "00000000000000000000000000000001"},
            "cells": {},
            "netnames": {},
            "ports": {},
        }
    }

    ports = {
        "clk": {"direction": "input", "bits": [-2]},
        #"out": {"direction": "output", "bits": [-1]},
    }

    top_module["top"]["ports"].update(ports)

    for i in range(len(critica_path)):
        cell = {}
        cell[critica_path[i].id] = {
            "type": critica_path[i].name,
            "attributes": {
                "module_not_derived": "00000000000000000000000000000001",
            },
            "port_directions": {},
            "connections": {},
        }
        for pin in critica_path[i].pins:
            connection_number = copy.copy(pin.net)
            if "clk" in connection_number:
                connection_number = -2
            elif "out" in connection_number:
                connection_number = -1
            else:
                connection_number = int(connection_number.replace("net", ""))

            cell[critica_path[i].id]["connections"][pin.name] = [connection_number]
            cell[critica_path[i].id]["port_directions"][pin.name] = pin.type
        top_module["top"]["cells"].update(cell)

    for i in range(no_nets[index]):
        net = {
            "net"
            + str(i): {
                "bits": [i],
                "hide_name": 0,
            }
        }
        top_module["top"]["netnames"].update(net)

    modules["modules"].update(top_module)

    with open("signoff/path_view/" + designName + "/json/" + path + ".json", "w") as jsonfile:
        json.dump(modules, jsonfile, indent=4)


def generate_href(numberOfPaths):
    hrefs = """ <nav>"""
    for j in range(numberOfPaths):
        hrefs += (
            """<a href="path"""
            + str(j)
            + """.html">Slack: """
            + pathNames[j][2]
            + """</a> \n"""
        )
    hrefs += """ </nav>"""
    return hrefs


def sortPaths(sortType):

    if sortType == "desc":
        pathNames.sort(key=lambda x: float(x[2]), reverse=True)
    elif sortType == "asc":
        pathNames.sort(key=lambda x: float(x[2]))
    elif sortType == "none":
        pass


# Main Class
def main(argv):
    start = time.time()

    staReportFile, skinFile, numberOfPaths, sortType, STAtool = checkArgs(argv)
    global no_nets
    global designName
    no_nets = []
    
    designName = copy.copy(staReportFile)
    designName = designName.split("/")[-1]
    designName = designName.split(".")[0]

    generate_dirs(designName)
    
    
    if STAtool == "opensta":
        no_nets = parseOpenSta(staReportFile, no_nets)
    elif STAtool == "primetime":
        no_nets = parsePrimeTime(staReportFile, no_nets)
    else:
        print(STAtool, " is not a supported STA tool, -h for help")
        print("Invalid STA tool")
        sys.exit()

    if (numberOfPaths < 0) or (numberOfPaths > len(criticalPaths)):
        numberOfPaths = len(criticalPaths)

    json_blackbox_modules = get_json_blackbox_cells()

    sortPaths(sortType)

    hrefs = generate_href(numberOfPaths)
    for i in range(numberOfPaths):
        json_from_report(
            criticalPaths[pathNames[i][3]],
            "path" + str(i),
            json_blackbox_modules,
            pathNames[i][3],
        )
        generate_SVG_from_JSON("path" + str(i), skinFile)
        addInteraction("path" + str(i), i, pathNames[i][3], hrefs)

    end = time.time()
    print("Time taken: ", (end - start) / 60.0)


if __name__ == "__main__":
    main(sys.argv[1:])
