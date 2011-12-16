
# import the pickle module
try:
    import cPickle as pickle
except:
    import pickle

def wapickle(filename,variable):
    # open file for writing
    picklefile = open(filename, 'w')
    # now let's pickle the variable
    pickle.dump(variable,picklefile)
    # close the file
    picklefile.close()


def waunpickle(filename):
    # open unpickle file
    unpicklefile = open(filename, 'r')
    # now load the variable
    variable = pickle.load(unpicklefile)
    # close the file, just for safety
    unpicklefile.close()
    # return variable
    return variable
