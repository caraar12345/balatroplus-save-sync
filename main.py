import json
import plistlib
from os import makedirs, path

from slpp import slpp as lua

import util

BALATRO_STEAM_LOCATION = path.expanduser("~/Library/Application Support/Balatro")
BALATRO_ARCADE_LOCATION = path.expanduser(
    "~/Library/Containers/com.playstack.balatroarcade/Data/Library/Preferences"
)


def main_menu():
    """
    Main menu for the program.
    """
    print("Welcome to Balatro+ Save Manager")
    print("1. From Arcade to Steam")
    print("2. From Steam to Arcade")
    print("3. Print Arcade Save")
    print("4. Print Steam Save")
    print("5. Exit")
    choice = input("Enter your choice: ")
    return choice


def get_save_number(game_type):
    """
    Get the save number from the user.
    """
    save_number = input(f"Enter the save number for {game_type} (1, 2, 3): ")
    while save_number not in ["1", "2", "3"]:
        print("Invalid choice. Please try again.")
        save_number = input(f"Enter the save number for {game_type} (1, 2, 3): ")
    return save_number


# object for arcade save containing the meta.jkr and profile.jkr files
class ArcadeSave:
    """
    Class to represent the Balatro+ Apple Arcade save file.
    """

    def __init__(self):
        self.save_number = get_save_number("Arcade")
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
            return lua.decode(str(util.raw_inflate(self.meta_jkr))[8:-1])

    def get_profile(self, raw=True):
        """
        Get the profile.jkr file.
        """
        if raw:
            return self.meta_jkr
        else:
            return lua.decode(str(util.raw_inflate(self.profile_jkr))[8:-1])

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

    def __init__(self):
        self.save_number = get_save_number("Steam")
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
            return lua.decode(str(util.raw_inflate(self.meta_jkr))[8:-1])

    def get_profile(self, raw=True):
        """
        Get the profile.jkr file.
        """
        if raw:
            return self.meta_jkr
        else:
            return lua.decode(str(util.raw_inflate(self.profile_jkr))[8:-1])

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
    while True:
        choice = main_menu()
        if choice == "1":
            arcade_save = ArcadeSave()
            arcade_save.load_save()

            steam_save = SteamSave()
            steam_save.set_meta(arcade_save.get_meta())
            steam_save.set_profile(arcade_save.get_profile())
            steam_save.save()
            print("Save copied from Arcade to Steam.")
        elif choice == "2":
            steam_save = SteamSave()
            steam_save.load_save()

            arcade_save = ArcadeSave()
            arcade_save.set_meta(steam_save.get_meta())
            arcade_save.set_profile(steam_save.get_profile())
            arcade_save.save()
            print("Save copied from Steam to Arcade.")
        elif choice == "3":
            arcade_save = ArcadeSave()
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
        elif choice == "4":
            steam_save = SteamSave()
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
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
