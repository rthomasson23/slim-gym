import xml.etree.ElementTree as ET

def scale_mujoco_model(input_path, output_path, scale=0.75):
    """
    Scales a MuJoCo XML model:
    - Adds mesh scale
    - Scales joint, body, and geom positions

    Parameters:
        input_path (str): Path to original XML
        output_path (str): Path to write scaled XML
        scale (float): Uniform scaling factor
    """
    tree = ET.parse(input_path)
    root = tree.getroot()

    scale_str = f"{scale} {scale} {scale}"

    def scale_pos_attr(elem, attr_name="pos"):
        if attr_name in elem.attrib:
            try:
                values = [float(v) * scale for v in elem.attrib[attr_name].split()]
                elem.attrib[attr_name] = " ".join(f"{v:.6f}" for v in values)
            except ValueError:
                pass  # ignore malformed values

    # 1. Scale all meshes
    for mesh in root.findall(".//mesh"):
        mesh.set("scale", scale_str)

    # 2. Scale all positions where needed
    for elem in root.iter():
        if elem.tag in {"body", "joint", "geom", "site"}:
            scale_pos_attr(elem, "pos")

    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ Scaled mesh, joint, body, and geom positions saved to: {output_path}")

if __name__ == "__main__":
    
    output_path = scale_mujoco_model("/home/rthom/Documents/Research/TRI/slim_opensource/robosuite/models/assets/grippers/leap_hand.xml", "/home/rthom/Documents/Research/TRI/slim_opensource/robosuite/models/assets/grippers/leap_hand_09.xml", 0.9)
    print(f"Scaled model saved to: {output_path}")