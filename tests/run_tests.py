import os
import subprocess
import shutil
import sys


def run_model(model_path):
    try:
        # Run the model file and capture the output
        model_dir = os.path.dirname(os.path.abspath(model_path))
        result = subprocess.run(
            [sys.executable, model_path], capture_output=True, text=True, cwd=model_dir
        )
        # Check if there was an error
        if result.returncode != 0:
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        return False, str(e)


def main(models_to_run_file):
    try:
        # Reading the test models and storing them in a dictionary
        with open(models_to_run_file, "r") as file:
            models_to_run = [
                line.strip()
                for line in file
                if not line.strip().startswith("*") and line.strip()
            ]

        # Running the test models
        with open("log_oneline.txt", "w") as logfile_oneline, open(
            "log.txt", "w"
        ) as logfile:
            # Creating a temporary folder to run the tests
            run_dir = "run_dir_tmp"
            try:
                if os.path.exists(run_dir):
                    shutil.rmtree(run_dir)
                os.makedirs(run_dir, exist_ok=False)
            except Exception:
                raise ValueError("The run directory could not be created.")
            for model_to_run in models_to_run:
                os.mkdir(os.path.join(run_dir, model_to_run))

            errCntr = 0
            cwd = os.getcwd()
            for i, model in enumerate(models_to_run):
                print(f"Running test {i+1} out of {len(models_to_run)}: {model}")
                src_dir = os.path.join(cwd, model)
                dst_dir = os.path.join(cwd, run_dir, model)
                shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                # Ensure shared test utilities are available to the test module
                utils_src = os.path.join(cwd, "utils")
                if os.path.isdir(utils_src):
                    shutil.copytree(utils_src, os.path.join(dst_dir, "utils"), dirs_exist_ok=True)
                model_file_name = model + ".py"
                success, message = run_model(os.path.join(dst_dir, model_file_name))
                if success:
                    logfile_oneline.write(f"{src_dir}\t\tOK\n")
                else:
                    errCntr += 1
                    logfile_oneline.write(f"{src_dir}\t\tError\n")
                logfile.write(f"Model {src_dir}\n")
                logfile.write(f"Output:\n{message}\n")
                logfile.write("----------------------------------------------\n")
            if errCntr >= 1:
                print(f"{errCntr} tests failed.")
            else:
                print("All tests passed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    models_to_run_file = "models_to_run.txt"

    main(models_to_run_file)
