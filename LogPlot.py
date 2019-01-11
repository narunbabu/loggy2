import matplotlib.pyplot as plt
class LogPlot():
    def __init__(self,ncols=1,nrows=1,vert_size=60,harsize=60):
        self.ax=[]
        self.colors=['#800000',	'#008080','#000080','#FF00FF','#800080','#00FFFF','#FFFF00','#FF0000','#00FF00','#008000','#0000FF','#808000','#C0C0C0','#D3D3D3',]
        if nrows>1:
            fig, self.ax = plt.subplots(nrows=nrows, ncols=1, figsize=(harsize,3*nrows), sharey=True)
            fig.subplots_adjust(top=0.75,wspace=0.1)
        else:
            fig, self.ax = plt.subplots(nrows=1, ncols=ncols, figsize=(3*ncols,vert_size), sharey=True)
            fig.subplots_adjust(top=0.75,wspace=0.1)
            plt.gca().invert_yaxis()
        # self.ax[0].invert_yaxis()

    def basicPlot(ax,depth,prop,lcolor='#800000'):
        # ax.get_xaxis().set_visible(False) 
        # ax.twiny()
        # print(prop,depth)
        ax.clear()
        ax.plot( prop,depth, label='keycol', color=lcolor)
        
        ax.yaxis.grid(True)
        ax.xaxis.grid(True)
        ax.xaxis.tick_top()
        # ax.set_title('Keys',verticalalignment='top')
        # ax.spines['top'].set_position(('outward',0))  
        
        # ax.set_xlabel('keycol',color=lcolor) 
        
        # ax.tick_params(axis='x', colors=lcolor)
        # ax.set_xlim(min(prop),max(prop))
        # # ax.margins(x=0.1, y=0.05)
        # ax.grid(True)
        
        return ax
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

