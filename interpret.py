"""
Name: interpret.py
Description: Script which interprets XML input and executes it. Part of IPP project.
Author: Daniel Pohancanik <xpohan03@stud.fit.vutbr.cz>
"""


import xml.etree.ElementTree as ET
import re
import getopt
import sys
import io

#######################################
#DEFINITIONS START
#######################################
EMPTY_ARG = -420
cmdList = []
excInstr = False
excArg = False
argList = []
opcode = ""
order = 0
varValue = ""
jumpTo = -1
dataStack = []
readCounter = 0
instrCounter = 0
globalFrame = []
localFrame = [] 
frameStack = []
tmpFrame = 'uninit'
labelList = []
jumpStack = []

#This method runs through code and fetches order and names of all labels. Saves it into labelList array.
def GetAllLabels(commands):
    global labelList
    for command in commands:
        if(command.GetOpcode() == 'LABEL'):
            order = command.order
            name = command.arglist[0].value
            for item in labelList:
                if item['name'] == name:
                    exit(52) #label defined
            var = {'name': name, 'order': order}
            labelList.append(var)

#Method used for getting order of label by its name. Also checks whether said label exists
def GetLabelOrder(name):
    found = False
    for label in labelList:
        if name == label['name']:
            found = True
            return label['order']
    if found != True:
        exit(52)

#Get.......(name) methods are all used to extract specific information about variables stored in specific frames(LF,GF,TF). Each of them check whether
#frame exists and whether looked for variable exists.
def GetValueFromGFrame(name):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            found = True
            ret = itm
            
    if found != True :
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['value']

def GetVarFromGFrame(name):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            found = True
            ret = itm
            
    if found != True :
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret

def GetTypeFromGFrame(name):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            found = True
            ret = itm
            
    if found != True :
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['type']

def GetTypeFromGFrameForTYPE(name):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            found = True
            ret = itm
            
    if found != True :
        exit(54)

    return ret['type']

def GetValueFromLFrame(name):
    found = False
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['value']

def GetVarFromLFrame(name):
    found = False
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret

def GetTypeFromLFrame(name):
    found = False
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['type']


def GetTypeFromLFrameForTYPE(name):
    found = False
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    return ret['type']

def GetValueFromTFrame(name):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['value']

def GetVarFromTFrame(name):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret

def GetTypeFromTFrame(name):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    if ret['value'] == 'uninit':
        exit(56)
    return ret['type']

def GetTypeFromTFrameForTYPE(name):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            ret = itm
    if found != True:
        exit(54)
    return ret['type']


#Update.......(name, value) methods used to update variable (change its value or type) in specific frames. Checks whether frame or variable exists.
#Cant be used to create new vars.    
def UpdateGFrameValue(name, value):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            itm['value'] = value
            found = True
    if found != True:
        exit(54)

def UpdateGFrameType(name, value):
    global globalFrame
    found = False
    for itm in globalFrame:
        if itm['name'] == name:
            itm['type'] = value
            found = True
    if found != True:
        exit(54)

def UpdateLFrameValue(name, value):
    found = False
    global frameStack
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            itm['value'] = value
            found = True
    if found != True:
        exit(54)


def UpdateLFrameType(name, value):
    found = False
    global frameStack
    if len(frameStack) < 1:
        exit(55) #no LF
    for itm in frameStack[len(frameStack)-1]:
        if itm['name'] == name:
            itm['type'] = value
            found = True
    if found != True:
        exit(54)


def UpdateTFrameValue(name, value):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            itm['value'] = value

    if found != True:
        exit(54)


def UpdateTFrameType(name, value):
    found = False
    if type(tmpFrame) is not list:
        exit(55) #uninit TF
    for itm in tmpFrame:
        if itm['name'] == name:
            found = True
            itm['type'] = value

    if found != True:
        exit(54)


orderList = []

#Class that hold information about specific commands (instructions).
class Command:
    def __init__(self, opcode, order, arg):
        global orderList
        orderList.append(order)
        opcode.upper()
        self.opcode = opcode
        try:
            order = int(order)
        except:
            exit(32)
        self.order = order
        self.arglist = arg
        self.argDicList = []

        #Check for wrong argument numbers.
        for item in arg:
            if len(arg) == 0:
                pass
            if len(arg) == 1 and item.order not in ['1']:
                exit(32)
            if len(arg) == 2 and item.order not in ['1','2']:
                exit(32)
            if len(arg) == 3 and item.order not in ['1','2','3']:
                exit(32)

        

        #Checks whether every instruction has its required number of arguments.
        if opcode in ['PUSHFRAME', 'CREATEFRAME', 'POPFRAME', 'RETURN', 'BREAK'] and len(arg) != 0:
            exit(32)

        if opcode in ['DEFVAR', 'CALL', 'PUSHS', 'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DPRINT'] and len(arg) != 1:
            exit(32)

        if opcode in ['MOVE', 'INT2CHAR', 'READ', 'NOT', 'STRLEN', 'TYPE'] and len(arg) != 2:
            exit(32)

        if opcode in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR', 'JUMPIFEQ', 'JUMPIFNEQ'] and len(arg) != 3:
            exit(32)

    #Getters for command class. Used to extract information about instruction. Safer to use than direct access
    def GetArgCount(self):
        return len(self.arglist)
    
    def GetOpcode(self):
        return self.opcode

    def GetOrder(self):
        try:
            return int(self.order)
        except:
            exit(32)

#Class of argument. Hold specific information about passed argument.
class Argument:
    def __init__(self, varType, value, order):
        self.varType = varType
        self.value = value
        self.order = order
        
        #This block is used to determine if all arguments have valid types.
        if varType == 'int':
            try:
                value = int(value)
            except:
                exit(32)
        elif varType == 'bool' and (value != 'true' and value != 'false'):
            exit(53)
        
        elif varType == 'nil' and value != 'nil':
            exit(53)
        
        elif varType == 'var':
            tmp = value.split('@')
            if len(tmp) < 2:
                exit(53)
            else:
                if tmp[0] != "GF" and tmp[0] != "LF" and tmp[0] != "TF":
                    exit(53) 

        if varType not in ['var', 'int', 'string', 'nil', 'bool', 'label', 'type']:
            exit(32)

#######################################
#DEFINITIONS END
#######################################

#Argument processing
source = EMPTY_ARG
progInput = EMPTY_ARG
options, args = getopt.getopt(
            sys.argv[1:], "h:p:l",
            ["input=", "source=", "help"])

for opt, arg in options:
    if opt in ('--source'):
        source = arg
    if opt in ('--input'):
        progInput = arg
    if opt in ('--help'):
        if len(options) > 1:
            exit(10)
        else:
            print("""Program načte XML reprezentaci programu a tento program s využitím vstupu dle parametrů příka-zové řádky interpretuje a generuje výstup. 
Vstupní XML reprezentace je 
např. generována skriptemparse.php(ale ne nutně) ze zdrojového kódu v IPPcode20.""")
            exit(0)

   

if source == EMPTY_ARG and progInput == EMPTY_ARG:
    exit(10)

if source == EMPTY_ARG:
    source = sys.stdin

if progInput == EMPTY_ARG:
    progInput = sys.stdin.read().splitlines()
else:
    try:
        progInput = open(progInput, "r").read().splitlines()
    except:
        exit(11)

inputArr = []
for line in progInput:
    inputArr.append(line)

#Parsing of XML file. Its parsed into array of.
try:
    tree = ET.parse(source)
except:
    exit(31)
root = tree.getroot()
if(root.attrib['language'] != 'IPPcode20' or len(root.attrib) > 3 ):
    exit(32)
commands = []
argCheck = []
for child in root.iter():
    if child.tag not in ['program', 'instruction', 'arg1', 'arg2', 'arg3']:
        exit(32)
    for line in child.attrib.keys():
        
        if child.tag == "program":
                for itm in child.attrib.keys():
                    if itm  not in ['name', 'language','description']:
                        exit(32) 
        elif line not in ['order', 'opcode', 'type']:
            exit(32)
    
    commands.append(child.tag)
    commands.append(child.attrib)
    if re.match(r'^\s*$', str(child.text)):
        pass
    else:
        commands.append(child.text)

#Further processing of XML. List of command objects is constructed here.
for line in commands:
    #print(line)
    if type(line) is dict:
        try:

            opcode = line["opcode"]
            order = line["order"]
            continue
        except:
            try:
                varType = line["type"]
                #argList.append(line)
                excArg = True
                continue
            except:
                continue
    if line == "program":
        continue
    elif line == "instruction":
        cmdList.append(Command(opcode,order,argList))
        opcode = ""
        order = 0
        argList = []
        varType = ""
        varValue = ""
        excInstr = True
        continue

    elif line == "arg1" or line == "arg2" or line == "arg3":
        argOrder = re.findall('\d+', line )[0]
    
    
    else:
        if excArg:
            #argList.append(line)
            varValue = line
            argList.append(Argument(varType, varValue, argOrder))
            excArg = False

    
    
   
#workaround to get last argument to the list
cmdList.append(Command(opcode,order,argList))        

#sort list of commands by their order


#Sorting of instructions by their order.
sortedCmdList = sorted(cmdList, key=lambda x: int(x.order))
GetAllLabels(sortedCmdList)
for command in sortedCmdList:
    command.arglist.sort(key=lambda x: int(x.order))

sortedCmdList.pop(0)



if len(orderList) != len(set(orderList)):
    exit(32)


restart = True
#While loop used for restarting iteration over instructions in case of jumps.
while restart:
    restart = False

    #Main loop which iterates over instructions.
    for command in sortedCmdList:
        instrCounter = instrCounter + 1
        if command.GetOrder() < 1:
            exit(32)
    
        #Loop which modifies string types in so python can naturally print them.
        for item in command.arglist:
            if item.varType == 'string':
                if item.value == "" or type(item.value) is not str:
                    item.value = ""
                else:
                    while re.search(r'\\[0-9][0-9][0-9]', item.value):
                        fixed = re.sub(r'\\[0-9][0-9][0-9]', chr(int(re.search(r'\\[0-9][0-9][0-9]', item.value).group(0).split('\\')[1])), item.value, count=1)
                        item.value = fixed
                    if re.search(r'#', item.value):
                        exit(32)

        #This is used to iterate of over instructions until instruction with correct order is reached. Triggered by jump instructions.
        if jumpTo == -1:
           pass
        else:
            if command.GetOrder() == jumpTo:
                jumpTo = -1
                #continue
            else:
                continue

        #BEGINNING OF DEFINITION OF BEHAVIOUR FOR SPECIFIC INSTRUCTIONS.
        #Arguments are firstly extracted from each command. Then they are checked for their type and their types and values are pulled from frames if needed.
        #After arguments are processed, corresponding action based on instruction is carried out. Result, if any, is then stored into destination variable (if aplicable)
        #using Update...() methods defined earlier. This applies for all instructions.
        if command.GetOpcode() == 'DEFVAR':
            value = command.arglist[0].value.split('@')
            if value[0] == "GF":
                for var in globalFrame:
                    if value[1] == var['name']:
                        exit(52)
                var = {'name': value[1], 'value': 'uninit', 'type': 'unknown'}
                globalFrame.append(var)
            if value[0] == "LF":
                if len(frameStack) < 1:
                    exit(55) #check ERRCODE. Ziadny local frame neexistuje
                else:
                    for var in frameStack[len(frameStack)-1]:
                        if value[1] == var['name']:
                            exit(52)
                    var = {'name': value[1], 'value': 'uninit', 'type': 'unknown'}
                    frameStack[len(frameStack)-1].append(var)
            if value[0] == "TF":
                if tmpFrame == 'uninit':
                    exit(55) #no tmp frame
                else:
                    for var in tmpFrame:
                        if value[1] == var['name']:
                            exit(52)
                    var = {'name': value[1], 'value': 'uninit', 'type': 'unknown'}
                    tmpFrame.append(var)
                
            else:
                #TODO Implement other frames
                pass

        elif command.GetOpcode() == 'MOVE':
            dst = command.arglist[0].value.split('@')
            src = command.arglist[1]
            dstType = command.arglist[0].varType
            
            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    if dst[0] == "GF":
                        UpdateGFrameValue(dst[1], GetValueFromGFrame(src.value.split('@')[1]))
                        UpdateGFrameType(dst[1], GetTypeFromGFrame(src.value.split('@')[1]))

                    if dst[0] == "LF":
                        UpdateLFrameValue(dst[1], GetValueFromGFrame(src.value.split('@')[1]))
                        UpdateLFrameType(dst[1], GetTypeFromGFrame(src.value.split('@')[1]))

                    if dst[0] == "TF":
                        UpdateTFrameValue(dst[1], GetValueFromGFrame(src.value.split('@')[1]))
                        UpdateTFrameType(dst[1], GetTypeFromGFrame(src.value.split('@')[1]))

                if src.value.split('@')[0] == "LF":
                    if dst[0] == "GF":
                        UpdateGFrameValue(dst[1], GetValueFromLFrame(src.value.split('@')[1]))
                        UpdateGFrameType(dst[1], GetTypeFromLFrame(src.value.split('@')[1]))

                    if dst[0] == "LF":
                        UpdateLFrameValue(dst[1], GetValueFromLFrame(src.value.split('@')[1]))
                        UpdateLFrameType(dst[1], GetTypeFromLFrame(src.value.split('@')[1]))

                    if dst[0] == "TF":
                        UpdateTFrameValue(dst[1], GetValueFromTFrame(src.value.split('@')[1]))
                        UpdateTFrameType(dst[1], GetTypeFromTFrame(src.value.split('@')[1]))

                if src.value.split('@')[0] == "TF":
                    if dst[0] == "GF":
                        UpdateGFrameValue(dst[1], GetValueFromTFrame(src.value.split('@')[1]))
                        UpdateGFrameType(dst[1], GetTypeFromTFrame(src.value.split('@')[1]))

                    if dst[0] == "LF":
                        UpdateLFrameValue(dst[1], GetValueFromTFrame(src.value.split('@')[1]))
                        UpdateLFrameType(dst[1], GetTypeFromTFrame(src.value.split('@')[1]))

                    if dst[0] == "TF":
                        UpdateTFrameValue(dst[1], GetValueFromTFrame(src.value.split('@')[1]))
                        UpdateTFrameType(dst[1], GetTypeFromTFrame(src.value.split('@')[1]))

            else:
                if dst[0] == "GF":
                        UpdateGFrameValue(dst[1], src.value)
                        UpdateGFrameType(dst[1], src.varType)

                if dst[0] == "LF":
                    UpdateLFrameValue(dst[1], src.value)
                    UpdateLFrameType(dst[1], src.varType)

                if dst[0] == "TF":
                    UpdateTFrameValue(dst[1], src.value)
                    UpdateTFrameType(dst[1], src.varType)
                


            

        elif command.GetOpcode() == 'WRITE':
            value = command.arglist[0].value
            vType = command.arglist[0].varType
            if vType == 'var':
                if command.arglist[0].value.split('@')[0] == "GF":
                   
                    if GetTypeFromGFrame(command.arglist[0].value.split('@')[1]) == "nil":
                        print('', end='')
                    else:
                        print(GetValueFromGFrame(command.arglist[0].value.split('@')[1]), end='')

                if command.arglist[0].value.split('@')[0] == "LF":
                    if GetTypeFromLFrame(command.arglist[0].value.split('@')[1]) == "nil":
                        print('', end='')
                    else:
                        print(GetValueFromLFrame(command.arglist[0].value.split('@')[1]), end='')

                if command.arglist[0].value.split('@')[0] == "TF":
                    
                    if tmpFrame == 'uninit':
                        exit(55) 
                    if(GetTypeFromTFrame(command.arglist[0].value.split('@')[1]) == "nil"):
                        print('', end='')
                    else:
                        print(GetValueFromTFrame(command.arglist[0].value.split('@')[1]), end='')
            else:
                if command.arglist[0].varType == 'nil':
                    print('', end='')
                else:
                    print(command.arglist[0].value, end='')
        elif command.GetOpcode() == 'LABEL':
            pass
        elif command.GetOpcode() == 'JUMP':
            label = command.arglist[0].value
            labelOrder = GetLabelOrder(label)
            jumpTo = int(labelOrder)
            restart = True
            break

        elif command.GetOpcode() == 'JUMPIFEQ':
            label = command.arglist[0].value
            labelOrder = GetLabelOrder(label)
            helperList = []
            for arg in command.arglist:
                if(arg.varType == 'label'):
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            #print(arg1['value'], arg2['value'])
            if (arg1['type'] != arg2['type']):
                if arg1['type'] == 'nil' or arg2['type'] == 'nil':
                    pass
                else:
                    exit(53)

            arg1['value'] = str(arg1['value'])   
            arg2['value'] = str(arg2['value'])  
            if (arg1['value']) == (arg2['value']):
                jumpTo = int(labelOrder)
                restart = True
                break
            else:
                continue

        elif command.GetOpcode() == 'JUMPIFNEQ':
            label = command.arglist[0].value
            labelOrder = GetLabelOrder(label)
            helperList = []
            for arg in command.arglist:
                if(arg.varType == 'label'):
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            
            if (arg1['type'] != arg2['type']):
                if arg1['type'] == 'nil' or arg2['type'] == 'nil':
                    pass
                else:
                    exit(53)
                
            if arg1['value'] != arg2['value']:
                jumpTo = int(labelOrder)
                restart = True
                break
            else:
                continue

        elif command.GetOpcode() == 'ADD':
            dest = command.arglist[0]
            skipFirst = True
            helperList = []
            for arg in command.arglist:
                if skipFirst:
                    skipFirst = False
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        if tmpFrame == 'uninit':
                            exit(55) 
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            arg1['value'] = str(arg1['value'])   
            arg2['value'] = str(arg2['value'])  
            if (arg1['type'] == 'int') and (arg2['type'] == 'int'):
                UpdateGFrameValue(dest.value.split('@')[1], (int(arg1['value']) + int(arg2['value'])))
                UpdateGFrameType(dest.value.split('@')[1], 'int')
            else:
                exit(53)
        
        elif command.GetOpcode() == 'SUB':
            dest = command.arglist[0]
            skipFirst = True
            helperList = []
            for arg in command.arglist:
                if skipFirst:
                    skipFirst = False
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        if tmpFrame == 'uninit':
                            exit(55) 
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            if arg1['type'] == 'int' and arg2['type'] == 'int':
                UpdateGFrameValue(dest.value.split('@')[1], (int(arg1['value']) - int(arg2['value'])))
                UpdateGFrameType(dest.value.split('@')[1], 'int')
            else:
                exit(53)
        elif command.GetOpcode() == 'MUL':
            dest = command.arglist[0]
            skipFirst = True
            helperList = []
            for arg in command.arglist:
                if skipFirst:
                    skipFirst = False
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        if tmpFrame == 'uninit':
                            exit(55) 
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            if arg1['type'] == 'int' and arg2['type'] == 'int':
                UpdateGFrameValue(dest.value.split('@')[1], (int(arg1['value']) * int(arg2['value'])))
                UpdateGFrameType(dest.value.split('@')[1], 'int')
            else:
                exit(53)

        elif command.GetOpcode() == 'IDIV':
            dest = command.arglist[0]
            skipFirst = True
            helperList = []
            for arg in command.arglist:
                if skipFirst:
                    skipFirst = False
                    continue

                if(arg.varType == 'var'):
                    if arg.value.split('@')[0] == "GF":
                        args = {'value':GetValueFromGFrame(arg.value.split('@')[1]), 'type': GetTypeFromGFrame(arg.value.split('@')[1])}
                        helperList.append(args)

                    elif arg.value.split('@')[0] == "LF":
                        args = {'value':GetValueFromLFrame(arg.value.split('@')[1]), 'type': GetTypeFromLFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                    elif arg.value.split('@')[0] == "TF":
                        if tmpFrame == 'uninit':
                            exit(55) 
                        args = {'value':GetValueFromTFrame(arg.value.split('@')[1]), 'type': GetTypeFromTFrame(arg.value.split('@')[1])}
                        helperList.append(args)
                else:
                    args = {'value': arg.value, 'type': arg.varType}
                    helperList.append(args)

            arg1 = helperList[0]
            arg2 = helperList[1]
            if arg1['type'] == 'int' and arg2['type'] == 'int':
                try:
                    UpdateGFrameValue(dest.value.split('@')[1], int((int(arg1['value']) // int(arg2['value']))))
                except ZeroDivisionError:
                    exit(57)
                UpdateGFrameType(dest.value.split('@')[1], 'int')
            else:
                exit(53)
        
        elif command.GetOpcode() == 'CREATEFRAME':
            tmpFrame = []

        elif command.GetOpcode() == 'PUSHFRAME':
            if tmpFrame == 'uninit':
                exit(55) #Neexistujuci TF
            else:
                frameStack.append(tmpFrame)
                tmpFrame = 'uninit'
        
        elif command.GetOpcode() == 'POPFRAME':
            if len(frameStack) < 1:
                exit(55) #vrchny ramec nie je LF
            else:
                tmpFrame = frameStack.pop()
        
        elif command.GetOpcode() == 'CALL':
            jumpStack.append(command.GetOrder())
            label = command.arglist[0].value
            labelOrder = GetLabelOrder(label)
            jumpTo = int(labelOrder)
            restart = True
            break
        
        elif command.GetOpcode() == 'RETURN':
            if len(jumpStack) == 0:
                exit (56) #nowhere to jump
            whereTo = jumpStack.pop()
            labelOrder = GetLabelOrder(label)
            jumpTo = int(whereTo+1)
            restart = True
            break

        elif command.GetOpcode() == 'PUSHS':
            src = command.arglist[0]
            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    dataStack.append(GetVarFromGFrame(src.value.split('@')[1]))

                if src.value.split('@')[0] == "LF":
                    dataStack.append(GetVarFromLFrame(src.value.split('@')[1]))

                if src.value.split('@')[0] == "TF":
                    if tmpFrame == 'uninit':
                            exit(55) 
                    dataStack.append(GetVarFromTFrame(src.value.split('@')[1]))
            else:
                var = {'value': src.value, 'type': src.varType}
                dataStack.append(var)

        
        elif command.GetOpcode() == 'POPS':
            if len(dataStack) < 1:
                exit(56)
            dst = command.arglist[0]
            if dst.value.split('@')[0] == "GF":
                popped = dataStack.pop()
                UpdateGFrameValue(dst.value.split('@')[1], popped['value'])
                UpdateGFrameType(dst.value.split('@')[1], popped['type'])

            if dst.value.split('@')[0] == "LF":
                popped = dataStack.pop()
                UpdateLFrameValue(dst.value.split('@')[1], popped['value'])
                UpdateLFrameType(dst.value.split('@')[1], popped['type'])
            
            if dst.value.split('@')[0] == "TF":
                if tmpFrame == 'uninit':
                    exit(55) 
                popped = dataStack.pop()
                UpdateTFrameValue(dst.value.split('@')[1], popped['value'])
                UpdateTFrameType(dst.value.split('@')[1], popped['type'])

        elif command.GetOpcode() == 'INT2CHAR':
            dst = command.arglist[0]
            src = command.arglist[1]

            
            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    if GetTypeFromGFrame(src.value.split('@')[1]) != 'int':
                        exit(53)
                    try:
                        ret = chr(int(GetValueFromGFrame(src.value.split('@')[1])))
                    except:
                        exit(58) #Wrong type for chr

                if src.value.split('@')[0] == "LF":
                    if GetTypeFromLFrame(src.value.split('@')[1]) != 'int':
                        exit(53)
                    
                    try:
                        ret = chr(int(GetValueFromLFrame(src.value.split('@')[1])))
                    except:
                        exit(58) #Wrong type for chr

                if src.value.split('@')[0] == "TF":
                    if GetTypeFromTFrame(src.value.split('@')[1]) != 'int':
                        exit(53)
                    try:
                        ret = chr(int(GetValueFromTFrame(src.value.split('@')[1])))
                    except:
                        exit(58) #Wrong type for chr

            else:
                if src.varType != 'int':
                    exit(53)
                try:
                    ret = chr(int(src.value))
                except:
                    exit(58)
            
            if dst.value.split('@')[0] == "GF":
                UpdateGFrameValue(dst.value.split('@')[1], ret)
                UpdateGFrameType(dst.value.split('@')[1], 'string')

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameValue(dst.value.split('@')[1], ret)
                UpdateLFrameType(dst.value.split('@')[1], 'string')

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameValue(dst.value.split('@')[1], ret)
                UpdateTFrameType(dst.value.split('@')[1], 'string')

        elif command.GetOpcode() == 'STRI2INT':
            dst = command.arglist[0]
            src = command.arglist[1]
            pos = command.arglist[2]

            

            if pos.varType == 'var':
                if pos.value.split('@')[0] == "GF":
                    if GetTypeFromGFrame(pos.value.split('@')[1]) != 'int':
                        exit(53)
                    position = GetValueFromGFrame(pos.value.split('@')[1])
                
                if pos.value.split('@')[0] == "LF":
                    if GetTypeFromLFrame(pos.value.split('@')[1]) != 'int':
                        exit(53)
                    position = GetValueFromLFrame(pos.value.split('@')[1])

                if pos.value.split('@')[0] == "TF":
                    if GetTypeFromTFrame(pos.value.split('@')[1]) != 'int':
                        exit(53)
                    position = GetValueFromTFrame(pos.value.split('@')[1])
            
            else:
                if pos.varType != 'int':
                    exit(53)
                position = pos.value

            try:
                position = int(position)
            except:
                exit(53)

            if position < 0:
                    exit(58)
            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    if GetTypeFromGFrame(src.value.split('@')[1]) != 'string':
                        exit(53)
                    try:
                        ret = ord(GetValueFromGFrame(src.value.split('@')[1])[position])
                    except IndexError:
                        exit(58) #Wrong type for ord
                    except:
                        exit(53)

                if src.value.split('@')[0] == "LF":
                    if GetTypeFromLFrame(src.value.split('@')[1]) != 'string':
                        exit(53)
                    try:
                        ret = ord(GetValueFromLFrame(src.value.split('@')[1])[position])
                    except IndexError:
                        exit(58) #Wrong type for ord
                    except:
                        exit(53)

                

                if src.value.split('@')[0] == "TF":
                    if GetTypeFromTFrame(src.value.split('@')[1]) != 'string':
                        exit(53)
                    try:
                        ret = ord(GetValueFromTFrame(src.value.split('@')[1])[position])
                    except IndexError:
                        exit(58) #Wrong type for ord
                    

            else:
                if src.varType != 'string':
                    exit(53)
                try:
                    ret = ord(src.value[position])
                except IndexError:
                    exit(58)
            
            if dst.value.split('@')[0] == "GF":
                UpdateGFrameValue(dst.value.split('@')[1], ret)
                UpdateGFrameType(dst.value.split('@')[1], 'int')

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameValue(dst.value.split('@')[1], ret)
                UpdateLFrameType(dst.value.split('@')[1], 'int')

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameValue(dst.value.split('@')[1], ret)
                UpdateTFrameType(dst.value.split('@')[1], 'int')
        
        elif command.GetOpcode() == 'EXIT':
            src = command.arglist[0]
            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    value = GetValueFromGFrame(src.value.split('@')[1])
                    valueType = GetTypeFromGFrame(src.value.split('@')[1])

                if src.value.split('@')[0] == "TF":
                    value = GetValueFromTFrame(src.value.split('@')[1])
                    valueType = GetTypeFromTFrame(src.value.split('@')[1])

                if src.value.split('@')[0] == "LF":
                    value = GetValueFromLFrame(src.value.split('@')[1])
                    valueType = GetTypeFromLFrame(src.value.split('@')[1])
                
                
                if valueType != 'int':
                    exit(53)

                try:
                    value = int(value)
                except:
                    exit(57)

                if value < 0 or value > 49:
                    exit(57)
                
                
                exit(value)

            else:
                #src.value = int(src.value)
                if src.varType != 'int':
                    exit(53)

                try:
                    src.value = int(src.value)
                except:
                    exit(57)

                if src.value < 0 or src.value > 49:
                    exit(57)
                
                
                exit(src.value)

        elif command.GetOpcode() == 'TYPE':
            dst = command.arglist[0]
            src = command.arglist[1]

            if src.varType == 'var':
                if src.value.split('@')[0] == "GF":
                    varType = GetTypeFromGFrameForTYPE(src.value.split('@')[1])
                    if varType == 'unknown':
                        varType = ''

                if src.value.split('@')[0] == "LF":
                    varType = GetTypeFromLFrameForTYPE(src.value.split('@')[1])
                    if varType == 'unknown':
                        varType = ''

                if src.value.split('@')[0] == "TF":
                    varType = GetTypeFromTFrameForTYPE(src.value.split('@')[1])
                    if varType == 'unknown':
                        varType = ''

            else:
                varType = src.varType

            if varType == 'unknown':
                varType = ''
            
            if dst.value.split('@')[0] == "GF":
                UpdateGFrameValue(dst.value.split('@')[1], varType)
                UpdateGFrameType(dst.value.split('@')[1], 'string')

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameValue(dst.value.split('@')[1], varType)
                UpdateLFrameType(dst.value.split('@')[1], 'string')

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameValue(dst.value.split('@')[1], varType)
                UpdateTFrameType(dst.value.split('@')[1], 'string')

        elif command.GetOpcode() == 'READ':
            
            
            dst = command.arglist[0]
            src = command.arglist[1]
            readType = src.value
            
            if src.varType != 'type':
                exit(53)
            
            if progInput == EMPTY_ARG:
                readInput = input()
            else:
                if readCounter < len(inputArr):
                    readInput = inputArr[readCounter]
                    readCounter = readCounter + 1
                else:
                    readInput = ""
            if src.value == 'bool':
                if re.search('true', readInput, re.IGNORECASE):
                    readInput = 'true'
                else:
                    readInput = 'false'
            elif src.value == 'int':
                try:
                    readInput = int(readInput)
                except:
                    readInput = ""
            elif src.value == 'nil':
                exit(32)
            elif src.value == 'string':
                readInput = str(readInput)
            
            if readInput is None or readInput == "":
                readInput = 'nil'
                readType = 'nil'

            
            
            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], readType)
                UpdateGFrameValue(dst.value.split('@')[1], readInput)

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], readType)
                UpdateLFrameValue(dst.value.split('@')[1], readInput)

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], readType)
                UpdateTFrameValue(dst.value.split('@')[1], readInput)


        elif command.GetOpcode() in ['LT', 'GT', 'EQ', 'AND', 'OR', 'NOT']:
            dst = command.arglist[0]
            arg1 = command.arglist[1]
            if command.GetOpcode() == 'NOT': 
                arg2 = arg1
            else:
                arg2 = command.arglist[2]
            

            if arg1.varType == 'var':
                if arg1.value.split('@')[0] == "GF":
                    arg1Type = GetTypeFromGFrame(arg1.value.split('@')[1])
                    arg1Value = GetValueFromGFrame(arg1.value.split('@')[1])

                elif arg1.value.split('@')[0] == "LF":
                    arg1Type = GetTypeFromLFrame(arg1.value.split('@')[1])
                    arg1Value = GetValueFromLFrame(arg1.value.split('@')[1])

                elif arg1.value.split('@')[0] == "TF":
                    arg1Type = GetTypeFromTFrame(arg1.value.split('@')[1])
                    arg1Value = GetValueFromTFrame(arg1.value.split('@')[1])
            else:
                arg1Type = arg1.varType
                arg1Value = arg1.value

            if arg2.varType == 'var':
                if arg2.value.split('@')[0] == "GF":
                    arg2Type = GetTypeFromGFrame(arg2.value.split('@')[1])
                    arg2Value = GetValueFromGFrame(arg2.value.split('@')[1])

                elif arg2.value.split('@')[0] == "LF":
                    arg2Type = GetTypeFromLFrame(arg2.value.split('@')[1])
                    arg2Value = GetValueFromLFrame(arg2.value.split('@')[1])

                elif arg2.value.split('@')[0] == "TF":
                    arg2Type = GetTypeFromTFrame(arg2.value.split('@')[1])
                    arg2Value = GetValueFromTFrame(arg2.value.split('@')[1])
            else:
                arg2Type = arg2.varType
                arg2Value = arg2.value

            if command.GetOpcode() != "EQ" and (arg1Type == 'nil' or arg2Type == 'nil'):
                exit(53)

            elif arg1Type != arg2Type:
                if command.GetOpcode() == "EQ":
                    if arg1Type == 'nil' or arg2Type == 'nil':
                        pass
                    else:
                        exit(53)
                        pass
                else:
                    exit(53)
            
            if arg1Type == 'int' and command.GetOpcode() != "EQ":
                try:
                    arg1Value = int(arg1Value)
                    arg2Value = int(arg2Value)
                except:
                    exit()
            
            if arg1Type == 'string':
                try:
                    arg1Value = str(arg1Value)
                    arg2Value = str(arg2Value)
                except:
                    exit(53)

            if arg1Type == 'bool' and (arg1Value not in ['true','false'] and arg2Value not in ['true','false']):
                exit(53)

            if ((arg1Type == 'bool' or arg2Type == 'bool') and (command.GetOpcode() != "EQ")):
                arg1Value = arg1Value == 'true'
                if command.GetOpcode() != 'NOT':
                    arg2Value = arg2Value == 'true'
            
            if command.GetOpcode() == 'LT':
                ret = arg1Value < arg2Value

            if command.GetOpcode() == 'GT':
                ret = arg1Value > arg2Value

            if command.GetOpcode() == 'EQ':
                ret = arg1Value == arg2Value
            
            if command.GetOpcode() in ['AND', 'OR']:
                if arg1Type != arg2Type and arg1Type != 'bool':
                    exit(53)
                if command.GetOpcode() == 'AND':
                    ret = (arg1Value and arg2Value)
                
                if command.GetOpcode() == 'OR':
                    ret = arg1Value or arg2Value

            if command.GetOpcode() == 'NOT':
                if arg1Type != 'bool':
                    exit(53)
                ret = not arg1Value
            

            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], 'bool')
                UpdateGFrameValue(dst.value.split('@')[1], str(ret).lower())
            elif dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], 'bool')
                UpdateLFrameValue(dst.value.split('@')[1], str(ret).lower())

            elif dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], 'bool')
                UpdateTFrameValue(dst.value.split('@')[1], str(ret).lower())
            
        
        elif command.GetOpcode() == 'STRLEN':
            dst = command.arglist[0]
            src = command.arglist[1]

            if src.varType == "var":
                if src.value.split('@')[0] == "GF":
                    srcType = GetTypeFromGFrame(src.value.split('@')[1])
                    srcValue = GetValueFromGFrame(src.value.split('@')[1])
                
                if src.value.split('@')[0] == "LF":
                    srcType = GetTypeFromLFrame(src.value.split('@')[1])
                    srcValue = GetValueFromLFrame(src.value.split('@')[1])

                if src.value.split('@')[0] == "TF":
                    srcType = GetTypeFromTFrame(src.value.split('@')[1])
                    srcValue = GetValueFromTFrame(src.value.split('@')[1])

            else:
                srcType = src.varType
                srcValue = src.value

            if srcType != "string":
                exit(53)
            
            try:
               srcValue = str(srcValue)
            except:
                exit(53)

            ret = len(srcValue)

            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], 'int')
                UpdateGFrameValue(dst.value.split('@')[1], ret)
            
            if dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], 'int')
                UpdateLFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], 'int')
                UpdateTFrameValue(dst.value.split('@')[1], ret)


        elif command.GetOpcode() == 'CONCAT':
            dst = command.arglist[0]
            arg1 = command.arglist[1]
            arg2 = command.arglist[2]

            if arg1.varType == 'var':
                if arg1.value.split('@')[0] == "GF":
                    arg1Value = GetValueFromGFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromGFrame(arg1.value.split('@')[1])

                if arg1.value.split('@')[0] == "LF":
                    arg1Value = GetValueFromLFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromLFrame(arg1.value.split('@')[1])


                if arg1.value.split('@')[0] == "TF":
                    arg1Value = GetValueFromTFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromTFrame(arg1.value.split('@')[1])

            else:
                arg1Value = arg1.value
                arg1Type = arg1.varType

            if arg2.varType == 'var':
                if arg2.value.split('@')[0] == "GF":
                    arg2Value = GetValueFromGFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromGFrame(arg2.value.split('@')[1])

                if arg2.value.split('@')[0] == "LF":
                    arg2Value = GetValueFromLFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromLFrame(arg2.value.split('@')[1])


                if arg2.value.split('@')[0] == "TF":
                    arg2Value = GetValueFromTFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromTFrame(arg2.value.split('@')[1])
            
            else:
                arg2Value = arg2.value
                arg2Type = arg2.varType

            
            if arg1Type != arg2Type:
                exit(53)

            if arg1Type != "string":
                exit(53)

            try:
                arg1Value = str(arg1Value)
                arg2Value = str(arg2Value)
            except:
                exit(53)

            ret = arg1Value + arg2Value

            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], 'string')
                UpdateGFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], 'string')
                UpdateLFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], 'string')
                UpdateTFrameValue(dst.value.split('@')[1], ret)

        elif command.GetOpcode() == 'GETCHAR':
            dst = command.arglist[0]
            arg1 = command.arglist[1]
            arg2 = command.arglist[2]

            if arg1.varType == 'var':
                if arg1.value.split('@')[0] == "GF":
                    arg1Value = GetValueFromGFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromGFrame(arg1.value.split('@')[1])

                if arg1.value.split('@')[0] == "LF":
                    arg1Value = GetValueFromLFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromLFrame(arg1.value.split('@')[1])


                if arg1.value.split('@')[0] == "TF":
                    arg1Value = GetValueFromTFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromTFrame(arg1.value.split('@')[1])

            else:
                arg1Value = arg1.value
                arg1Type = arg1.varType
            
            if arg2.varType == 'var':
                if arg2.value.split('@')[0] == "GF":
                    arg2Value = GetValueFromGFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromGFrame(arg2.value.split('@')[1])

                if arg2.value.split('@')[0] == "LF":
                    arg2Value = GetValueFromLFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromLFrame(arg2.value.split('@')[1])


                if arg2.value.split('@')[0] == "TF":
                    arg2Value = GetValueFromTFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromTFrame(arg2.value.split('@')[1])
            
            else:
                arg2Value = arg2.value
                arg2Type = arg2.varType
            
            if arg1Type != "string" or arg2Type != "int":
                exit(53)
            
            try:
                arg1Value = str(arg1Value)
                arg2Value = int(arg2Value)
            except:
                exit(53)

            if arg2Value < 0:
                exit(58)

            try:
                ret = arg1Value[arg2Value]
            except IndexError:
                exit(58)

            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], 'string')
                UpdateGFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], 'string')
                UpdateLFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], 'string')
                UpdateTFrameValue(dst.value.split('@')[1], ret)

            
            
        elif command.GetOpcode() == 'SETCHAR':
            dst = command.arglist[0]
            arg1 = command.arglist[1]
            arg2 = command.arglist[2]

            if arg1.varType == 'var':
                if arg1.value.split('@')[0] == "GF":
                    arg1Value = GetValueFromGFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromGFrame(arg1.value.split('@')[1])

                if arg1.value.split('@')[0] == "LF":
                    arg1Value = GetValueFromLFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromLFrame(arg1.value.split('@')[1])


                if arg1.value.split('@')[0] == "TF":
                    arg1Value = GetValueFromTFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromTFrame(arg1.value.split('@')[1])

            else:
                arg1Value = arg1.value
                arg1Type = arg1.varType
            
            if arg2.varType == 'var':
                if arg2.value.split('@')[0] == "GF":
                    arg2Value = GetValueFromGFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromGFrame(arg2.value.split('@')[1])

                if arg2.value.split('@')[0] == "LF":
                    arg2Value = GetValueFromLFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromLFrame(arg2.value.split('@')[1])


                if arg2.value.split('@')[0] == "TF":
                    arg2Value = GetValueFromTFrame(arg2.value.split('@')[1])
                    arg2Type = GetTypeFromTFrame(arg2.value.split('@')[1])
            
            else:
                arg2Value = arg2.value
                arg2Type = arg2.varType

            if dst.varType == 'var':
                if dst.value.split('@')[0] == "GF":
                    dstValue = GetValueFromGFrame(dst.value.split('@')[1])
                    dstType = GetTypeFromGFrame(dst.value.split('@')[1])

                if dst.value.split('@')[0] == "LF":
                    dstValue = GetValueFromLFrame(dst.value.split('@')[1])
                    dstType = GetTypeFromLFrame(dst.value.split('@')[1])


                if dst.value.split('@')[0] == "TF":
                    dstValue = GetValueFromTFrame(dst.value.split('@')[1])
                    dstType = GetTypeFromTFrame(dst.value.split('@')[1])
            
            else:
                dstValue = dst.value
                dstType = dst.varType

            if dstType != "string" or arg1Type != "int" or arg2Type != "string":
                exit(53)

            if arg2Value == "":
                exit(58)

            try:
                arg1Value = int(arg1Value)
                arg2Value = str(arg2Value)
                dstValue = str(dstValue)

            except:
                exit(53)

            if arg1Value < 0:
                exit(58)

            dstValue = list(dstValue)

            try:
                dstValue[arg1Value] = arg2Value[0]
            except IndexError:
                exit(58)

            ret = "".join(dstValue)

            if dst.value.split('@')[0] == "GF":
                UpdateGFrameType(dst.value.split('@')[1], 'string')
                UpdateGFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "LF":
                UpdateLFrameType(dst.value.split('@')[1], 'string')
                UpdateLFrameValue(dst.value.split('@')[1], ret)

            if dst.value.split('@')[0] == "TF":
                UpdateTFrameType(dst.value.split('@')[1], 'string')
                UpdateTFrameValue(dst.value.split('@')[1], ret)


        elif command.GetOpcode() == 'DPRINT':
            
            arg1 = command.arglist[0]

            if arg1.varType == 'var':
                if arg1.value.split('@')[0] == "GF":
                    arg1Value = GetValueFromGFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromGFrame(arg1.value.split('@')[1])

                if arg1.value.split('@')[0] == "LF":
                    arg1Value = GetValueFromLFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromLFrame(arg1.value.split('@')[1])


                if arg1.value.split('@')[0] == "TF":
                    arg1Value = GetValueFromTFrame(arg1.value.split('@')[1])
                    arg1Type = GetTypeFromTFrame(arg1.value.split('@')[1])

            else:
                arg1Val = arg1.value
                arg1Type = arg1.varType

            sys.stderr.write(arg1Val)
  
        elif command.GetOpcode() == 'BREAK':
            instrCounter = instrCounter -1
            sys.stderr.write('Pocet vykonanych instrukcii: ')
            sys.stderr.write(str(instrCounter))
            sys.stderr.write('\nGlobal Frame:\n')
            for item in globalFrame:
                sys.stderr.write(str(item))
                sys.stderr.write('\n')
            
            sys.stderr.write('\nLocal Frames:\n')
            if len(frameStack) == 0:
                sys.stderr.write('No Local Frames\n')
            for item in frameStack:
                for frame in item:
                    sys.stderr.write(item)
                    sys.stderr.write('\n')
            sys.stderr.write('\nTemporary Frame (if exists):\n')
            if type(tmpFrame) is list:
                for item in tmpFrame:
                    sys.stderr.write(item)
                    sys.stderr.write('\n')
            else:
                sys.stderr.write("No Temporary Frame\n")

        else:
            exit(32)


        

        


    