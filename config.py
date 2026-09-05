"""
Package registry: where each platform/firmware's secondary-dev package lives.

Fill zip_link with the Yandex Disk PUBLIC link after uploading
out/r1/unitree_secondary_dev_r1_1.4.2.zip. zip_md5 is the sidecar value printed by
package_r1.py. Until zip_link is set, the tool can still install from a LOCAL path
(menu: "Install from local package" / --package <dir-or-zip>).
"""

PACKAGES = {
    "R1": {
        "1.4.2": {
            "zip_link": "https://disk.yandex.com/d/Tl8GczEd9Z78NA",
            "zip_md5": "978ec5406542a5ecc2c44bd5e6d5213f",
            # optional: a standalone manifest.json link (small, for a pre-download preview)
            "manifest_link": "",
        },
    },
    # "G1": { "<ver>": {...} },
    # "Go2": { ... existing legacy flow ... },
}

DOWNLOAD_DIR = "/unitree/tmp/fwtools_downloads"


def package_for(platform, firmware):
    return PACKAGES.get(platform, {}).get(firmware)
