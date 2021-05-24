import json
import os
from svgelements import Path, Matrix
import requests
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()

    if (args.source.startswith('https://github.com')):
        repo = args.source.replace("https://github.com/", "")
        parts = repo.split("/")
        # User supplied repo + folder
        if (len(parts) == 2):
            repo = f"{parts[0]}/{parts[1]}"
            folder = parts[2]
            fix_chars_from_github(repo, folder, args.destination)
        else:
            fix_chars_from_github(repo, destination=args.destination)
    else:
        fix_chars_from_fs(args.source, args.destination)

    print("All done!")


def progressBar(filename: str, current, total, barLength=20):
    percent = float(current) * 100 / total
    arrow = '-' * int(percent/100 * barLength - 1) + '>'
    spaces = ' ' * (barLength - len(arrow))
    print(
        f"Parsing file '{filename}': [{arrow}{spaces}] {percent:.0f}%",
        end='\r'
    )


def fix_chars_from_github(repo="chanind/hanzi-writer-data", folder="data", destination="fixed"):
    """
    Fetches all .json files from a github repository (hanzi-writer-data, hanzi-writer-data-jp, etc)

    Attempts to transform the pathing (horinzontal flip + translateY) and saves the result to a desintation file

    :param repo: Path to the repository
    :param folder: Path to the folder in the repository
    :param destination: Output file destination path
    """
    if not os.path.exists(destination):
        os.makedirs(destination)

    repo_root = requests.get(
        f"https://api.github.com/repos/{repo}/git/trees/master").json()

    # Find the . This should be at the root of the repository
    matches = [el for el in repo_root["tree"] if el["path"] == folder]
    if (len(matches) == 0):
        print(f"Folder '{folder}' was not found in the repo '{repo}' root")
        return

    # Get the list of .json files in the folder
    data_folder = requests.get(
        f"https://api.github.com/repos/{repo}/git/trees/{matches[0]['sha']}").json()

    fixed_files = {}

    num_files = len(data_folder["tree"])

    for i in range(num_files):
        print(f"Parsing file {i+1}/{num_files}...", end="\r")
        file_listing = data_folder["tree"][i]

        filename = file_listing["path"]

        # skip long file names
        if ".json" not in filename or len(filename.replace(".json", "")) > 1:
            continue

        filename = file_listing['path']

        file_json_data = requests.get(
            f"https://raw.githubusercontent.com/chanind/hanzi-writer-data/master/{folder}/{filename}").text

        char_data = fix_char(file_json_data)

        # For all.json
        fixed_files[filename.replace(".json", "")] = char_data

        with open(f"{destination}/{filename}", "w") as outfile:
            json.dump(char_data, outfile)

    # Write all.json
    with open(f"{destination}/all.json", "w", encoding="utf-8") as outfile:
        json.dump(fixed_files, outfile, ensure_ascii=False)


def fix_chars_from_fs(source="orig", destination="fixed"):
    """
    Fetches all .json files from a local folder

    Attempts to transform the pathing (horinzontal flip + translateY) and saves the result to a desintation file

    :param source: Source folder path
    :param destination: Output file destination path
    """
    if not os.path.exists(destination):
        os.makedirs(destination)

    fixed_files = {}
    source_directory = os.listdir(source)
    num_files = len(source_directory)

    for i in range(num_files):
        filename = source_directory[i]
        # skip long file names
        if ".json" not in filename or len(filename.replace(".json", "")) > 1:
            continue

        progressBar(filename, i, num_files)

        # Read character
        with open(os.path.join(source, filename), 'r') as char:
            data = char.read()

        char_data = fix_char(data)

        # For all.json
        fixed_files[filename.replace(".json", "")] = char_data

        with open(f"{destination}/{filename}", "w") as outfile:
            json.dump(char_data, outfile)

    # Write all.json
    with open(f"{destination}/all.json", "w", encoding="utf-8") as outfile:
        json.dump(fixed_files, outfile, ensure_ascii=False)


def fix_char(data: str):
    """
    Transforms the individual stroke paths (horinzontal flip + translateY) and returns the JSON-writeable format

    :param data: Raw JSON data
    """
    c = json.loads(data)

    # Flip back horizontally and move up 900px
    flipped_strokes = map(
        lambda stroke: (Path(stroke) * "scaleY(-1) translateY(-900)").d(),
        c["strokes"]
    )

    c["strokes"] = list(flipped_strokes)

    # Fix the Y median stroke
    fixed_medians = []
    for median in c["medians"]:
        medians = map(lambda xy: [xy[0], 900 - xy[1]], median)
        fixed_medians.append(list(medians))

    c["medians"] = fixed_medians

    return c


if __name__ == '__main__':
    main()
