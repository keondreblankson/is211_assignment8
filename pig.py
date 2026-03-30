import argparse
import random
import time


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def decide(self, turn_total):
        raise NotImplementedError("Subclasses must implement decide().")


class HumanPlayer(Player):
    def decide(self, turn_total):
        while True:
            choice = input(
                f"{self.name}, your turn total is {turn_total}. Roll or hold? "
            ).strip().lower()

            if choice in ("roll", "r"):
                return "roll"
            if choice in ("hold", "h"):
                return "hold"

            print("Invalid choice. Please enter 'roll' or 'hold'.")


class ComputerPlayer(Player):
    def decide(self, turn_total):
        hold_value = min(25, 100 - self.score)

        if turn_total >= hold_value:
            print(f"{self.name} chooses to hold.")
            return "hold"

        print(f"{self.name} chooses to roll.")
        return "roll"


class PlayerFactory:
    @staticmethod
    def create_player(player_type, name):
        player_type = player_type.lower()

        if player_type == "human":
            return HumanPlayer(name)
        if player_type == "computer":
            return ComputerPlayer(name)

        raise ValueError(f"Invalid player type: {player_type}")


class Game:
    WINNING_SCORE = 100

    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.current_player_index = 0
        self.game_over = False
        self.winner = None

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_other_player(self):
        return self.players[1 - self.current_player_index]

    def switch_player(self):
        self.current_player_index = 1 - self.current_player_index

    def roll_die(self):
        return random.randint(1, 6)

    def display_scores(self):
        print(
            f"Scores -> {self.players[0].name}: {self.players[0].score}, "
            f"{self.players[1].name}: {self.players[1].score}"
        )

    def take_turn(self):
        player = self.get_current_player()
        turn_total = 0

        print(f"\n--- {player.name}'s turn ---")
        self.display_scores()

        while True:
            choice = player.decide(turn_total)

            if choice == "roll":
                roll = self.roll_die()
                print(f"{player.name} rolled a {roll}.")

                if roll == 1:
                    print(f"{player.name} rolled a 1 and loses all turn points.")
                    turn_total = 0
                    break

                turn_total += roll
                print(f"{player.name}'s turn total is now {turn_total}.")

            elif choice == "hold":
                player.score += turn_total
                print(f"{player.name} holds and adds {turn_total} points.")
                print(f"{player.name}'s total score is now {player.score}.")
                break

        if player.score >= self.WINNING_SCORE:
            self.game_over = True
            self.winner = player
            return

        self.switch_player()

    def play(self):
        print("Starting Pig Game!")

        while not self.game_over:
            self.take_turn()

        print(f"\nGame Over! {self.winner.name} wins with {self.winner.score} points!")


class TimedGameProxy:
    def __init__(self, game, time_limit=60):
        self.game = game
        self.time_limit = time_limit
        self.start_time = None

    def time_expired(self):
        return (time.time() - self.start_time) >= self.time_limit

    def determine_winner_on_time(self):
        player1 = self.game.players[0]
        player2 = self.game.players[1]

        print("\nTime is up!")

        if player1.score > player2.score:
            self.game.winner = player1
        elif player2.score > player1.score:
            self.game.winner = player2
        else:
            self.game.winner = None

        self.game.game_over = True

    def play(self):
        print("Starting Timed Pig Game!")
        self.start_time = time.time()

        while not self.game.game_over:
            if self.time_expired():
                self.determine_winner_on_time()
                break

            self.game.take_turn()

            if not self.game.game_over and self.time_expired():
                self.determine_winner_on_time()
                break

        print("\nFinal Scores:")
        self.game.display_scores()

        if self.game.winner is None:
            print("The game ends in a tie.")
        else:
            print(
                f"Game Over! {self.game.winner.name} wins with "
                f"{self.game.winner.score} points!"
            )


def parse_args():
    parser = argparse.ArgumentParser(description="Play the game of Pig.")
    parser.add_argument(
        "--player1",
        choices=["human", "computer"],
        required=True,
        help="Type of player 1: human or computer",
    )
    parser.add_argument(
        "--player2",
        choices=["human", "computer"],
        required=True,
        help="Type of player 2: human or computer",
    )
    parser.add_argument(
        "--timed",
        action="store_true",
        help="Play a timed version of the game (1 minute limit)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    player1 = PlayerFactory.create_player(args.player1, "Player 1")
    player2 = PlayerFactory.create_player(args.player2, "Player 2")

    game = Game(player1, player2)

    if args.timed:
        timed_game = TimedGameProxy(game)
        timed_game.play()
    else:
        game.play()


if __name__ == "__main__":
    main()