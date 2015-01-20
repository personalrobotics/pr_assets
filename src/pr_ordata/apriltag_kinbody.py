PACKAGE = 'pr_ordata'
import os
import shutil
import cv2
import numpy
from catkin.find_in_workspaces import find_in_workspaces

def build_apriltag_kinbody(family, index, width, thickness, name, path):
    
    family_name = 'tag%ih%i'%family
    str_index = str(index).zfill(5)
    texture_name = 'tag%i_%i_%s.png'%(family + (str_index,))
    
    blank_kinbody_path = find_in_workspaces(
            search_dirs=['share'],
            project=PACKAGE,
            path='data/tags/apriltag_blank.kinbody.xml',
            first_match_only=True)
    blank_mesh_path = find_in_workspaces(
            search_dirs=['share'],
            project=PACKAGE,
            path='data/tags/apriltag_blank.dae',
            first_match_only=True)
    texture_path = find_in_workspaces(search_dirs=['share'],
            project=PACKAGE,
            path='data/tags/textures/%s/%s'%(family_name, texture_name),
            first_match_only=True)
    
    if not blank_kinbody_path:
        raise Exception, 'Unable to find data/tags/apriltag_blank.kinbody.xml'
    
    if not blank_mesh_path:
        raise Exception, 'Unable to find data/tags/apriltag_blank.dae'
    
    if not texture_path:
        raise Exception, ('Unable to find data/tags/textures/%s/%s'%
                          family_name, texture_name)
    
    # Write out the kinbody
    with open(blank_kinbody_path[0], 'r') as f:
        kinbody_data = f.read()
    
    kinbody_data = kinbody_data.replace('NAME', name)
    kinbody_data = kinbody_data.replace('MESH', '%s.dae'%name)
    
    kinbody_path = os.path.join(path, '%s.kinbody.xml'%name)
    with open(kinbody_path, 'w') as f:
        f.write(kinbody_data)
    
    # Write out the mesh
    
    # The width parameter above specifies the width of the black square region
    # of the tag.  This means the resulting mesh will be a little bit wider
    # than what is specified.
    block_width = family[0]**0.5
    tag_xy = ((block_width+4.)/(block_width+2.)) * width * 0.5
    tag_z = thickness/2.
    
    mesh_positions = [
        (-tag_xy, -tag_xy, tag_z),
        (tag_xy, -tag_xy, tag_z),
        (-tag_xy, tag_xy, tag_z),
        (tag_xy, tag_xy, tag_z),
        (-tag_xy, tag_xy, -tag_z),
        (tag_xy, tag_xy, -tag_z),
        (-tag_xy, -tag_xy, -tag_z),
        (tag_xy, -tag_xy, -tag_z)
    ]
    
    mesh_block = '\n'.join([' '.join([str(p) for p in position])
                            for position in mesh_positions])
    
    with open(blank_mesh_path[0], 'r') as f:
        dae_data = f.read()
    
    dae_data = dae_data.replace('MESH_VERTICES', mesh_block)
    dae_data = dae_data.replace('TEXTURE_PATH', texture_name)
    
    mesh_path = os.path.join(path, '%s.dae'%name)
    with open(mesh_path, 'w') as f:
        f.write(dae_data)
    
    # Write out the texture
    hires_texture_path = os.path.join(path, texture_name)
    resize_texture(texture_path[0], hires_texture_path)
    

def resize_texture(read_path, write_path, factor=10.0):
    orig_image = cv2.imread(read_path)
    scaled_size = (orig_image.shape[0]*factor, orig_image.shape[1]*factor,
                orig_image.shape[2])
    
    scaled_image = numpy.zeros(scaled_size, dtype=orig_image.dtype)
    
    for row in xrange(orig_image.shape[0]):
        for col in xrange(orig_image.shape[1]):
            print orig_image[row,col].tolist()
            cv2.rectangle(scaled_image,
                          (int(row*factor), int(col*factor)),
                          (int((row+1)*factor-1), int((col+1)*factor-1)),
                          orig_image[row,col].tolist(), -1)
    
    cv2.imwrite(write_path, scaled_image)


