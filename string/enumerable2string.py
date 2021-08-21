def enumerable2string(enu,split=' '):
    '''
    conver something enumerable(list,tuple,1D-array,...) to string
    :param enu: something enumerable(list,tuple,1D-array,...)
    :param split: splitting symbol. ' ' as default.
    :return: string
    '''
    if enu is None: return ''
    l=len(enu)
    if l==0: return ''
    if l==1: return str(l)
    s=str(enu[0])
    for itm in enu[1:]:
        s+=f'{split}{itm}'
    return s