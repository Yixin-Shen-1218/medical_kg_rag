import json
import os
import shutil
from pathlib import Path

def copy_images_with_structure(image_paths, source_dir, target_dir):
    """
    Copy image files from source directory to target directory while maintaining directory structure
    
    Args:
        image_paths: List of image paths
        source_dir: Source image directory
        target_dir: Target image directory
    """
    copied_images = []
    
    for img_path in image_paths:
        # Build full source and target paths
        src_path = os.path.join(source_dir, img_path)
        
        # Extract directory and filename parts
        dir_name = os.path.dirname(img_path)
        file_name = os.path.basename(img_path)
        
        # Create target directory
        target_subdir = os.path.join(target_dir, dir_name)
        os.makedirs(target_subdir, exist_ok=True)
        
        # Build target path
        dst_path = os.path.join(target_subdir, file_name)
        
        try:
            # Copy file
            shutil.copy2(src_path, dst_path)
            copied_images.append(dst_path)
            print(f"Copied: {src_path} -> {dst_path}")
        except FileNotFoundError:
            print(f"Warning: File not found {src_path}")
        except Exception as e:
            print(f"Error copying file {src_path}: {str(e)}")
    
    return copied_images

# Read JSON file
with open('./iu_xray/annotation.json', 'r') as f:
    data = json.load(f)

# Extract all report contents and image paths
reports = [item['report'] for item in data['train']]
all_image_paths = [path for item in data['train'] for path in item['image_path']]

print(f"Number of reports: {len(reports)}")
print(f"Number of images: {len(all_image_paths)}")

# Combine all reports into a single string, separated by newlines
combined_reports = '\n'.join(reports)

# Write combined content to report.txt file
with open('report.txt', 'w') as output_file:
    output_file.write(combined_reports)

print("All reports successfully merged to report.txt file")

# Copy all images to ./images folder, maintaining directory structure
source_image_dir = './iu_xray/images/'
target_image_dir = './images/'
copied_images = copy_images_with_structure(all_image_paths, source_image_dir, target_image_dir)

# Save image path list to file
with open('image_list.txt', 'w') as f:
    for img_path in copied_images:
        f.write(f"{img_path}\n")

print(f"Copied {len(copied_images)} images to {target_image_dir} folder")
print("Image path list saved to image_list.txt file")

# Extract first 50 reports and their image paths
reports_50 = [item['report'] for item in data['train']][:50]
image_paths_50 = [path for item in data['train'][:50] for path in item['image_path']]

print(f"Number of first 50 reports: {len(reports_50)}")
print(f"Number of images for first 50 reports: {len(image_paths_50)}")

# Combine first 50 reports into a single string, separated by newlines
combined_reports_50 = '\n'.join(reports_50)

# Write combined content to report_50.txt file
with open('report_50.txt', 'w') as output_file:
    output_file.write(combined_reports_50)

print("First 50 reports successfully merged to report_50.txt file")

# Copy images for first 50 reports to ./images_50 folder, maintaining directory structure
target_image_dir_50 = './images_50/'
copied_images_50 = copy_images_with_structure(image_paths_50, source_image_dir, target_image_dir_50)

# Save image path list to file
with open('image_list_50.txt', 'w') as f:
    for img_path in copied_images_50:
        f.write(f"{img_path}\n")

print(f"Copied {len(copied_images_50)} images to {target_image_dir_50} folder")
print("Image path list saved to image_list_50.txt file")

# Extract first 10 reports and their image paths
reports_10 = [item['report'] for item in data['train']][:10]
image_paths_10 = [path for item in data['train'][:10] for path in item['image_path']]

print(f"Number of first 10 reports: {len(reports_10)}")
print(f"Number of images for first 10 reports: {len(image_paths_10)}")

# Combine first 10 reports into a single string, separated by newlines
combined_reports_10 = '\n'.join(reports_10)

# Write combined content to report_10.txt file
with open('report_10.txt', 'w') as output_file:
    output_file.write(combined_reports_10)

print("First 10 reports successfully merged to report_10.txt file")

# Copy images for first 10 reports to ./images_10 folder, maintaining directory structure
target_image_dir_10 = './images_10/'
copied_images_10 = copy_images_with_structure(image_paths_10, source_image_dir, target_image_dir_10)

# Save image path list to file
with open('image_list_10.txt', 'w') as f:
    for img_path in copied_images_10:
        f.write(f"{img_path}\n")

print(f"Copied {len(copied_images_10)} images to {target_image_dir_10} folder")
print("Image path list saved to image_list_10.txt file")