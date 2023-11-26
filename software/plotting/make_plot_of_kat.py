import copy
import sys, getopt
from pdfrw import PdfReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from pykat import finesse                 # Importing the pykat.finesse package
import numpy as np          
from PlotIFO_helper_functions import *



######################################## Main ####################################

def main(argv):
    
    inputfile = ''
    outputfile = ''
    parseUIFO = False
    threshold = 0
    simplify = False
    simpfilename = ''
    shotransparentoptic = 0
    disablelabels = False
    simplifyfast = False
    
    helpmsg = '''plotsolution_SQZ_filtered_vacuum_and_LO_wText.py -i <inputfile> [-o <outputfile>] [-p] [-s filename] [-k] [-t threshold] [-x] [-f value]
                
                optional arguments:
                    -h, --help      Show this help message and exit.
                    -p, --parse     Parse a UIFO kat file.
                    -s, --simplify  Simplify the kat file. Output simplified kat to file.
                    -k, --fastsimpl Simplify the kat file using quantum noise only. Output is specified in -s option.
                    -t, --threshold Score threshold for eliminating an element in simplifying algorithm.
                    -f, --showtrans 0. Don't show optics with 100% transmission 1. Show 2. Show semi transparent
                    -x, --labelsoff Turn off labels
    '''
    try:
        opts, args = getopt.getopt(argv,"hi:o:ps:t:f:xk",["ifile=","ofile=","parse","simplify=", "threshold=", "showtrans=", "labelsoff", "fastsimpl"])
    except getopt.GetoptError:
        print(helpmsg)
        sys.exit(2)    
      
    for opt, arg in opts:
        if opt == '-h':
            print(helpmsg)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--parse"):
            parseUIFO = True
        elif opt in ("-s", "--simplify"):
            if '-k' in [op1 for op1,_ in opts]:
                simplifyfast = True
            simplify = True
            simpfilename = arg
        elif opt in ("-t", "--threshold"):
            try:
                threshold = float(arg)
            except getopt.GetoptError:
                print(helpmsg)
                sys.exit(2)
        elif opt in ("-f", "showtrans"):
            shotransparentoptic = arg
        elif opt in ("-x", "labelsoff"):
            disablelabels = True
            
    import os
    abspath1=os.path.dirname(inputfile)
    if len(abspath1)==0:
        abspath=''
    else:
        abspath = os.path.dirname(inputfile)+'/'
    
    print(inputfile)
    file1 = open(inputfile, "r")
    readfile = file1.read()
    file1.close()
    katstartidx = readfile.find("const")
    if katstartidx==-1: katstartidx=0
    # if readfile.split('\n')[-1].split(' ')[-1]=='log':
    #     readfile = readfile[:] + ' 5 2e4 500'
    log_ind = readfile.find('log')
    if (len(readfile) - log_ind)<10:
        readfile = readfile[:log_ind+3] + ' 5 2e4 500\n'
    kat = finesse.kat()
    kat.parse(readfile[katstartidx:], preserveConstants = True)
    
    if simplify:
        import matplotlib.pyplot as plt
        out_orig = kat.run()
        sens_orig = CalculateBHDSens(out_orig)
        plt.loglog(out_orig.x, sens_orig,label='original')
        katxaxislimits = copy.deepcopy(kat.xaxis.limits)
        oldsteps = kat.xaxis.steps
        
        target=int(os.path.basename(inputfile)[5])
        if target == 0:
            f_start, f_end = [30,1000] # normal BH
            pltname='normal BH'
        elif target == 1:
            f_start, f_end = [2000, 3300] #[2700,3300] # merger
            pltname = 'merger'
        elif target == 2:
            f_start, f_end = [200,1000] # supernova  
            pltname='supernova'
        elif target == 3:
            f_start, f_end = [10,30] # cosmology   
            pltname='cosmology'
        elif target == 4:
            f_start, f_end = [30,5000] # broadband   
            pltname='broadband'
        elif target == 5:
            f_start, f_end = [10,5000] # ultrabroadband   
            pltname='ultrabroadband'
        elif target == 6:
            f_start, f_end = [2000,3000] # ultrabroadband   
            pltname='merger2'
        elif target in [7,8]:
            f_start, f_end = [800,3000] # ultrabroadband   
            pltname='merger3'
        elif target == 9:
            f_start, f_end = [10,30] # ultrabroadband   
            pltname='merger3'
        kat = KatCleanup(kat, threshold, f_start = f_start, f_end = f_end , pt_no = 10, fast = simplifyfast)
        for compname in kat.components:
            comp = kat.components[compname]
            if all([not node.isConnected() for node in comp.nodes]):
                comp.remove()
        kat.xaxis.limits = katxaxislimits
        kat.xaxis.steps = oldsteps
        out_new = kat.run()
        sens_new = CalculateBHDSens(out_new)
        plt.loglog(out_new.x, sens_new,label='simplified')
        plt.legend()
        # print("".join(kat.generateKatScript()))
        
        if simpfilename == '':
            simpfilename = inputfile[:-4]+'_simplified.txt'
            #simpfilename = 'simplified_kat.txt'
        with open(simpfilename, 'w') as f:
            print('Removing unsused constants for auto-optimization...')
            import re
            katscript = "".join(kat.generateKatScript())
            consts4removal = [const for const in kat.constants if len(re.findall(const, katscript))<2]
            for const in consts4removal: 
                kat.constants[const].remove()
            kattemp = kat.deepcopy()
            kattemp.xaxis.remove()
            katlines = kattemp.generateKatScript()
            katlines.append('xaxis '+kat.xaxis.getFinesseText()[0].split(' ')[1]+' f log\n')
            kattext = "".join(katlines)
            # for old in old_new_dict:
            #     new = old_new_dict[old]
            #     kattext = kattext.replace(old,new)
            f.write(kattext)
            
    old_new_dict = {}
    if parseUIFO:
        kat = ParseUIFOkat(kat, 6, ['BSfin', 'L_LO', 'BSDet', 'DetLO'], old_new_dict) #Comment out when parsing regular solutions
        # 
        kat =  FixDetectorCode(kat, 'sToDetector', 'BSDet', 2, old_new_dict)
        # kat =  FixDetectorCode(kat, 'sToDetector', 'B_finBSref1', -2, old_new_dict)
        kat =  FixDetectorCode(kat, 'SFI2', 'B_finBSref2', old_new_dict=old_new_dict)
        kat =  FixDetectorCode(kat, 'SFI1', 'F_finDBS', old_new_dict=old_new_dict)
        kat =  FixDetectorCode(kat, 'sqToDBS2', 'BSfin', old_new_dict=old_new_dict)
#        kat =  FixDetectorCode(kat, 'sfinS2', 'BSfin', -3, old_new_dict, previous_comp_ind = 0)
        kat =  FixDetectorCode(kat, 'sfinS2', 'B_finBSref1', 3, old_new_dict)
        # kat =  FixDetectorCode(kat, 'sqToDBS2', 'B_finBSref1', 3, old_new_dict)
#        kat =  FixDetectorCode(kat, 'sfinS3', 'F_finDBS', 3, old_new_dict, previous_comp_ind = 0)
        kat =  FixDetectorCode(kat, 'sfinS3', 'B_finBSref2', 3, old_new_dict)
        
        kat =  FixDetectorCode(kat, 'SrNodes4', old_new_dict=old_new_dict)
        kat =  FixDetectorCode(kat, 'SrNodes5', old_new_dict=old_new_dict)
        
        kat =  FixDetectorCode(kat, 'SArmU', 'mAtArmU', old_new_dict=old_new_dict, replace_comp='M')
        kat =  FixDetectorCode(kat, 'SArmR', 'mAtArmR', old_new_dict=old_new_dict, replace_comp='M')
        kat =  FixDetectorCode(kat, 'sToLO', 'DetLO', old_new_dict=old_new_dict, replace_comp='L')

    kat  = FixDetectorCode(kat, 'stoPD1', no_of_grid_points=-1, old_new_dict=old_new_dict)
    kat  = FixDetectorCode(kat, 'stoPD2', no_of_grid_points=1, old_new_dict = old_new_dict)  
    # kat  = FixDetectorCode(kat, 'SDet', no_of_grid_points=1, old_new_dict = old_new_dict)
    kat  = FixDetectorCode(kat, 'SDet1', no_of_grid_points=-1, old_new_dict=old_new_dict)
    kat  = FixDetectorCode(kat, 'SDet2', no_of_grid_points=1, old_new_dict = old_new_dict) 
    kat  = FixDetectorCode(kat, 'sToDet1', no_of_grid_points=-1, old_new_dict=old_new_dict)
    kat  = FixDetectorCode(kat, 'sToDet2', no_of_grid_points=-1, old_new_dict = old_new_dict)
    # kat = MakeSpacesUniform(kat)
    # print("".join(kat.generateKatScript()))
    #print(old_new_dict)
    if outputfile == '': 
        outputfile = inputfile[:-4]+'_Plot.pdf'
    outputfilename = outputfile
    #with open('test.txt', 'w') as f:
    #    f.write(''.join(kat.generateKatScript()))
    #Prepare component images
    comp_dir = 'Components'#/Mirror.pdf
    comp_filenames = ['Mirror', 'BS', 'Laser', 'PD', 'Squeezer', 'FI']
    comp_T_filenames = ['Mirror_T', 'BS_T', 'Laser_T', 'PD_T', 'Squeezer_T', 'FI_T']
    comp_type_names = ['M','B','L', 'P', 'Q', 'F']
    comp_paths = [comp_dir+'/'+filename+'.pdf' for filename in comp_filenames]
    pagess = [PdfReader(comp_path).pages[0] for comp_path in comp_paths]
    comp_paths = [comp_dir+'/'+filename+'.pdf' for filename in comp_T_filenames]
    pagess_T = [PdfReader(comp_path).pages[0] for comp_path in comp_paths]
    comp_F_dict = dict(zip(comp_type_names, pagess))
    comp_T_dict = dict(zip(comp_type_names, pagess_T))
    comps_cors = []
    spaces_cors = []
    
    #Calculate coordinates of all components on the pdf page
    # space_powers = ComputeSpaceSignals(kat, 200)
    try:
        space_powers = ComputeSpacePowers(kat)
    except:
        return
    #print(space_powers)
    #Get detector name
    for detector_name in [comp_name for comp_name in kat.components if comp_name.find("P")==0]:
    # detector_name = [comp_name for comp_name in kat.components if comp_name.find("P")==0][0]
        PopulateCors(kat, detector_name, None, np.array([0,0]), space_powers, comps_cors, spaces_cors, comp_stack=[], node_stack=[])
        LaserFound=False
        for comp_cor_dict in comps_cors:
            if comp_cor_dict['compname'][0]=='L':
                LaserFound=True
                break
        if LaserFound:
            break
    for comp_cors in comps_cors:
        if getComponentCoordinates(comp_cors['compname']) is None:
          comps_cors.remove(comp_cors)
          
    #Since the distances are shown logarithmicly some components and spaces which should have been aligned
    #, have coordinates that are misaligned. AlignComponents fixes this.
    [comps_cors, space_cors] = AlignComponents(comps_cors, spaces_cors)
    
    #Fit pdf page to content
    cors = np.array([comp_cors['cor'] for comp_cors in comps_cors])
    mincors = cors.min(axis=0)
    maxcors = cors.max(axis=0)
    canvas = Canvas(outputfilename, pagesize=tuple((maxcors-mincors + [1,1])*inch))
    #canvas = Canvas(outputfilename, pagesize=tuple((30, 30))
    
    spaces_cors_fitted = copy.deepcopy(spaces_cors)
    comps_cors_fitted = copy.deepcopy(comps_cors)
    #print(comps_cors)
    for space_cors in spaces_cors_fitted:
        space_cors['cor'] = space_cors['cor'] - mincors + [0.5, 0.5]
        space_cors['nextcor'] = space_cors['nextcor'] - mincors + [0.5, 0.5]
        DrawSpace(space_cors, space_powers[space_cors['spacename']], kat.components[space_cors['spacename']].L.value, canvas, disablelabels)
    
    for comp_cors in comps_cors_fitted:
        comp_dict = comp_F_dict
        [comp_name, cor, orient] = list(comp_cors.values())
        
        if comp_name[0] in ['B', 'M'] and hasattr(kat.components[comp_name],'T'):
            if kat.components[comp_name].T.value==1:
                if shotransparentoptic==0:
                    continue
                if shotransparentoptic==2:
                    comp_dict = comp_T_dict
        
        if comp_name[0]=='L' and hasattr(kat.components[comp_name],'P'):
            if kat.components[comp_name].P.value==0:
                if shotransparentoptic==0:
                    continue
                if shotransparentoptic==2:
                    comp_dict = comp_T_dict
        
        if comp_name[0]=='Q' and hasattr(kat.components[comp_name],'db'):
            if kat.components[comp_name].db.value==0:
                if shotransparentoptic==0:
                    continue
                if shotransparentoptic==2:
                    comp_dict = comp_T_dict
                    
        comp_cors['cor'] = comp_cors['cor'] - mincors + [0.5, 0.5]
        comp = kat.components[comp_cors['compname']]
        DrawComp(kat, comp_cors, canvas, comp_dict, old_new_dict, disablelabels)  
    
    
    canvas.save()

def make_plot_kat(kat_file, pdf_file):
    
    ### Change scripts parameters here
    
    input_file = kat_file
    output_file = pdf_file 
    parse_UIFO = True
    simplify = False
    simplified_filename = ''
    simplify_fast = True # True for quantum noise calculation only.
    simplifier_thresh = -0.2
    showtrans = 0
    disablelabels = False
    
    ### End of script parameters
    
    sys.argv = ['plotsolution_SQZ_filtered_vacuum_and_LO_wText.py'
            , '-i', input_file, '-o', output_file, '-t', simplifier_thresh, '-f', showtrans]
    
    if simplify:
        sys.argv.append('-s')
        sys.argv.append(simplified_filename)
    
    if parse_UIFO:
        sys.argv.append('-p')
    
    if simplify_fast:
        sys.argv.append('-k')
        
    if disablelabels:
        sys.argv.append('-x')

    main(sys.argv[1:])




if __name__ == "__main__":
    make_plot_kat('example_setup.kat', 'setup.pdf')