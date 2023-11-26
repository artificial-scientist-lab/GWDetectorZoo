#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 10:04:13 2022

@author: jonathandrori
"""

from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from pykat import finesse                 # Importing the pykat.finesse package
from scipy.stats import logistic
import numpy as np
import matplotlib.pyplot as plt


def getSpaceCoordinates(space_name):
    if space_name[2:4].isdigit() and space_name[5:7].isdigit() and space_name[9:11].isdigit() and space_name[12:14].isdigit():
        return np.array([int(space_name[2:4]), int(space_name[5:7]), int(space_name[9:11]), int(space_name[12:14])])
    else:
        #print(space_name + ' has no coordinates')
        return None
    
def getComponentCoordinates(comp_name):
    if comp_name[1:3].isdigit() and comp_name[4:6].isdigit():
        return np.array([int(comp_name[1:3]), int(comp_name[4:6])])
    else:
        #print(comp_name + ' has no coordinates')
        return None

def GetNextCor(space_name, comp_name, L, cor):
    space_cors = getSpaceCoordinates(space_name)
    comp_cors = getComponentCoordinates(comp_name)
    space_dirX = -np.sign(int(np.array([space_cors[2],space_cors[0]]).max()<=comp_cors[0])-0.5)*int(space_name[1]=='X')
    space_dirY = np.sign(int(np.array([space_cors[3],space_cors[1]]).min()>=comp_cors[1])-0.5)*int(space_name[1]=='Y')
    return cor + np.array([L*space_dirX,L*space_dirY])
    
def PopulateCors(kat_, comp_name, node_name, cor, space_powers, comps_cors=[], space_cors=[], comp_stack=[], node_stack=[]):
    #Recursively draw all the component and spaces
    kattemp = kat_
    
    comp = kattemp.components[comp_name]
    # Loop prevention
    if comp_name in comp_stack:     
        node_stack.append(kattemp.nodes[node_name].name)
        return
    
    comp_stack = comp_stack + [comp_name]
    
    #Is it first component?
    if node_name is not None: 
        node = kattemp.nodes[node_name]
    else:
        node = None

    
    #Draw next component
    comp_nodes = np.array(kattemp.nodes.getComponentNodes(comp))
    other_nodes = comp_nodes[comp_nodes!=node]
    for other_node in other_nodes:
        if other_node.isConnected() and other_node.name not in node_stack:
            other_node_comps = np.array(kattemp.nodes.getNodeComponents(other_node))
            space = other_node_comps[other_node_comps!=comp][0]
            L = np.log10(space.L.value)
            #Expand space if it is too small
            if L<1: L = 1
            #Make the space left to right and down up
            next_cor = GetNextCor(space.name, comp_name, L, cor)
            if np.sum(next_cor-cor)>0:
                space_cors.append({'spacename':space.name , 'cor':cor, 'nextcor':next_cor})
            else:
                space_cors.append({'spacename':space.name , 'cor':next_cor, 'nextcor':cor})
            space_nodes = np.array(space.nodes)
            next_node = space_nodes[space_nodes!=other_node][0]
            next_node_components = np.array(next_node.components)
            next_component = next_node_components[next_node_components!=space][0]
            if next_component is None:
                continue
            next_component_name = next_component.name
            PopulateCors(kat_, next_component_name, next_node.name, next_cor, space_powers, comps_cors, space_cors, comp_stack, node_stack)
    #print(comp_stack)
    #Draw current component
    orient = FindOrientation(kattemp, comp_name, space_powers)
    comps_cors.append({'compname':comp_name, 'cor':cor, 'orient':orient})
    return

def DrawSpace(space_cors, space_power, space_len, canvas, disablelabels=False):
    [cor, next_cor, spacename] = [space_cors['cor'], space_cors['nextcor'], space_cors['spacename']]
    linewidth = np.log10(space_power)
    # if linewidth<-5: 
    #     return
    if linewidth<0: linewidth=0.1

    canvas.saveState()
    #setLineWidth
    canvas.setStrokeColorRGB(1, 0, 0)
    canvas.setLineWidth(linewidth*2)
    canvas.line(cor[0]*inch, cor[1]*inch, next_cor[0]*inch, next_cor[1]*inch)
    canvas.restoreState()
    if not disablelabels:
#        print(spacename)
        DrawSpaceText(space_cors, space_power, space_len, canvas, 8)
    
def DrawSpaceText(space_cors, space_power, space_len, canvas, fontsize = 8):
    canvas.saveState()
    cor, next_cor = [space_cors['cor'], space_cors['nextcor']]
    if space_power < 1e-9:
        txt = '<nW'
    if space_power >= 1e-9:
        txt = str(int(space_power*1e9)) + 'nW'
    if space_power >= 1e-6:
        txt = str(int(space_power*1e6)) + 'uW'
    if space_power >= 1e-3:
        txt = str(int(space_power*1e3)) + 'mW'
    if space_power >= 1:
        txt = str(int(space_power)) + 'W'
    if space_power >= 1e3:
        txt = str(int(space_power/1e3)) + 'kW'
    if space_power >= 1e6:
       txt = str(int(space_power*10/1e6)/10) + 'MW'
    
    linewidth = np.log10(space_power)
    if linewidth<0: linewidth=0.1
    
    if space_len < 1e-3:
        txt2 = '< mm'
    if space_len >= 1e-3:
        txt2 = str(int(space_len*1e3)) + 'mm'
    if space_len >= 1:
        txt2 = str(int(space_len)) + 'm'
    if space_len >= 1e3:
        txt2 = str(int(space_len*1e-3)) + 'km'
    txt = txt  + ', ' + txt2
    textobject = canvas.beginText()
    textobject.setFont('Times-Roman', fontsize)
    if space_cors['spacename'][1]=='X':
        
        textobject.setTextOrigin((cor[0] + next_cor[0] - stringWidth(txt, 'Times-Roman', fontsize)/inch)*inch/2, cor[1]*inch - linewidth/2 - fontsize*1.5)
    
    if space_cors['spacename'][1]=='Y':
        textobject.setTextOrigin(cor[0]*inch - linewidth/2 - stringWidth(txt, 'Times-Roman', fontsize) - 6, (cor[1] + next_cor[1] - fontsize*1.5/inch)*inch/2)
#        canvas.rotate(-90)
        
    textobject.textLine(txt)
    canvas.drawText(textobject)
    canvas.restoreState()
    
def DrawComp(kat, comp_cors, canvas, comp_dict, old_new_dict={}, disablelabels=False):
    [comp_name, cor, orient] = list(comp_cors.values())
    page = comp_dict[comp_name[0]].copy()
    canvas.saveState()
    page.Rotate = orient
    page.Alpha=0.5
    xsign = -np.sign(int(orient in (180, 270))-0.5)
    ysign = -np.sign(int(orient in (180, 90))-0.5)
    if orient in (0, 180):
        half_xdim = pagexobj(page).BBox[2]/2  
        half_ydim = pagexobj(page).BBox[3]/2
    else:
        half_xdim = pagexobj(page).BBox[3]/2  
        half_ydim = pagexobj(page).BBox[2]/2
    
    cor = np.array([cor[0]*inch-xsign*half_xdim, cor[1]*inch-ysign*half_ydim])
    canvas.translate(*cor)
    canvas.doForm(makerl(canvas,  pagexobj(page)))
    comp_cors_more = comp_cors.copy()
    comp_cors_more['cor'] = cor + np.array([xsign*half_xdim, ysign*half_ydim])
    comp_cors_more['half_size'] = np.array([half_xdim, half_ydim])
    canvas.restoreState()
    if not disablelabels:
        DrawCompText(kat, comp_cors_more, canvas, 8, old_new_dict=old_new_dict)

def DrawCompText(kat, comp_cors_more, canvas, fontsize = 8, old_new_dict={}):
    [comp_name, cor_inches, orient, half_size] = list(comp_cors_more.values())
    comp = kat.components[comp_name]
    textcors = cor_inches + half_size + np.array([5, 10])
    # print(comp_name)
    # print(str(cor_inches))
    # print(str(textcors))
    textobject = canvas.beginText()
    textobject.setTextOrigin(*textcors)
    textobject.setFont('Times-Roman', fontsize)
    if comp_name in old_new_dict.keys():
        textobject.textLine(text=old_new_dict[comp_name])
    else:
        textobject.textLine(text=comp_name)
    if comp_name[0] in ['B','M'] and hasattr(kat.components[comp_name],'T'):
        T = comp.T.value
        if T>1e-4:
            txt = f'{T*1e2:0.4}%'
        else:
            txt = str(int(T*1e6))+'ppm'
        
        txt = txt
        if hasattr(comp,'mass'):
            if comp.mass.value is not None and comp.mass.value<1e3:
                if comp.mass.value<1:
                    txt2 = str(int(comp.mass.value*1e3))+'g'
                else:
                    txt2 = str(int(comp.mass.value))+'kg'
                
                txt = txt + ', '+txt2
        if comp.phi != 0:
            txt = txt + ', ' + str(int(comp.phi.value))+'deg'
        textobject.textLine(text=txt) 
        
    if comp_name[0]=='L':
        textobject.textLine(text=str(int(comp.P.value*100)/100)+'W, ' + str(int(comp.phase.value))+'deg')
        
    if comp_name[0]=='Q':
            textobject.textLine(text=str(int(comp.db.value))+'dB, ' + str(int(comp.phase.value))+'deg')
            
    canvas.drawText(textobject)
    canvas.drawText(textobject)

def IsOrientable(kattemp, comp_name, spaces_names):
    comp = kattemp.components[comp_name]
    if comp_name[0] in ('B', 'F'):
        comp_nodes = np.array(kattemp.nodes.getComponentNodes(comp))
        if (comp_nodes[0].isConnected() and comp_nodes[1].isConnected()):
            return [0,1]
        if (comp_nodes[2].isConnected() and comp_nodes[3].isConnected()):
            return [3,2]
        return False

def FindOrientation(kattemp, comp_name, space_powers):
    # import ipdb
    # ipdb.set_trace()
    comp = kattemp.components[comp_name]
    comp_nodes = np.array(kattemp.nodes.getComponentNodes(comp))
    nodes_comps = np.array([np.array(kattemp.nodes.getNodeComponents(node)) for node in comp_nodes])
    comp_spaces_names = np.array([comps[comps!=comp][0].name if comps[comps!=comp][0] is not None else '' for comps in nodes_comps])
    comp_nodes_isConnected = np.array([node.isConnected() for node in comp_nodes])
    connected_nodes_comps = nodes_comps[comp_nodes_isConnected]
    connected_comp_spaces_names = np.array([comps[comps!=comp][0].name for comps in connected_nodes_comps])

    if comp_name[0] in ('B', 'F'):
        #It's a BS, find handedness and return the appropriate rotation angle
        BS_inds = IsOrientable(kattemp, comp_name, comp_spaces_names)
        if BS_inds:
            handedness = 1
            for space_name in comp_spaces_names[BS_inds]:
                handedness = handedness*np.sign(SpaceCompFlipFactor(space_name, comp_name)-0.5)
                
            BSFangle =  -(handedness-1)*45
            flipAngle = 0
            
            if comp_name[0] == 'F':
                if BSFangle == 0:
                    if ((comp_spaces_names[BS_inds[0]][1]=='X' and not SpaceCompFlipFactor(comp_spaces_names[BS_inds[0]], comp_name)) or (comp_spaces_names[BS_inds[0]][1]=='Y' and SpaceCompFlipFactor(comp_spaces_names[BS_inds[0]], comp_name))):
                        flipAngle = 180
                if BSFangle == 90:
                    if ((comp_spaces_names[BS_inds[0]][1]=='X' and not SpaceCompFlipFactor(comp_spaces_names[BS_inds[0]], comp_name)) or (comp_spaces_names[BS_inds[0]][1]=='Y' and not SpaceCompFlipFactor(comp_spaces_names[BS_inds[0]], comp_name))):
                        flipAngle = 180
            
            return BSFangle + flipAngle
    
    if comp_name[0] in ['M', 'L', 'Q', 'P']:
        #It's a mirror, orient in space direction and face the space with largest power
        maxpower = 0 
        chosen_space = ''
        for space_name in connected_comp_spaces_names:
            if space_powers[space_name]>=maxpower:
                maxpower = space_powers[space_name]
                chosen_space = space_name

        return SpaceCompFlipFactor(chosen_space, comp_name)*180 + 90*int(chosen_space[1]=='Y')
        
def SpaceCompFlipFactor(space_name, comp_name):
    space_cor = getSpaceCoordinates(space_name)
    comp_cor = getComponentCoordinates(comp_name)
    if (space_cor[2]-space_cor[0]): 
        #It's X space
        return int(comp_cor[0]>=np.max([space_cor[2], space_cor[0]]))
    else:
        return int(comp_cor[1]<=np.min([space_cor[3], space_cor[1]]))

def ComputeSpacePowers(kat_):
    katWithDCPDs = kat_.deepcopy()
    katWithDCPDs.verbose=False
    PDNames1=[] #PD Names
    PDNames2=[] #PD Names
    PDNames3=[] #PD Names
    PDNames4=[] #PD Names
    isspace=np.array(['space' in str(type(katWithDCPDs.components[comp])) for comp in katWithDCPDs.components])
    componentsnames = np.array(list(katWithDCPDs.components.keys()))
    spacenames = componentsnames[isspace]

    for spacename in spacenames:
        spacenodes = katWithDCPDs.nodes.getComponentNodes(katWithDCPDs.components[spacename])
        PDName1 = 'poutdc_'+spacename+'_'+'1'
        PDName2 = 'poutdc_'+spacename+'_'+'2'
        PDName3 = 'poutdc_'+spacename+'_'+'1A'
        PDName4 = 'poutdc_'+spacename+'_'+'2A'
        PDNames1.append(PDName1)
        PDNames2.append(PDName2)
        PDNames3.append(PDName3)
        PDNames4.append(PDName4)
        katWithDCPDs.parse('pd0 '+PDName1+' '+spacenodes[0].name)
        katWithDCPDs.parse('pd0 '+PDName2+' '+spacenodes[1].name)
        katWithDCPDs.parse('pd0 '+PDName3+' '+spacenodes[0].name+'*')
        katWithDCPDs.parse('pd0 '+PDName4+' '+spacenodes[1].name+'*')
        katWithDCPDs.yaxis = 'abs'
    katWithDCPDs.parse('noxaxis') #no xaxis
    
    outALigoWithDCPDs = katWithDCPDs.run()    
    
    Powers1 = np.array(outALigoWithDCPDs[PDNames1]) # Get measured powers in PDDCs
    Powers2 = np.array(outALigoWithDCPDs[PDNames2]) # Get measured powers in PDDCs
    Powers3 = np.array(outALigoWithDCPDs[PDNames3]) # Get measured powers in PDDCs
    Powers4 = np.array(outALigoWithDCPDs[PDNames4]) # Get measured powers in PDDCs
    Powers = np.array([Powers1, Powers2, Powers3, Powers4]).max(axis=0)
#    Powers = Powers + 1e-3
    return dict(zip(spacenames, Powers))

def ComputeSpaceSignals(kat_, f):
    katWithDCPDs = kat_.deepcopy()
    PDNames1=[] #PD Names
    PDNames2=[] #PD Names
    PDNames3=[] #PD Names
    PDNames4=[] #PD Names
    isspace=np.array(['space' in str(type(katWithDCPDs.components[comp])) for comp in katWithDCPDs.components])
    componentsnames = np.array(list(katWithDCPDs.components.keys()))
    spacenames = componentsnames[isspace]

    for spacename in spacenames:
        spacenodes = katWithDCPDs.nodes.getComponentNodes(katWithDCPDs.components[spacename])
        PDName1 = 'poutac_'+spacename+'_'+'1'
        PDName2 = 'poutac_'+spacename+'_'+'2'
        PDName3 = 'poutac_'+spacename+'_'+'1A'
        PDName4 = 'poutac_'+spacename+'_'+'2A'
        PDNames1.append(PDName1)
        PDNames2.append(PDName2)
        PDNames3.append(PDName3)
        PDNames4.append(PDName4)
        katWithDCPDs.parse('ad '+PDName1+' 0 0 $fs '+spacenodes[0].name)
        katWithDCPDs.parse('ad '+PDName2+' 0 0 $fs '+spacenodes[1].name)
        katWithDCPDs.parse('ad '+PDName3+' 0 0 $fs '+spacenodes[0].name+'*')
        katWithDCPDs.parse('ad '+PDName4+' 0 0 $fs '+spacenodes[1].name+'*')
        katWithDCPDs.yaxis = 'abs'
    katWithDCPDs.parse('noxaxis') #no xaxis
    katWithDCPDs.signals.f = f
    outALigoWithDCPDs = katWithDCPDs.run()    

    Powers1 = np.array(outALigoWithDCPDs[PDNames1]) # Get measured powers in PDDCs
    Powers2 = np.array(outALigoWithDCPDs[PDNames2]) # Get measured powers in PDDCs
    Powers3 = np.array(outALigoWithDCPDs[PDNames3]) # Get measured powers in PDDCs
    Powers4 = np.array(outALigoWithDCPDs[PDNames4]) # Get measured powers in PDDCs
    Powers = np.array([Powers1, Powers2, Powers3, Powers4]).max(axis=0)
    return dict(zip(spacenames, Powers/1e10))
    

def FixDetectorCode(kat_, detector_space_text, replace_text = None, no_of_grid_points = 1, old_new_dict = {}, replace_comp = ''):
    
    def findnextcor(dir):
        if dir=='X':
            nextcor = previous_comp_cor + np.array([no_of_grid_points, 0])#*occupy_sign
        elif dir=='Y':
            nextcor = previous_comp_cor + np.array([0, no_of_grid_points])#*occupy_sign
        for compname in kat_.components:
            if compname[0] not in 'BMFLP':
                continue
            compcor = getComponentCoordinates(compname)
            if (nextcor==compcor).all() and (replace_text is None or replace_text in kat_.components):
                if dir=='X':
                    nextcor = previous_comp_cor + np.array([-no_of_grid_points, 0])#*occupy_sign
                elif dir=='Y':
                    nextcor = previous_comp_cor + np.array([0, -no_of_grid_points])#*occupy_sign
                break
        return nextcor
    
#    kattemp = kat_.deepcopy()
    # if replace_text is not None and replace_text not in kat_.components:
        # return kat_
    if detector_space_text not in kat_.components:
        return kat_
    detector_space = kat_.components[detector_space_text]
    detector_space_nodes = detector_space.nodes
    nodes_comps = np.array([np.array(kat_.nodes.getNodeComponents(node)) for node in detector_space_nodes])
    previous_comps = nodes_comps[nodes_comps!=detector_space]
    # previous_comp = previous_comps[previous_comps!=None][previous_comp_ind]
    previous_comp_find_success = False
    previous_comp_ind = 0
    for previous_comp in previous_comps[previous_comps!=None]:
        previous_comp_cor = getComponentCoordinates(previous_comp.name) 
        if previous_comp_cor is not None:
            previous_comp_find_success = True
            break
        previous_comp_ind = previous_comp_ind + 1
        
    if not previous_comp_find_success:
        print('Cannot find previous comp with coordinates. Aborting!')
        return None
    
    previous_comp_nodes = np.array(previous_comp.nodes)
    detector_space_direction='X'
    nextcor = findnextcor('X')  
    for node in previous_comp_nodes[previous_comp_nodes!=detector_space_nodes[previous_comp_ind]]:
        if node.isConnected():
            nodecomps = np.array(node.components)
            space = nodecomps[nodecomps!=previous_comp][0]
            spacecor = getSpaceCoordinates(space.name)
            if spacecor is None:
                continue
            
            nextcor = previous_comp_cor
            if previous_comp.name[0]=='M':
                if space.name[1]=='X':
#                    occupy_sign = -int(np.sign(int(isOccupied(kattemp, nextcor + [no_of_grid_points, 0]))-0.5))
                    nextcor = findnextcor('X')                            
                    detector_space_direction = 'X'
                else:
 #                   occupy_sign = -int(np.sign(int(isOccupied(kattemp, nextcor + [0, no_of_grid_points]))-0.5))
                    
                     nextcor = findnextcor('Y')       
                     detector_space_direction = 'Y'
                break
            if previous_comp.name[0] in ('B', 'F'):
                nodes_index_diff = np.abs(np.where(previous_comp_nodes==node)[0][0]-np.where(previous_comp_nodes==detector_space_nodes[previous_comp_ind])[0][0])
                if nodes_index_diff in [1,3] and space.name[1]=='Y' or nodes_index_diff==2 and space.name[1]=='X':
                    #occupy_sign = -int(np.sign(int(isOccupied(kattemp, nextcor + [no_of_grid_points, 0]))-0.5))
                    nextcor = findnextcor('X') 
                    detector_space_direction = 'X'
                else:
                    #occupy_sign = -int(np.sign(int(isOccupied(kattemp, nextcor + [0, no_of_grid_points]))-0.5))
                    nextcor = findnextcor('Y') 
                    detector_space_direction = 'Y'
                break
    
    newkat = finesse.kat()
    new_space_name = 'S'+detector_space_direction+FormatCorString(previous_comp_cor)+'__'+FormatCorString(nextcor)
    
    if detector_space_text in old_new_dict.keys():
        old_new_dict[new_space_name] = old_new_dict[detector_space_text]
        old_new_dict.pop(detector_space_text)
    else:
        old_new_dict[new_space_name] = detector_space_text
        
    newkattext = ''.join(kat_.generateKatScript()).replace(detector_space_text, new_space_name)
    
    if replace_text is None:
        for detector_space_node in detector_space_nodes:
            if any([component is None for component in detector_space_nodes[0].components]):
                break
            
        detectortext = ('m1 P'+FormatCorString(nextcor)+' 1 0 0 '+detector_space_node.name + ' dump')
        newkattext = newkattext + detectortext
    else:
        if replace_comp=='':
            replace_comp1 = replace_text[0]
        else:
            replace_comp1 = replace_comp
        newtext = replace_comp1+FormatCorString(nextcor)
        newkattext = newkattext.replace(replace_text, newtext)
        if replace_text in old_new_dict.keys():
            old_new_dict[newtext] = old_new_dict[replace_text]
            old_new_dict.pop(replace_text)
        else:
            old_new_dict[newtext] = replace_text
    #newkat.components[new_space_name].L.value = 1
    newkat.parse(newkattext, preserveConstants=True)
    return newkat

def FormatCorString(cor):
    return f'{cor[0]:02d}'+'_'+f'{cor[1]:02d}'

# def isOccupied(kat_, cor):
#     kattemp = kat_.deepcopy()
#     comps_names = np.array(list(kattemp.components.keys()))
#     spaces_names = np.array([comp_name for comp_name in comps_names if comp_name[0]=='S'])
    
#     for space_name in spaces_names:
#         if space_name in ('SFI1', 'SFI2'): continue
#         space_cors = np.array(getSpaceCoordinates(space_name))
        
#         if space_name[1]=='X' and cor[0] in range(space_cors[[0, 2]].min(), space_cors[[0, 2]].max()+1) and cor[1]==space_cors[1]:
#             return True
#         if space_name[1]=='Y' and cor[1] in range(space_cors[[1, 3]].min(), space_cors[[1, 3]].max()+1) and cor[0]==space_cors[0]:
#             return True
#     return False

def MakeSpacesUniform(kat_):
    kattemp = kat_.deepcopy()
    kat_script = "".join(kattemp.generateKatScript())
       
    for compname, comp in kattemp.components.items():
        if compname[0]=='S':
            new_space_name = compname
            allcors = getSpaceCoordinates(compname)
            cors = allcors[0:2]
            nextcors = allcors[2:4]
            if np.sum(nextcors-cors)<0:
                new_space_name = compname[0:2] + FormatCorString(nextcors)+'__'+FormatCorString(cors)
            kat_script = kat_script.replace(' '+compname+' ', ' '+new_space_name+' ')
    
    newkat = finesse.kat()
    newkat.parse(kat_script, preserveConstants = True)
    return newkat
    
def AlignComponents(comps_struct, spaces_struct):
    comps_struct_new = np.array(comps_struct.copy())
    spaces_struct_new = np.array(spaces_struct.copy())
    is_aligned_x = np.array([False]*len(comps_struct))
    is_aligned_y = np.array([False]*len(comps_struct))
    cors = np.array([comp_struct['cor'] for comp_struct in comps_struct])
    spaces_cors = np.array([space_struct['cor'] for space_struct in spaces_struct])
    space_nextcors = np.array([space_struct['nextcor'] for space_struct in spaces_struct])
    
    comps_names = np.array([comp_struct['compname'] for comp_struct in comps_struct])
    grid_comps_cors = np.array([getComponentCoordinates(comp_name) for comp_name in comps_names])
    spaces_names = np.array([space_struct['spacename'] for space_struct in spaces_struct])
    grid_spaces_cors = np.array([getSpaceCoordinates(space_name) for space_name in spaces_names])

    for i in range(len(comps_struct)):
        same_x_ind = np.where(grid_comps_cors[:,0]==grid_comps_cors[i,0])[0]
        same_y_ind = np.where(grid_comps_cors[:,1]==grid_comps_cors[i,1])[0]
        new_xcor = cors[same_x_ind,0].mean()
        new_ycor = cors[same_y_ind,1].mean()
        cors[same_x_ind,0] = new_xcor
        cors[same_y_ind,1] = new_ycor
        is_aligned_x[same_x_ind] = True
        is_aligned_y[same_y_ind] = True

        same_x_ind = np.where(grid_spaces_cors[:,0]==grid_comps_cors[i,0])[0]
        spaces_cors[same_x_ind,0] = new_xcor
        
        same_x_ind = np.where(grid_spaces_cors[:,2]==grid_comps_cors[i,0])[0]
        space_nextcors[same_x_ind,0] = new_xcor
        
        same_y_ind = np.where(grid_spaces_cors[:,1]==grid_comps_cors[i,1])[0]
        spaces_cors[same_y_ind,1] = new_ycor
        
        same_y_ind = np.where(grid_spaces_cors[:,3]==grid_comps_cors[i,1])[0]
        space_nextcors[same_y_ind,1] = new_ycor
        
        if all(is_aligned_x) and all(is_aligned_y): 
            break
    
    for i in range(len(comps_struct)):
        comps_struct_new[i]['cor'] = cors[i]
    
    for i in range(len(spaces_struct)):
        spaces_struct_new[i]['cor'] = spaces_cors[i]
        spaces_struct_new[i]['nextcor'] = space_nextcors[i]
        
    return [comps_struct_new, spaces_struct_new]


def ParseUIFOkat(kat_, gridsize, skip_comps = [], old_new_dict={}):
    kattemp = kat_.deepcopy()
    kat_script = "".join(kattemp.generateKatScript())
       
    for compname, comp in kattemp.components.items():
        # print(compname)
        newcompname = compname
        if compname in skip_comps:
            continue
        if compname[0]=='L':
            cor = getUIFOCors(compname[2:5], gridsize)
            if 'squeezer' in str(type(comp)):
                newcompname = 'Q' + FormatCorString(cor)
            else:
                newcompname = 'L' + FormatCorString(cor)
        if compname.find("ML")==0:
            cor = getUIFOCors(compname[3:6], gridsize)
            newcompname = 'M' + FormatCorString(cor+getUIFODisp(comp.nodes[1].name[7])[0])
        if compname[0]=='B':
            cor = getUIFOCors(compname[1:4], gridsize)
            if 'dbs' in str(type(comp)):
                newcompname = 'F' + FormatCorString(cor)
            else:
                newcompname = 'B' + FormatCorString(cor)
        if compname.find("MB")==0:
            cor = getUIFOCors(compname[2:5], gridsize)
            newcompname = 'M' + FormatCorString(cor+getUIFODisp(compname[6])[0])
        if compname.find("SL_")==0:
            space_nodes = comp.nodes
            mirror = space_nodes[1].components[0]
            mirror_node_name = mirror.nodes[1].name
            cor = getUIFOCors(compname[3:6], gridsize)
            dirc = getUIFODisp(mirror_node_name[7])
            newcompname = 'S' + dirc[1] + FormatCorString(cor)+'__'+FormatCorString(cor+dirc[0])
        if compname.find("SLMB")==0:
            cor = getUIFOCors(compname[4:7], gridsize)
            dirc = getUIFODisp(compname[8])            
            newcompname = 'S' + dirc[1]  + FormatCorString(cor)+'__'+FormatCorString(cor + dirc[0])
        if compname.find("mUD")==0:
            cor = getUIFOCors(compname[4:7], gridsize)
            newcompname = 'SY' + FormatCorString(cor-[0,1])+'__'+FormatCorString(cor-[0,2])
        if compname.find("mRL")==0:
            cor = getUIFOCors(compname[4:7], gridsize)
            newcompname = 'SX' + FormatCorString(cor+[1,0])+'__'+FormatCorString(cor+[2,0])
        if compname in ('MDet', 'MFI1', 'MFI2', 'MrNodes4', 'MrNodes5', 'MDet1', 'MDet2', 'MDetX', 'MArmU', 'MArmR'):
            cor = getUIFOCors(comp.nodes[1].name[3:6], gridsize)+getUIFODisp(comp.nodes[1].name[7])[0]
            newcompname = 'M' + FormatCorString(cor) 
        if compname in ['SDet', 'SDetX']:
            newcompname = 'sToDetector'
        if compname=='finDBS':
            newcompname = 'F_finDBS'
        # if compname=='FinSqueeze':
        #     newcompname = 'Q_FinSqueeze'
        if compname=='finBSref1':
            newcompname='B_finBSref1'
        if compname=='finBSref2':
            newcompname='B_finBSref2'
        if compname=='finS2':
            newcompname='sfinS2'
        if compname=='finS3':
            newcompname='sfinS3'
        

        old_new_dict[newcompname] = compname
        kat_script = kat_script.replace(' '+compname+' ', ' '+newcompname+' ')

    
    kat_script = kat_script.replace('nDet_node nMDet_laser', 'nMDet_laser nDet_node')
    kat_script = kat_script.replace('nsqFinNode ndbsSQin', 'ndbsSQin nsqFinNode')
    kat_script = kat_script.replace('nFI2_node nMFI2_laser', 'nMFI2_laser nFI2_node')
    kat_script = kat_script.replace('nFI1_node nMFI1_laser', 'nMFI1_laser nFI1_node')
    kat_script = kat_script.replace('nrNodes_4 nMrNodes4_laser', 'nMrNodes4_laser nrNodes_4')
    kat_script = kat_script.replace('nrNodes_5 nMrNodes5_laser', 'nMrNodes5_laser nrNodes_5')
    newkat = finesse.kat()
    newkat.parse(kat_script, preserveConstants = True)
    return newkat
    
def getUIFOCors(corstr,gridsize):
    x = int(corstr[0])
    y = int(corstr[2])
    y = np.abs(y - gridsize - 1) #Put the origin at the bottom of the page
    return 3*np.array([x,y])

def getUIFODisp(dispstr):
    if dispstr[0]=='u':
        return (np.array([0,+1]),'Y')
    if dispstr[0]=='d':
        return (np.array([0,-1]), 'Y')
    if dispstr[0]=='r':
        return (np.array([1,0]), 'X')
    if dispstr[0]=='l':
        return (np.array([-1,0]), 'X')
    
def KatCleanup(kat_, score_thresh = 0, f_start = 5, f_end = 1e4, pt_no = 10, fast = False, exclusionlist=[]):   
    freq_info = [f_start, f_end, pt_no]  

    file1 = open("geo_aligo_pure7.kat", "r")
    readfile = file1.read() + ' ' + str(f_start)+' '+str(f_end)+' '+str(pt_no)
    file1.close()
    kataligo = finesse.kat()
    kataligo.parse(readfile)
    kataligo.verbose = False
    kataligo.xaxis.limits = [f_start, f_end]
    kataligo.xaxis.steps = pt_no
    kataligo.parse('pd0 poutdc1 AtPD1')
    kataligo.parse('pd0 poutdc2 AtPD2')
    freq, aligoSSens, lossPowerElements, lossPowerPD=compute_strain(freq_info, kataligo, fast)
    aligoSSenslog = np.log10(aligoSSens)
        
    kattemp = kat_.deepcopy()
    kattemp.verbose = False
    kattemp.xaxis.limits = [f_start, f_end]
    kattemp.xaxis.steps = pt_no
    kattemp.parse('pd0 poutdc1 AtPD1') # kattemp.parse('pd0 poutdc1 AtPD1')
    kattemp.parse('pd0 poutdc2 AtPD2')
    freq, sens_orig, lossPowerElements, lossPowerPD = compute_strain(freq_info, kattemp, fast)
    
    LSens_log=np.log10(sens_orig)
    LSens_log_diff=(LSens_log-aligoSSenslog)
    LSens_objective_list=(LSens_log_diff)
    lossStrain=sum(LSens_objective_list)
    
    score_orig=lossStrain+lossPowerElements+lossPowerPD
               
#    plt.loglog(freq, sens_orig)
    def check_importance(kat_, text):
        #print(text)
        if fast:
            try:
                out_new = kat_.run()
            except:
                return True
            sens_new = CalculateBHDSens(out_new)
            score_diff = np.sum(np.log10(sens_orig)-np.log10(sens_new))
        else:
            try:
                freq, SSens, lossPowerElements, lossPowerPD = compute_strain(freq_info, kat_)
            except:
                return True
            LSens_log=np.log10(SSens)            
            LSens_log_diff=(LSens_log-aligoSSenslog)
            LSens_objective_list=(LSens_log_diff)
            lossStrain=sum(LSens_objective_list)            
            newscore=lossStrain+lossPowerElements+lossPowerPD
            
            score_diff = score_orig - newscore
            
        if score_diff<=score_thresh or np.isnan(score_diff):
            #print(str(score_diff)+" Yes!")
            return True
        else:
            #print(str(score_diff)+" No!")
            pass
 
#            plt.plot(out_new.x, sens_new)
        return False
    
    def ChangeTransmission(kat, comp, newvalue):
        Tconstantname = comp.T.constantName
        if Tconstantname is None:
            comp.T.value = newvalue
        else:
            kat.constants[Tconstantname[1:]].value = newvalue
        
    for compname in kattemp.components:
        if compname in exclusionlist:
            continue
        targetarray = np.array(kattemp.signals.targets)
        spaces_names = np.array([target.owner for target in targetarray])
        signal_names = np.array([target.name for target in targetarray])
        if compname not in kattemp.components.keys():
            continue
        comp = kattemp.components[compname]
        if ('beamSplitter' in str(type(comp)) or 'mirror' in str(type(comp))) and hasattr(comp,'L'):
            if comp.L.value!=0:
                old_L = comp.L.value
                old_T = comp.T.value
                comp.L.value = 0
                Tconstantname = comp.T.constantName
                ChangeTransmission(kattemp, comp, 1)
                if check_importance(kattemp, 'Is ' + compname + ' transmission ok?'):
                    comp.L.value = old_L
                    ChangeTransmission(kattemp, comp, old_T)
                else:
                    comp.T.value = 1
                    if Tconstantname is not None:
                        kattemp.constants[Tconstantname[1:]].remove()
                    if comp.mass.value is not None:
                        compmassconstantname = comp.mass.constantName
                        comp.mass.value = comp.mass.value
                        if compmassconstantname is not None:
                            kattemp.constants[compmassconstantname[1:]].remove()
                        
                
            if comp.T.value < 0.01 and comp.L.value!=0:
                # saved_state = kattemp.deepcopy()
                # comp = kattemp.components[compname]
                old_T = comp.T.value
                old_L = comp.L.value
                # comp.L.value = 0
                Tconstantname = comp.T.constantName
                ChangeTransmission(kattemp, comp, 15e-6) 
                if check_importance(kattemp, 'Is ' + compname + ' transmission ok?'):
                    comp.L.value = old_L
                    ChangeTransmission(kattemp, comp, old_T)
                else:
                    comp.T.value = 15e-6
                    if Tconstantname is not None:
                        kattemp.constants[Tconstantname[1:]].remove()
                    if comp.mass.value is not None:
                        compmassconstantname = comp.mass.constantName
                        comp.mass.value = comp.mass.value
                        if compmassconstantname is not None:
                            kattemp.constants[compmassconstantname[1:]].remove()
            
        if 'space' in str(type(comp)) and compname!='SX98_99__99_99':
            saved_state = kattemp.deepcopy()
            space_comps = comp.connectingComponents()
            for space_comp in space_comps:
                if space_comp is None:
                    continue
                if space_comp.name[0] in ['L', 'Q']:
                    #print(space_comp.name)
                    space_comp.remove()
                    kattemp.parse("""l L98_99 1.0 0.0 0.0 nDummy0
                                     s SX98_99__99_99 0 nDummy0 nDummy1""")
            comp.remove()
            if len(targetarray[spaces_names==compname])>0:
                targetarray[spaces_names==compname][0].remove()
                
            kattemp.xaxis.remove()
            different_signal = signal_names[spaces_names!=compname][0]
            kattemp.parse("xaxis " + different_signal + f' f log {f_start:.2f} {f_end:.2f} {pt_no:d}')
            if check_importance(kattemp, 'Is '+compname+' important?'):
                kattemp = saved_state
                
    if 'L98_99' in kattemp.components:
        kattemp.L98_99.remove()
    if 'SX98_99__99_99' in kattemp.components:
        kattemp.SX98_99__99_99.remove()
    return kattemp

def CalculateBHDSens(out):
#>>>>>>> 2514eac788bde1335f80872b6f0489ecfee44bd1
    return np.abs(out['nodeFinalDet'])/np.abs(out['poutf1']-out['poutf2'])

def compute_strain(freq_info, katALigoSens, fast=False):
    
    freq_min, freq_max, freq_steps=freq_info
    freq_string=str(freq_min)+' '+str(freq_max)+' '+str(freq_steps)

    outALigo = katALigoSens.run()
    ###### compute laser amplitude modulation transfer functions
    freq = outALigo.x    
    if not fast:
        katamptf = katALigoSens.deepcopy()
        katamptf.signals.remove()
        katamptf.xaxis.remove()
        # for comp_name in katamptf.components:
        #     comp = katamptf.components[comp_name]
        #     if hasattr(comp,'mass'):
        #         if comp.mass.value is not None:
        #             comp.mass.value = None
                    
        for compname in katamptf.components:
            comp = katamptf.components[compname]
            if 'laser' in str(type(comp)):
                alasername = compname + "_ffsig "
                katamptf.parse("fsig " + alasername +  compname + " amp 1 0 " + str(np.sqrt(comp.P.value)))
        katamptf.parse("xaxis "+alasername+" f log "+freq_string)
        outamptf = katamptf.run()
        
        #compute laser freq modulation transfer functions
        
        katfreqtf = katALigoSens.deepcopy()
        katfreqtf.signals.remove()
        katfreqtf.xaxis.remove()
        for compname in katfreqtf.components:
            comp = katfreqtf.components[compname]
            if 'laser' in str(type(comp)):
                alasername = compname + "_ffsig "
                katfreqtf.parse("fsig " + alasername +  compname + " freq 1 0 1")
        
        katfreqtf.parse("xaxis "+alasername+" f log "+freq_string)
        outfreqtf = katfreqtf.run()
        
           
        
        #Use state of the art input RIN and frequency noises and project them on the readout 
        #using the transfer functions computed above
        RINinputnoise = (freq/freq)*4e-9 # 1/sqrt(Hz) taken from Phys. Rev. D 102, 062003
        RINoutputnoises = RINinputnoise*np.abs(outamptf['poutf1']-outamptf['poutf2'])
        
        freqinputnoise = (freq)*1e-8 #Hz/sqrt(Hz) taken from Phys. Rev. D 102, 062003
        freqoutputnoises = freqinputnoise*np.abs(outfreqtf['poutf1']-outfreqtf['poutf2']) 
        Seismic_Sens = 1e-11*freq**-11.3
        Thermal_Sens = 1e-23*freq**-0.6
    else:
        RINoutputnoises = 0
        freqoutputnoises = 0
        Seismic_Sens = 0
        Thermal_Sens = 0

    #Displacement noise calculation

    Displacement_Sens = np.sqrt(Seismic_Sens**2 + Thermal_Sens**2)
    #fig, axs = plt.subplots(3, 1,  figsize=(10,17))
    
    pout_deg = np.abs(outALigo["poutf1"]-outALigo["poutf2"]) # Demodulated power [W/???]
    poutf_m = pout_deg # Demodulated power  [W/Strain]
    qnoise = np.abs(outALigo["nodeFinalDet"])
    totalnoise = np.sqrt(qnoise**2 + RINoutputnoises**2 + freqoutputnoises**2)
    if np.any(poutf_m==0):
        SSens=np.array([1 for ii in poutf_m])
        print('problem with poutf_m in geo_aLIGO7.py')
#        print_file(['problem with poutf_m in geo_aLIGO7.py, ', log_file], file=log_file)
#        time.sleep(0.1)
        
        
        
    else:
        SSens = totalnoise/poutf_m # Differential length change sensitivity [1/sqrt(Hz)]
        SSens_quant = qnoise/poutf_m # Differential length change quantum limited sensitivity [1/sqrt(Hz)]
        
    SSens = np.sqrt(SSens**2 + Displacement_Sens**2)


    katALigoSensWithDCPDs = katALigoSens.deepcopy()
    PDNames=[] #PD Names
    Trans=[] #Components' transmissivities
    for key in katALigoSensWithDCPDs.nodes.getNodes(): #going over all nodes
        for comp in katALigoSensWithDCPDs.nodes.getNodeComponents(katALigoSensWithDCPDs.nodes.getNodes()[key]): #going over all component connected to the node
            if any([relevantcomp in str(type(comp)) for relevantcomp in ['mirror', 'beamSplitter','modulator']]): # If the component is m/bs/m put a dc pd measuring the power going into the node
                PDName = 'poutdc_'+str(comp)+'_'+key
                PDNames.append(PDName)
                katALigoSensWithDCPDs.parse('pd0 '+PDName+' '+key+'*') #Put a DCPD in that node
                    
                if 'modulator' in str(type(comp)): #get the transmission through the component if it is specified. Otherwise compute it from T+R+L=1.
                    Trans.append(1)
                else:
                    if comp.T.value is None:
                        Trans.append(1-comp.R.value-comp.L.value)
                    else:
                        Trans.append(comp.T.value)
                                   
    katALigoSensWithDCPDs.parse('noxaxis') #no xaxis
    outALigoWithDCPDs = katALigoSensWithDCPDs.run()
    
    Trans = np.array(Trans)
    Powers = np.array(outALigoWithDCPDs[PDNames]) # Get measured powers in PDDCs
    #TransmittedPowers = dict(zip(PDNames, Trans*Powers))
    
    poutdc = np.max([np.abs(outALigo["poutdc1"][0]), np.abs(outALigo["poutdc2"][0])])
    all_powers=np.real(Trans*Powers)
    lossPowerElements=500*logistic.cdf(0.003*(max(all_powers) - 5*1e4))
    lossPowerPD=100*logistic.cdf(7500*(poutdc - 10**-2))
    #print('outALigo["poutdc"][0]: ', poutdc)

    return freq, SSens, lossPowerElements, lossPowerPD
