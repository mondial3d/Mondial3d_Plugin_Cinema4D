import sys

def ConvertFBXtoGLB(input_filepath):
    import bpy
    output_filepath= input_filepath.replace(".fbx",".glb")

    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=input_filepath)
    bpy.ops.export_scene.gltf(filepath=output_filepath)
    return output_filepath

def main():
    input_filepath = sys.argv[-1]
    ConvertFBXtoGLB(input_filepath)

if __name__ == "__main__":
    main()
