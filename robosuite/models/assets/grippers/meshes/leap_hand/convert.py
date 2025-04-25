import trimesh
import os

input_dir = "./"  # Change this
output_dir = input_dir  # or set a different output dir

for filename in os.listdir(input_dir):
    if filename.endswith(".obj"):
        obj_path = os.path.join(input_dir, filename)
        mesh = trimesh.load(obj_path)
        stl_path = os.path.join(output_dir, filename.replace(".obj", ".stl"))
        mesh.export(stl_path)
        print(f"Converted: {filename} -> {os.path.basename(stl_path)}")