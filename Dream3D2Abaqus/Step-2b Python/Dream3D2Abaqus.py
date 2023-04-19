######################
# VERSION 3 OF DREAM 3D TO ABAQUS 
#MADE BY ALVARO MARTINEZ
# DPhil student of the Oxford Engineering Department
#Any questions email to alvaro.martinezpechero@eng.ox.ac.uk
#####################



import numpy as np
import pandas as pd

def Dream3D2Abaqus(filename,matID,noDepvar):
    with open(filename + '.vox', 'r') as f:
        raw_data = np.genfromtxt(f, delimiter=' ')
    euler = raw_data[:, :3]
    xyz = raw_data[:, 3:6]
    grains = raw_data[:, 6].astype(int)
    phases = raw_data[:, 7].astype(int)

    total_els=len(euler[:,1])
    #print(total_els)
    
    materials = np.ones(total_els, dtype=int)*matID
    
    grain_order, grain_record = np.unique(grains, return_index=True)
    phase_order = phases[grain_record]
    
    material_order = materials[grain_record]
    
    euler_angle1 = euler[grain_record, 0]
    euler_angle2 = euler[grain_record, 1]
    euler_angle3 = euler[grain_record, 2]
    
    
    
    with open(f"{filename}_nodes.inp", "r+") as fid:
        indata = fid.readlines()[4:-4]
        indata = [line.strip().split(",") for line in indata]
        indata = [[float(x[0]), float(x[1]), float(x[2]), float(x[3])] for x in indata]

    nodes = np.array(indata)
    nodes = nodes[:]
    


    with open(filename + '_elems.inp', 'r') as f:
        elem = np.genfromtxt(f, delimiter=',', skip_header=4, skip_footer=3)
    #print(elem.shape)
        
    #return euler, xyz, grain_order, phase_order, euler_angle1, euler_angle2, euler_angle3, nodes, elem

    ## Write the overall element and node sets to input file
    # open inp file and write keywords 
    with open(f"{filename}.inp", 'wt') as inp_file:
        inp_file.write("** Generated by: Dream3DtoAbaqus.m\n")
        inp_file.write("**PARTS\n**\n")
        inp_file.write("*Part, name=DREAM3D\n")

        # write nodes
        inp_file.write("*NODE\n")
        for node in nodes:
            inp_file.write(f"{int(node[0])},\t{'{:.6e}'.format(node[1])},\t{'{:.6e}'.format(node[2])},\t{'{:.6e}'.format(node[3])}\n")
            #inp_file.write(f"{int(node[0])},\t{node[1]},\t{node[2]},\t{node[3]}\n")
            
        # write elements
        inp_file.write("*Element, type=C3D8\n")
        for elementj in elem:
            inp_file.write(f"   {int(elementj[0])},   {int(elementj[1])},   {int(elementj[2])}   ,{int(elementj[3])}   ,{int(elementj[4])},   {int(elementj[5])}   ,{int(elementj[6])}   ,{int(elementj[7])}   ,{int(elementj[8])}\n")

        unique_grains = np.unique(grains)
        
        
        numels_total=[]
 
        inp_file.write("\n")

        for ii in range(len(unique_grains)):
            inp_file.write(f"*Elset, elset=GRAIN-{grain_order[ii]}\n")
            grain_elements = elem[grain_order[ii]]
            for ee in range(0,len(elem[grains == grain_order[ii]][:,0]),9):
                inp_file.write(", ".join(str(int(e)) for e in elem[grains == grain_order[ii]][ee:ee+9,0]) + "\n")
            numels = 0
            for tt in range(len(grain_elements)):
                numels += 1

            
                 
            
        uniPhases = np.unique(phases)
        for ii in range(len(np.unique(phases))):
            inp_file.write(f"\n*Elset, elset=Phase-{ii + 1}\n")        
            elem_for_ii = elem[phases == uniPhases[ii]]
            for ee in range(0,len(elem_for_ii[:,0]),9):
                inp_file.write(", ".join(str(int(e)) for e in elem_for_ii[ee:ee+9,0]) + "\n")
            #for tt in range(elem_for_ii.shape[0]):
                #inp_file.write(f"{elem_for_ii[tt, 0]}, {elem_for_ii[tt, 1]}, {elem_for_ii[tt, 2]}, {elem_for_ii[tt, 3]}, {elem_for_ii[tt, 4]}, {elem_for_ii[tt, 5]}, {elem_for_ii[tt, 6]}, {elem_for_ii[tt, 7]}, {elem_for_ii[tt, 8]}\n")

                
        for ii in range(len(grain_order)):
            inp_file.write("\n**Section: Section_Grain-%d\n" % grain_order[ii])
            inp_file.write("*Solid Section, elset=GRAIN-%d, material=MATERIAL-GRAIN%d\n" % (grain_order[ii], grain_order[ii]))
            inp_file.write(",\n")
            
            
            
            
        # Write the closing keyword
        inp_file.write("*End Part\n")

        # Write the assembly information
        inp_file.write("**\n**ASSEMBLY\n**\n")
        inp_file.write("*Assembly, name=Assembly\n**\n")
        inp_file.write("*Instance, name=DREAM3D-1, part=DREAM3D\n")

        # Write the nodes
        inp_file.write("*NODE\n")
        for i in range(nodes.shape[0]):
            inp_file.write(f"{int(nodes[i, 0])},\t{'{:.6e}'.format(nodes[i, 1])},\t{'{:.6e}'.format(nodes[i, 2])},\t{'{:.6e}'.format(nodes[i, 3])}\n")
            #inp_file.write("%d, %.2f, %.2f, %.2f\n" % (i+1, nodes[i, 1], nodes[i, 2], nodes[i, 3]))            


        # Write the elements
        inp_file.write("*Element, type=C3D8\n")
        for i in range(elem.shape[0]):
            inp_file.write("%d, %d, %d, %d, %d, %d, %d, %d, %d\n" % (i+1, elem[i, 1], elem[i, 2], elem[i, 3], elem[i, 4], elem[i, 5], elem[i, 6], elem[i, 7], elem[i, 8]))

        inp_file.write('\n*End Instance\n')
        inp_file.write('**\n')
        inp_file.write('*End Assembly\n**MATERIALS\n**\n')
        
        #import material parameters to be used in the development of materials
        #for each grain.
        df = pd.read_excel('PROPS.xlsx', sheet_name='Material_parameters', usecols="A", header=None)
        A16 = np.array(df.iloc[0:6, :])
        #print(A19)
        
        # Flag for reading the inputs from the file or material library
        # "0": material library in usermaterial.f will be used
        # "1": use the material parameters in excel file       
        
        if A16[5] == 0:
            A = [""] * 6

            A[5] = 0 #CHANGE HERE
            noPROPS = 6
            
        # Flag for reading the inputs from the file or material library
        # "0": material library in usermaterial.f will be used
        # "1": use the material parameters in excel file              

        else:
            A = [""] * 250

            A[5] = 1
            noPROPS = 250

        
        

        for ii in range(len(grain_order)):
            inp_file.write("\n*Material, name=MATERIAL-GRAIN%d" % grain_order[ii])
            inp_file.write(f"\n*Depvar\n{noDepvar},")
            inp_file.write(f"\n*User Material, constants={noPROPS}\n")

            A[0:3] = [euler_angle1[ii], euler_angle2[ii], euler_angle3[ii]]
            A[3] = grain_order[ii]
            
            # If a non-zero material-ID defined by user
            if matID>0:
                A[4] = material_order[ii]
            else:
                A[4] = phase_order[ii]

            if A16[5] ==1:
                for iph in uniPhases:
                    letter = chr(iph + 64)
                    xlRange = f"{letter}1:{letter}250"#CHANGE
                    df = pd.read_excel("PROPS.xlsx", sheet_name='Material_parameters', usecols="A", header=None)
                    B = np.array(df.iloc[0:251, :]).flatten()
                    #print(B)
                    #B=tolist(B)
                    
                    nslip = B[6]
                    # All parameters
                    A[6:251] = B[6:251]
                    

            #print(A)
            for i in range(0, len(A), 8):
                inp_file.write(",".join(str(x) for x in A[i:i+8]) + "\n")
                
            #inp_file.write("{}, {}, {}, {}, {}, {}, {}, {}, {},".format(*A))

        inp_file.write("\n**")
        inp_file.write("\n**\n** STEP: Loading\n**\n*Step, name=Loading, nlgeom=YES, inc=10000\n*Static\n0.01, 10., 1e-05, 1.")
        inp_file.write("\n**\n** OUTPUT REQUESTS\n**")
        inp_file.write("\n*Restart, write, frequency=0\n**")
        inp_file.write("\n** FIELD OUTPUT: F-Output-1\n**\n*Output, field, variable=PRESELECT\n**")
        if noDepvar>0:
            inp_file.write("\n** FIELD OUTPUT: F-Output-2\n**\n*Element Output, directions=YES\nSDV,\n**")
        inp_file.write("\n** HISTORY OUTPUT: H-Output-1\n**\n*Output, history, variable=PRESELECT\n**")
        inp_file.write("\n*End Step")

    inp_file.close()

    return  


 