import os
import subprocess

def merge_obj_files(input_files, output_file):
    with open(output_file, 'w') as outfile:
        for obj_file in input_files:
            with open(obj_file, 'r') as infile:
                outfile.write(infile.read())

def convert_to_glb(input_obj, output_glb):
    command = f"obj2gltf -i {input_obj} -o {output_glb}"
    subprocess.run(command, shell=True, check=True)

def process_category(category_path):
    obj_files = [os.path.join(category_path, f) for f in os.listdir(category_path) if f.endswith('.obj')]
    if not obj_files:
        return

    merged_obj = os.path.join("C:/Users/byun6/Desktop/2024-solution-challenge/ai-server/postprocess/output", "merged.obj")
    #output_glb = os.path.join(category_path, "model.glb")
    
    merge_obj_files(obj_files, merged_obj)

    #convert_to_glb(merged_obj, output_glb)
    
    #os.remove(merged_obj)
    
    print(f"Converted to GLB: {merged_obj}")

base_dir = "C:/Users/byun6/Desktop/2024-solution-challenge/viewer/data"
categories = ['ship']

for category in categories:
    category_path = os.path.join(base_dir, category)
    process_category(category_path)
