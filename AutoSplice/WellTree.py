import os
import lasio
import numpy as np
from categorize_v2 import LogCategorize

class WellsParent():
    def __init__(self,parent_path):
        self.parent_path=parent_path
        self.well_folders=[]
        for filename in os.listdir(self.parent_path): 
            if os.path.isdir(self.parent_path+filename):
                self.well_folders.append(filename)
        
    def getWellLas(self,extensions=['.las','dlis','.lis']):
        self.wfiles={}
        for wname in self.well_folders:
            self.wfiles[wname]={}
            for root,folder,files in os.walk(self.parent_path+wname):
                for file in files:            
                    if len(file)>4:
                        if file[-4:].lower() in extensions:
                            if (file[-4:].lower()=='dlis'):
                                if file[-5:].lower() =='.dlis':
                                    self.wfiles[wname][file]= os.path.join(root,file)
                            else:
                                self.wfiles[wname][file]=os.path.join(root,file)
        return self.wfiles
    def LookgetWellLas(self,extensions=['.las']):
        self.wfiles={}
        for wname in self.well_folders:
            self.wfiles[wname]={}
            for root,folder,files in os.walk(self.parent_path+wname):
                # print(root)
                # for fld in folder:
                rootfolders=root.split('\\')
                # rootfolders=root.split('\\')
                # print(rootfolders)
                # print(wname)
                if (rootfolders[-1].lower()=='las')&(rootfolders[-2]==wname):
                    # print(rootfolders)
                    # print(root)
                    for file in files:            
                        if len(file)>4:
                            if file[-4:].lower() in extensions:
                                if (file[-4:].lower()=='dlis'):
                                    if file[-5:].lower() =='.dlis':
                                        self.wfiles[wname][file]= os.path.join(root,file)
                                else:
                                    self.wfiles[wname][file]=os.path.join(root,file)
        return self.wfiles
    def limitwitMinNfiles(self,nfiles):
        newwfiles={}
        if self.wfiles:
            for key in self.wfiles:
                if len(self.wfiles[key])>=nfiles:
                    newwfiles[key]= self.wfiles[key]
            self.wfiles=newwfiles
            return self.wfiles
        else:
            self.getWellLas(extensions=['.las','dlis','.lis'])
            self.limitwitMinNfiles(nfiles)

    def get_wells_withfiles(self):
        wnames=[]
        fnames=[]
        fpaths=[]
        for wf in self.wfiles:
            wnames.append(wf['wellname'])
            fnames.append(wf['file'])
            fpaths.append(wf['parent_path'])
        wnames=np.array(wnames)
        uwellnames=np.unique(wnames)
        print(uwellnames)
        fnames=np.array(fnames)
        for uwn in uwellnames:
            print(fnames[np.where(wnames==uwn)[0]])

def isitWireline(file_path):
    if(file_path[-4:].lower()=='.las'):
        try:
            las=lasio.read(file_path,ignore_data=True)
            if 'OPMD' in las.header['Parameter'].keys():
                if las.header['Parameter']['OPMD']['value']=='OH.WIRE':
                    return 1
            else:
                return 0
        except:
            print('Unable to read las file.....')
            return 2
    else:
        print(file_path.split('\\')[-1],' is not a las file')
        return 3
def count_filetypes(files):
    lascount=dliscount=liscount=0
    for f in files:

        if f[-4:].lower()=='.las':
            lascount +=1
        elif f[-4:].lower()=='dlis':
            dliscount +=1
        else :
            liscount +=1
    
    return lascount,dliscount,liscount
def getCategDepthrange(lc,file_w_path):
    las=lasio.read(file_w_path,ignore_data=True)    
    lc.set_las(las)
    lc.lasCategorize()
    return lc.get_catePresent(),lc.get_lasdepthrange()
def getLasAttr4wells(well_las_dict,mnomonicsfile):
    well_las_attr_dict={}
    lc=LogCategorize(mnomonicsfile)
    for well in well_las_dict:
        print('Getting attributes for well: ',well)
        well_las_attr_dict[well]={}
        for lf in well_las_dict[well]:
            well_las_attr_dict[well][lf]={}
            a,b=[],(0,0)
            try:
                a,b=getCategDepthrange(lc,well_las_dict[well][lf])
            except:
                print('unable to pasrse ', well)
            well_las_attr_dict[well][lf]['categories']=a
            well_las_attr_dict[well][lf]['depthrange']=b
            well_las_attr_dict[well][lf]['path']=well_las_dict[well][lf]
    return well_las_attr_dict
if __name__=='__main__':
    # # well_folders_parent_path='I:\\10. Database\\WELL\\Well Data\\Well_Data\\'
    # well_folders_parent_path='\\172.16.165.171\Team_DM\OALP\5829_WELLDATA\\'
    # # upaths_level_wise[5]
    
    parent_path=r'\\172.16.165.171\Team_DM\Well_Data\\'
    mnomonicsfile=r'E:\Data\mnemonics_revised.txt'

    parent_path=r'D:\Ameyem Office\Projects\Cairn\\'
    mnomonicsfile=r'D:\Ameyem Office\Projects\Cairn\mnemonics_revised.txt'
    lf=WellsParent(parent_path)
    well_las_dict=lf.LookgetWellLas(extensions=['.las'])
    # print(well_las_dict)
    print('Well dict size before limit : ',len(well_las_dict))
    well_las_dict=lf.limitwitMinNfiles(2)
    np.save('well_las_dict.npy',[well_las_dict])


    # well_las_dict=np.load('well_las_dict.npy')[0]
    print('Well dict size after limit : ',len(well_las_dict))

    
    well_las_attr_dict=getLasAttr4wells(well_las_dict,mnomonicsfile)
    np.save('well_las_attr_dict.npy',[well_las_attr_dict])

#     well_las_attr_dict=np.load('well_las_attr_dict.npy')[0]

# for i,well in enumerate(well_las_attr_dict):
#     print(i,well)
#     for lf in well_las_attr_dict[well]:
#         # print(well_las_attr_dict[well][lf]['depthrange'])
#             # well_las_attr_dict[well][lf]={}
#         print('      {:>25} : {:4.1f}-{:4.1f} , {:>15}'.format(lf,min(well_las_attr_dict[well][lf]['depthrange']),max(well_las_attr_dict[well][lf]['depthrange']),
#         ', '.join(well_las_attr_dict[well][lf]['categories'])))
#     # print(well_las_dict)
    
    # for well in well_las_dict:  
    #     lascount,dliscount,liscount=count_filetypes(list(well_las_dict[well]))  
    #     print('{}: Las: {} | lis: {} | dlis: {}'.format(well,*count_filetypes(list(well_las_dict[well]))))

    # well_folder=r'D:\Ameyem Office\Projects\Cairn\W1\LAS\\'
    # files_w_path=well_folder+'W1_SUITE2_COMPOSITE.las'
    # mnomonicsfile=well_folder+'../../mnemonics_revised.txt'

    # well_folder=r'E:\Data\W1\LAS\\'
    # files_w_path=well_folder+'W1_SUITE2_COMPOSITE.las'
    # mnomonicsfile=well_folder+'../../mnemonics_revised.txt'

    # # las=lasio.read(files_w_path)

    # # print(lc.treeview_dict)
    # print(lc.get_catePresent())
    # print( lc.get_lasdepthrange())



    # print( lc.get_curverange('CAL'))
    # lcates=lc.get_catePresent()
    # for l in lcates:
    #     for key in lc.treeview_dict[l]:
    #         print('{}: {}'.format(key, lc.get_curverange(key)))