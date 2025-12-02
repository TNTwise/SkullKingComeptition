"""
GUI for displaying Skull King game - Pygame Version (SMOOTH & FAST!)
"""
import os
import pygame
import pygame.font
from typing import List, Optional
from cards import Card, CardType, Suit
from player import Player
from game_engine import SkullKingGame, GameState, Trick

# Initialize Pygame
try:
    pygame.init()
    pygame.font.init()
    pygame.display.init()
except Exception as e:
    print(f"Error initializing pygame: {e}")
    raise

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
FPS = 60

# Colors
COLORS = {
    'bg': (26, 26, 46),        # #1a1a2e
    'bg2': (22, 33, 62),       # #16213e
    'bg3': (15, 52, 96),       # #0f3460
    'accent': (233, 69, 96),   # #e94560
    'accent2': (255, 107, 157), # #ff6b9d
    'gold': (255, 215, 0),     # #ffd700
    'silver': (192, 192, 192), # #c0c0c0
    'bronze': (205, 127, 50),  # #cd7f32
    'text': (255, 255, 255),   # #ffffff
    'text2': (224, 224, 224),   # #e0e0e0
    'success': (0, 255, 136),   # #00ff88
    'warning': (255, 170, 0),   # #ffaa00
    'card_bg': (45, 45, 68),    # #2d2d44
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}


class SkullKingGUI:
    """GUI for displaying and controlling Skull King game - Pygame version."""
    
    def __init__(self, game: SkullKingGame):
        """
        Initialize the GUI.
        
        Args:
            game: The SkullKingGame instance to display
        """
        self.game = game
        # Create windowed display (explicitly NOT fullscreen)
        # Explicitly set windowed mode - no FULLSCREEN flag
        os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'  # Position window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("SKULL KING - BOT COMPETITION")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts - use default system font
        try:
            default_font = pygame.font.get_default_font()
            self.fonts = {
                'title': pygame.font.Font(default_font, 48),
                'large': pygame.font.Font(default_font, 32),
                'medium': pygame.font.Font(default_font, 24),
                'small': pygame.font.Font(default_font, 18),
                'card': pygame.font.Font(default_font, 16),
            }
        except Exception as e:
            print(f"Warning: Could not load fonts, using default: {e}")
            # Fallback to default font
            self.fonts = {
                'title': pygame.font.Font(None, 48),
                'large': pygame.font.Font(None, 32),
                'medium': pygame.font.Font(None, 24),
                'small': pygame.font.Font(None, 18),
                'card': pygame.font.Font(None, 16),
            }
        
        # UI elements
        self.scroll_y = 0
        self.scroll_speed = 5  # Slower, smoother scrolling
        self.max_scroll = 0
        self.controls_height = 200  # Height of fixed controls area
        self.content_bottom = 0  # Track bottom of content
        
        # Horizontal scroll for player hands (per player)
        self.player_hand_scroll = {player: 0 for player in self.game.players}
        self.hand_scroll_speed = 15
        self.player_scrollbars = {}  # Store scrollbar info for click detection
        
        # Button states
        self.buttons = {}
        self.create_buttons()
        
        # Highlight state
        self.highlighted_player = None
        self.highlight_timer = 0
        
    def create_buttons(self):
        """Create button rectangles."""
        # Buttons positioned below header and info bar (always visible)
        button_y = 140
        button_width = 180
        button_height = 50
        button_spacing = 20
        
        self.buttons['next_trick'] = {
            'rect': pygame.Rect(20, button_y, button_width, button_height),
            'text': 'NEXT TRICK',
            'color': COLORS['accent'],
            'hover_color': COLORS['accent2'],
            'enabled': False,
            'action': self.next_trick
        }
        
        self.buttons['next_round'] = {
            'rect': pygame.Rect(220, button_y, button_width, button_height),
            'text': 'NEXT ROUND',
            'color': COLORS['success'],
            'hover_color': (0, 204, 112),
            'enabled': False,
            'action': self.next_round
        }
        
        self.buttons['auto_play'] = {
            'rect': pygame.Rect(420, button_y, button_width, button_height),
            'text': 'AUTO PLAY',
            'color': COLORS['warning'],
            'hover_color': (255, 153, 0),
            'enabled': True,
            'action': self.auto_play_round
        }
    
    def get_card_color(self, card: Card) -> tuple:
        """Get color scheme for a card based on its type."""
        if card.card_type == CardType.SKULL_KING:
            return ((139, 0, 0), (255, 0, 0), COLORS['white'])
        elif card.card_type == CardType.PIRATE:
            return ((45, 80, 22), (74, 124, 42), COLORS['white'])
        elif card.card_type == CardType.MERMAID:
            return ((0, 51, 102), (0, 102, 204), COLORS['white'])
        elif card.card_type == CardType.ESCAPE:
            return ((74, 74, 74), (128, 128, 128), COLORS['white'])
        elif card.card_type == CardType.NUMBER:
            suit_colors = {
                Suit.RED: ((139, 0, 0), (255, 68, 68), COLORS['white']),
                Suit.YELLOW: ((139, 117, 0), (255, 215, 0), COLORS['black']),
                Suit.BLUE: ((0, 0, 139), (68, 68, 255), COLORS['white']),
                Suit.GREEN: ((0, 100, 0), (68, 255, 68), COLORS['white']),
            }
            return suit_colors.get(card.suit, (COLORS['card_bg'], (102, 102, 102), COLORS['white']))
        return (COLORS['card_bg'], (102, 102, 102), COLORS['white'])
    
    def draw_text(self, text: str, font, color: tuple, x: int, y: int, center: bool = False):
        """Draw text on screen."""
        try:
            if text is None:
                text = ""
            text_str = str(text)
            if not text_str:
                text_str = " "
            surface = font.render(text_str, True, color)
            if center:
                rect = surface.get_rect(center=(x, y))
                self.screen.blit(surface, rect)
            else:
                self.screen.blit(surface, (x, y))
            return surface.get_rect()
        except Exception as e:
            print(f"Error drawing text '{text}': {e}")
            return pygame.Rect(x, y, 0, 0)
    
    def draw_button(self, button_key: str, mouse_pos: tuple):
        """Draw a button and return if it's clicked."""
        try:
            button = self.buttons[button_key]
            rect = button['rect']
            
            # Check hover
            hover = rect.collidepoint(mouse_pos) if mouse_pos else False
            color = button['hover_color'] if hover and button['enabled'] else button['color']
        except KeyError:
            return False
        except Exception as e:
            print(f"Error in draw_button: {e}")
            return False
        
        # Draw button
        if button['enabled']:
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['white'], rect, width=2, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (color[0]//3, color[1]//3, color[2]//3), rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['text2'], rect, width=2, border_radius=10)
        
        # Draw text
        text_surface = self.fonts['medium'].render(button['text'], True, COLORS['white'])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return hover and button['enabled'] and pygame.mouse.get_pressed()[0]
    
    def draw_card(self, card: Card, x: int, y: int, width: int = 100, height: int = 70):
        """Draw a card."""
        bg_color, border_color, text_color = self.get_card_color(card)
        
        # Draw card border
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, border_color, card_rect, border_radius=5)
        
        # Draw card background
        inner_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
        pygame.draw.rect(self.screen, bg_color, inner_rect, border_radius=3)
        
        # Draw card text
        card_text = str(card)
        if len(card_text) > 15:
            card_text = card_text[:12] + "..."
        
        # Split text if needed
        words = card_text.split()
        if len(words) > 2:
            mid = len(words) // 2
            line1 = ' '.join(words[:mid])
            line2 = ' '.join(words[mid:])
            text1 = self.fonts['card'].render(line1, True, text_color)
            text2 = self.fonts['card'].render(line2, True, text_color)
            self.screen.blit(text1, (x + width//2 - text1.get_width()//2, y + height//2 - 15))
            self.screen.blit(text2, (x + width//2 - text2.get_width()//2, y + height//2 + 5))
        else:
            text = self.fonts['card'].render(card_text, True, text_color)
            self.screen.blit(text, (x + width//2 - text.get_width()//2, y + height//2 - text.get_height()//2))
        
        return card_rect
    
    def draw_players_section(self, y_offset: int):
        """Draw the players section."""
        y = y_offset + 20  # Less spacing
        
        # Section title
        title_rect = pygame.Rect(20, y, WINDOW_WIDTH - 40, 50)
        pygame.draw.rect(self.screen, COLORS['bg2'], title_rect, border_radius=10)
        self.draw_text("⚔️ PLAYERS ⚔️", self.fonts['large'], COLORS['gold'], 
                      WINDOW_WIDTH // 2, y + 25, center=True)
        
        y += 70
        
        if not self.game.state:
            return y
        
        # Draw each player
        num_players = len(self.game.players)
        player_width = (WINDOW_WIDTH - 60) // num_players
        player_spacing = 10
        
        for i, player in enumerate(self.game.players):
            x = 30 + i * (player_width + player_spacing)
            player_rect = pygame.Rect(x, y, player_width, 220)  # Increased height for scrollbar
            
            # Highlight if active
            if self.highlighted_player == player:
                pygame.draw.rect(self.screen, COLORS['accent'], player_rect, border_radius=10, width=3)
            else:
                pygame.draw.rect(self.screen, COLORS['bg3'], player_rect, border_radius=10)
            
            # Player name header
            name_rect = pygame.Rect(x, y, player_width, 40)
            pygame.draw.rect(self.screen, COLORS['accent'], name_rect, border_radius=10)
            self.draw_text(player.name, self.fonts['medium'], COLORS['white'], 
                          x + player_width // 2, y + 20, center=True)
            
            # Stats
            text_y = y + 50
            bid = self.game.state.bids.get(player, -1)
            tricks = self.game.state.tricks_won.get(player, 0)
            hand_size = len(self.game.state.hands.get(player, []))
            
            self.draw_text(f"🎯 Bid: {bid if bid >= 0 else '-'}", self.fonts['small'], 
                          COLORS['accent2'], x + 10, text_y)
            self.draw_text(f"🏆 Tricks: {tricks}", self.fonts['small'], 
                          COLORS['success'], x + 10, text_y + 25)
            self.draw_text(f"🃏 Cards: {hand_size}", self.fonts['small'], 
                          COLORS['text2'], x + 10, text_y + 50)
            
            # Hand cards (scrollable horizontally)
            hand_y = y + 120
            hand = self.game.state.hands.get(player, [])
            
            # Get horizontal scroll for this player
            hand_scroll = self.player_hand_scroll.get(player, 0)
            
            # Calculate visible card area
            hand_area_width = player_width - 20
            card_width = 80
            card_spacing = 85
            
            # Set clipping for player's hand area to prevent overflow
            hand_clip_rect = pygame.Rect(x + 10, hand_y, hand_area_width, 70)
            self.screen.set_clip(hand_clip_rect)
            
            # Draw visible cards based on scroll position
            start_card = max(0, int(hand_scroll / card_spacing))
            end_card = min(len(hand), start_card + int(hand_area_width / card_spacing) + 3)
            
            card_x = x + 10 - (hand_scroll % card_spacing)
            for j in range(start_card, end_card):
                if j >= len(hand):
                    break
                card = hand[j]
                # Draw card (clipping will prevent overflow)
                self.draw_card(card, card_x, hand_y, width=card_width, height=60)
                card_x += card_spacing
            
            # Remove clipping
            self.screen.set_clip(None)
            
            # Draw scroll indicator if there are more cards
            total_hand_width = len(hand) * card_spacing
            if total_hand_width > hand_area_width:
                # Draw a small scrollbar at the bottom of the hand area
                scrollbar_y = hand_y + 65
                scrollbar_height = 6
                scrollbar_width = hand_area_width
                scrollbar_x = x + 10
                
                # Background
                pygame.draw.rect(self.screen, COLORS['bg2'], 
                               (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
                
                # Scroll indicator (thumb)
                indicator_width = max(30, (hand_area_width / total_hand_width) * scrollbar_width)
                max_hand_scroll = max(1, total_hand_width - hand_area_width)
                indicator_x = scrollbar_x + (hand_scroll / max_hand_scroll) * (scrollbar_width - indicator_width)
                indicator_x = max(scrollbar_x, min(scrollbar_x + scrollbar_width - indicator_width, indicator_x))
                pygame.draw.rect(self.screen, COLORS['accent'], 
                               (indicator_x, scrollbar_y, indicator_width, scrollbar_height))
                
                # Store scrollbar rect for click detection
                if not hasattr(self, 'player_scrollbars'):
                    self.player_scrollbars = {}
                self.player_scrollbars[player] = {
                    'rect': pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height),
                    'indicator_rect': pygame.Rect(indicator_x, scrollbar_y, indicator_width, scrollbar_height),
                    'hand_area_width': hand_area_width,
                    'total_hand_width': total_hand_width,
                    'player_x': x,
                    'hand_y': hand_y
                }
        
        return y + 240  # Increased for scrollbars
    
    def draw_trick_section(self, y_offset: int):
        """Draw the current trick section."""
        y = y_offset + 20
        
        # Section title
        title_rect = pygame.Rect(20, y, WINDOW_WIDTH - 40, 50)
        pygame.draw.rect(self.screen, COLORS['bg2'], title_rect, border_radius=10)
        self.draw_text("🎴 CURRENT TRICK 🎴", self.fonts['large'], COLORS['gold'], 
                      WINDOW_WIDTH // 2, y + 25, center=True)
        
        y += 70
        
        if not self.game.state or not self.game.state.current_trick:
            no_trick_rect = pygame.Rect(20, y, WINDOW_WIDTH - 40, 100)
            pygame.draw.rect(self.screen, COLORS['bg2'], no_trick_rect, border_radius=10)
            self.draw_text("No active trick", self.fonts['medium'], COLORS['text2'], 
                          WINDOW_WIDTH // 2, y + 50, center=True)
            return y + 120
        
        trick = self.game.state.current_trick
        
        # Led suit
        if trick.led_suit and trick.led_suit != Suit.SPECIAL:
            self.draw_text(f"Led Suit: {trick.led_suit.value} 🎯", self.fonts['medium'], 
                          COLORS['accent2'], WINDOW_WIDTH // 2, y, center=True)
            y += 30
        
        # Cards in trick
        cards_y = y + 20
        num_cards = len(trick.cards_played)
        card_spacing = 150
        start_x = (WINDOW_WIDTH - (num_cards * card_spacing)) // 2
        
        for i, (player, card) in enumerate(trick.cards_played):
            card_x = start_x + i * card_spacing
            
            # Player name
            self.draw_text(player.name, self.fonts['small'], COLORS['gold'], 
                          card_x + 65, cards_y, center=True)
            
            # Card
            self.draw_card(card, card_x, cards_y + 25, width=130, height=90)
        
        # Winner if trick is complete
        if len(trick.cards_played) == len(self.game.players):
            winner = trick.determine_winner()
            if winner:
                winner_y = cards_y + 130
                winner_text = f"🏆 WINNER: {winner.name} 🏆"
                self.draw_text(winner_text, self.fonts['large'], COLORS['gold'], 
                              WINDOW_WIDTH // 2, winner_y, center=True)
                return winner_y + 50
        
        return cards_y + 130
    
    def draw_scores_section(self, y_offset: int):
        """Draw the scores section."""
        y = y_offset + 20
        
        # Section title
        title_rect = pygame.Rect(20, y, WINDOW_WIDTH - 40, 50)
        pygame.draw.rect(self.screen, COLORS['bg2'], title_rect, border_radius=10)
        self.draw_text("🏆 SCORES 🏆", self.fonts['large'], COLORS['gold'], 
                      WINDOW_WIDTH // 2, y + 25, center=True)
        
        y += 70
        
        if not self.game.state:
            return y
        
        scores = self.game.state.scores
        sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        medals = ['🥇', '🥈', '🥉']
        score_spacing = 250
        start_x = (WINDOW_WIDTH - (len(sorted_players) * score_spacing)) // 2
        
        for i, (player, score) in enumerate(sorted_players):
            x = start_x + i * score_spacing
            
            # Medal
            if i < len(medals):
                self.draw_text(medals[i], self.fonts['large'], COLORS['gold'], x, y)
            
            # Color based on position
            color = COLORS['gold'] if i == 0 else \
                   COLORS['silver'] if i == 1 else \
                   COLORS['bronze'] if i == 2 else \
                   COLORS['text']
            
            # Score text
            score_text = f"{player.name}: {score}"
            self.draw_text(score_text, self.fonts['medium'], color, x + 30, y)
        
        return y + 80  # More space at bottom to ensure scores are visible
    
    def draw_info_bar(self):
        """Draw the info bar at the top."""
        info_rect = pygame.Rect(20, 80, WINDOW_WIDTH - 40, 50)
        pygame.draw.rect(self.screen, COLORS['bg3'], info_rect, border_radius=10)
        
        if not self.game.state:
            return
        
        state = self.game.state
        round_text = f"⚔️ Round: {state.round_num}/{self.game.num_rounds}"
        num_tricks = len(state.tricks)
        current_trick_num = num_tricks + (1 if state.current_trick else 0)
        trick_text = f"🎴 Trick: {current_trick_num}/{state.round_num}"
        
        # Status
        if state.current_trick:
            if len(state.current_trick.cards_played) < len(self.game.players):
                cards_played = len(state.current_trick.cards_played)
                total_players = len(self.game.players)
                status_text = f"🎮 Playing... ({cards_played}/{total_players} cards)"
                status_color = COLORS['warning']
            else:
                status_text = "✅ Trick Complete!"
                status_color = COLORS['success']
        elif self.is_round_complete():
            status_text = "🎉 Round Complete!"
            status_color = COLORS['success']
        else:
            status_text = "⏳ Waiting for next trick..."
            status_color = COLORS['text2']
        
        self.draw_text(round_text, self.fonts['medium'], COLORS['accent2'], 40, 105)
        self.draw_text(trick_text, self.fonts['medium'], COLORS['accent2'], 300, 105)
        self.draw_text(status_text, self.fonts['medium'], status_color, 600, 105)
    
    def draw(self):
        """Draw everything on screen."""
        try:
            # Clear screen
            self.screen.fill(COLORS['bg'])
            
            # Draw header (fixed, not scrolled)
            header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 70)
            pygame.draw.rect(self.screen, COLORS['bg2'], header_rect)
            self.draw_text("SKULL KING", self.fonts['title'], COLORS['gold'], 
                          WINDOW_WIDTH // 2, 35, center=True)
            
            # Draw info bar (fixed, not scrolled)
            self.draw_info_bar()
            
            # Draw buttons (fixed, not scrolled)
            try:
                mouse_pos = pygame.mouse.get_pos()
            except:
                mouse_pos = None
            for button_key in self.buttons:
                self.draw_button(button_key, mouse_pos)
            
            # Create a clipping rectangle for scrollable content area
            # This prevents content from drawing over the controls
            content_area = pygame.Rect(0, self.controls_height, WINDOW_WIDTH, WINDOW_HEIGHT - self.controls_height)
            self.screen.set_clip(content_area)
            
            # Reset scrollbar info
            self.player_scrollbars = {}
            
            # Draw sections (accounting for scroll, starting below controls)
            y = self.controls_height - self.scroll_y
            
            try:
                y = self.draw_players_section(y)
                y = self.draw_trick_section(y)
                y = self.draw_scores_section(y)
            except Exception as e:
                print(f"Error drawing sections: {e}")
                import traceback
                traceback.print_exc()
            
            # Remove clipping
            self.screen.set_clip(None)
            
            # Update max scroll based on content height
            # Calculate the total height of all content
            self.content_bottom = y
            content_height = self.content_bottom - self.controls_height
            visible_height = WINDOW_HEIGHT - self.controls_height
            
            # Calculate max scroll - ensure we can scroll to see all content
            if content_height > visible_height:
                # Add extra padding so user can scroll past the bottom to see everything
                # Increased padding to allow scrolling past scores section
                self.max_scroll = content_height - visible_height + 200
            else:
                self.max_scroll = content_height - visible_height + 200
            
            # Clamp current scroll position to valid range
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
            
            # Update display
            pygame.display.flip()
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_events(self):
        """Handle pygame events."""
        try:
            mouse_pos = pygame.mouse.get_pos()
        except:
            mouse_pos = (0, 0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    # Ensure we can scroll to see all content
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                elif event.key == pygame.K_HOME:
                    self.scroll_y = 0
                elif event.key == pygame.K_END:
                    self.scroll_y = self.max_scroll
                elif event.key == pygame.K_PAGEUP:
                    self.scroll_y = max(0, self.scroll_y - (WINDOW_HEIGHT - self.controls_height) // 2)
                elif event.key == pygame.K_PAGEDOWN:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + (WINDOW_HEIGHT - self.controls_height) // 2)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Only check buttons if click is in the controls area
                    if mouse_pos[1] < self.controls_height:
                        for button_key, button in self.buttons.items():
                            if button['rect'].collidepoint(mouse_pos) and button['enabled']:
                                try:
                                    button['action']()
                                except Exception as e:
                                    print(f"Error in button action {button_key}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                break
                
                elif event.button == 4:  # Scroll up (mouse wheel - Linux)
                    # Only scroll if mouse is in content area
                    if mouse_pos[1] >= self.controls_height:
                        self.scroll_y = max(0, self.scroll_y - self.scroll_speed * 3)
                elif event.button == 5:  # Scroll down (mouse wheel - Linux)
                    # Only scroll if mouse is in content area
                    if mouse_pos[1] >= self.controls_height:
                        self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * 3)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Check if mouse is over a player's hand area (horizontal scroll)
                if self.game.state and hasattr(self, 'player_scrollbars') and len(self.player_scrollbars) > 0:
                    mouse_x, mouse_y = mouse_pos
                    hand_scrolled = False
                    
                    # Check each player's hand area
                    for player, scrollbar_info in self.player_scrollbars.items():
                        # Calculate actual screen position accounting for vertical scroll
                        # hand_y in scrollbar_info is relative to content area, need to add scroll offset
                        screen_hand_y = scrollbar_info['hand_y'] + self.scroll_y
                        
                        # Check if mouse is in this player's hand area (on screen)
                        if (scrollbar_info['player_x'] + 10 <= mouse_x <= scrollbar_info['player_x'] + 10 + scrollbar_info['hand_area_width'] and
                            screen_hand_y <= mouse_y <= screen_hand_y + 70):
                            # Mouse is over this player's hand - scroll horizontally
                            hand = self.game.state.hands.get(player, [])
                            if len(hand) > 0:
                                current_scroll = self.player_hand_scroll.get(player, 0)
                                scroll_amount = -event.y * self.hand_scroll_speed
                                max_hand_scroll = max(0, scrollbar_info['total_hand_width'] - scrollbar_info['hand_area_width'])
                                self.player_hand_scroll[player] = max(0, min(max_hand_scroll, current_scroll + scroll_amount))
                                hand_scrolled = True
                                break
                    
                    # Vertical scroll if not scrolling hands
                    if not hand_scrolled and mouse_pos[1] >= self.controls_height:
                        # Smooth scrolling - reduce multiplier to make it less jittery
                        scroll_amount = event.y * self.scroll_speed * 1.5
                        new_scroll = self.scroll_y - scroll_amount
                        # Clamp to valid range
                        self.scroll_y = max(0, min(self.max_scroll, new_scroll))
                elif mouse_pos[1] >= self.controls_height:
                    # Vertical scroll if no hand scrolling
                    scroll_amount = event.y * self.scroll_speed * 1.5
                    new_scroll = self.scroll_y - scroll_amount
                    self.scroll_y = max(0, min(self.max_scroll, new_scroll))
    
    def is_round_complete(self) -> bool:
        """Check if current round is complete."""
        return self.game.is_round_complete()
    
    def next_trick(self):
        """Advance to the next trick."""
        if not self.game.state:
            return
        
        if not self.game.state.current_trick:
            if self.is_round_complete():
                self.game.calculate_scores()
                self.game.check_special_bonuses()
                self.update_buttons()
                return
            
            self.game.start_trick()
            self.play_trick()
        else:
            self.play_trick()
        
        self.update_buttons()
    
    def play_trick(self):
        """Play one card in the current trick."""
        if not self.game.state or not self.game.state.current_trick:
            return
        
        trick = self.game.state.current_trick
        
        played_players = {p for p, _ in trick.cards_played}
        next_player = None
        for player in self.game.players:
            if player not in played_players:
                next_player = player
                break
        
        if not next_player:
            return
        
        self.highlighted_player = next_player
        self.highlight_timer = 30  # Frames to highlight
        
        legal_cards = self.game.state.get_legal_cards(next_player)
        
        if not legal_cards:
            return
        
        hand = self.game.state.hands[next_player]
        current_trick_list = [(p, c) for p, c in trick.cards_played]
        previous_tricks = [[(p, c) for p, c in t.cards_played] for t in self.game.state.tricks]
        
        try:
            card = next_player.play_card(
                hand,
                current_trick_list,
                previous_tricks,
                self.game.state.bids,
                self.game.state.tricks_won,
                self.game.state.round_num
            )
            
            if card not in legal_cards:
                card = legal_cards[0] if legal_cards else hand[0]
            
            cards_played_before = len(trick.cards_played)
            will_complete_trick = (cards_played_before + 1) == len(self.game.players)
            
            trick_complete = self.game.play_card(next_player, card)
            
            if trick_complete:
                if self.is_round_complete():
                    self.game.calculate_scores()
                    self.game.check_special_bonuses()
                self.update_buttons()
            else:
                if will_complete_trick:
                    self.buttons['next_trick']['text'] = '▶️ NEXT TRICK'
                else:
                    self.buttons['next_trick']['text'] = '▶️ NEXT CARD'
        
        except Exception as e:
            print(f"Error playing card for {next_player.name}: {e}")
            import traceback
            traceback.print_exc()
            if legal_cards:
                card = legal_cards[0]
                try:
                    self.game.play_card(next_player, card)
                except:
                    pass
        
        self.highlighted_player = None
    
    def next_round(self):
        """Start the next round."""
        if self.game.current_round >= self.game.num_rounds:
            self.buttons['next_round']['enabled'] = False
            return
        
        self.game.current_round += 1
        self.game.start_round(self.game.current_round)
        self.game.collect_bids()
        self.game.start_trick()
        
        self.update_buttons()
        self.buttons['next_trick']['text'] = '▶️ NEXT CARD'
    
    def auto_play_round(self):
        """Automatically play through the current round."""
        if not self.game.state:
            return
        
        self.buttons['auto_play']['enabled'] = False
        
        while not self.is_round_complete():
            if not self.game.state.current_trick:
                self.game.start_trick()
            
            while self.game.state.current_trick and \
                  len(self.game.state.current_trick.cards_played) < len(self.game.players):
                self.play_trick()
                self.draw()
                self.clock.tick(FPS)
            
            if self.is_round_complete():
                break
        
        self.game.calculate_scores()
        self.game.check_special_bonuses()
        
        self.update_buttons()
        self.buttons['auto_play']['enabled'] = True
    
    def update_buttons(self):
        """Update button states based on game state."""
        if not self.game.state:
            return
        
        # Next trick button
        if self.game.state.current_trick:
            self.buttons['next_trick']['enabled'] = True
        elif not self.is_round_complete():
            self.buttons['next_trick']['enabled'] = True
        else:
            self.buttons['next_trick']['enabled'] = False
        
        # Next round button
        if self.is_round_complete() and self.game.current_round < self.game.num_rounds:
            self.buttons['next_round']['enabled'] = True
        else:
            self.buttons['next_round']['enabled'] = False
    
    def update_display(self):
        """Update the display (no-op for pygame, it draws continuously)."""
        # Pygame draws continuously in the run loop, so this is a no-op
        pass
    
    def run(self):
        """Start the GUI main loop."""
        try:
            self.update_buttons()
        except Exception as e:
            print(f"Error updating buttons: {e}")
        
        try:
            while self.running:
                try:
                    self.handle_events()
                    
                    # Update highlight timer
                    if self.highlight_timer > 0:
                        self.highlight_timer -= 1
                        if self.highlight_timer == 0:
                            self.highlighted_player = None
                    
                    self.draw()
                    self.clock.tick(FPS)
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    import traceback
                    traceback.print_exc()
                    # Try to continue
                    self.clock.tick(FPS)
        except KeyboardInterrupt:
            print("Interrupted by user")
        except Exception as e:
            print(f"Fatal error in GUI: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                pygame.quit()
            except:
                pass

