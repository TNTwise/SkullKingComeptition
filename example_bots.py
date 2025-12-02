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


class SmartBot(Player):
    """A smarter bot that considers the game state more carefully."""
    
    def __init__(self, name: str = "SmartBot"):
        super().__init__(name)
    
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict[Player, int]) -> int:
        """Make a bid based on hand strength."""
        # Count strong cards
        skull_king = sum(1 for c in hand if c.card_type == CardType.SKULL_KING)
        pirates = sum(1 for c in hand if c.card_type == CardType.PIRATE)
        mermaids = sum(1 for c in hand if c.card_type == CardType.MERMAID)
        high_cards = sum(1 for c in hand if c.card_type == CardType.NUMBER and c.value >= 11)
        
        # Estimate tricks we can win
        estimated_tricks = skull_king + pirates + mermaids + (high_cards // 2)
        
        # Adjust based on round number
        if round_num <= 3:
            estimated_tricks = min(estimated_tricks, 2)
        
        return min(max(0, estimated_tricks), round_num)
    
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list],
                  bids: Dict[Player, int], tricks_won: Dict[Player, int], round_num: int) -> Card:
        """Play strategically based on bid and current state."""
        my_bid = bids.get(self, 0)
        my_tricks = tricks_won.get(self, 0)
        tricks_needed = my_bid - my_tricks
        tricks_remaining = round_num - len(previous_tricks)
        
        # If we've already met our bid, try to avoid winning
        if tricks_needed <= 0:
            escape_cards = [c for c in hand if c.card_type == CardType.ESCAPE]
            if escape_cards:
                return escape_cards[0]
            low_cards = [c for c in hand if c.card_type == CardType.NUMBER]
            if low_cards:
                return min(low_cards, key=lambda c: c.value)
        
        # If we need tricks, try to win
        if tricks_needed > 0 and current_trick:
            # Analyze current trick
            led_suit = None
            if current_trick:
                first_card = current_trick[0][1]
                if first_card.card_type == CardType.NUMBER:
                    led_suit = first_card.suit
            
            # Check if we can win
            highest_so_far = None
            if current_trick:
                highest_so_far = current_trick[0][1]
                for _, card in current_trick[1:]:
                    if card.beats(highest_so_far, led_suit or Suit.SPECIAL):
                        highest_so_far = card
            
            # Try to beat the highest card
            if highest_so_far:
                winning_cards = [c for c in hand if c.beats(highest_so_far, led_suit or Suit.SPECIAL)]
                if winning_cards:
                    # Prefer using weaker cards if possible
                    if tricks_needed == tricks_remaining:
                        # Need all remaining tricks - use strongest
                        return max(winning_cards, key=lambda c: self._card_strength(c))
                    else:
                        # Can save strong cards - use weakest that still wins
                        return min(winning_cards, key=lambda c: self._card_strength(c))
            
            # Can't win, play low
            escape_cards = [c for c in hand if c.card_type == CardType.ESCAPE]
            if escape_cards:
                return escape_cards[0]
            low_cards = [c for c in hand if c.card_type == CardType.NUMBER]
            if low_cards:
                return min(low_cards, key=lambda c: c.value)
        
        # Default: follow suit if possible, otherwise play low
        if current_trick:
            first_card = current_trick[0][1]
            if first_card.card_type == CardType.NUMBER:
                led_suit = first_card.suit
                following = [c for c in hand if c.card_type == CardType.NUMBER and c.suit == led_suit]
                if following:
                    return min(following, key=lambda c: c.value)
        
        return random.choice(hand)
    
    def _card_strength(self, card: Card) -> int:
        """Get numeric strength of a card (higher = stronger)."""
        if card.card_type == CardType.SKULL_KING:
            return 100
        elif card.card_type == CardType.PIRATE:
            return 80
        elif card.card_type == CardType.MERMAID:
            return 70
        elif card.card_type == CardType.NUMBER:
            return card.value
        elif card.card_type == CardType.ESCAPE:
            return 0
        return 1

