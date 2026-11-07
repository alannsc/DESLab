import _pickle as cPickle
import os


class _PortableModelUnpickler(cPickle.Unpickler):
    """Load DESLab models using portable classes, without changing old imports."""

    def find_class(self, module, name):
        # Existing .des files record class paths such as
        # deslab.src.automatadefs.fsa. Resolve them in this package only;
        # do not alias sys.modules, which would affect the installed DESLab.
        if module == 'deslab' or module.startswith('deslab.'):
            module = 'deslab_portable' + module[len('deslab'):]
        return super().find_class(module, name)


def save(self, filename='default',path=None,tmx=False):
    """
    Saves the automaton to a .des file if no extention type is passed in filename
    or
    Saves the transition matrix to a txt file when tmx = True
    
    Exemple:
    --------

    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7'
    S = [a,b,c,d,e,sf]
    X = [x1,x2,x3,x4,x5,x6,x7]
    X0, Xm  = [x1], [x1]
    T = [(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),(x4,d,x4),(x1,a,x5),
    (x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7),(x1,a,x2)]
    G = fsa(X,S,T,X0,Xm)

    save(G)
    save(G,"name","c:\\folder")
    save(G,tmx=True)
    save(G,"name","c:\\folder",True)

    
    """

    if filename == 'default':
        filename = self.name
    filename = os.fspath(filename)
    if path:
        filename = os.path.join(os.fspath(path), filename)
        
    if not tmx:
        name , ext = os.path.splitext(filename)
        if ext == '':
            filename = filename+'.des' 
        fileobj = open(filename, 'wb')
        cPickle.dump(self, fileobj)
        fileobj.close()
        return

    if tmx: 
        text = ""
        matrix = self.tmx()
        for ln in matrix:
                for col in ln:
                        text+=str(col)+'\t'
                text+="\n"
        arq = open(filename+'.txt','w')
        arq.write(text)
        arq.close()
        return


def load(filename,path=None):
    filename = os.fspath(filename)
    if path:
        filename = os.path.join(os.fspath(path), filename)
        
    path , ext = os.path.splitext(filename)
    if ext == '':
        filename = filename+'.des'      
    
    fileobj = open(filename, 'rb')
    self = _PortableModelUnpickler(fileobj).load()
    fileobj.close()
    return self


    
    
    
