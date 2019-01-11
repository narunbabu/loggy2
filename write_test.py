def write_txtdict(file,text_dict,delimiter=','):
    with open(file,'w') as f:
        for key in text_dict:
            line="{} = {} \n".format(key,delimiter.join(text_dict))
            f.writelines(line)
        # lines=f.writelines('second hi')
        # file_dict={}
        # for l in lines:
        #     [key,val]=l.split('=')
        #     file_dict[key.strip()]=[v.strip() for v in val.split(delimiter)]
    # return file_dict

if __name__ == '__main__':
    file=r'D:\Ameyem Office\Projects\Cairn/ionics.txt'
    treeview_dict={'Log': {'GR': ['GR_ARC'], 'RHOB': ['RHOB', 'ROBB'], 'NPHI': ['TNPH'], 'NA': ['DEPT', 'ROP5_RM', 'A16H', 'A22H', 'A28H', 'A34H', 'A40H', 'P16H', 'P22H', 'P28H', 'P34H', 'P40H', 'A16L', 'A22L', 'A28L', 'A34L', 'A40L', 'P16L', 'P22L', 'P28L', 'P34L', 'P40L', 'ECD_ARC', 'APRS_ARC', 'ATMP', 'DRHO', 'DRHB', 'DCHO', 'DCVE', 'DCAV', 'VERD', 'HORD']}}

    write_txtdict(file,treeview_dict['Log'],delimiter=' ')
