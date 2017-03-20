# fix_urdf.py

import os
import sys


def script_main():
    if len(sys.argv) != 2:
        print('usage: python %s <filename>' % sys.argv[0])
        return
    if not os.path.isfile(sys.argv[1]):
        print('Could not open file: %s' % sys.argv[1])
        return
    
    filename = sys.argv[1]
    if not filename.endswith('.urdf'):
        print('Invalid input file: %s' % filename)
        return

    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    newfile = open(filename + '.new', 'w')

    for idx, line in enumerate(lines):
        if (line.strip().startswith('<origin xyz=') or
            line.strip().startswith('<box size=')):
            
            elem = line.split('\"')
            numbers = map(float, elem[1].split(' '))
            temp = numbers[1]
            numbers[1] = numbers[2]
            numbers[2] = temp

            new_line = '%s\"%.5f %.5f %.5f\"%s' % (elem[0],
                numbers[0], numbers[1], numbers[2],
                elem[2])

            newfile.write(new_line)

        else:
            newfile.write(line)

    newfile.close()


if __name__ == '__main__':
    script_main()

# End of script
