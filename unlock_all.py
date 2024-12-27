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
    add_extra_game_id = input(
        "Would you like to add games that you don't own as well? \nYou could still unlock their achievements, \nbut it will take more time to retrieve all the achievements.\n(1) Yes \n(2) No \n:"
    )
    if add_extra_game_id == "1":
        xbox.add_extra_games()
        break
    if add_extra_game_id == "2":
        if len(xbox.games) <= 0:
            exit(0)
        break
    else:
        continue

xbox.printy(f"\nGamertag: {player_info['gamertag']}\n")
games = xbox.games
games_completed = 0

while True:
    try:
        for index, game in enumerate(games):
            if 'processed' in games[index] and games[index]['processed']:
                continue

            success, _ = xbox.get_achievements(game=game)

            games_completed += 1

            xbox.printg(
                f"Achievements collected for game {games_completed}/{len(games)}! \n"
            )

            games[index]['processed'] = True

        break

    except KeyboardInterrupt:
        xbox.printr("\nAchievement Collection Interrupted.")
        xbox.printy(
            "Achievement Collection will resume in 10 minutes. \nPress Ctrl+C to start unlocking achievements."
        )
        timer_start = time.time()
        try:
            while True:
                if time.time() - timer_start >= 600:
                    break
            continue
        except KeyboardInterrupt:
            pass
    break

new_games_list = []
for index, game in enumerate(xbox.games):
    game_achievements = game.get("achievements", None)
    if game_achievements and len(game_achievements) > 0:
        if "processed" in game:
            game.pop("processed")
        new_games_list.append(game)
xbox._games = new_games_list

if len(xbox.games) <= 0:
    xbox.printr("\nThere are no unlockable achievements.")
    exit(0)

print("\n")

xbox.printy(f"\nAll achievements from {len(xbox.games)} games are about to be unlocked!\n")

total_achievements = 0
achievements_completed = 0
games_completed = 0
games = xbox.games

while True:
    for index, game in enumerate(games):
        game = games[index]
        try:
            if 'processed_unlock' in games[index] and games[index]['processed_unlock']:
                continue
            
            achievements_completed = 0
            title_id = game["title_id"]
            game_achievements = game["achievements"]
            total_achievements = len(game_achievements)

            for achievement in game_achievements:
                if achievement.get('unlocked', False):
                    achievements_completed += 1
                    continue

                achievement_id = achievement["achievement_id"]
                achievement_service_conf_id = achievement["achievement_service_conf_id"]

                success, _ = xbox.unlock_achievement(
                    title_id=title_id,
                    achievement_id=achievement_id,
                    achievement_service_conf_id=achievement_service_conf_id,
                )

                achievements_remaining = total_achievements - (achievements_completed + 1)

                achievements_completed += 1

                xbox.printg(
                    f"Unlocking achievements: {achievements_completed}/{total_achievements} achievements, {games_completed}/{len(xbox.games)} games \n"
                )

                achievement['unlocked'] = True

            print("\n")

            games_completed += 1
            achievements_completed = 0
            games[index]['processed_unlock'] = True

            xbox.printy(
                f"All possible unlockable achievements for the game {game.get('name', 'Unknown')} have been unlocked.\n"
            )
        except KeyboardInterrupt:
            xbox.printr("\nInterruption of achievement unlocking.")
            xbox.printy(
                "Achievements unlocking will continue in 10 minutes, \nPress Ctrl+C to exit."
            )
            timer_start = time.time()
            try:
                while True:
                    if time.time() - timer_start >= 600:
                        break
                break
            except KeyboardInterrupt:
                xbox.printr("\nExiting...")
                exit(0)
                
    if all(game.get('processed_unlock') is True for game in games):
        break
    else:
        continue

xbox.printy("\nAll possible unlockable achievements have been unlocked.")
