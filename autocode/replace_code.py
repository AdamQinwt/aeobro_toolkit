allowed_tree_starts=['list','all']
allowed_states=['float','int','text','f_float','f_int','f_text','last','middle']

def parse_code(template,new_name,global_defines:dict,cols:list):
    print(cols)
    print('Parsing '+template+' to '+new_name)
    t=open(template,'r')
    n=open(new_name,'w')
    cur='root'
    l=len(cols)

    for line in t.readlines():
        print(line)
        is_flag = False
        for tmp in allowed_tree_starts:
            tt='$'+tmp
            if tt in line:
                cur=tmp
                tr={tmp:''}
                is_flag=True
                break
        if is_flag: continue
        for tmp in allowed_states:
            tt='$'+tmp
            if tt in line:
                tr[tmp]=''
                cur=tmp
                is_flag=True
                break
        if is_flag: continue
        elif '$endlist' in line:
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
            tr={}
            cur = 'root'
            continue
        elif '$endall' in line:
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
        if cur=='root':
            s=line
            for orig,rep in global_defines.items():
                s=s.replace(orig,rep)
            n.write(s)
        else:
            s = line
            for orig, rep in global_defines.items():
                s = s.replace(orig, rep)
            tr[cur]+=s
    t.close()
    n.close()

def read_defines(defines):
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