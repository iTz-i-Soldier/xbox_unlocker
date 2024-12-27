import requests
from collections.abc import Callable
from colorama import init, Fore
import time
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from urllib.parse import unquote
import json
from datetime import datetime, timezone
import os

init(autoreset=True)

class XboxUnlocker:
    def __init__(self):
        self.xuid: str = ""
        self.gamertag: str = ""
        self._games: list = []
        self.xauthtoken_start: str = "XBL3.0 x="
        self.xauthtoken_end: str | None = None
        self.xauthtoken_expiration: str | None = None
        self.last_token_method: Callable | None = None

    def update_last_token_method(func: Callable) -> Callable:
        """
        Updates the last method used to obtain the token, allowing it to be reused
        as the default method in the future.

        Returns:
            Callable: The decorated function.
        """

        def wrapper(self, *args, **kwargs):
            self.last_token_method = func
            return func(self, *args, **kwargs)

        return wrapper

    def token_expiration_check(func: Callable) -> Callable:
        """
        Checks if the token has expired; if it has, attempts to retrieve a new token
        using the last method used to obtain the token.

        Returns:
            Callable: The decorated function.
        """

        def wrap(self, *args, **kwargs):
            valid = self.is_token_not_expired()
            if not valid:
                self.printr("Token expired.")
                self.printr("Trying to obtain the token again.")
                if self.last_token_method:
                    success, _ = self.last_token_method(self, *args, **kwargs)
                    if not success:
                        return False, None
            if self.last_token_method is None:
                self.printy(
                    "Please note, there is no backup method to retrieve the token if it expires during the process."
                )
            return func(self, *args, **kwargs)

        return wrap

    def delete_token_data(func: Callable) -> Callable:
        """
        Deletes the token data (token and expiration time).

        Returns:
            Callable: The decorated function.
        """

        def wrap(self, *args, **kwargs):
            self.xauthtoken_end = None
            self.xauthtoken_expiration = None
            return func(self, *args, **kwargs)

        return wrap

    @staticmethod
    def printr(text: str):
        """
        Prints the provided text in red color in the terminal.

        Args:
            text (str): The text to be printed in red.
        """
        print(Fore.RED + text)

    @staticmethod
    def printg(text: str):
        """
        Prints the provided text in green color in the terminal.

        Args:
            text (str): The text to be printed in green.
        """
        print(Fore.GREEN + text)

    @staticmethod
    def printy(text: str):
        """
        Prints the provided text in yellow (orange-like) color in the terminal.

        Args:
            text (str): The text to be printed in yellow.
        """
        print(Fore.YELLOW + text)

    def save_token_to_file(self):
        """
        Saves the current token and its expiration time to a text file.
        """
        try:
            with open("token.json", "w") as file:
                json_token = {
                    "token": self.xauthtoken_end,
                    "expiration": self.xauthtoken_expiration,
                }
                file.write(json.dumps(json_token, indent=4))
        except:
            pass

    def add_extra_games(self):
        """
        Add extra games from a JSON file to the existing list of games.

        This method checks for the existence of a file named 'games.json'. If the file exists:
        - It attempts to read the content of the file, which is expected to be a JSON array of games.
        - The content is extended to the current list of games (`self._games`).
        - If the file content is invalid or improperly formatted, the file is deleted, and an error message is printed.

        Returns:
            tuple[bool, list | None]:
                - A boolean indicating success (`True`) or failure (`False`).
                - A list of games if the operation was successful, otherwise `None`.

        Side Effects:
            - Prints messages to inform the user about the file status and errors.
            - Deletes the `games.json` file if it contains invalid content.

        Expected Format of 'games.json':
            The file should contain a JSON array of objects with the following structure:
            [
                {
                    "displayImage": "link to image (optional, can be None if empty)",
                    "title_id": "game ID (required)",
                    "name": "game name (optional, must be None if empty)"
                }
            ]

            Example:
            [
                {
                    "displayImage": "https://example.com/image.png",
                    "title_id": "1234",
                    "name": "Super Game"
                },
                {
                    "displayImage": None,
                    "title_id": "5678",
                    "name": None
                }
            ]
        """
        file_path = "games.json"
        if os.path.exists(file_path):
            self.printg("Found file games.json, and the content is being checked.")
            try:
                with open(file_path, "r") as file:
                    games = json.load(file)
                    self._games.extend(games)
                    self.printg(f"{len(games)} Extra games added successfully.")
                    return True, games
            except:
                os.remove(file_path)
                self.printr(f"Error while reading the games file")
                self.printr("The file might contain improperly formatted content")
                return False, None

        else:
            self.printr("File not found")
            return False, None

    def get_token_from_file(func: Callable) -> Callable | None:
        def wrapper(self, *args, **kwargs):
            file_path = "token.json"

            if os.path.exists(file_path):
                self.printg("The token file has been found, content check in progress.")
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)
                        if "token" in data:
                            if "expiration" in data:
                                self.xauthtoken_expiration = data["expiration"]
                                if self.is_token_not_expired():
                                    pass

                                else:
                                    self.xauthtoken_expiration = None
                                    self.printr(
                                        "The token appears to be expired, deleting the file."
                                    )
                                    os.remove(file_path)
                                    return func(self, *args, **kwargs)
                            else:
                                print(
                                    "The token has been found but does not have an expiration, it will be considered valid."
                                )

                            self.xauthtoken_end = data["token"]
                            self.printg("Token obtained successfully.")
                            return True, data["token"]
                except:
                    os.remove(file_path)
                    self.printr(f"Error while reading the token file")
                    return func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)

        return wrapper

    def is_token_not_expired(self):
        """
        Checks if the current token has expired.

        This method compares the current time (in UTC) with the token's expiration time
        (`xauthtoken_expiration`). If the token's expiration time is later than the current
        time, it returns `True`, indicating the token is still valid. Otherwise, it returns `False`,
        indicating the token has expired.

        Returns:
            bool: `True` if the token is still valid, `False` if the token has expired.
        """
        if not self.xauthtoken_expiration:
            self.printy(
                "The token does not have an expiration date, so it will be considered valid."
            )
            return True
        expiration_time = datetime.fromisoformat(
            self.xauthtoken_expiration.replace("Z", "+00:00")
        )
        return datetime.now(timezone.utc) < expiration_time

    @delete_token_data
    @update_last_token_method
    @get_token_from_file
    def get_token_from_variable(self, token: str) -> tuple[bool, str | None]:
        """
        Sets the token from a provided variable.
        """
        if token:
            self.xauthtoken_end = token
            return True, token
        else:
            return False, None

    @delete_token_data
    @update_last_token_method
    @get_token_from_file
    def get_token_from_input(self) -> tuple[bool, str | None]:
        """
        Input the token and sets it.
        """
        token = input("Insert the token.: ")
        if token:
            self.xauthtoken_end = token
            return True, token
        else:
            return False, None

    @delete_token_data
    @update_last_token_method
    @get_token_from_file
    def get_token_from_process(self) -> tuple[bool, str | None]:
        """
        obtaining the token from the process of the xbox app.
        """
        pass

    @delete_token_data
    @update_last_token_method
    @get_token_from_file
    def get_token_from_browser(
        self,
        login_page: str = "https://www.xbox.com/auth/msa?action=logIn&returnUrl=https%3A%2F%2Fwww.xbox.com%2F&ru=https%3A%2F%2Fwww.xbox.com%2F",
        cookie_key: str = "XBXXtkhttp%3A%2F%2Fxboxlive.com",
        *args, 
        **kwargs
    ) -> tuple[bool, str | None]:
        """
        obtaining the token from the xbox website.
        """
        try:
            self.printy("Let the program run on its own; you just need to log in.")
            self.printy("Be patient during the loading process.")
            options = Options()
            options.headless = False
            driver = webdriver.Firefox(options=options)

            driver.get(login_page)

            while True:
                time.sleep(1)

                try:
                    current_url = driver.current_url
                except WebDriverException:
                    return False, None

                xbox_cookie = driver.get_cookie(cookie_key)
                if not xbox_cookie:
                    continue

                value = (
                    json.loads(unquote(xbox_cookie["value"]))
                    if xbox_cookie.get("value")
                    else None
                )
                if not value:
                    continue

                token_data = value.get("tokenData")
                if not token_data:
                    continue

                token = token_data.get("token")
                expiration = token_data.get("expiration")
                user_hash = token_data.get("userHash")

                if not token_data or not user_hash:
                    continue

                xbox_token = f"{user_hash};{token}"
                if not xbox_token:
                    continue

                self.xauthtoken_end = xbox_token
                self.xauthtoken_expiration = expiration

                if self.xauthtoken_end:
                    self.save_token_to_file()
                    driver.quit()
                    self.printg("Token obtained successfully.")
                    return True, self.xauthtoken_end

        except Exception as e:
            if driver:
                driver.quit()
            return False, None

    @property
    def xauthtoken(self) -> str:
        """Returns the complete auth token"""
        return f"{self.xauthtoken_start}{self.xauthtoken_end}"

    @property
    def games(self):
        """
        Returns a copy of the 'games' list to avoid direct modifications to the original list
        or to prevent unintended side effects on it.
        """
        return self._games.copy()

    @token_expiration_check
    def get_player_info(self) -> tuple[bool, list | None]:
        """
        Attempts to retrieve the XUID (Xbox User ID) and gamertag for the authenticated user.

        This method sends a request to retrieve the XUID and gamertag associated with the
        currently authenticated user. If the request is successful, the XUID and gamertag
        are stored in the instance variables `self.xuid` and `self.gamertag`.

        Returns:
            tuple:
                A tuple containing:
                    - bool: True if the XUID and gamertag were successfully retrieved,
                            False otherwise.
                    - dict or None: A dictionary containing the 'xuid' and 'gamertag'
                                    if the retrieval is successful, None if there is an error.
        """

        headers = {
            "x-xbl-contract-version": "2",
            "Accept-Encoding": "gzip, deflate",
            "accept": "application/json",
            "accept-language": "en-GB",
            "Authorization": self.xauthtoken,
        }
        get_player_info_url = (
            "https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag"
        )
        try:
            response = requests.get(url=get_player_info_url, headers=headers)

            if response.status_code != 200:
                error_messages = {
                    401: "Authentication error: Token expired.",
                    403: "Authentication error: Wrong token.",
                    429: "Too many requests made. Please try again later.",
                }
                error_message = error_messages.get(
                    response.status_code, f"Unexpected error: {response.status_code}"
                )
                self.printr(error_message)
                return False, None

            response_json = response.json()
            try:
                gamertag = response_json["profileUsers"][0]["settings"][0]["value"]
                xuid = response_json["profileUsers"][0]["id"]
            except (KeyError, IndexError):
                self.printr("Error: Data not found in the response. Please try again.")
                return False, None

            self.xuid = xuid
            self.gamertag = gamertag
            self.printg(f"XUID successfully retrieved: {self.xuid}")
            return True, {"xuid": xuid, "gamertag": gamertag}

        except requests.exceptions.RequestException:
            self.printr(
                "Network error: Unable to connect. Please check your connection and try again."
            )
            return False, None

        except:
            self.printr("Unexpected error: Please try again later.")
            return False, None

    @token_expiration_check
    def get_owned_game_info(self) -> tuple[bool, list[list] | None]:
        titles_list = None
        """
        Retrieves information about all games owned by the authenticated user.

        This method sends a request to retrieve a list of games owned by the user
        and stores detailed information about each game, including the game IDs,
        in the `self.games` attribute. The method returns a list of
        dictionaries, each containing information about a game (such as ID, name, img, etc.).

        Returns:
            tuple:
                A tuple containing:
                    - bool: True if at least one game was successfully retrieved,
                            False otherwise.
                    - list or None: A list of dictionaries, where each dictionary
                    contains detailed information about a game (e.g., ID, name, img),
                        or None if no games are found or
                    if there is an error.
        """

        headers = {
            "x-xbl-contract-version": "2",
            "Accept-Encoding": "gzip, deflate",
            "accept": "application/json",
            "accept-language": "en-GB",
            "Authorization": self.xauthtoken,
        }

        get_owned_game_info_url = f"https://titlehub.xboxlive.com/users/xuid({self.xuid})/titles/titleHistory/decoration/Achievement,scid"
        try:
            response = requests.get(url=get_owned_game_info_url, headers=headers)
            
            if response.status_code != 200:
                error_messages = {
                    401: "Authentication error: Token expired.",
                    403: "Authentication error: Wrong token.",
                    429: "Too many requests made. Please try again later.",
                }
                error_message = error_messages.get(
                    response.status_code, f"Unexpected error: {response.status_code}"
                )
                self.printr(error_message)
                return False, None

            response_json = response.json()
            titles = response_json.get("titles", None)
            if titles:
                titles_list = [
                    {
                        "name": f"{title.get('name', None)}",
                        "title_id": title["titleId"],
                        "img": title.get("displayImage", None),
                    }
                    for title in titles
                    if "titleId" in title
                ]

                for title in titles_list:
                    existing_game = next(
                        (
                            game
                            for game in self._games
                            if game["title_id"] == title["title_id"]
                        ),
                        None,
                    )

                    if existing_game:
                        self._games.remove(existing_game)
                        self.printr(
                            f"Removed existing game with ID {title['title_id']}."
                        )

                    self._games.append(title)

                self.printg("Game IDs were successfully retrieved.")
                return True, titles_list
            else:
                self.printr("No owned games found.")
                return False, None

        except KeyError:
            self.printr("An error occurred while collecting the IDs.")
            return False, None

        except requests.exceptions.RequestException:
            self.printr(
                "Network error: Unable to connect. Please check your connection and try again."
            )
            return False, None

        except KeyboardInterrupt:
            if titles:
                self.printg("Game IDs were successfully retrieved.")
                return True, titles_list
            else:
                self.printr("No owned games found.")
                return False, None

        except:
            self.printr("Unexpected error: Please try again later.")
            return False, None

    @token_expiration_check
    def get_achievements(self, game: list, *args, **kwargs) -> tuple[bool, list | None]:
        """
        Retrieves the achievements for a specific game.

        This method sends a request to retrieve a list of achievements for the specified
        game (identified by its `title_id`). If achievements are found, it populates the
        `game["achievements"]` attribute with detailed information about each achievement
        (such as ID, name, description, and img). The method then returns a tuple
        indicating the success of the operation and the game data.

        Returns:
            tuple:
                A tuple containing:
                    - bool: True if the achievements were successfully retrieved and added,
                            False otherwise.
                    - dict or None: A dictionary representing the game with the achievements
                                    added to it if successful, None if no achievements
                                    were found or if there was an error.
        """

        for index, game_in_list in enumerate(self._games):
            if game_in_list == game:
                self._games.pop(index)

        title_id = game["title_id"]
        game["achievements"] = []

        header = {
            "x-xbl-contract-version": "4",
            "Accept-Encoding": "gzip, deflate",
            "accept": "application/json",
            "accept-language": "en-GB",
            "Authorization": self.xauthtoken,
            "Host": "achievements.xboxlive.com",
            "Connection": "Keep-Alive",
        }

        self.printg(
            f"Getting achievements for {game['name']} with ID {game['title_id']}."
        )
        get_achievements_url = f"https://achievements.xboxlive.com/users/xuid({self.xuid})/achievements?titleId={title_id}"
        try:
            response = requests.get(url=get_achievements_url, headers=header)
            
            if response.status_code == 429:
                self.printr(
                    "Too many requests have been made and are being blocked. \nWait 10/15 minutes or more, or use a high-quality VPN."
                )
                raise KeyboardInterrupt
            
            if response.status_code != 200:
                error_messages = {
                    401: "Authentication error: Token expired.",
                    403: "Authentication error: Wrong token.",
                }
                error_message = error_messages.get(
                    response.status_code, f"Unexpected error: {response.status_code}"
                )
                self.printr(error_message)

                return False, None

            response_json = response.json()
            achievements = response_json.get("achievements", None)
            
            if response_json and achievements:
                for achievement in achievements:
                    achievement_id = achievement.get("id", None)
                    achievement_name = achievement.get("name", None)
                    achievement_description = achievement.get("description", None)
                    achievement_service_conf_id = achievement.get(
                        "serviceConfigId", None
                    )
                    achievement_progress_state = achievement.get("progressState", None)
                    achievement_progression_requirements = achievement.get(
                        "progression", {}
                    ).get("requirements", [])
                    achievement_progression_id = (
                        achievement_progression_requirements[0].get("id", None)
                        if achievement_progression_requirements
                        else None
                    )
                    achievement_name = achievement.get("name", None)
                    achievement_description = achievement.get("description", None)
                    achievement_media_assets = achievement.get("mediaAssets", [])
                    achievement_media_url = achievement_media_assets[0].get("url", None)

                    if (
                        achievement_service_conf_id
                        and achievement_progress_state != "Achieved"
                        and (
                            achievement_progression_id
                            == "00000000-0000-0000-0000-000000000000"
                            or achievement_progression_id.startswith(
                                "00000000-0000-0000-0000-"
                            )
                        )
                    ):
                        achievement_json = {
                            "achievement_id": achievement_id,
                            "achievement_name": achievement_name,
                            "achievement_description": achievement_description,
                            "achievement_service_conf_id": achievement_service_conf_id,
                            "achievement_img": achievement_media_url,
                        }
                        game["achievements"].append(achievement_json)

                if len(game["achievements"]) > 0:
                    self._games.append(game)
                    return True, game
                else:
                    return False, None

            else:
                self.printr("No achievements found.")
                return False, None

        except KeyboardInterrupt:
            new_games_list = []
            for index, game in enumerate(self.games):
                game_achievements = game.get("achievements")
                if game_achievements and len(game_achievements) > 0:
                    new_games_list.append(game)

            self._games = new_games_list
            raise KeyboardInterrupt

        except requests.exceptions.RequestException:
            self.printr(
                "Network error: Unable to connect. Please check your connection and try again."
            )
            return False, None

    @token_expiration_check
    def unlock_achievement(
        self, achievement_id: str, achievement_service_conf_id: str, title_id: str, *args, **kwargs
    ) -> tuple[bool | None]:
        """
        Unlocks a specific achievement for a game by updating its progress.

        This method sends a request to unlock an achievement for the specified game,
        marking it as 100% complete. The request includes the achievement ID, service
        configuration ID, and title ID. If any of the required parameters are missing,
        it returns an error message. The method returns a tuple indicating the success
        of the operation.

        Returns:
            tuple:
                A tuple containing:
                    - bool: True if the achievement was successfully unlocked,
                            False otherwise.
                    - None: No additional data is returned, only a status indication.
        """

        if any(
            val is None
            for val in [achievement_id, achievement_service_conf_id, title_id]
        ):
            self.printr("Missing information to unlock this achievement.")
            return False, None

        request_body = {
            "action": "progressUpdate",
            "serviceConfigId": achievement_service_conf_id,
            "titleId": title_id,
            "userId": self.xuid,
            "achievements": [{"id": achievement_id, "percentComplete": "100"}],
        }

        headers = {
            "x-xbl-contract-version": "2",
            "Accept-Encoding": "gzip, deflate",
            "accept": "application/json",
            "accept-language": "en-GB",
            "Authorization": self.xauthtoken,
            "Host": "achievements.xboxlive.com",
            "Connection": "Keep-Alive",
            "User-Agent": "XboxServicesAPI/2021.04.20210610.3 c",
        }

        unlock_achievement_url = f"https://achievements.xboxlive.com/users/xuid({self.xuid})/achievements/{achievement_service_conf_id}/update"
        try:
            response = requests.post(
                url=unlock_achievement_url, headers=headers, json=request_body
            )

            if response.status_code == 429:
                self.printr(
                    "Too many requests have been made and are being blocked. \nWait 10/15 minutes or more, or use a high-quality VPN."
                )
                raise KeyboardInterrupt

            if response.status_code != 200:
                error_messages = {
                    401: "Authentication error: Token expired.",
                    403: "Authentication error: Wrong token.",
                    304: "Achievement already unlocked.",
                }
                error_message = error_messages.get(
                    response.status_code, f"Unexpected error: {response.status_code}"
                )
                self.printr(error_message)

                return False, None

            self.printg(
                f"Achievement with ID {achievement_id} unlocked successfully for Game ID {title_id}."
            )
            return True, None

        except requests.exceptions.RequestException:
            self.printr(
                "Network error: Unable to connect. Please check your connection and try again."
            )
            return False, None
