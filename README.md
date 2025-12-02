# Skull King Bot Competition

A Python implementation of the Skull King card game where players create bots to compete against each other.

## Installation

### Basic Installation (Tkinter - Default)
No additional dependencies required! Python 3.7+ with tkinter (usually included).

### Enhanced Installation (Recommended)
For the best performance and smoothest rendering:

**Pygame (Best Performance - Recommended)**
```bash
pip install pygame
```

## Game Rules

Skull King is a trick-taking card game played over 10 rounds. In each round:
- Players receive a number of cards equal to the round number (1 card in round 1, 2 in round 2, etc.)
- Players simultaneously bid how many tricks they expect to win
- Players take turns playing cards, following suit when possible
- The player who wins the trick leads the next one
- Scoring: 20 points per trick bid + 10 bonus for correct bid, or -10 points per trick off

### Card Hierarchy (Modified Rule)
- **Escape** < **Numbered Cards** < **Mermaid** < **Pirate** < **Skull King**
- **Special Rule**: Mermaids beat Skull King but lose to Pirates
- **Special Cards**: Can be played at any time, regardless of suit led

### Special Bonuses
- Capturing Skull King with Mermaid: +100 points
- Capturing Skull King with Pirate: +50 points

## Creating Your Bot

**examples in example_bots.py**

1. Create a new Python file (e.g., `my_bot.py`)

2. Import the Player base class:
```python
from player import Player
from cards import Card, CardType
from typing import List, Dict
```

3. Create your bot class:
```python
class MyBot(Player):
    def __init__(self, name: str = "MyBot"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """
        Decide how many tricks to bid.
        
        Args:
            hand: Your cards for this round
            round_num: Current round (1-10)
            previous_bids: Other players' bids (may be empty if simultaneous)
        
        Returns:
            Number of tricks you expect to win (0 to round_num)
        """
        # Your bidding strategy here
        return 1
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], 
                  previous_tricks: List[list], bids: Dict[Player, int], 
                  tricks_won: Dict[Player, int], round_num: int) -> Card:
        """
        Choose which card to play.
        
        Args:
            hand: Your current hand
            current_trick: List of (player, card) tuples for current trick
            previous_tricks: List of previous tricks
            bids: All players' bids for this round
            tricks_won: Tricks won so far this round
            round_num: Current round number
        
        Returns:
            The card to play (must be in hand)
        """
        # Your card playing strategy here
        return hand[0]
```

4. Add your bot to `main.py`:
```python
from my_bot import MyBot
bots.append(MyBot("MyBot"))
```

## Running the Competition

### With GUI (Recommended for Display)
```bash
python main.py
```

The GUI will show:
- Current round and trick information
- Each player's bid, tricks won, and hand
- Current trick cards
- Scores
- Buttons to advance one trick at a time or auto-play a round

### Headless Mode (For Testing)
```bash
python main.py --headless [num_games]
```

Runs without GUI, useful for testing multiple games quickly.

## Files

- `cards.py` - Card and deck classes
- `game_engine.py` - Game logic and state management
- `player.py` - Base Player class for bots
- `example_bots.py` - Example bot implementations
- `gui.py` - GUI for displaying the game (Tkinter version)
- `gui_customtkinter.py` - GUI for displaying the game (CustomTkinter version - smoother!)
- `main.py` - Main competition runner
- `requirements.txt` - Optional dependencies

## Example Bots

- **DummyPlayer**: Makes completely random moves
- **RandomBot**: Makes random bids and plays random cards
- **ConservativeBot**: Bids low and tries to avoid winning tricks
- **AggressiveBot**: Bids high and tries to win with strong cards
- **SmartBot**: More sophisticated strategy considering game state

## Tips for Creating a Winning Bot

1. **Bidding Strategy**: Accurately predict how many tricks you can win based on your hand strength
2. **Card Management**: Save strong cards for when you need them, use weak cards when you don't
3. **Track State**: Use `previous_tricks` and `tricks_won` to understand what cards have been played
4. **Follow Suit**: When you must follow suit, play the lowest card that can't win (if you don't want to win)
5. **Special Cards**: Use Pirates, Mermaids, and Skull King strategically - they can capture each other!

