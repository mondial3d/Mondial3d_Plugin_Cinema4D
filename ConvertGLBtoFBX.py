import bpy


def clear_meshes():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def convert_glb_to_fbx(input_filepath, output_filepath):
    clear_meshes()
    bpy.ops.import_scene.gltf(filepath=input_filepath)
    bpy.ops.export_scene.fbx(filepath=output_filepath)



convert_glb_to_fbx("C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/file.glb", "C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/file.fbx")
# "C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/file.glb"
# "C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/file.fbx"
# "C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/FBX_Convertor.py"
# "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"
# cmd.exe /C '"C:/Program Files/Blender Foundation/Blender 4.0/blender.exe" --background --python "C:/Users/saleh/OneDrive/Documents/Work/Cinema 4D Plugin/FBX_convertor.py"'
