import matplotlib.pyplot as plt
import numpy as np
def str_array2floats(strarray):
    floats=[]
    for s in strarray:
        try:
            floats.append(float(s))
        except:
            floats.append(s)
    return np.array(floats)
def find_keyIndxWithStr(log,string):
    found=False
    indx=-999
    for i,key in enumerate(log.keys()):
        if string in key:
            found=True
            indx=i
            break
    
    return found,indx
def find_depth_indx(log):
    found,indx=find_keyIndxWithStr(log,'DEPT')
    if not found:
        found,indx=find_keyIndxWithStr(log,'TVD')
    if not found:
        print('Depth collumn not found with existing tokens. Refine token in find_depth_indx function...')
    return indx

# log=las[0]
def find_prop_indexes(log):
    propindxs=[]
    for i,key in enumerate(log.keys()):
        if (key not in ['TIME', 'DATE']) & ('DEPT' not in key):
#             print(log.curves[i].data)
            propindxs.append(i)
    return np.array(propindxs)


def get_allcols(log):
    lindx2bplotted=find_prop_indexes(log)
    allcols=log.keys()
    allcols=np.array(allcols)
    allcols=allcols[lindx2bplotted]
    ncols=len(allcols)
    n4divcols=4*int(ncols/4)
    excesscols=allcols[n4divcols:]
    allcols=allcols[:n4divcols]
    allcols.shape=(4,n4divcols/4)
    allcols=list(allcols)
    for i,e in enumerate(excesscols):
        allcols[i]=np.append(allcols[i],e)
    return allcols

class LogPlot():
    def __init__(self,ncols=1,vert_size=60):
        self.ax=[]
        self.colors=['#800000',	'#008080','#000080','#FF00FF','#800080','#00FFFF','#FFFF00','#FF0000','#00FF00','#008000','#0000FF','#808000','#C0C0C0','#D3D3D3',]
        fig, self.ax = plt.subplots(nrows=1, ncols=ncols, figsize=(3*ncols,vert_size), sharey=True)
        fig.subplots_adjust(top=0.75,wspace=0.1)
        plt.gca().invert_yaxis()
        # self.ax[0].invert_yaxis()

    def basicPlot(self,ax,depth,prop,lcolor='#800000'):
        ax.get_xaxis().set_visible(False) 
        ax.twiny()
        ax.plot( prop,depth, label='keycol', color=lcolor)
        
        # ax.yaxis.grid(True)
        
        ax.set_title('Keys',verticalalignment='top')
        ax.spines['top'].set_position(('outward',0))  
        
        ax.set_xlabel('keycol',color=lcolor) 
        
        ax.tick_params(axis='x', colors=lcolor)
        ax.set_xlim(min(prop),max(prop))
        ax.grid(True)
        ax.invert_yaxis()
    def las_plot(self,single_las,keysets):
        if len(keysets)<1:
            print('Please imput the keys you want to plot')
        dcol=single_las.keys()[find_depth_indx(single_las)]
        depth_col=str_array2floats(single_las[dcol])
        for i,keys in enumerate(keysets):
            for key in keys:
                try:
                    keycol=single_las.keys()[find_keyIndxWithStr(single_las,key)[1]]
                    log_col=str_array2floats(single_las[keycol])            
                    self.basicPlot(self.ax[i],depth,log_col,lcolor=self.colors[i])
                except:
                    pass

    def key_plot(las,key):
        j=0
        for l in las:
            dcol=l.keys()[find_depth_indx(l)]
            print(find_keyIndxWithStr(l,key))            
            try:
                keycol=l.keys()[find_keyIndxWithStr(l,key)[1]]
                log_col=str_array2floats(l[keycol])
                depth_col=str_array2floats(l[dcol])
                basicPlot(self.ax[0],depth_col,log_col,lcolor=self.colors[0])
                # ax.plot( log_col,depth_col, label=keycol, color=colors[j])
                j +=1
            except:
                pass

        return log_col

def log_plot4(log,top_depth,bottom_depth):
    dcol=log.keys()[find_depth_indx(log)]
    allcols=get_allcols(log)
    
    cols=log.keys()
    df=log.df().sort_values([dcol])
    log.set_data(df)
    
    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(12,60), sharey=True)
#     fig.suptitle("Well Composite", fontsize=22)
    fig.subplots_adjust(top=0.75,wspace=0.1)

    #General setting for all axis
    for axes in ax:
        axes.set_ylim (top_depth,bottom_depth)
        axes.invert_yaxis()
        axes.yaxis.grid(True)
        axes.get_xaxis().set_visible(False) 

    colors=['#800000',		'#008080',		'#000080',	'#FF00FF',	'#800080',	'#00FFFF',	'#FFFF00','#FF0000',	'#00FF00',	'#008000',	'#0000FF','#808000','#C0C0C0','#D3D3D3',]
    
    axx=[]
    i=0
    axid=0
    depth_col=str_array2floats(log[dcol])
    for cols in allcols:
        out_pos=j=0
        ax[axid].set_title('.las file',verticalalignment='top')
        for c in cols:
            axx.append(ax[axid].twiny())
            axx[i].plot( str_array2floats(log[c]),depth_col, label=c, color=colors[j])
            axx[i].spines['top'].set_position(('outward',out_pos))
            axx[i].set_xlabel(c,color=colors[j])    
            axx[i].tick_params(axis='x', colors=colors[j])
            axx[i].grid(True)
            out_pos += 30
            i +=1
            j +=1
        axid +=1
def segregate_files(files,filetypes):
    # initiate  type_wise_files       
    type_wise_files={}
    for ft in filetypes:
        type_wise_files[ft]=[]
    type_wise_files['others']=[]
    # separate according to filetypes
    for tf in files:
        entered=False
        for key in filetypes:
            for ft in filetypes[key]:
                if ft in tf:
                    type_wise_files[key].append(tf)
                    entered=True
                    break
            if entered: break
        if not entered:
            type_wise_files['others'].append(tf)
            print('File type not found for the file ',tf,' so putting in others')
    return type_wise_files
def get_descr(label,las):
    for l in las:
        try:
            return l.curves[label]['descr']
        except:
            pass