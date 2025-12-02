"""
Card and Deck classes for Skull King game.
"""
from enum import Enum
from typing import List, Optional
import random


class Suit(Enum):
    """Card suits in Skull King."""
    RED = "Red"
    YELLOW = "Yellow"
    BLUE = "Blue"
    GREEN = "Green"
    SPECIAL = "Special"  # For special cards


class CardType(Enum):
    """Types of special cards."""
    NUMBER = "Number"
    ESCAPE = "Escape"
    PIRATE = "Pirate"
    MERMAID = "Mermaid"
    SKULL_KING = "Skull King"
    TIGRESS = "Tigress"
    JOLLY_ROGER = "Jolly Roger"  # Trump suit


class Card:
    """Represents a single card in Skull King."""
    
    def __init__(self, card_type: CardType, suit: Optional[Suit] = None, value: Optional[int] = None):
        """
        Create a card.
        
        Args:
            card_type: Type of card (NUMBER, ESCAPE, PIRATE, etc.)
            suit: Suit for numbered cards (None for special cards)
            value: Number value (1-13) for numbered cards, None for special cards
        """
        self.card_type = card_type
        self.suit = suit
        self.value = value
        
        # Validate card
        if card_type == CardType.NUMBER:
            if suit is None or suit == Suit.SPECIAL:
                raise ValueError("Number cards must have a suit")
            if value is None or value < 1 or value > 13:
                raise ValueError("Number cards must have value 1-13")
        elif card_type in [CardType.ESCAPE, CardType.PIRATE, CardType.MERMAID, 
                           CardType.SKULL_KING, CardType.TIGRESS]:
            self.suit = Suit.SPECIAL
            self.value = None
    
    def __str__(self):
        if self.card_type == CardType.NUMBER:
            return f"{self.value} of {self.suit.value}"
        elif self.card_type == CardType.ESCAPE:
            return "Escape"
        elif self.card_type == CardType.PIRATE:
            return "Pirate"
        elif self.card_type == CardType.MERMAID:
            return "Mermaid"
        elif self.card_type == CardType.SKULL_KING:
            return "Skull King"
        elif self.card_type == CardType.TIGRESS:
            return "Tigress"
        elif self.card_type == CardType.JOLLY_ROGER:
            return f"{self.value} of Jolly Roger (Trump)"
        return "Unknown Card"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return (self.card_type == other.card_type and 
                self.suit == other.suit and 
                self.value == other.value)
    
    def __hash__(self):
        return hash((self.card_type, self.suit, self.value))
    
    def can_follow_suit(self, led_suit: Suit) -> bool:
        """Check if this card can follow the led suit."""
        if self.card_type in [CardType.ESCAPE, CardType.PIRATE, CardType.MERMAID,
                              CardType.SKULL_KING, CardType.TIGRESS]:
            return True  # Special cards can always be played
        return self.suit == led_suit
    
    def beats(self, other: 'Card', led_suit: Suit, trump_suit: Optional[Suit] = None) -> bool:
        """
        Determine if this card beats another card in a trick.
        
        Modified rule: Mermaids beat Skull King but lose to Pirates.
        Hierarchy: Escape < Numbered Cards < Jolly Roger (trump) < Mermaid < Pirate < Skull King
        Exception: Mermaid beats Skull King
        """
        # Escape cards never win (unless everyone plays escape)
        if self.card_type == CardType.ESCAPE:
            return False
        if other.card_type == CardType.ESCAPE:
            return True
        
        # Special cards hierarchy
        # Modified rule: Mermaid beats Skull King but loses to Pirate
        # So: Skull King < Mermaid < Pirate
        special_hierarchy = {
            CardType.SKULL_KING: 3,
            CardType.MERMAID: 4,  # Beats Skull King
            CardType.PIRATE: 5    # Beats Mermaid and Skull King
        }
        
        self_special = special_hierarchy.get(self.card_type)
        other_special = special_hierarchy.get(other.card_type)
        
        # Both are special cards
        if self_special is not None and other_special is not None:
            # Use hierarchy: Skull King (3) < Mermaid (4) < Pirate (5)
            return self_special > other_special
        
        # One is special, one is not
        if self_special is not None:
            return True
        if other_special is not None:
            return False
        
        # Both are numbered cards
        if self.card_type == CardType.NUMBER and other.card_type == CardType.NUMBER:
            # Check if either is trump
            if trump_suit:
                self_is_trump = self.suit == trump_suit
                other_is_trump = other.suit == trump_suit
                if self_is_trump and not other_is_trump:
                    return True
                if other_is_trump and not self_is_trump:
                    return False
                # Both trump or both not trump - compare values
                if self_is_trump and other_is_trump:
                    return self.value > other.value
            
            # Same suit - higher value wins
            if self.suit == other.suit:
                return self.value > other.value
            # Different suits - only the led suit matters
            if self.suit == led_suit:
                return True
            if other.suit == led_suit:
                return False
            # Neither matches led suit - shouldn't happen in valid play
            return False
        
        return False


class Deck:
    """Represents a deck of Skull King cards."""
    
    def __init__(self):
        """Create a standard Skull King deck."""
        self.cards: List[Card] = []
        self._create_deck()
    
    def _create_deck(self):
        """Create the standard Skull King deck."""
        # Number cards: 1-13 in each of 4 suits
        for suit in [Suit.RED, Suit.YELLOW, Suit.BLUE, Suit.GREEN]:
            for value in range(1, 14):
                self.cards.append(Card(CardType.NUMBER, suit, value))
        
        # Special cards
        # 5 Escape cards
        for _ in range(5):
            self.cards.append(Card(CardType.ESCAPE))
        
        # 2 Mermaids
        for _ in range(2):
            self.cards.append(Card(CardType.MERMAID))
        
        # 2 Pirates
        for _ in range(2):
            self.cards.append(Card(CardType.PIRATE))
        
        # 1 Skull King
        self.cards.append(Card(CardType.SKULL_KING))
        
        # 1 Tigress
        self.cards.append(Card(CardType.TIGRESS))
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int) -> List[Card]:
        """Deal a specified number of cards from the deck."""
        if num_cards > len(self.cards):
            raise ValueError(f"Not enough cards in deck. Requested {num_cards}, have {len(self.cards)}")
        
        dealt = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt
    
    def __len__(self):
        return len(self.cards)

