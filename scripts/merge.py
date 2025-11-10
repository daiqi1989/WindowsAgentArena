

import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description="Merge text files from a directory into a single file.")
    parser.add_argument("--A_dir", type=str, help="Path to the input directory containing text files.")
    parser.add_argument("--B_dir", type=str, help="Path to the output dir where merged content will be saved.")
    parser.add_argument("--out_dir", type=str, help="rename the merge b dir to this name.")
    parser.add_argument("--model_name", type=str, default="o4-mini", help="Path to the output dir where merged content will be saved.")
    return parser.parse_args()

def merge_files(A_dir, B_dir, model_name):
    apps = os.listdir(os.path.join(A_dir, "pyautogui/a11y_tree", model_name, "0"))
    for app in apps:
        if not os.path.exists(os.path.join(B_dir, "pyautogui/a11y_tree", model_name, "0", app)):
            # copy entire directory if it doesn't exist, use
            os.system("cp -r {} {}".format(
                os.path.join(A_dir, "pyautogui/a11y_tree", model_name, "0", app),
                os.path.join(B_dir, "pyautogui/a11y_tree", model_name, "0", app)
            ))
            continue
        
        task_folders = os.listdir(os.path.join(A_dir, "pyautogui/a11y_tree", model_name, "0", app))
        # remove the corresponding app directory in B_dir
        for task_folder in task_folders:
            os.system("rm -rf {}".format(
                os.path.join(B_dir, "pyautogui/a11y_tree", model_name, "0", app, task_folder)
            ))
            # copy the app directory from A_dir to B_dir
            os.system("cp -r {} {}".format(
                os.path.join(A_dir, "pyautogui/a11y_tree", model_name, "0", app, task_folder),
                os.path.join(B_dir, "pyautogui/a11y_tree", model_name, "0", app, task_folder)
            ))
    
    # rename B_dir to out_dir
    os.system("mv {} {}".format(B_dir, args.out_dir))


if __name__ == "__main__":
    args = parse_arguments()
    merge_files(args.A_dir, args.B_dir, args.model_name)
