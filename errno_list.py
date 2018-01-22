import pdb
import os

def main():
    """
    Generate the list of errno entries in a format suitable to be included in a
    rust program
    """
    # pdb.set_trace()
    elist = {}
    nlist = [(x, getattr(os.errno, x))
             for x in dir(os.errno) if x.startswith('E')]
    for item in nlist:
        (name, value) = item
        elist[value] = {
            'name': name,
            'value': value,
            'desc': os.strerror(value)
            }

    for key in sorted(elist.keys()):
        print("({}, \"{}\", \"{}\"),".format(key,
                                         elist[key]['name'],
                                         elist[key]['desc']))

if __name__ == '__main__':
    main()
