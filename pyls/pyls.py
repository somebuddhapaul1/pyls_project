import json
import os
import argparse
import time

def format_permissions(permissions):
    """Format the permission string, ensuring it's 10 characters long."""
    return permissions.ljust(10)

def format_time(timestamp):
    """Convert the Unix timestamp to a human-readable date format."""
    return time.strftime('%b %d %H:%M', time.localtime(timestamp))

def human_readable_size(size):
    """Convert file size to human-readable format."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f}K"
    elif size < 1024 ** 3:
        return f"{size / 1024 ** 2:.1f}M"
    else:
        return f"{size / 1024 ** 3:.1f}G"

def find_path_in_structure(data, path_parts):
    """
    Recursively finds a file or directory in the structure based on the path_parts.

    :param data: Dictionary representing the current directory structure.
    :param path_parts: List of path parts (e.g., ['parser', 'parser.go']).
    :return: The found file or directory, or None if not found.
    """
    if not path_parts:
        return data

    current_part = path_parts[0]
    contents = data.get('contents', [])

    for item in contents:
        if item.get('name') == current_part:
            if len(path_parts) == 1:
                return item  # Return this item if it's the last part of the path
            if 'contents' in item:
                return find_path_in_structure(item, path_parts[1:])  # Recurse into subdirectory

    return None  # Path not found

def list_top_level_files(data, path="", show_all=False, detailed=False, reverse=False, sort_by_time=False,
                         filter_by=None, human_readable=False):
    """
    Lists top-level files and directories from the JSON structure.
    
    :param data: Dictionary representing the directory structure.
    :param path: String, the path to navigate within the structure.
    :param show_all: Boolean, if True, includes hidden files (starting with '.').
    :param detailed: Boolean, if True, prints detailed information for each file (like ls -l).
    :param reverse: Boolean, if True, reverses the order of the files.
    :param sort_by_time: Boolean, if True, sorts files by time_modified.
    :param filter_by: String, either 'file' or 'dir', to filter the listing.
    :param human_readable: Boolean, if True, converts sizes to human-readable format (like ls -h)
    :return: A list of top-level files and directories, optionally including hidden ones.
    """
    # Split the path into parts
    path_parts = path.split('/') if path else []

    # Find the item corresponding to the given path
    item = find_path_in_structure(data, path_parts)

    if item is None:
        print(f"error: cannot access \'{path}\': No such file or directory")
        return
    if 'contents' in item:
        # If it's a directory, list its contents
        contents = item['contents']
        top_level_items = []
        for entry in contents:
            name = entry.get("name", "")
            permissions = entry.get("permissions", "")
            size = entry.get("size", 0)
            time_modified = entry.get("time_modified", 0)
            is_directory = "contents" in entry  # Determine if the item is a directory

            # Skip hidden files (those starting with a '.'), unless -A is passed
            if show_all or not name.startswith('.'):
                # Apply filtering based on the --filter option
                if filter_by:
                    if filter_by == "file" and is_directory:
                        continue  # Skip directories when filtering for files
                    if filter_by == "dir" and not is_directory:
                        continue  # Skip files when filtering for directories
                    if filter_by != "dir" and  filter_by != "file":
                        print("error: {0} is not a valid filter criteria. Available filters are 'dir' and 'file'".format(filter_by))
                        break
                top_level_items.append({
                    'name': name,
                    'permissions': permissions,
                    'size': size,
                    'time_modified': time_modified,
                    'is_directory': is_directory
                })
        # Sort by time_modified if -t is passed
        if sort_by_time:
            top_level_items.sort(key=lambda x: x['time_modified'])

        # Reverse the list if -r is passed
        if reverse:
            top_level_items.reverse()

        if detailed:
            for item in top_level_items:
                formatted_permissions = format_permissions(item['permissions'])
                formatted_time = format_time(item['time_modified'])
                size = human_readable_size(entry['size']) if human_readable else entry['size']
                print(f"{formatted_permissions} {size:>8} {formatted_time} {item['name']}")
        else:
            print(" ".join(item['name'] for item in top_level_items))
    else:
        # If it's a file, just print its info
        if detailed:
            formatted_permissions = format_permissions(item['permissions'])
            formatted_time = format_time(item['time_modified'])
            size = human_readable_size(entry['size']) if human_readable else entry['size']
            print(f"{formatted_permissions} {size:>8} {formatted_time} ./{path}")
        else:
            print(item['name'])
    return [item['name'] for item in top_level_items]

def load_json_file(file_path):
    """
    Load the JSON file containing the directory structure.
    
    :param file_path: Path to the JSON file
    :return: Parsed JSON content as a dictionary
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser(
        description="pyls - A Python-based implementation of the 'ls' command.",
        usage="This project can help you with multiple utility option for 'ls' command tool",
        epilog="For more information, refer to the 'ls' command documentation or run with --help."
    )
    parser.add_argument('path', nargs='?', default='',
                        help="Path to the directory or file (default: current directory)")
    parser.add_argument('-A', action='store_true',
                        help="List all files, including hidden files (default: excludes hidden files)")
    parser.add_argument('-l', action='store_true', help="List files in detailed format (like 'ls -l')")
    parser.add_argument('-r', action='store_true', help="List files in reverse order")
    parser.add_argument('-t', action='store_true', help="Sort files by time modified")
    parser.add_argument('-H', action='store_true', help="Show file sizes in human-readable format")
    parser.add_argument('--filter',  help="Filter the output by file or directory")

    args = parser.parse_args()

    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'structure.json')
    
    # Load directory structure from JSON
    directory_data = load_json_file(json_file_path)
    # If detailed is enabled, print files in detailed format, otherwise, list normally
    # List files with options -A, -l, -t, -r, -H and --filter
    list_top_level_files(directory_data, path=args.path, show_all=args.A, detailed=args.l, reverse=args.r, sort_by_time=args.t,
                         filter_by=args.filter, human_readable=args.H)


if __name__ == "__main__":
    main()