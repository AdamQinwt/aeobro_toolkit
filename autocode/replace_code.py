allowed_tree_starts=['list','all']
allowed_states=['float','int','text','f_float','f_int','f_text','last','middle']

def parse_code(template,new_name,global_defines:dict,cols:list):
    print(cols)
    print('Parsing '+template+' to '+new_name+' ...')
    t=open(template,'r')
    n=open(new_name,'w')
    cur='root'  # status name
    l=len(cols)

    for line in t.readlines():
        # print(line)
        is_flag = False
        for tmp in allowed_tree_starts:
            # scan to find if the line is the start symbol of a sub-section
            # only ${start symbol} is scanned. So you can write anything after or before the symbol as long as it stays in the same line.
            # e.g., 'this is a $list for data\n' will yield a 'list' sub-section.
            tt='$'+tmp
            if tt in line:
                cur=tmp
                tr={tmp:''}
                is_flag=True
                break
        # if the line is a start symbol, simply go to the next line.
        if is_flag: continue

        for tmp in allowed_states:
            # scan to find if the line is the start symbol of a type specification.
            tt='$'+tmp
            if tt in line:
                tr[tmp]=''
                cur=tmp
                is_flag=True
                break
        if is_flag: continue

        # this is the part processing code which you can modify to create your own version of autocode.
        elif '$endlist' in line:
            # this part shows how to generate lines for each col(data column defined in exp_defines.txt) of different types.
            # 'f_' means final. In SQL, some ','s are omitted if the item is the last one
            # lists that require or don't require different line definitions are processed in the two branches in the following if-else.
            if 'f_text' in tr or 'f_int' in tr:
                for i in range(l-1):
                    name, types=cols[i][0],cols[i][1]
                    s = tr[types].replace('{$name}', name).replace('{$lower}', name.lower()).replace('{$type}',types)
                    n.write(s)
                i=l-1
                name, types = cols[i][0], cols[i][1]
                s = tr['f_'+types].replace('{$name}', name).replace('{$lower}', name.lower()).replace('{$type}',types)
                n.write(s)
            else:
                for name,types in cols:
                    s=tr[types].replace('{$name}',name).replace('{$lower}',name.lower()).replace('{$type}',types)
                    n.write(s)
            # after parsing, reset the current status to 'root' and clear all specific definitions.
            tr={}
            cur = 'root'
            continue
        elif '$endall' in line:
            # this part shows how to generate lines for each col(data column defined in exp_defines.txt) of regardless of types.
            # 'middle' means 'not the last one'. In SQL, some ','s are omitted if the item is the last one, so 'middle' and 'last' may require different processes.
            for i in range(l-1):
                name, types=cols[i][0],cols[i][1]
                s = tr['middle'].replace('{$name}', name).replace('{$lower}', name.lower()).replace('{$type}',types)
                n.write(s)
            i=l-1
            name, types = cols[i][0], cols[i][1]
            s=tr['last'] if 'last' in tr else tr['middle']
            s = s.replace('{$name}', name).replace('{$lower}', name.lower()).replace('{$type}',types)
            n.write(s)
            tr = {}
            cur='root'
            continue

        # otherwise it is a normal line

        # if it is not in any sub-section, replace with global macros and output
        if cur=='root':
            s=line
            for orig,rep in global_defines.items():
                s=s.replace(orig,rep)
            n.write(s)
        # if it is in a sub-section, replace with global macros and save to the sub-section
        else:
            s = line
            for orig, rep in global_defines.items():
                s = s.replace(orig, rep)
            tr[cur]+=s
    t.close()
    n.close()

def read_defines(defines):
    '''
    load global definitions including database columns and global variables
    exp_defines.txt is an example file.
    :param defines: definition file name.
    :return: database columns, global variables
    '''
    cols=[]#[('Id','int')]
    global_defines={}
    with open(defines,'r') as f:
        lines=f.readlines()
        for line in lines:
            if line.startswith('#'): continue
            elif line.startswith('$'):
                split=line.strip().split('=')
                global_defines[split[0].strip()]=split[1].strip()
            else:
                c=line.strip().split('|')
                cols.append((c[0],c[1]))
    return cols,global_defines

def rep_codes(template_defines,defines):
    '''
    Parse codes from templates using the definitions.
    :param template_defines: file source-target definition filename. exp_templates.txt is an example file.
    :param defines: definition filename for read_defines.
    :return: None
    '''
    cols,global_definess=read_defines(defines)
    print(cols,global_definess)
    with open(template_defines, 'r') as f:
        for line in f:
            try:
                c = line.strip().split('|')
                parse_code(c[0],c[1],global_definess,cols)
            except Exception as ex:
                print(str(ex))
                break

if __name__=='__main__':
    rep_codes('exp_templates.txt','exp_defines.txt')