"""
Game engine for Skull King card game.
"""
from typing import List, Dict, Optional, Tuple
from cards import Card, Deck, Suit, CardType
from player import Player


class Trick:
    """Represents a single trick in the game."""
    
    def __init__(self, round_num: int, trick_num: int, trump_suit: Optional[Suit] = None):
        self.round_num = round_num
        self.trick_num = trick_num
        self.trump_suit = trump_suit
        self.cards_played: List[Tuple[Player, Card]] = []
        self.led_suit: Optional[Suit] = None
        self.winner: Optional[Player] = None
    
    def play_card(self, player: Player, card: Card):
        """Record a card played in this trick."""
        if len(self.cards_played) == 0:
            # First card sets the led suit
            if card.card_type == CardType.NUMBER:
                self.led_suit = card.suit
            else:
                self.led_suit = Suit.SPECIAL
        
        self.cards_played.append((player, card))
    
    def determine_winner(self) -> Optional[Player]:
        """Determine the winner of this trick."""
        if not self.cards_played:
            return None
        
        winner_card = self.cards_played[0][1]
        winner_player = self.cards_played[0][0]
        
        for player, card in self.cards_played[1:]:
            if card.beats(winner_card, self.led_suit, self.trump_suit):
                winner_card = card
                winner_player = player
        
        self.winner = winner_player
        return winner_player
    
    def is_complete(self) -> bool:
        """Check if all players have played in this trick."""
        # This will be set by the game engine based on number of players
        return False


class GameState:
    """Represents the current state of the game."""
    
    def __init__(self, players: List[Player], round_num: int):
        self.players = players
        self.round_num = round_num
        self.num_cards = round_num
        self.bids: Dict[Player, int] = {}
        self.tricks_won: Dict[Player, int] = {}
        self.hands: Dict[Player, List[Card]] = {}
        self.current_trick: Optional[Trick] = None
        self.tricks: List[Trick] = []
        self.trump_suit: Optional[Suit] = None
        self.scores: Dict[Player, int] = {player: 0 for player in players}
        self.game_over = False
    
    def get_legal_cards(self, player: Player) -> List[Card]:
        """Get legal cards a player can play in the current trick."""
        if not self.current_trick:
            return self.hands[player]
        
        if not self.current_trick.cards_played:
            return self.hands[player]
        
        led_suit = self.current_trick.led_suit
        
        # Check if player has cards of the led suit
        if led_suit and led_suit != Suit.SPECIAL:
            following_cards = [c for c in self.hands[player] 
                             if c.card_type == CardType.NUMBER and c.suit == led_suit]
            if following_cards:
                # Must follow suit
                return following_cards
        
        # Can play any card (either no suit to follow, or special cards)
        return self.hands[player]


class SkullKingGame:
    """Main game engine for Skull King."""
    
    def __init__(self, players: List[Player], num_rounds: int = 10):
        """
        Initialize the game.
        
        Args:
            players: List of Player instances
            num_rounds: Number of rounds to play (default 10)
        """
        if len(players) < 2:
            raise ValueError("Need at least 2 players")
        if len(players) > 6:
            raise ValueError("Maximum 6 players supported")
        
        self.players = players
        self.num_rounds = num_rounds
        self.current_round = 0
        self.deck = Deck()
        self.state: Optional[GameState] = None
        self.game_history: List[GameState] = []
        # Maintain cumulative scores across rounds
        self.cumulative_scores: Dict[Player, int] = {player: 0 for player in players}
    
    def start_round(self, round_num: int) -> GameState:
        """Start a new round."""
        self.deck = Deck()
        self.deck.shuffle()
        
        num_cards = round_num
        state = GameState(self.players, round_num)
        
        # Preserve cumulative scores from previous rounds
        state.scores = self.cumulative_scores.copy()
        
        # Deal cards
        for player in self.players:
            state.hands[player] = self.deck.deal(num_cards)
            state.tricks_won[player] = 0
        
        self.state = state
        return state
    
    def collect_bids(self) -> Dict[Player, int]:
        """Collect bids from all players."""
        if not self.state:
            raise RuntimeError("No active round")
        
        bids = {}
        for player in self.players:
            hand = self.state.hands[player]
            bid = player.make_bid(hand, self.state.round_num, self.state.bids)
            if bid < 0 or bid > self.state.round_num:
                raise ValueError(f"Invalid bid from {player.name}: {bid}")
            self.state.bids[player] = bid
            bids[player] = bid
        
        return bids
    
    def start_trick(self) -> Trick:
        """Start a new trick."""
        if not self.state:
            raise RuntimeError("No active round")
        
        trick_num = len(self.state.tricks) + 1
        trick = Trick(self.state.round_num, trick_num, self.state.trump_suit)
        self.state.current_trick = trick
        return trick
    
    def play_card(self, player: Player, card: Card) -> bool:
        """
        Play a card in the current trick.
        
        Returns:
            True if the trick is complete, False otherwise
        """
        if not self.state or not self.state.current_trick:
            raise RuntimeError("No active trick")
        
        # Validate card is legal
        legal_cards = self.state.get_legal_cards(player)
        if card not in legal_cards:
            raise ValueError(f"Illegal card play: {card} not in legal cards {legal_cards}")
        
        # Remove card from hand
        self.state.hands[player].remove(card)
        
        # Play card
        self.state.current_trick.play_card(player, card)
        
        # Check if trick is complete
        if len(self.state.current_trick.cards_played) == len(self.players):
            # Determine winner
            winner = self.state.current_trick.determine_winner()
            if winner:
                self.state.tricks_won[winner] = self.state.tricks_won.get(winner, 0) + 1
            
            self.state.tricks.append(self.state.current_trick)
            self.state.current_trick = None
            return True
        
        return False
    
    def calculate_scores(self) -> Dict[Player, int]:
        """Calculate scores for the current round."""
        if not self.state:
            raise RuntimeError("No active round")
        
        round_scores = {}
        
        for player in self.players:
            bid = self.state.bids[player]
            tricks_won = self.state.tricks_won[player]
            
            if bid == tricks_won:
                # Correct bid: 20 points per trick + 10 bonus
                score = bid * 20 + 10
            else:
                # Incorrect bid: lose 10 points per trick off
                score = -10 * abs(bid - tricks_won)
            
            # Zero bid special scoring
            if bid == 0:
                if tricks_won == 0:
                    score = 10 * self.state.round_num
                else:
                    score = -10 * self.state.round_num
            
            round_scores[player] = score
            self.state.scores[player] += score
            # Update cumulative scores
            self.cumulative_scores[player] = self.state.scores[player]
        
        return round_scores
    
    def check_special_bonuses(self) -> Dict[Player, int]:
        """Check for special bonuses (capturing Skull King)."""
        if not self.state:
            return {}
        
        bonuses = {player: 0 for player in self.players}
        
        # Check each trick for Skull King captures
        for trick in self.state.tricks:
            # Check if Skull King was played in this trick
            skull_king_played = any(card.card_type == CardType.SKULL_KING 
                                   for _, card in trick.cards_played)
            
            if skull_king_played:
                # Determine winner of the trick
                winner = trick.determine_winner()
                if winner:
                    # Check what card the winner played
                    winner_card = next(card for player, card in trick.cards_played if player == winner)
                    
                    if winner_card.card_type == CardType.MERMAID:
                        bonuses[winner] += 100  # Mermaid captures Skull King
                    elif winner_card.card_type == CardType.PIRATE:
                        bonuses[winner] += 50  # Pirate captures Skull King
        
        # Apply bonuses to scores
        for player in self.players:
            self.state.scores[player] += bonuses[player]
            # Update cumulative scores
            self.cumulative_scores[player] = self.state.scores[player]
        
        return bonuses
    
    def is_round_complete(self) -> bool:
        """Check if the current round is complete."""
        if not self.state:
            return False
        
        # Round is complete when all cards are played
        total_cards_played = sum(len(trick.cards_played) for trick in self.state.tricks)
        if self.state.current_trick:
            total_cards_played += len(self.state.current_trick.cards_played)
        return total_cards_played == self.state.round_num * len(self.players)
    
    def get_final_scores(self) -> Dict[Player, int]:
        """Get final scores after all rounds."""
        if not self.state:
            return {player: 0 for player in self.players}
        return self.state.scores.copy()

