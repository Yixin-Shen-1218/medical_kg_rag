import os
import argparse

def count_images_in_directories(base_path, output_file):
    """
    Count the number of images in each subdirectory of the specified base path
    
    Parameters:
        base_path (str): Path to the base directory to scan
        output_file (str): Path to the output txt file for statistics
    """
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif'}
    
    # Check if the base directory exists
    if not os.path.exists(base_path):
        print(f"Error: Directory '{base_path}' does not exist")
        return
    
    # Get all subdirectories
    try:
        subdirs = [d for d in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, d))]
    except PermissionError:
        print(f"Error: No permission to access directory '{base_path}'")
        return
    
    # Sort subdirectories by name
    subdirs.sort()
    
    # Count images in each subdirectory
    results = []
    total_images = 0
    total_dirs = 0
    
    print(f"Scanning directory: {base_path}")
    print(f"Found {len(subdirs)} subdirectories")
    print("Counting images...")
    
    for subdir in subdirs:
        subdir_path = os.path.join(base_path, subdir)
        image_count = 0
        
        try:
            # Traverse files in the subdirectory
            for file in os.listdir(subdir_path):
                file_path = os.path.join(subdir_path, file)
                if os.path.isfile(file_path):
                    # Check if the file extension is an image format
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        image_count += 1
        except PermissionError:
            print(f"Warning: No permission to access directory '{subdir}', skipping")
            continue
        
        results.append((subdir, image_count))
        total_images += image_count
        if image_count > 0:
            total_dirs += 1
    
    # Write results to txt file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("IU_XRay Dataset Image Count Statistics\n")
            f.write("=" * 50 + "\n")
            f.write(f"Statistics Time: {os.path.getctime(output_file)}\n")
            f.write(f"Base Directory: {os.path.abspath(base_path)}\n")
            f.write(f"Total Subdirectories: {len(subdirs)}\n")
            f.write(f"Subdirectories Containing Images: {total_dirs}\n")
            f.write(f"Total Images: {total_images}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write detailed statistics for each directory
            f.write("Image Count Details by ID Directory:\n")
            f.write("-" * 50 + "\n")
            for subdir, count in results:
                f.write(f"{subdir}: {count} images\n")
                
        print(f"Statistics completed! Results saved to: {output_file}")
        print(f"Total images: {total_images}, Directories with images: {total_dirs}")
        
    except IOError:
        print(f"Error: Cannot write to file '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count the number of images in each ID directory of the iu_xray dataset')
    parser.add_argument('--base_path', default='./images/', 
                       help='Path to the base directory to scan (default: ./images/)')
    parser.add_argument('--output', default='image_count_stats.txt', 
                       help='Output file path (default: image_count_stats.txt)')
    
    args = parser.parse_args()
    
    count_images_in_directories(args.base_path, args.output)