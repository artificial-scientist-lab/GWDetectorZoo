from pykat import finesse                  # Importing the pykat.finesse package
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import logistic
import random
import os
import tempfile
import time
import shutil

from datetime import datetime, date


def print_file(content_list, file):
    full_str=''
    for item in content_list:
        full_str=full_str+' '+str(item)

    now = datetime.now()
    current_time = str(now.strftime("%H:%M:%S"))
    with open(os.path.join(file), 'a') as f:
        f.write(str(date.today())+' '+current_time+': '+full_str+'\n')

    return True

def delete_temp_files(tempdir, tempname):
    for ext in [".out", ".kat", ".log", ".log.bak"]:
        ccc=0
        curr_file_name=os.path.join(tempdir, tempname) + ext
        while os.path.isfile(curr_file_name) and ccc<3:
            ccc+=1
            try:
                os.remove(curr_file_name)
            except:
                time.sleep(0.5*ccc)
                print(curr_file_name,': file delete problem - ', ccc)
                
                
def get_loss_from_katstr(kat_string, freq_info, log_file='log.txt', use_classical_noise=True):
    did_succeed=False
    error_count=0
    loss=666.4242
    while (not did_succeed) and (error_count<5):
        try:
            freq_aligo, strain_aligo, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aLIGO, totalnoise, total_signal = compute_baseline_aligo(freq_info, use_classical_noise=use_classical_noise)
            aligoSSenslog=np.log10(strain_aligo)
            
            freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, total_signal=compute_strain(freq_info, kat_string=kat_string, use_classical_noise=use_classical_noise)
            LSens_log=np.log10(SSens)
            LSens_log_diff=(LSens_log-aligoSSenslog)
            LSens_objective_list=(LSens_log_diff)
            lossStrain=sum(LSens_objective_list)

                    
        
            loss=lossStrain+lossPowerElements+lossPowerPD+lossPowerCoating
            did_succeed=True
        except:
            #print('problem with get_loss_from_katstr in geo_aLIGO10.py_1')
            print_file(['problem with get_loss_from_katstr in geo_aLIGO10.py_1, ', log_file], file=log_file)
            time.sleep(0.1)
            error_count+=1
    return loss 


def get_loss_from_file(kat_file, freq_info, log_file='log.txt', use_classical_noise=True):
    did_succeed=False
    
    loss=666.4242
    error_count=0
    while (not did_succeed) and (error_count<5):
        if True:
            freq_aligo, strain_aligo, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aLIGO, totalnoise, total_signal = compute_baseline_aligo(freq_info, use_classical_noise=use_classical_noise)
            aligoSSenslog=np.log10(strain_aligo)
            file1 = open(kat_file, "r")
            kat_string = file1.read()
            file1.close()
            
            freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, total_signal=compute_strain(freq_info, kat_string=kat_string, use_classical_noise=use_classical_noise)
            LSens_log=np.log10(SSens)
            LSens_log_diff=(LSens_log-aligoSSenslog)
            LSens_objective_list=(LSens_log_diff)
            lossStrain=sum(LSens_objective_list)
            
            print(list(LSens_objective_list))
            
        
            loss=lossStrain+lossPowerElements+lossPowerPD+lossPowerCoating
            print(f'lossStrain: {lossStrain}')
            print(f'lossPowerElements: {lossPowerElements}')
            print(f'lossPowerPD: {lossPowerPD}')
            print(f'lossPowerCoating: {lossPowerCoating}')
            did_succeed=True
        else:
            #print('problem with get_loss_from_file in geo_aLIGO10.py_2')
            print_file(['problem with get_loss_from_file in geo_aLIGO10.py_2, ', log_file], file=log_file)
            time.sleep(0.1)
            error_count+=1
    return loss 


def get_loss_and_save_file(kat_file, freq_info, log_file='log.txt', use_classical_noise=True):
    did_succeed=False
    loss=666.4242
    error_count=0
    while (not did_succeed) and (error_count<5):
        try:
            freq_aligo, strain_aligo, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aLIGO = compute_baseline_aligo(freq_info, use_classical_noise=use_classical_noise)
            aligoSSenslog=np.log10(strain_aligo)
            file1 = open(kat_file, "r")
            kat_string = file1.read()
            file1.close()
            
            freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, total_signal=compute_strain(freq_info, kat_string=kat_string, use_classical_noise=use_classical_noise)
            LSens_log=np.log10(SSens)
            LSens_log_diff=(LSens_log-aligoSSenslog)
            LSens_objective_list=(LSens_log_diff)
            
            
            lossStrain=sum(LSens_objective_list)
        
            loss=lossStrain+lossPowerElements+lossPowerPD+lossPowerCoating
            did_succeed=True

            ss=kat_file.split('_')
            ss[1]='9'
            ss[2]=(str(loss)+'0000000')[0:6]
            dst='_'.join(ss).replace('results','resultsNew')
            
            shutil.copyfile(kat_file, dst)
            
            print(kat_file)
            print(dst)
            print('\n\n\n')
        except:
            print('problem with get_loss_and_save_file')
            print_file(['problem with get_loss_and_save_file, ', log_file], file=log_file)
            time.sleep(0.1)
            error_count+=1
    return loss 



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


def compute_strain(freq_info, kat_string, log_file='log.txt', use_classical_noise=True, give_noise_and_signal=False):
    kat_string=str(kat_string)
    if kat_string[-1]=='\n':
        kat_string=kat_string[0:-1]
        
    tempdir = tempfile._get_default_tempdir()
    tempname = next(tempfile._get_candidate_names())
    
    freq_min, freq_max, freq_steps=freq_info
    freq_string=str(freq_min)+' '+str(freq_max)+' '+str(freq_steps)
    #kat_string+=' '+freq_string
    
    kat_string_parts_last=kat_string.split('\n')[-1]
    
    
    if 'xaxis' in kat_string_parts_last:
        if kat_string[-1]!="0":
            kat_string+=' '+freq_string

    katALigoSens = finesse.kat(tempdir=tempdir, tempname=tempname)
    katALigoSens.verbose = False
    katALigoSens.parse(kat_string)
    katALigoSens.parse('pd0 poutdc1 AtPD1')
    katALigoSens.parse('pd0 poutdc2 AtPD2')

    outALigo = katALigoSens.run()
    #time_diff=time.time()-curr_time
    #print(f"Time1: {time_diff}sec")  
    #curr_time=time.time()
    ###### compute laser amplitude modulation transfer functions

    katamptf = katALigoSens.deepcopy()
    katamptf.signals.remove()
    katamptf.xaxis.remove()
    for compname in katamptf.components:
        comp = katamptf.components[compname]
        if 'laser' in str(type(comp)):
            alasername = compname + "_ffsig "
            katamptf.parse("fsig " + alasername +  compname + " amp 1 0 " + str(np.sqrt(comp.P.value)))
    katamptf.parse("xaxis "+alasername+" f log "+freq_string)
    outamptf = katamptf.run()
    #time_diff=time.time()-curr_time
    #print(f"Time2: {time_diff}sec")  
    #curr_time=time.time()
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
    
    freq = outamptf.x
    #time_diff=time.time()-curr_time
    #print(f"Time3: {time_diff}sec")    
    #curr_time=time.time()
    #Use state of the art input RIN and frequency noises and project them on the readout 
    #using the transfer functions computed above
    RINinputnoise = (freq/freq)*4e-9 # 1/sqrt(Hz) taken from Phys. Rev. D 102, 062003
    RINoutputnoises = RINinputnoise*np.abs(outamptf['poutf1']-outamptf['poutf2'])
    
    freqinputnoise = (freq)*1e-8 #Hz/sqrt(Hz) taken from Phys. Rev. D 102, 062003
    freqoutputnoises = freqinputnoise*np.abs(outfreqtf['poutf1']-outfreqtf['poutf2'])    
    #time_diff=time.time()-curr_time
    #print(f"Time4: {time_diff}sec")   
    #curr_time=time.time()
    #Displacement noise calculation
    Seismic_Sens = 1e-11*freq**-11.3
    Thermal_Sens = 1e-23*freq**-0.6
    Displacement_Sens = np.sqrt(Seismic_Sens**2 + Thermal_Sens**2)
    
    pout_deg = np.abs(outALigo["poutf1"]-outALigo["poutf2"]) # Demodulated power [W/???]
    poutf_m = pout_deg # Demodulated power  [W/Strain]
    qnoise = np.abs(outALigo["nodeFinalDet"])
    totalnoise = np.sqrt(qnoise**2 + RINoutputnoises**2 + freqoutputnoises**2)
    if np.any(poutf_m==0):
        SSens=np.array([1 for ii in poutf_m])
        print('problem with poutf_m in geo_aLIGO10.py')
        print_file(['problem with poutf_m in geo_aLIGO10.py, ', log_file], file=log_file)
        time.sleep(0.1)
        
    else:
        SSens = totalnoise/poutf_m # Differential length change sensitivity [1/sqrt(Hz)]
    #time_diff=time.time()-curr_time
    #print(f"Time5: {time_diff}sec")    
    #curr_time=time.time()
    if use_classical_noise==True:
        SSens = np.sqrt(SSens**2 + Displacement_Sens**2)
        #print("Classical noise!!!")
    else:
        SSens = np.sqrt(SSens**2)
        #print("No classical noise")

    # Compute transmission power now:
    did_succeed=False
    while did_succeed==False:
        try:
            space_powers = ComputeSpacePowers(katALigoSens)
            did_succeed=True
        except:
            print('problem with ComputeSpacePowers in geo_aLIGO10.py')
            print_file(['problem with ComputeSpacePowers in geo_aLIGO10.py, ', log_file], file=log_file)
            time.sleep(0.1)
    #time_diff=time.time()-curr_time
    #print(f"Time6: {time_diff}sec")    
    #curr_time=time.time()
    mirrors = [comp for compname, comp in katALigoSens.components.items() if 'mirror' in str(type(comp))]
    beamsplitters = [comp for compname, comp in katALigoSens.components.items() if 'beamSplitter' in str(type(comp))]
    comps_powers = {}
    comp_coating_power = {}
    #time_diff=time.time()-curr_time
    #print(f"Time7: {time_diff}sec") 
    #curr_time=time.time()
    for comp in mirrors:
        comp_powers = np.array([])
        for node in comp.nodes:
            connected_comps = np.array(node.components)
            if connected_comps[connected_comps!=comp][0] is None:
                comp_powers = np.append(comp_powers, 0)
            for connected_comp in connected_comps[connected_comps!=comp]:
                if 'space' in str(type(connected_comp)):
                    comp_powers = np.append(comp_powers, space_powers[connected_comp.name])
    #    print(comp.name+': ' + str(comp_powers))
        comps_powers[comp.name] = comp_powers.min()
        comp_coating_power[comp.name] = comp_powers.max()
    #time_diff=time.time()-curr_time
    #print(f"Time8: {time_diff}sec")
    #curr_time=time.time()    
    for comp in beamsplitters:
        comp_powers = np.array([])
        for node in comp.nodes:
            connected_comps = np.array(node.components)
            if connected_comps[connected_comps!=comp][0] is None:
                comp_powers = np.append(comp_powers, 0)
            for connected_comp in connected_comps[connected_comps!=comp]:
                if 'space' in str(type(connected_comp)):
                    comp_powers = np.append(comp_powers, space_powers[connected_comp.name])
                    
        comp_coating_power[comp.name] = comp_powers.max()           
        if comp_powers[0:2].max()<comp_powers[2:4].max():
            comps_powers[comp.name] = comp_powers[0:2].max()
        else:
            comps_powers[comp.name] = comp_powers[2:4].max()   
    #time_diff=time.time()-curr_time
    #print(f"Time9: {time_diff}sec") 
    #curr_time=time.time()

    # Computing the transmission power loss
    all_powers = [value for value in comps_powers.values()]
    loss_all_PowerElements = [500 * logistic.cdf(5 * (x - 2000)) for x in all_powers]
    lossPowerElements=sum(loss_all_PowerElements)
    
    # Computing the photo detector loss
    all_poutdc = [np.abs(outALigo["poutdc1"][0]), np.abs(outALigo["poutdc2"][0])]  
    loss_all_PowerPD=[100*logistic.cdf(7500*(poutdc - 10**-2)) for poutdc in all_poutdc]
    lossPowerPD=sum(loss_all_PowerPD)
    
    # Computing the photo detector loss
    all_coating = [value for value in comp_coating_power.values()]
    loss_all_coating = [500 * logistic.cdf(0.001 * (x - 3.5e6)) for x in all_coating]
    lossPowerCoating=sum(loss_all_coating)
    #time_diff=time.time()-curr_time
    #print(f"Time10: {time_diff}sec")    
    #delete_temp_files(tempdir=tempdir, tempname=tempname)

    #print(f' - lossPowerElements={lossPowerElements}\n - lossPowerPD={lossPowerPD}\n - lossPowerCoating={lossPowerCoating}')
    
    return freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, poutf_m


def compute_baseline_aligo(freq_info,baseline_file="geo_voyager_pure10.kat", log_file='log.txt', use_classical_noise=True):
    file1 = open(baseline_file, "r")
    readfile = file1.read()
    file1.close()
    did_succeed=False
    loss=666.42
    error_count=0
    while (not did_succeed) and (error_count<5):
        try:
            freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, total_signal=compute_strain(freq_info, kat_string=readfile, use_classical_noise=use_classical_noise)
            did_succeed=True
        except:
            print('problem with compute_baseline_aligo in geo_aLIGO10.py_3')
            print_file(['problem with compute_baseline_aligo in geo_aLIGO10.py_3, ', log_file], file=log_file)
            time.sleep(0.1)
            error_count+=1
    return freq, SSens, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise, total_signal

if __name__ == "__main__":
    freq_info=[800,3000,100]
    use_classical_noise=False
    freq_aligo, strain_aligo, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aLIGO, totalnoise, total_signal = compute_baseline_aligo(freq_info)
    #fn=os.path.join('results', 'BFGS_4_parsed_voyager.txt')
    #fn=os.path.join('aLIGOBaseline','CFGS_3_666.42_145_123456789_26720_3236194047.txt')
    
    #fn=os.path.join('results','CFGS_2_-23.65_72_7051608975_14237_8549804110_simplified_simplified_withFilter.txt')
    fn='CFGS_1_666.42_94_1732047184_0_4468576964.txt'
    file1 = open(fn, "r")
    readfile = file1.read()
    file1.close()

    #loss=get_loss_from_file(fn, freq_info, log_file='log.txt', use_classical_noise=True)
    loss=get_loss_from_katstr(readfile, freq_info, log_file='log.txt', use_classical_noise=True)
    print(loss)