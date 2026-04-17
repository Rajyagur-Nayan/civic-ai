import os
import xml.etree.ElementTree as ET

ANNOTATIONS_DIR = "datasets/train/annotations/xmls"
IMAGES_DIR = "datasets/train/images"
LABELS_DIR = "datasets/train/labels"
TARGET_CLASSES = ["D20", "D40"]

os.makedirs(LABELS_DIR, exist_ok=True)


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    filename = root.find("filename").text
    size = root.find("size")
    width = int(size.find("width").text)
    height = int(size.find("height").text)

    boxes = []
    for obj in root.findall("object"):
        class_name = obj.find("name").text
        if class_name in TARGET_CLASSES:
            bndbox = obj.find("bndbox")
            xmin = int(bndbox.find("xmin").text)
            ymin = int(bndbox.find("ymin").text)
            xmax = int(bndbox.find("xmax").text)
            ymax = int(bndbox.find("ymax").text)
            boxes.append((class_name, xmin, ymin, xmax, ymax))

    return filename, width, height, boxes


def convert_to_yolo(xmin, ymin, xmax, ymax, width, height):
    x_center = (xmin + xmax) / 2.0 / width
    y_center = (ymin + ymax) / 2.0 / height
    box_width = (xmax - xmin) / width
    box_height = (ymax - ymin) / height
    return x_center, y_center, box_width, box_height


xml_files = [f for f in os.listdir(ANNOTATIONS_DIR) if f.endswith(".xml")]
converted = 0
skipped = 0

for xml_file in xml_files:
    xml_path = os.path.join(ANNOTATIONS_DIR, xml_file)
    try:
        filename, width, height, boxes = parse_xml(xml_path)

        if not boxes:
            skipped += 1
            continue

        label_filename = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(LABELS_DIR, label_filename)

        with open(label_path, "w") as f:
            for box in boxes:
                class_name, xmin, ymin, xmax, ymax = box
                x_c, y_c, w, h = convert_to_yolo(xmin, ymin, xmax, ymax, width, height)
                f.write(f"0 {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

        converted += 1
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")

print(f"Converted: {converted}")
print(f"Skipped (no potholes): {skipped}")
