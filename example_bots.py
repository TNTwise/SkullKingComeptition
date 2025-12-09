"""
Example bot implementations for Skull King.
"""
import random
from typing import List, Dict
from cards import Card, CardType, Suit
from player import Player


class DummyPlayer(Player):
    """A simple dummy player that makes completely random moves."""
    
    def __init__(self, name: str = "DummyPlayer"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Make a completely random bid."""
        return random.randint(0, round_num)
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Play a completely random card from hand."""
        return random.choice(hand)


class RandomBot(Player):
    """A bot that makes random bids and plays random legal cards."""
    
    def __init__(self, name: str = "RandomBot"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Make a random bid."""
        return random.randint(0, round_num)
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Play a random legal card."""
        # Get legal cards (simplified - just return any card)
        return random.choice(hand)


class ConservativeBot(Player):
    """A bot that bids conservatively and tries to avoid winning tricks."""
    
    def __init__(self, name: str = "ConservativeBot"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Bid low, preferring to bid 0."""
        # Count escape cards
        escape_count = sum(1 for card in hand if card.card_type == CardType.ESCAPE)
        # Bid 0 if we have enough escapes, otherwise bid 1
        if escape_count >= round_num:
            return 0
        return min(1, round_num)
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Try to play escape cards or low cards."""
        # Prefer escape cards
        escape_cards = [c for c in hand if c.card_type == CardType.ESCAPE]
        if escape_cards:
            return escape_cards[0]
        
        # Otherwise play lowest numbered card
        number_cards = [c for c in hand if c.card_type == CardType.NUMBER]
        if number_cards:
            return min(number_cards, key=lambda c: c.value)
        
        # Fallback to random
        return random.choice(hand)


class AggressiveBot(Player):
    """A bot that bids high and tries to win tricks with strong cards."""
    
    def __init__(self, name: str = "AggressiveBot"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Bid high based on strong cards in hand."""
        strong_cards = sum(1 for card in hand 
                          if card.card_type in [CardType.PIRATE, CardType.MERMAID, 
                                                CardType.SKULL_KING] or
                          (card.card_type == CardType.NUMBER and card.value >= 10))
        bid = min(strong_cards, round_num)
        return max(1, bid)  # At least bid 1
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Play strong cards to win tricks."""
        # If we need to win this trick, play strong cards
        tricks_needed = bids.get(self, 0) - tricks_won.get(self, 0)
        
        if tricks_needed > 0 and current_trick:
            # Try to win - play strongest card
            special_cards = [c for c in hand if c.card_type in 
                           [CardType.SKULL_KING, CardType.PIRATE, CardType.MERMAID]]
            if special_cards:
                # Prefer Skull King, then Pirate, then Mermaid
                if any(c.card_type == CardType.SKULL_KING for c in special_cards):
                    return next(c for c in special_cards if c.card_type == CardType.SKULL_KING)
                if any(c.card_type == CardType.PIRATE for c in special_cards):
                    return next(c for c in special_cards if c.card_type == CardType.PIRATE)
                return special_cards[0]
            
            # Play high numbered cards
            number_cards = [c for c in hand if c.card_type == CardType.NUMBER]
            if number_cards:
                return max(number_cards, key=lambda c: c.value)
        else:
            # Don't need to win - play escape or low cards
            escape_cards = [c for c in hand if c.card_type == CardType.ESCAPE]
            if escape_cards:
                return escape_cards[0]
            number_cards = [c for c in hand if c.card_type == CardType.NUMBER]
            if number_cards:
                return min(number_cards, key=lambda c: c.value)
        
        return random.choice(hand)
    

class ExitBot(Player):
    """A bot that would rather quit than play."""
    
    def __init__(self, name: str = "QuitBot"):
        super().__init__(name)
        
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Make a random bid."""
        
        return random.randint(0, round_num)
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Play a random legal card."""
        # Get legal cards (simplified - just return any card)
        exit()