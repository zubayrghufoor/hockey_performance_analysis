import os

def list_directories(startpath):
    """
    Recursively lists all directories and files starting from a given directory.

    Args:
        startpath (str): The directory path to start listing from.

    Output:
        Prints the directory structure with indentation to represent the hierarchy.
    """
    for root, dirs, files in os.walk(startpath):
        # Calculate the indentation level based on the depth of the directory
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        # Print the current directory name with appropriate indentation
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        # Print all files in the current directory with additional indentation
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    # Define the starting path for directory listing
    # "." represents the current directory
    project_path = '.'
    # Call the function to list all directories and files
    list_directories(project_path)