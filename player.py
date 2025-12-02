"""
Base Player class for Skull King bots.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from cards import Card


class Player(ABC):
    """Base class for all Skull King bot players."""
    
    def __init__(self, name: str):
        """
        Initialize a player.
        
        Args:
            name: Name of the player/bot
        """
        self.name = name
        self.hand: List[Card] = []
    
    @abstractmethod
    def make_bid(self, hand: List[Card], round_num: int, previous_bids: Dict['Player', int]) -> int:
        """
        Make a bid for the current round.
        
        Args:
            hand: The player's hand for this round
            round_num: Current round number (1-10)
            previous_bids: Dictionary of bids made by other players (may be empty if bidding simultaneously)
        
        Returns:
            Number of tricks the player expects to win (0 to round_num)
        """
        pass
    
    @abstractmethod
    def play_card(self, hand: List[Card], current_trick: List[tuple], previous_tricks: List[list], 
                  bids: Dict['Player', int], tricks_won: Dict['Player', int], 
                  round_num: int) -> Card:
        """
        Choose a card to play in the current trick.
        
        Args:
            hand: The player's current hand
            current_trick: List of (player, card) tuples for the current trick
            previous_tricks: List of previous tricks (each trick is a list of (player, card) tuples)
            bids: Dictionary of all players' bids for this round
            tricks_won: Dictionary of tricks won so far this round
            round_num: Current round number
        
        Returns:
            The card to play (must be in hand)
        """
        pass
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Player(name={self.name})"
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return self.name == other.name

