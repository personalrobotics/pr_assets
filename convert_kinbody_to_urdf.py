# convert_kinbody_to_urdf.py

import os
import sys
import xml.etree.ElementTree as ET


class Kinbody_Converter:
    def __init__(self):
        self.kinbody = None
        self.urdf = None
        self.link = None

    def parse_from_file(self, filename):
        if not filename.endswith('.kinbody.xml'):
            print('Invalid input file: %s' % filename)
            return False

        self.kinbody = ET.parse(filename)
        if self.kinbody is None:
            print('Could not open file: %s' % filename)
            return False

        print('read kinbody from  %s' % filename)
        return True

    # TODO:
    # Body - Geom - Quat, RotationAxis, RotationMat, Vertices
    # Translation
    # Joint
    # Mass
    # Kinbody (load other kinbody file)
    # orcdchomp support?
    def convert_child(self, parent, level=0):
        print(level, parent.tag, parent.attrib, parent.text.strip())
        if (parent.tag.lower() == 'body') and (self.link is None):
            robot = self.urdf.iter('robot').next()
            link_name = parent.attrib['name'] if 'name' in parent.attrib else 'base_link'
            self.link = self.add_sub_element(robot, 'link',
                                             {'name': link_name})
            for child in parent:
                self.convert_child(child, level + 1)

            if len(self.link.getchildren()) == 0:
                robot.remove(self.link)
                self.link = None

        elif parent.tag.lower() == 'geom':
            gtype = parent.attrib['type']
            if 'render' in parent.attrib:
                is_render = parent.attrib['render']
            else:
                is_render = 'true'
            features = dict()
            for child in parent:
                if child.tag.lower() == 'extents':
                    extents = map(float, child.text.strip().split(' '))
                    extents_str = ''
                    for val in extents:
                        tval = '%.5f' % (float(val) * 2)
                        extents_str += tval.rstrip('0') + ' '
                    features[child.tag.lower()] = extents_str.strip()
                else:
                    features[child.tag.lower()] = child.text.strip()
            if 'translation' not in features:
                features['translation'] = '0 0 0'

            self.add_geom(self.link, features, gtype, is_render)

        elif parent.tag.lower() == 'orcdchomp':
            return
        else:
            for child in parent:
                self.convert_child(child, level + 1)

    def add_sub_element(self, parent, tag, attrib={}, text=''):
        sub_elem = ET.SubElement(parent, tag)
        sub_elem.attrib = attrib
        sub_elem.text = text
        return sub_elem

    def add_origin(self, parent, val):
        self.add_sub_element(parent, 'origin', {'xyz': val})

    def add_geom(self, parent, features, gtype, is_render='true'):
        collision = self.add_sub_element(parent, 'collision')
        visual = self.add_sub_element(parent, 'visual')
        if gtype == 'trimesh':
            self.add_mesh_data(collision, features['data'])
            if 'render' in features:
                self.add_mesh_render(visual, features['render'])
            else:
                parent.remove(visual)
        elif gtype == 'sphere':
            if 'render' in features:
                self.add_mesh_render(visual, features['render'])
                if ('diffusecolor' in features) or ('ambientColor' in features):
                    self.add_color(visual, features)
                parent.remove(collision)
            else:
                self.add_origin(collision, features['translation'])
                self.add_origin(visual, features['translation'])
                self.add_color(visual, features)
                self.add_sphere(collision, features['radius'])
                self.add_sphere(visual, features['radius'])
        else:
            self.add_origin(collision, features['translation'])
            self.add_origin(visual, features['translation'])
            self.add_color(visual, features)
            if gtype == 'box':
                self.add_box(collision, features['extents'])
                self.add_box(visual, features['extents'])
            elif gtype == 'cylinder':
                self.add_cylinder(collision,
                                  features['radius'],
                                  features['height'])
                self.add_cylinder(visual,
                                  features['radius'],
                                  features['height'])

        if is_render == 'false':
            parent.remove(visual)

    def add_box(self, parent, val):
        geo = self.add_sub_element(parent, 'geometry')
        self.add_sub_element(geo, 'box', {'size': val})

    def add_cylinder(self, parent, radius, length):
        geo = self.add_sub_element(parent, 'geometry')
        self.add_sub_element(geo, 'cylinder', {'radius': radius, 'length': length})

    def add_sphere(self, parent, radius):
        geo = self.add_sub_element(parent, 'geometry')
        self.add_sub_element(geo, 'sphere', {'radius': radius})

    def add_mesh_render(self, parent, filename):
        geo = self.add_sub_element(parent, 'geometry')
        self.add_sub_element(geo, 'mesh', {'filename': filename})

    def add_mesh_data(self, parent, val):
        ws = val.split(' ')
        geo = self.add_sub_element(parent, 'geometry')
        if len(ws) == 1:
            self.add_sub_element(geo, 'mesh', {'filename': ws[0]})
        else:
            scale = float(ws[1])
            self.add_sub_element(geo, 'mesh',
                                 {'filename': ws[0],
                                  'scale': '%.2f %.2f %.2f' % (scale, scale, scale)})

    def add_color(self, parent, features):
        if 'diffusecolor' in features:
            val = features['diffusecolor']
        elif 'ambientcolor' in features:
            val = features['ambientcolor']
        else:
            return

        if 'transparency' in features:
            val += ' ' + features['transparency']
        else:
            val += ' 1.0'

        mat = self.add_sub_element(parent, 'material', {'name': 'c'})
        self.add_sub_element(mat, 'color', {'rgba': val})

    def get_urdf(self):
        if self.urdf is not None:
            return self.urdf

        self.urdf = ET.ElementTree()
        urdf_root = ET.Element('robot')
        urdf_root.attrib = self.kinbody.getroot().attrib
        urdf_root.text = ''
        self.urdf._setroot(urdf_root)
        self.convert_child(self.kinbody.getroot())
        return self.urdf

    def print_tree(self, parent, level=0):
        print(level, parent.tag, parent.attrib, parent.text.strip())
        for child in parent:
            self.print_tree(child, level + 1)


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def script_main():
    if len(sys.argv) != 2:
        print('usage: python %s <filename>' % sys.argv[0])
        return
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print('Could not find file: %s' % filename)
        return

    kconv = Kinbody_Converter()
    if not kconv.parse_from_file(filename):
        return

    urdf = kconv.get_urdf()

    indent(urdf.getroot())

    newfilename = filename.replace('.kinbody', '').replace('.xml', '') + '.urdf'
    if os.path.isfile(newfilename):
        backup_name = newfilename + '.back'
        if os.path.isfile(backup_name):
            from time import gmtime, strftime
            backup_name = '%s_%s.back' % (newfilename, strftime('%y%m%d%H%M%S', gmtime()))
        from shutil import copyfile
        copyfile(newfilename, backup_name)

    newfile = open(newfilename, 'w')
    newfile.write(ET.tostring(urdf.getroot()))
    newfile.close()
    print('new file was created: %s' % newfilename)


if __name__ == '__main__':
    script_main()

# End of script
