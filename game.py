import pygame
import sys
import random
import itertools

from typing import Optional, List, Dict


# Initialize Pygame
pygame.init()

# Constants
NUM_VOTERS = 100

# Global variables with type annotations
winner: Optional[str] = None
round_results: List[Dict[str, int]] = []
user_rankings: Dict[str, int] = {}

# define quiz questions
quiz_questions = [
    {
        "question": "What happens if no candidate receives more than 50% of the first-choice votes?",
        "options": ["A random candidate is chosen as the winner", "Votes are recounted", "The candidate with the least votes is eliminated", "The election is declared invalid"],
        "answer": "The candidate with the least votes is eliminated"
    },
    {
        "question": "Why are votes redistributed in IRV?",
        "options": ["To ensure all votes count", "To eliminate a candidate", "To speed up the voting process", "None of the above"],
        "answer": "To ensure all votes count"
    },
    {
        "question": "Which of the following best describes 'Instant Runoff Voting'?",
        "options": ["A system where the last candidate is always eliminated", "A system where voters can vote multiple times", "A system that ranks candidates by preference", "A voting system without primaries"],
        "answer": "A system that ranks candidates by preference"
    },
    {
        "question": "What is the main advantage of IRV over traditional plurality voting?",
        "options": ["Faster results", "Lower cost", "Reduces the likelihood of needing a runoff election", "Allows voting by mail"],
        "answer": "Reduces the likelihood of needing a runoff election"
    }
]

# Set up the display
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Voter Education Game for RCV')

# Constants to adjust the size of the bars and spacing
BAR_WIDTH = 20  # Width of each bar
BAR_SPACING = 30  # Spacing between bars
MAX_BAR_HEIGHT = 100  # Maximum height of bars
GRAPH_HEIGHT = 40  # Height of the graph area
TEXT_SPACING = 20  # Spacing between text and bars
PADDING_LEFT = 120  # Left padding
PADDING_BOTTOM = 30  # Bottom padding
PADDING_TOP = 40  # Top padding
TEXT_HEIGHT = 30
NAME_FONT_SIZE = 22  
VOTE_COUNT_FONT_SIZE = 20


# Define button for submitting vote
submit_button_rect = pygame.Rect(screen_width - 160, screen_height - 70, 150, 50)
submit_button_text = 'Submit'

LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (21, 101, 192)
WHITE = (255, 255, 255)
LIGHT_GREY = (211, 211, 211)
DARK_GREY = (32, 32, 32) 
GREEN = (0, 200, 0)  
BLACK = (0, 0, 0)
RED = (255, 0, 0)

tutorial_content = [
    "Welcome to the RCV Tutorial!",
    "In RCV, you rank the candidates by preference.",
    "A candidate needs more than 50% of the votes to win outright.",
    "If no one gets 50%, the last-place candidate is eliminated,",
    "and their votes go to the voters' next choice.",
    "This process continues until a candidate wins by majority.",
    "Now, go to the main menu and try ranking the candidates",
    "to see who wins in a simulated RCV election."
]

# Tutorial state
tutorial_step = 0

def draw_tutorial_screen():
    screen.fill(LIGHT_GREY)
    # Draw the tutorial text based on the current step
    tutorial_text = tutorial_content[tutorial_step]
    draw_text(tutorial_text, (100, 100), DARK_BLUE, font_size=48)
    
    # Provide navigation options based on the tutorial step
    if tutorial_step < len(tutorial_content) - 1:
        draw_text("Press [N] for Next, [M] for Menu", (100, 500), GREEN, font_size=36)
    else:  # On the last step of the tutorial
        draw_text("Press [S] to Start Voting, [M] for Menu", (100, 500), GREEN, font_size=36)

def reset_voting():
    # Reset candidate rankings for a new voting round
    global candidate_rankings
    candidate_rankings = {candidate: None for candidate in candidates}
        
def draw_button(button_rect, button_text, position, button_color, text_color):
    pygame.draw.rect(screen, button_color, button_rect)  # Button background
    pygame.draw.rect(screen, WHITE, button_rect, 2)  # Button border
    draw_text(button_text, position, text_color, font_size=24)

def check_button_click(mouse_x, mouse_y, button_rect):
    return button_rect.collidepoint(mouse_x, mouse_y)

def transition_to_results():
    global game_state
    game_state = RESULTS
    
def draw_voting_screen():
    # Use a dark grey background for the voting screen
    screen.fill(DARK_GREY)

    # Draw candidate buttons with a new color scheme and larger font
    button_width = 200
    for candidate, position in candidate_positions.items():
        button_rect = pygame.Rect(position[0], position[1], button_width, 50)
        pygame.draw.rect(screen, LIGHT_GREY, button_rect)
        draw_text(candidate, (position[0] + 10, position[1] + 5), DARK_BLUE)

        # Draw rankings next to candidate names
        rank = candidate_rankings[candidate]
        if rank is not None:
            draw_text(f'Rank: {rank}', (position[0] + button_width + 10, position[1] + 5), WHITE)

    # Draw the submit button (only if all candidates are ranked)
    all_ranked = all(rank is not None for rank in candidate_rankings.values())
    submit_button_color = GREEN if all_ranked else DARK_GREY  # Grey out button if not all ranked
    draw_button(submit_button_rect, submit_button_text, (submit_button_rect.x + 20, submit_button_rect.y + 5), submit_button_color, WHITE)

    # If not all candidates are ranked, provide feedback to the player with a visible message
    if not all_ranked:
        draw_text("Please rank all candidates.", (50, screen_height - 100), color=WHITE)
    pygame.display.flip()
    
def run_what_if_analysis(initial_votes):
    print("Would you like to try a different voting strategy based on the results? (yes/no)")
    response = input()
    if response.lower() == 'yes':
        new_rankings = input("Enter your new rankings (e.g., Diana, Alice, Bob, Charlie): ")
        sorted_candidate_names = new_rankings.split(', ')
        winner, new_round_results = simulate_voting_rounds(NUM_VOTERS, sorted_candidate_names)
        draw_results_screen(winner, new_round_results, {i+1: name for i, name in enumerate(sorted_candidate_names)})
        
def prompt_what_if_analysis():
    print("Enter your new rankings (e.g., Diana, Alice, Bob, Charlie): ")
    new_rankings = input()
    if new_rankings:
        sorted_candidate_names = new_rankings.split(', ')
        global candidate_rankings
        candidate_rankings = {name: i+1 for i, name in enumerate(sorted_candidate_names)}
        winner, new_round_results = simulate_voting_rounds(NUM_VOTERS, sorted_candidate_names)
        global round_results
        round_results = new_round_results
        draw_results_screen(winner, round_results, candidate_rankings)
        pygame.display.flip()  # Ensure this call is here to update the screen


def handle_voting_simulation(candidate_names):
    winner, new_round_results = simulate_voting_rounds(NUM_VOTERS, candidate_names)
    global round_results
    round_results = new_round_results
    global game_state
    game_state = RESULTS
    pygame.display.flip()
    draw_results_screen(winner, round_results, candidate_rankings)


def start_new_round():
    new_candidates = ['Eve', 'Frank', 'Gina', 'Harry']  # New set of candidates as example
    global candidates, candidate_positions, candidate_rankings
    candidates = new_candidates
    candidate_positions = {candidate: (100, i * 100 + 50) for i, candidate in enumerate(new_candidates)}
    candidate_rankings = {candidate: None for candidate in new_candidates}
    global game_state
    game_state = VOTING  # Switch back to the voting screen with new candidates
    print("New round started with different candidates. Please rank them.")

def draw_bar_graph(vote_counts, x_offset, y_offset, screen, bar_width, bar_spacing, max_bar_height):
    max_votes = max(vote_counts.values())
    num_candidates = len(vote_counts)
    
    # Calculate the total width required for all bars and spacing
    total_width = num_candidates * (bar_width + bar_spacing) - bar_spacing
    
    # Adjust x_offset to center the bars horizontally
    x_offset += (total_width - (bar_width + bar_spacing)) / 2
    
    for i, (candidate, votes) in enumerate(sorted(round_votes.items(), key=lambda item: item[1], reverse=True)):
        bar_height = (votes / max_votes) * MAX_BAR_HEIGHT
        bar_x = bar_graph_center_x + i * (BAR_WIDTH + BAR_SPACING)
        bar_y = y_offset + MAX_BAR_HEIGHT - bar_height
    
    # Draw the bar
    pygame.draw.rect(screen, LIGHT_BLUE, (bar_x, bar_y, BAR_WIDTH, bar_height))
    
    # Draw candidate name centered under the bar
    draw_name_under_bar(candidate, bar_x, bar_y, BAR_WIDTH, bar_height)

    draw_text(str(votes), (bar_x + bar_width / 2, bar_y - TEXT_SPACING), WHITE, font_size=25)

def draw_text_centered(surface, text, center_x, y, color, font_size):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, y))
    surface.blit(text_surface, text_rect)


def draw_results_screen(winner, round_results, user_rankings):
    global screen  # Ensure 'screen' is the pygame display surface
    global font  # Make sure to use the global font variable

    screen.fill(BLACK)  # Clear the screen

    y_offset = PADDING_TOP  # Start below the top padding
    
    for round_num, round_votes in enumerate(round_results, start=1):
        # Left-align the round results text
        round_text = f"Round {round_num} Results"
        draw_text(round_text, (PADDING_LEFT, y_offset), LIGHT_BLUE, font_size=30)

        # Determine the bar graph center position
        num_bars = len(round_votes)
        bar_graph_center_x = (screen_width // 2) - ((BAR_WIDTH + BAR_SPACING) * num_bars // 2)

        # Draw bars, names, and vote counts
        for i, (candidate, votes) in enumerate(sorted(round_votes.items(), key=lambda item: item[1], reverse=True)):
            bar_x = bar_graph_center_x + i * (BAR_WIDTH + BAR_SPACING)
            bar_height = (votes / max(round_votes.values())) * MAX_BAR_HEIGHT
            bar_y = y_offset + TEXT_HEIGHT + (MAX_BAR_HEIGHT - bar_height)

            # Draw the bar
            pygame.draw.rect(screen, LIGHT_BLUE, (bar_x, bar_y, BAR_WIDTH, bar_height))

            # Draw candidate name centered under the bar with a smaller font size
            draw_text(candidate, (bar_x + (BAR_WIDTH - font.size(candidate)[0]) // 2, bar_y + bar_height + TEXT_SPACING), WHITE, font_size=NAME_FONT_SIZE)

            # Draw vote count above the bar with a smaller font size
            draw_text(str(votes), (bar_x + (BAR_WIDTH - font.size(str(votes))[0]) // 2, bar_y - font.size(str(votes))[1] - TEXT_SPACING), WHITE, font_size=VOTE_COUNT_FONT_SIZE)

        # Update y_offset for the next block of content
        y_offset += MAX_BAR_HEIGHT + TEXT_HEIGHT * 2 + TEXT_SPACING * 3

    # Find the winner's rank in the user's rankings
    winner_rank = next((rank for rank, name in user_rankings.items() if name == winner), None)

    # Construct the winner text based on whether the winner was in the user's rankings
    if winner_rank is not None:
        winner_text = f"The winner is: {winner} - Your rank {winner_rank} won!"
    else:
        winner_text = f"The winner is: {winner} - They were not in your ranking."

    # Draw the winner text at the bottom of the screen
    y_offset = screen_height - TEXT_HEIGHT - PADDING_BOTTOM
    draw_text(winner_text, (PADDING_LEFT, y_offset), GREEN, font_size=30)

    # Ensure the 'Main Menu' button is in the bottom right
    main_menu_button_rect = pygame.Rect(screen_width - 170, screen_height - 60, 150, 40)
    draw_button(main_menu_button_rect, 'Main Menu', (main_menu_button_rect.x + 10, main_menu_button_rect.y + 5), LIGHT_BLUE, WHITE)


    pygame.display.flip()  # Update the display




# Set up the clock for managing frame rate
clock = pygame.time.Clock()

# Define game states
MENU = 0
VOTING = 1
RESULTS = 2
TUTORIAL = 3
EDUCATIONAL = 4
TUTORIAL_INTRO = 5
TUTORIAL_VOTING = 6
TUTORIAL_COUNTING = 7
TUTORIAL_RESULT = 8
RE_VOTING = 9
QUIZ = 10

# Add an initial state for the educational content
initial_state = MENU

# Start with the initial state
game_state = initial_state

def draw_educational_screen():
    screen.fill(LIGHT_GREY)
    
    # Title
    draw_text("Ranked Choice Voting (RCV)", (50, 50), DARK_BLUE)
    
    # Content - Split into multiple lines for better fit
    lines = [
        "RCV allows voters to rank candidates in order of preference.",
        "If no candidate gets a majority of first-preference votes,",
        "the last-place candidate is eliminated, and votes are redistributed.",
        "This process repeats until a candidate has a majority."
    ]
    
    y_offset = 150
    line_spacing = 50
    
    for line in lines:
        draw_text(line, (50, y_offset), DARK_BLUE)
        y_offset += line_spacing  # Move down for the next line
    
    # Instruction to proceed
    draw_text("Press any key to start", (50, y_offset + 100), GREEN)


# Define candidates
candidates = ['Alice', 'Bob', 'Charlie', 'Diana']
candidate_positions = {candidate: (100, i * 100 + 50) for i, candidate in enumerate(candidates)}
candidate_rankings = {candidate: None for candidate in candidates}  # None means unranked

# Initialize a dictionary to store votes. Each key represents a candidate's name, and the value is their vote count.
votes = {candidate: 0 for candidate in candidates}

def generate_voter_preferences(candidates, num_voters):
    # Generate random voter preferences for each voter
    preferences = []
    for _ in range(num_voters):
        # Generate a random preference list for each voter
        preference = random.sample(candidates, len(candidates))
        preferences.append(preference)
    return preferences


def simulate_voting_rounds(num_voters, candidates):
    # This function simulates the voting process
    preferences = generate_voter_preferences(candidates, num_voters)
    active_candidates = candidates[:]
    round_details = []

    while True:
        vote_counts = get_vote_counts(preferences, active_candidates)
        round_details.append(vote_counts)
        winner = get_winner(vote_counts)
        
        if winner:
            return winner, round_details

        eliminated = eliminate_candidate(vote_counts)
        if not eliminated:
            # In a rare case, there might be a perfect tie and no candidate to eliminate
            return None, round_details

        active_candidates.remove(eliminated)
        preferences = redistribute_votes(preferences, eliminated)

def redistribute_votes(preferences, eliminated_candidate):
    # Remove the eliminated candidate from all voter preferences
    new_preferences = []
    for pref in preferences:
        new_pref = [c for c in pref if c != eliminated_candidate]
        new_preferences.append(tuple(new_pref))
    return new_preferences

# Font setup
font = pygame.font.Font(None, 48)


def draw_text(text, position, color, font_size=36):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def handle_submit_button(mouse_x, mouse_y):
    global round_results, game_state, winner, user_rankings
    if check_button_click(mouse_x, mouse_y, submit_button_rect):
        if all(rank is not None for rank in candidate_rankings.values()):
            sorted_candidates_by_rank = sorted(candidate_rankings.items(), key=lambda item: item[1])
            sorted_candidate_names = [candidate for candidate, rank in sorted_candidates_by_rank]
            user_rankings = {rank: candidate for candidate, rank in sorted_candidates_by_rank}

            # Pass the sorted candidate names to simulate_voting_rounds
            winner, new_round_results = simulate_voting_rounds(NUM_VOTERS, sorted_candidate_names)

            # Initialize round_results as an empty list if it is None
            if round_results is None:
                round_results = []

            round_results.extend(new_round_results)  # Append the results

            if winner:
                game_state = RESULTS  # Change the state to show the results
                print(f"The winner is: {winner}")  # This should be displayed in your game window
                draw_results_screen(winner, round_results, user_rankings)  # Pass user_rankings here
            else:
                print("Tie or no majority. Further action needed.")
        else:
            print("Please rank all candidates before submitting.")  # Show this message in your game window


            
def draw_menu_screen():
    screen.fill(DARK_GREY)  # Menu background
    
    # Game Title
    game_title = "VoteQuest: The RCV Adventure"
    title_surface = font.render(game_title, True, LIGHT_BLUE)
    # Center the title surface
    title_rect = title_surface.get_rect(center=(screen_width // 2, 100))
    screen.blit(title_surface, title_rect)

    # Menu options
    menu_options = ["[S] Start Game", "[T] Tutorial", "[Q] Quiz", "[X] Quit"]
    y_offset = 250  # You can adjust this value as needed
    for option in menu_options:
        option_surface = font.render(option, True, WHITE)
        option_rect = option_surface.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(option_surface, option_rect)
        y_offset += 60  # Adjust the spacing as needed

    pygame.display.flip()

def draw_name_under_bar(candidate, bar_x, bar_y, bar_width, bar_height):
    name_text = font.render(candidate, True, WHITE)
    # Calculate the center position for the name based on the bar's position and width
    name_text_rect = name_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height + TEXT_SPACING))
    screen.blit(name_text, name_text_rect)



def draw_re_voting_screen(remaining_candidates):
    # Clear the screen
    screen.fill(DARK_GREY)
    
    # Title and instructions
    draw_text("Re-rank the remaining candidates", (50, 50), LIGHT_BLUE, font_size=48)
    draw_text("Click on the candidates to rank them.", (50, 100), WHITE, font_size=36)
    
    # Draw candidate buttons
    button_width = 200
    y_offset = 150
    for candidate in remaining_candidates:
        button_rect = pygame.Rect(100, y_offset, button_width, 50)
        pygame.draw.rect(screen, LIGHT_GREY, button_rect)
        draw_text(candidate, (110, y_offset + 5), DARK_BLUE, font_size=36)
        
        # Draw rankings next to candidate names
        rank = candidate_rankings.get(candidate)
        if rank is not None:
            draw_text(f'Rank: {rank}', (310, y_offset + 5), WHITE, font_size=36)

        y_offset += 60

    # Draw a submit button
    submit_button_rect = pygame.Rect(screen_width - 160, screen_height - 70, 150, 50)
    draw_button(submit_button_rect, "Submit Rankings", (submit_button_rect.x + 20, submit_button_rect.y + 5), GREEN, WHITE)



def run_game():
    global game_state, tutorial_step, winner, round_results, user_rankings
    # Mouse position used for candidate selection
    mouse_x, mouse_y = 0, 0
    round_results = None
    quiz_questions_index = 0

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Start Game
                        game_state = VOTING
                    elif event.key == pygame.K_t:  # Tutorial
                        tutorial_step = 0  # Reset tutorial step to the beginning
                        game_state = TUTORIAL_INTRO
                    elif event.key == pygame.K_q:  # Quiz
                        game_state = QUIZ
                    elif event.key == pygame.K_x:  # Quit Game
                        pygame.quit()
                        sys.exit()

            elif game_state == TUTORIAL_INTRO:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:  # Next
                        tutorial_step += 1
                        if tutorial_step >= len(tutorial_content):
                            game_state = MENU  # Loop back to the menu after the last step
                    elif event.key == pygame.K_m:  # Menu
                        game_state = MENU
                    elif event.key == pygame.K_s:  # Skip to voting
                        game_state = VOTING
                        
            elif game_state == RESULTS:
                if round_results is None:
                    winner, round_results = count_votes()
                draw_results_screen(winner, round_results, user_rankings)
                pygame.display.flip()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:  # Return to menu
                        game_state = MENU
                        winner = None
                        round_results = []
                        user_rankings = {}
                    elif event.key == pygame.K_w:  # Trigger "what if" analysis
                        prompt_what_if_analysis()
                    elif event.key == pygame.K_r:  # Restart with the same candidates
                        reset_voting()
                        game_state = VOTING
                    elif event.key == pygame.K_n:  # New round with different candidates
                        start_new_round()
            
            elif game_state == QUIZ:
                if quiz_questions_index < len(quiz_questions):
                    options_positions = display_quiz_question(quiz_questions[quiz_questions_index])
                    waiting_for_answer = True
                    while waiting_for_answer:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                mouse_x, mouse_y = event.pos
                                for rect, option in options_positions:
                                    if rect.collidepoint(mouse_x, mouse_y):
                                        if option == quiz_questions[quiz_questions_index]['answer']:
                                            feedback_text = "Correct!"
                                            feedback_color = GREEN
                                        else:
                                            feedback_text = f"Incorrect! Correct answer: {quiz_questions[quiz_questions_index]['answer']}"
                                            feedback_color = RED
                                        draw_text(feedback_text, (screen_width // 2 - 100, screen_height - 100), feedback_color, font_size=24)
                                        pygame.display.flip()
                                        pygame.time.wait(2000)  # Wait two seconds to show feedback
                                        waiting_for_answer = False
                                        quiz_questions_index += 1
                                        if quiz_questions_index >= len(quiz_questions):
                                            quiz_questions_index = 0
                                            game_state = MENU
                                        break
                else:
                    game_state = MENU



            if game_state == VOTING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Check if the submit button is clicked
                    if check_button_click(mouse_x, mouse_y, submit_button_rect):
                        handle_submit_button(mouse_x, mouse_y)
                        if winner:
                            draw_results_screen(winner, round_results, user_rankings)
                    else:
                        # If the click is not on the submit button, then handle the voting
                        handle_voting(mouse_x, mouse_y)
                    draw_voting_screen()  # Redraw the voting screen after any click


            elif game_state == RESULTS and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Return to menu
                    game_state = MENU
                    winner = None
                    round_results = []
                elif event.key == pygame.K_r:  # Restart voting with same candidates
                    reset_voting()
                    round_results = []
                    game_state = VOTING
                elif event.key == pygame.K_w:  # "What if" analysis
                    prompt_what_if_analysis()
                elif event.key == pygame.K_n:  # Start new round with different candidates
                    start_new_round()
                if not winner:
                    reset_voting()  # Reset the rankings for the next round of voting
                    round_results = []  # Clear past round results
            elif game_state == RE_VOTING:
                # Prompt user to re-rank remaining candidates
                # This can be a separate function that updates the display
                draw_re_voting_screen()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    handle_voting(mouse_x, mouse_y)
                    # Here check if all remaining candidates are ranked, then transition to RESULTS
                    remaining_candidates_ranked = all(candidate_rankings[candidate] is not None for candidate in active_candidates)
                    if remaining_candidates_ranked:
                        winner, new_round_results = count_votes()
                        round_results.extend(new_round_results)  # Append new round results to existing
                        game_state = RESULTS

        # Drawing the screen based on the state
        if game_state == MENU:
            draw_menu_screen()
        elif game_state in [TUTORIAL_INTRO, TUTORIAL_VOTING, TUTORIAL_COUNTING, TUTORIAL_RESULT]:
            draw_tutorial_screen()
        elif game_state == VOTING:
            draw_voting_screen()
        elif game_state == RESULTS:
            # Ensure that count_votes is called only once when entering the RESULTS state
            if round_results is None:
                winner, round_results = count_votes()
            draw_results_screen(winner, round_results, user_rankings)

        # Update display
        pygame.display.flip()
        clock.tick(60)
        
def display_quiz_question(question):
    screen.fill(WHITE)
    draw_text(question['question'], (100, 50), BLACK, font_size=36)

    options_positions = []
    y_start = 150
    for index, option in enumerate(question['options']):
        option_rect = pygame.Rect(100, y_start, screen_width - 200, 40)
        pygame.draw.rect(screen, LIGHT_GREY, option_rect)
        draw_text(f"{index + 1}. {option}", (110, y_start + 5), BLACK, font_size=24)
        options_positions.append((option_rect, option))
        y_start += 50

    pygame.display.flip()
    return options_positions




def handle_voting(mouse_x, mouse_y):
    for candidate, position in candidate_positions.items():
        button_rect = pygame.Rect(position[0], position[1], 200, 50)
        if button_rect.collidepoint(mouse_x, mouse_y):
            rank_candidate(candidate)
            return  # Exit after the first button is found and handled


def rank_candidate(candidate):
    global candidate_rankings
    # Determine the next available rank
    current_rank = candidate_rankings[candidate]
    if current_rank is None:
        # Assign the next highest rank if not already ranked
        ranks = set(candidate_rankings.values()) - {None}
        if ranks:
            next_rank = max(ranks) + 1
        else:
            next_rank = 1
        candidate_rankings[candidate] = next_rank
    else:
        # Remove the candidate's rank and downgrade ranks of others if necessary
        for other_candidate, rank in candidate_rankings.items():
            if rank and rank > current_rank:
                candidate_rankings[other_candidate] = rank - 1
        candidate_rankings[candidate] = None

def get_vote_counts(vote_rankings, active_candidates):
    counts = {candidate: 0 for candidate in active_candidates}
    for ranking in vote_rankings:  # Changed from vote_rankings.values() to vote_rankings
        if ranking:
            first_choice = ranking[0]
            if first_choice in active_candidates:
                counts[first_choice] += 1
    return counts


def get_winner(vote_counts):
    total_votes = sum(vote_counts.values())
    for candidate, count in vote_counts.items():
        if count > total_votes / 2:
            return candidate  # This candidate is the winner
    return None  # No winner if nobody has more than half the votes



def count_irv_votes(vote_rankings):
    round_details = []
    while True:
        # Count the votes
        counts = get_vote_counts(vote_rankings)
        round_details.append(dict(counts))  # Keep track of each round's details
        winner = get_winner(counts)
        if winner:
            return winner, round_details  # Return both the winner and the round details
        else:
            eliminated = eliminate_candidate(counts)
            # Redistribute votes from the eliminated candidate
            for prefs in vote_rankings.values():
                if eliminated in prefs:
                    prefs.remove(eliminated)
    

    
# Eliminate the candidate with the fewest votes
def eliminate_candidate(counts):
    # Find the candidate with the least votes
    lowest_votes = min(counts.values())
    for candidate, count in counts.items():
        if count == lowest_votes:
            return candidate
    
    # The main counting loop
    while True:
        counts = get_vote_counts(temp_rankings)
        winner = get_winner(counts)
        if winner:
            return winner
        else:
            # Eliminate the lowest candidate and remove them from the rankings
            to_eliminate = eliminate_candidate(counts)
            for ranking in temp_rankings.values():
                if to_eliminate in ranking:
                    ranking.remove(to_eliminate)

def count_votes():
    global game_state, tutorial_step, round_results
    vote_preferences = {
        candidate: [cand for cand, rank in sorted(candidate_rankings.items(), key=lambda item: item[1]) if rank]
        for candidate in candidates
    }
    round_results = []
    active_candidates = candidates.copy()
    
    while len(active_candidates) > 1:
        round_votes = get_vote_counts(vote_preferences, active_candidates)
        round_results.append(round_votes.copy())  # Track results for each round
        
        # Check for a winner or redistribute votes
        total_votes = sum(round_votes.values())
        for candidate, votes in round_votes.items():
            if votes > total_votes / 2:
                return candidate, round_results  # Winner found
        
        # No winner, eliminate last place candidate and redistribute votes
        eliminated_candidates = eliminate_candidate(round_votes)
        active_candidates = [cand for cand in active_candidates if cand not in eliminated_candidates]
        for preference_list in vote_preferences.values():
            preference_list[:] = [cand for cand in preference_list if cand in active_candidates]  # In-place modification of the list
    
    # If all candidates are eliminated and no winner is found
    return None, round_results


if __name__ == '__main__':
    run_game()
