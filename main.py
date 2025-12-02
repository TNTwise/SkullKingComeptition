"""
Main competition runner for Skull King bot competition.
"""
import sys
from typing import List
from game_engine import SkullKingGame

# Try to use Pygame first (best performance), then CustomTkinter, then regular tkinter
try:
    from gui_pygame import SkullKingGUI
    USE_PYGAME = True
    print("Using Pygame GUI (best performance)")
except ImportError:
    try:
        from gui_customtkinter import SkullKingGUI
        USE_PYGAME = False
        print("Using CustomTkinter GUI")
    except ImportError:
        try:
            from gui import SkullKingGUI
            USE_PYGAME = False
            print("Using Tkinter GUI (basic)")
            print("Note: Install pygame or customtkinter for better rendering:")
            print("  pip install pygame")
            print("  or")
            print("  pip install customtkinter")
        except ImportError:
            print("Error: Could not import GUI module")
            sys.exit(1)

from example_bots import DummyPlayer, RandomBot, ConservativeBot, AggressiveBot, SmartBot
from player import Player


def create_competition_bots() -> List[Player]:
    """
    Create the bots for the competition.
    
    Players should create their own bot classes that inherit from Player
    and implement make_bid() and play_card() methods.
    
    To add your bot:
    1. Create a new file (e.g., my_bot.py)
    2. Import Player: from player import Player
    3. Create a class that inherits from Player
    4. Implement make_bid() and play_card() methods
    5. Import and add your bot here
    """
    bots = [
        RandomBot("RandomBot"),
        ConservativeBot("ConservativeBot"),
        AggressiveBot("AggressiveBot"),
        SmartBot("SmartBot"),
    ]
    
    # TODO: Add your custom bots here
    # Example:
    # from my_bot import MyCustomBot
    # bots.append(MyCustomBot("MyBot"))
    
    return bots


def run_competition_with_gui(num_rounds: int = 10):
    """Run the competition with GUI display."""
    bots = create_competition_bots()
    
    if len(bots) < 2:
        print("Error: Need at least 2 bots to play")
        return
    
    print(f"Starting Skull King competition with {len(bots)} bots")
    print(f"Bots: {[bot.name for bot in bots]}")
    
    # Create game
    game = SkullKingGame(bots, num_rounds)
    
    # Start first round
    game.current_round = 1
    game.start_round(1)
    game.collect_bids()
    game.start_trick()
    
    # Create and run GUI
    gui = SkullKingGUI(game)
    gui.update_display()
    gui.run()
    
    # Print final results
    final_scores = game.get_final_scores()
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (player, score) in enumerate(sorted_scores, 1):
        print(f"{i}. {player.name}: {score} points")
    print("="*50)


def run_competition_headless(num_rounds: int = 10, num_games: int = 1):
    """Run the competition without GUI (for testing)."""
    bots = create_competition_bots()
    
    if len(bots) < 2:
        print("Error: Need at least 2 bots to play")
        return
    
    all_scores = {bot: [] for bot in bots}
    
    for game_num in range(num_games):
        print(f"\nGame {game_num + 1}/{num_games}")
        print("-" * 50)
        
        game = SkullKingGame(bots, num_rounds)
        
        # Play all rounds
        for round_num in range(1, num_rounds + 1):
            game.current_round = round_num
            game.start_round(round_num)
            game.collect_bids()
            
            print(f"\nRound {round_num}")
            print(f"Bids: {[(p.name, game.state.bids[p]) for p in bots]}")
            
            # Play all tricks
            while not game.is_round_complete():
                if not game.state.current_trick:
                    game.start_trick()
                
                # Play all cards in current trick
                while game.state.current_trick and \
                      len(game.state.current_trick.cards_played) < len(bots):
                    # Find next player
                    played_players = {p for p, _ in game.state.current_trick.cards_played}
                    next_player = next(p for p in bots if p not in played_players)
                    
                    # Get card from player
                    hand = game.state.hands[next_player]
                    current_trick_list = [(p, c) for p, c in game.state.current_trick.cards_played]
                    previous_tricks = [[(p, c) for p, c in t.cards_played] for t in game.state.tricks]
                    
                    try:
                        card = next_player.play_card(
                            hand,
                            current_trick_list,
                            previous_tricks,
                            game.state.bids,
                            game.state.tricks_won,
                            round_num
                        )
                        
                        legal_cards = game.state.get_legal_cards(next_player)
                        if card not in legal_cards:
                            card = legal_cards[0] if legal_cards else hand[0]
                        
                        game.play_card(next_player, card)
                    except Exception as e:
                        print(f"Error: {e}")
                        break
            
            # Calculate scores
            round_scores = game.calculate_scores()
            bonuses = game.check_special_bonuses()
            
            print(f"Tricks won: {[(p.name, game.state.tricks_won[p]) for p in bots]}")
            print(f"Round scores: {[(p.name, round_scores[p]) for p in bots]}")
            if any(bonuses.values()):
                print(f"Bonuses: {[(p.name, bonuses[p]) for p in bots if bonuses[p] > 0]}")
        
        # Final scores
        final_scores = game.get_final_scores()
        for bot in bots:
            all_scores[bot].append(final_scores[bot])
        
        print(f"\nFinal scores: {[(p.name, final_scores[p]) for p in bots]}")
    
    # Print statistics
    if num_games > 1:
        print("\n" + "="*50)
        print("STATISTICS (across all games)")
        print("="*50)
        for bot in bots:
            avg_score = sum(all_scores[bot]) / len(all_scores[bot])
            print(f"{bot.name}: Avg {avg_score:.1f} points")
        print("="*50)


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--headless":
        num_games = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_competition_headless(num_games=num_games)
    else:
        # Run with GUI by default
        run_competition_with_gui()

