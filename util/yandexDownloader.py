import argparse
import requests
import urllib.parse
import os
import hashlib
from tqdm import tqdm  # Import tqdm for the progress bar


class YandexDiskDownloader:
    def __init__(self, link, download_location, md5sum = None):
        self.link = link
        self.download_location = download_location
        self.md5 = md5sum

    def calculate_md5(self, file_path):
        """Calculate the MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def file_exists_and_valid(self, file_path):
        """Check if the file exists and has the correct MD5 checksum."""
        if os.path.exists(file_path):
            print(f"File '{file_path}' already exists. Verifying MD5 checksum...")
            calculated_md5 = self.calculate_md5(file_path)
            if calculated_md5 == self.md5:
                print("MD5 checksum matches. File is valid.")
                return True
            else:
                print("MD5 checksum does not match. File is invalid.")
        else:
            print(f"File '{file_path}' does not exist.")
        return False

    def download(self):
        # Step 1: Get the download URL from Yandex Disk API
        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve download URL. Status code: {response.status_code}")
        
        download_url = response.json()["href"]
        file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
        save_path = os.path.join(self.download_location, file_name)

        # Step 2: Check if the file exists and is valid (only in case if we provide md5sum)
        if self.md5:
            if self.file_exists_and_valid(save_path):
                print("No need to download. Using existing file.")
                return file_name

        # Step 3: Download the file if it doesn't exist or is invalid
        print(f"Downloading file to '{save_path}'...")
        download_response = requests.get(download_url, stream=True)
        if download_response.status_code != 200:
            raise Exception(f"Failed to download file. Status code: {download_response.status_code}")

        total_size = int(download_response.headers.get('content-length', 0))  # Total file size in bytes

        # Step 4: Write the file while showing a progress bar.
        # Keep desc short and let tqdm shrink to the terminal width so the
        # bar stays on one line even on narrow SSH sessions.
        with open(save_path, "wb") as file, tqdm(
            desc="Downloading",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            dynamic_ncols=True,
            leave=True,
        ) as progress_bar:
            for chunk in download_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    file.flush()
                    progress_bar.update(len(chunk))  # Update the progress bar

        print("Download complete.")

        # Step 5: Verify the downloaded file's MD5 checksum
        if self.md5:
            if self.file_exists_and_valid(save_path):
                print("Downloaded file is valid.")
            else:
                print("Downloaded file is invalid. Please try again.")
                os.remove(save_path)  # Remove the invalid file
                raise Exception("MD5 checksum verification failed.")

        return file_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL', required=True)
    parser.add_argument('-d', '--download_location', type=str, help='Download location in PC', required=True)
    args = parser.parse_args()

    downloader = YandexDiskDownloader(args.link, args.download_location)
    downloader.download()