import sys

def ConvertGLBtoFBX(input_filepath):
    import bpy
    output_filepath= input_filepath.replace(".glb",".fbx")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=input_filepath)
    bpy.ops.export_scene.fbx(filepath=output_filepath)
    return output_filepath

def main():
    input_filepath = sys.argv[-1]
    ConvertGLBtoFBX(input_filepath)

if __name__ == "__main__":
    main()
