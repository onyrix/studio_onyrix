import os
import urllib.request
import zipfile

INDEX_DIR = "dataset/index"
RAW_DIR = "dataset/raw"

os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)


class DatasetManager:

    # ----------------------------
    # MAESTRO (OFFICIAL DOWNLOAD)
    # ----------------------------
    def download_maestro(self):
        print("Downloading MAESTRO dataset...")

        url = "https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip"

        out_path = os.path.join(RAW_DIR, "maestro.zip")

        if not os.path.exists(out_path):
            urllib.request.urlretrieve(url, out_path)
            print("Downloaded MAESTRO")

        else:
            print("MAESTRO already downloaded")

        self._extract_zip(out_path, os.path.join(RAW_DIR, "maestro"))

    # ----------------------------
    # LAKH MIDI (MANUAL DOWNLOAD)
    # ----------------------------
    def download_lakh_info(self):
        print("LAKH MIDI must be downloaded manually.")
        print("https://colinraffel.com/projects/lmd/")
        print("Place it into: dataset/raw/lakh/")

    # ----------------------------
    # EXTRACT
    # ----------------------------
    def _extract_zip(self, path, dest):
        if os.path.exists(dest):
            print("Already extracted")
            return

        print("Extracting...")

        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(dest)

        print("Extracted")


# ----------------------------
# TEST
# ----------------------------
if __name__ == "__main__":
    manager = DatasetManager()

    print("\nStable dataset setup...\n")

    manager.download_maestro()
    manager.download_lakh_info()

    print("\nDONE")
