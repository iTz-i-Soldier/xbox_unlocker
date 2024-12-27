import time
from xbox_unlocker import XboxUnlocker

xbox = XboxUnlocker()

success, token = xbox.get_token_from_browser()
if not token:
    exit(0)

success, player_info = xbox.get_player_info()
if not success:
    exit(0)

xbox.get_owned_game_info()

print("\n")

while True:
    try:
        add_extra_game_id = input(
            "Would you like to add games that you don't own as well? \nYou could still unlock their achievements, \nbut it will take more time to retrieve all the achievements.\n(1) Yes \n(2) No \nCtrl + C to exit \n:"
        )
    except KeyboardInterrupt:
        xbox.printr("\nExiting...")
        exit(0)

    if add_extra_game_id == "1":
        xbox.add_extra_games()
        break
    if add_extra_game_id == "2":
        if len(xbox.games) <= 0:
            exit(0)
        break
    else:
        continue

while True:
    try:
        for index, game in enumerate(xbox.games):
            print(f"({index + 1}) {game.get('name', 'Unknown')}")
        print(f"({len(xbox.games) + 1}) All")

        choice = input(
            "Enter the game number for which you want to get the achievement,\n"
            "or press Ctrl + C to exit \n:"
        )

        game_achievement_choice = int(choice)

        if 1 <= game_achievement_choice <= len(xbox.games):
            xbox._games = [xbox.games[game_achievement_choice - 1]]
            break
        elif game_achievement_choice == len(xbox.games) + 1:
            xbox.printg("Collecting all the achievements...")
            break
        else:
            continue
    except KeyboardInterrupt:
        xbox.printr("\nExiting...")
        exit(0)
    except Exception as e:
        print(e)
        continue

xbox.printy(f"\nGamertag: {player_info['gamertag']}\n")
games = xbox.games
total_games = len(games)
games_completed = 0

game_index = 0

while game_index < total_games:
    try:
        game = games[game_index]
        start_time = time.time()
        success, _ = xbox.get_achievements(game=game)

        if success:
            games_completed += 1
            xbox.printg(
                f"Achievements collected for game {games_completed}/{total_games}!"
            )

        game_index += 1

        end_time = time.time()
        elapsed_time = end_time - start_time

    except KeyboardInterrupt:
        xbox.printr("\nAchievement Collection Interrupted.")
        print("(1) to continue")
        print("(2) to the game list")
        print("Ctrl + C to exit")
        while True:
            try:
                choice = int(input(":"))
                if choice == 1:
                    break
                elif choice == 2:
                    game_index = 0
                    break
            except KeyboardInterrupt:
                xbox.printr("\nExiting...")
                exit(0)
            except:
                continue

if len(xbox.games) <= 0:
    xbox.printr("There are no unlockable achievements.")
    exit(0)

print("\n")

while True:
    for index, game in enumerate(xbox.games):
        print(f"({index + 1}) {game.get('name', 'Unknown')}")

    print(
        "Enter the game number for which you want to unlock the achievement, \nor press Ctrl + C to exit."
    )

    try:
        choice_game = int(input(":")) - 1

        if choice_game < 0 or choice_game >= len(xbox.games):
            continue

    except KeyboardInterrupt:
        xbox.printr("\nExiting...")
        exit(0)
    except:
        continue

    chosen_game = xbox.games[choice_game]
    xbox.printg(f"\nThe chosen game is {chosen_game.get('name', 'Unknown')}.")
    while True:

        game_achievements = chosen_game.get("achievements", None)
        if game_achievements is None:
            xbox.printr("There are no achievements for this game.")
            break

        for index, achievement in enumerate(game_achievements):
            print(f"({index + 1}) {achievement.get('achievement_name', 'Unknown')}")

        print(
            "\nEnter the achievement number you want to unlock, \nor press Ctrl + C to return to the game list."
        )

        try:
            choice_achievement = int(input(":")) - 1

            if choice_achievement < 0 or choice_achievement >= len(game_achievements):
                continue

        except KeyboardInterrupt:
            xbox.printr("\nReturn to the game list.\n")
            break
        
        except:
            continue

        chosen_achievement = game_achievements[choice_achievement]
        xbox.printg(
            f'The chosen achievement is "{chosen_achievement.get("achievement_name", "Unknown")}" \nfrom "{chosen_game.get("name", "Unknown")}".'
        )

        achievement_id = chosen_achievement.get("achievement_id", None)
        achievement_service_conf_id = chosen_achievement.get(
            "achievement_service_conf_id", None
        )
        title_id = chosen_game.get("title_id", None)

        if achievement_id and achievement_service_conf_id and title_id:
            try:
                success, _ = xbox.unlock_achievement(
                    achievement_id, achievement_service_conf_id, title_id
                )
            except KeyboardInterrupt:
                xbox.printr("\nInterruption of achievement unlocking.")
                print("Press Enter to return to the game list., \nor Ctrl + C to exit")
                try:
                    input(":")
                except KeyboardInterrupt:
                    xbox.printr("\nExiting...")
                    exit(0)

            if success:
                xbox.printg(
                    f'"{chosen_achievement.get("achievement_name", "Unknown")}" unlocked successfully'
                )
                chosen_game["achievements"].pop(choice_achievement)
        else:
            xbox.printr(
                "Some important information to unlock the achievement is missing, impossible to proceed."
            )

        break
