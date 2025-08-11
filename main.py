#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "argcomplete>=3.6.2",
#     "fabric>=3.2.2",
#     "slpp",
# ]
#
# [tool.uv.sources]
# slpp = { git = "https://github.com/SirAnthony/slpp" }
# ///
# PYTHON_ARGCOMPLETE_OK

import argparse
import base64
import json
import plistlib
import sys
import zlib
from os import makedirs, path

import argcomplete
from slpp import slpp as lua

BALATRO_STEAM_LOCATION = path.expanduser("~/Library/Application Support/Balatro")
BALATRO_ARCADE_LOCATION = path.expanduser(
    "~/Library/Containers/com.playstack.balatroarcade/Data/Library/Preferences"
)


def decode_base64_and_inflate(b64string):
    decoded_data = base64.b64decode(b64string)
    return zlib.decompress(decoded_data, -15)


def raw_inflate(byte):
    return zlib.decompress(byte, -15)


def deflate_and_base64_encode(string_val):
    zlibbed_str = zlib.compress(string_val)
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string)


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Balatro+ Save Manager - Sync saves between Steam and Apple Arcade versions"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Copy from Arcade to Steam
    arcade_to_steam = subparsers.add_parser(
        "arcade-to-steam", help="Copy save from Arcade to Steam"
    )
    arcade_to_steam.add_argument(
        "--arcade-save",
        choices=["1", "2", "3"],
        required=True,
        help="Arcade save slot number (1, 2, or 3)",
    )
    arcade_to_steam.add_argument(
        "--steam-save",
        choices=["1", "2", "3"],
        required=True,
        help="Steam save slot number (1, 2, or 3)",
    )

    # Copy from Steam to Arcade
    steam_to_arcade = subparsers.add_parser(
        "steam-to-arcade", help="Copy save from Steam to Arcade"
    )
    steam_to_arcade.add_argument(
        "--steam-save",
        choices=["1", "2", "3"],
        required=True,
        help="Steam save slot number (1, 2, or 3)",
    )
    steam_to_arcade.add_argument(
        "--arcade-save",
        choices=["1", "2", "3"],
        required=True,
        help="Arcade save slot number (1, 2, or 3)",
    )

    # Print Arcade save
    print_arcade = subparsers.add_parser("print-arcade", help="Print Arcade save data")
    print_arcade.add_argument(
        "--save",
        choices=["1", "2", "3"],
        required=True,
        help="Save slot number (1, 2, or 3)",
    )

    # Print Steam save
    print_steam = subparsers.add_parser("print-steam", help="Print Steam save data")
    print_steam.add_argument(
        "--save",
        choices=["1", "2", "3"],
        required=True,
        help="Save slot number (1, 2, or 3)",
    )
    argcomplete.autocomplete(parser)
    return parser.parse_args()


def get_save_number_from_args(save_number):
    """
    Return the save number from arguments (no user input needed).
    """
    return save_number


# object for arcade save containing the meta.jkr and profile.jkr files
class ArcadeSave:
    """
    Class to represent the Balatro+ Apple Arcade save file.
    """

    def __init__(self, save_number):
        self.save_number = save_number
        self.save_file = path.join(
            BALATRO_ARCADE_LOCATION, "com.playstack.balatroarcade.plist"
        )
        self.load_save()

    def load_save(self):
        """
        Load the save file.
        """
        with open(self.save_file, "rb") as f:
            data = plistlib.load(f)
            self.full_plist = dict(data)
            try:
                self.meta_jkr = bytes(data[self.save_number + "__meta.jkr.data"])
                self.profile_jkr = bytes(data[self.save_number + "__profile.jkr.data"])
            except KeyError:
                self.meta_jkr = bytes()
                self.profile_jkr = bytes()
                print("No save found for this save number, creating new one.")

    def save(self):
        """
        Save the save file.
        """
        self.full_plist[self.save_number + "__meta.jkr.data"] = self.meta_jkr
        self.full_plist[self.save_number + "__profile.jkr.data"] = self.profile_jkr
        with open(self.save_file, "wb") as f:
            plistlib.dump(
                self.full_plist,
                f,
            )

    def get_meta(self, raw=True):
        """
        Get the meta.jkr file.
        """
        if raw:
            return self.meta_jkr
        else:
            return lua.decode(str(raw_inflate(self.meta_jkr))[8:-1])

    def get_profile(self, raw=True):
        """
        Get the profile.jkr file.
        """
        if raw:
            return self.profile_jkr
        else:
            return lua.decode(str(raw_inflate(self.profile_jkr))[8:-1])

    def set_meta(self, meta_jkr):
        """
        Set the meta.jkr file.
        """
        self.meta_jkr = meta_jkr

    def set_profile(self, profile_jkr):
        """
        Set the profile.jkr file.
        """
        self.profile_jkr = profile_jkr


# object for steam save
class SteamSave:
    """
    Class to represent the Balatro Steam save file.
    """

    def __init__(self, save_number):
        self.save_number = save_number
        self.meta_jkr_path = path.join(
            BALATRO_STEAM_LOCATION, self.save_number, "meta.jkr"
        )
        self.profile_jkr_path = path.join(
            BALATRO_STEAM_LOCATION, self.save_number, "profile.jkr"
        )

    def load_save(self):
        """
        Load the save file.
        """
        with open(self.meta_jkr_path, "rb") as f:
            self.meta_jkr = f.read()
        with open(self.profile_jkr_path, "rb") as f:
            self.profile_jkr = f.read()

    def save(self):
        """
        Save the save file.
        """
        try:
            with open(self.meta_jkr_path, "wb") as f:
                f.write(self.meta_jkr)
            with open(self.profile_jkr_path, "wb") as f:
                f.write(self.profile_jkr)
        except FileNotFoundError:
            makedirs(
                path.dirname(self.meta_jkr_path),
                exist_ok=True,
            )
            with open(self.meta_jkr_path, "wb") as f:
                f.write(self.meta_jkr)
            with open(self.profile_jkr_path, "wb") as f:
                f.write(self.profile_jkr)
        except Exception as e:
            print(f"Error saving file: {e}")
            raise

    def get_meta(self, raw=True):
        """
        Get the meta.jkr file.
        """
        if raw:
            return self.meta_jkr
        else:
            return lua.decode(str(raw_inflate(self.meta_jkr))[8:-1])

    def get_profile(self, raw=True):
        """
        Get the profile.jkr file.
        """
        if raw:
            return self.profile_jkr
        else:
            return lua.decode(str(raw_inflate(self.profile_jkr))[8:-1])

    def set_meta(self, meta_jkr):
        """
        Set the meta.jkr file.
        """
        self.meta_jkr = meta_jkr

    def set_profile(self, profile_jkr):
        """
        Set the profile.jkr file.
        """
        self.profile_jkr = profile_jkr


def main():
    """
    Main function for the program.
    """
    args = parse_arguments()

    if args.command is None:
        print("Error: No command specified. Use --help for usage information.")
        sys.exit(1)

    if args.command == "arcade-to-steam":
        print(
            f"Copying save from Arcade slot {args.arcade_save} to Steam slot {args.steam_save}..."
        )

        arcade_save = ArcadeSave(args.arcade_save)
        arcade_save.load_save()

        steam_save = SteamSave(args.steam_save)
        steam_save.set_meta(arcade_save.get_meta())
        steam_save.set_profile(arcade_save.get_profile())
        steam_save.save()
        print("Save copied from Arcade to Steam.")

    elif args.command == "steam-to-arcade":
        print(
            f"Copying save from Steam slot {args.steam_save} to Arcade slot {args.arcade_save}..."
        )

        steam_save = SteamSave(args.steam_save)
        steam_save.load_save()

        arcade_save = ArcadeSave(args.arcade_save)
        arcade_save.set_meta(steam_save.get_meta())
        arcade_save.set_profile(steam_save.get_profile())
        arcade_save.save()
        print("Save copied from Steam to Arcade.")

    elif args.command == "print-arcade":
        # print(f"Printing Arcade save slot {args.save}...")

        arcade_save = ArcadeSave(args.save)
        arcade_save.load_save()
        print(
            json.dumps(
                {
                    "meta": arcade_save.get_meta(raw=False),
                    "profile": arcade_save.get_profile(raw=False),
                },
                indent=4,
            )
        )

    elif args.command == "print-steam":
        # print(f"Printing Steam save slot {args.save}...")

        steam_save = SteamSave(args.save)
        steam_save.load_save()
        print(
            json.dumps(
                {
                    "meta": steam_save.get_meta(raw=False),
                    "profile": steam_save.get_profile(raw=False),
                },
                indent=4,
            )
        )


if __name__ == "__main__":
    main()
