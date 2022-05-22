import os,glob
import argparse
class Node():
    def __init__(self, path):
        self.path = path
        self.Ca = 0
        self.Ce = 0
        self.Nc = 0
        self.Na = 0

    def analysis(self):
        if self.Ca + self.Ce + self.Nc + self.Na > 0:
            I = self.Ce/max(self.Ce+self.Ca,1)
            A = self.Na/max(self.Na+self.Nc,1)

            D = abs(A+I-1)
            print(self.path)
            #print(self.Ce,self.Ca)
            print('\t Instability : ',I)
            print('\t Abstractness : ', A)
            print('\t Metric : ', D)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, required=True)
    return parser.parse_args()

def build_graph(root, path = []):
    tree = {}
    try:
        filenames = glob.glob(os.path.join(root, "*"))
        for file in filenames:
            if os.path.isdir(file):
                key = os.path.basename(file)
                subtree = build_graph(file, path+[key])
                tree.update(subtree)
            else:
                ext = os.path.splitext(file)[-1]
                if ext == '.py':
                    name = os.path.basename(file)
                    key = os.path.splitext(name)[0]
                    key = tuple(path+[key])
                    tree[key] = Node(file)
    except PermissionError:
        pass
    return tree

def parse(file):
    dst = set()
    valid_name = list(map(lambda x: chr(x + ord('A')), range(26))) + list(map(lambda x: chr(x + ord('a')), range(26))) + list(map(str, range(10)))
    tot_c = 0
    Na = 0
    with open(file, "r") as f:
        lines = f.readlines()
        comment_count = 0
        for line in lines:
            line = line.strip()
            cnt_s = line.count("'''")
            cnt_l = line.count('"""')
            comment_count += cnt_s+cnt_l
            if comment_count&1:
                continue
            if cnt_s > 0:
                line = line[line.rfind("'''") + 3:]
            if cnt_l>0:
                line =line[line.rfind('"""')+3:]
            if line.startswith('import'):
                rem = line.split(maxsplit=1)[-1]
                toks = rem.split(',')
                for tok in toks:
                    tok = tok.split(maxsplit=1)[0]
                    path = tok.split('.')
                    dst.add(tuple(path))
            elif line.startswith('from'):

                toks = line.split(maxsplit=3)
                from_pkg,import_pkg = toks[1],toks[3]


                relative = False
                print(line)
                if from_pkg.startswith('.'):
                    edge = [-1]
                    if len(from_pkg)>1 and from_pkg[1]=='.':
                        edge.append('..')
                        edge.append('..')
                        from_pkg = from_pkg[2:]
                    else:
                        edge.append('..')
                        from_pkg = from_pkg[1:]
                    relative = True

                    edge.extend(from_pkg.split('.'))
                    #print(edge)
                    for postfix in import_pkg.split(','):
                        if postfix=='*':
                            continue
                        dst.add(tuple(edge+[postfix]))
                else:
                    tok = line.split()[1]
                    path = tok.split('.')
                    # print("before")
                    # print(path)
                    dst.add(tuple(path))
                #print(dst)
            elif line.startswith('class'):
                tot_c+=1
                pos = line.find('ABCMeta')
                if pos !=-1:
                    l,r = line[pos-1],line[pos+7]
                    if l not in valid_name and r not in valid_name:
                        Na+=1



    return dst, tot_c-Na, Na


def MartinMetric(tree):
    for k,v in tree.items():
        edges, Na, Nc = parse(v.path)
        for edge in edges:
            edge = list(edge)
            if edge[0]==-1:
                edge=edge[1:]
                path = list(k)
                for tok in edge:
                    if tok=='..':
                        path.pop()
                    elif tok in ['','.']:
                        continue
                    else:
                        path.append(tok)
                dst = tuple(path)
                if dst not in tree:
                    dst = tuple(path[:-1])
            else:
                dst = tuple(edge)
            v.Ce+=1
            v.Na += Na
            v.Nc += Nc
            if dst in tree:
                tree[dst].Ca+=1
    for k, v in tree.items():
        v.analysis()


def run():
    parser = get_parser()
    tree = build_graph(parser.dir)
    for k,v in tree.items():
        print(k)
    MartinMetric(tree)


if __name__ == '__main__':
    run()