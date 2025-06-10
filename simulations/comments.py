import random
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored
from tqdm import tqdm
import math
import scipy.stats as st


class User:
    def __init__(self, id):
        self.id = id
        # Normal distribution with median 800 and standard deviation 200
        self.elo = max(0, random.gauss(800, 200))
        self.vote_count = 0
        self.percentile_rank = None  # Will be calculated after all users are created

    def get_voting_accuracy(self):
        """
        Return the voting accuracy based on percentile rank.
        0th percentile: 0.5 (random guessing)
        100th percentile: 1.0 (perfect accuracy)
        """
        if self.percentile_rank is None:
            return 0.5  # Default to random guessing if percentile not set

        # Linear scaling from 0.5 (random) to 1.0 (perfect)
        return 0.5 + 0.5 * (self.percentile_rank / 100)


class Comment:
    def __init__(self, id):
        self.id = id
        self.quality = self.generate_quality()  # Intrinsic quality from 0 to 1
        self.elo = 800  # Default ELO rating
        self.upvotes = 0
        self.downvotes = 0

    def generate_quality(self):
        """
        Generate quality with exponential decay distribution.
        Similar to user goodness factor in the posts simulation.
        """
        quality = np.random.exponential(scale=0.3)  # Adjusted scale to 0.3
        if quality > 1:
            quality = np.random.uniform()
        return quality

    def get_score(self):
        return self.upvotes - self.downvotes

    def get_total_votes(self):
        return self.upvotes + self.downvotes


def elo_update(winner_elo, loser_elo, k=32):
    expected_score = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_score)
    new_loser_elo = loser_elo - k * (1 - expected_score)
    return new_winner_elo, new_loser_elo


def calculate_sorting_quality(real_comments, ideal_comments):
    """
    Calculate sorting quality using Spearman's rank correlation coefficient (ρ).
    This measures how well the ranking by ELO correlates with the ideal ranking by quality.

    Args:
        real_comments: List of comments sorted by ELO rating
        ideal_comments: List of comments sorted by intrinsic quality

    Returns:
        Spearman's ρ scaled to percentage (100% means perfect correlation)
    """
    # Create mappings from comment ID to rank
    real_ranks = {comment.id: i for i, comment in enumerate(real_comments)}
    ideal_ranks = {comment.id: i for i, comment in enumerate(ideal_comments)}

    # Get all comment IDs
    comment_ids = list(real_ranks.keys())

    # Extract ranks for each comment
    real_rank_values = [real_ranks[cid] for cid in comment_ids]
    ideal_rank_values = [ideal_ranks[cid] for cid in comment_ids]

    # Calculate Spearman's rank correlation coefficient
    if len(comment_ids) <= 1:
        return 100.0  # Perfect correlation for 0 or 1 comment

    correlation, _ = st.spearmanr(real_rank_values, ideal_rank_values)

    # Convert to percentage (1.0 -> 100%, -1.0 -> 0%)
    # Scale from [-1, 1] to [0, 100]
    return ((correlation + 1) / 2) * 100


def calculate_percentile_ranks(users):
    """
    Calculate percentile ranks for all users based on their ELO ratings.
    """
    # Sort users by ELO
    sorted_users = sorted(users, key=lambda u: u.elo)
    total_users = len(sorted_users)

    # Calculate percentile ranks (0-100)
    for i, user in enumerate(sorted_users):
        user.percentile_rank = (i / (total_users - 1)) * 100 if total_users > 1 else 50


def compare_comments(user, comment_a, comment_b):
    """
    User compares two comments and selects the one with higher perceived quality.
    The user's ability to choose correctly depends on their percentile rank.
    Comment quality difference also influences the decision.

    Returns: The comment chosen by the user (either comment_a or comment_b)
    """
    # Determine which comment actually has higher quality
    higher_quality_comment = (
        comment_a if comment_a.quality > comment_b.quality else comment_b
    )
    lower_quality_comment = (
        comment_b if higher_quality_comment == comment_a else comment_a
    )

    # Calculate quality difference - influences how easy it is to tell which is better
    quality_diff = abs(comment_a.quality - comment_b.quality)

    # Combine user percentile rank and quality difference to determine accuracy
    # If quality diff is high, even users with lower percentile can identify better comment
    # If quality diff is low, even users with high percentile may struggle
    perception_accuracy = user.get_voting_accuracy() * (0.5 + quality_diff)

    # Cap accuracy at 0.99 (even the best users might make mistakes)
    perception_accuracy = min(0.99, perception_accuracy)

    # User makes the correct choice based on perception accuracy
    if random.uniform(0, 1) < perception_accuracy:
        chosen_comment = (
            higher_quality_comment  # User correctly identifies higher quality
        )
    else:
        chosen_comment = random.choice([comment_a, comment_b])  # Random choice

    user.vote_count += 1

    return chosen_comment


def run_simulation():
    max_population = 10000  # All users at once
    max_comments = 100  # Maximum number of comments to add
    voting_rounds_per_comment = 20  # Number of voting rounds for each new comment

    # Initialize all 10000 users at the start
    all_users = [User(i) for i in range(max_population)]

    # Calculate percentile ranks for all users
    calculate_percentile_ranks(all_users)

    # Filter users with ELO > 800 who can vote
    voting_users = [user for user in all_users if user.elo > 800]
    print(
        f"Total users: {len(all_users)}, Voting users (ELO > 800): {len(voting_users)}"
    )

    # Start with just 1 comment
    comments = [Comment(0)]
    comment_id_counter = 1

    # Metrics to track
    population_sizes = []
    voting_rates = []
    sorting_quality_scores = []
    random_sorting_quality_scores = []
    ideal_quality_scores = []
    comments_count = []

    total_voters = 0
    processed_count = 0

    with tqdm(total=max_comments, desc="Adding comments") as pbar:
        # Add comments one by one, up to max_comments
        while len(comments) < max_comments:
            # Add a new comment
            new_comment = Comment(comment_id_counter)
            comments.append(new_comment)
            comment_id_counter += 1

            # For each new comment, run multiple rounds of voting
            for _ in range(voting_rounds_per_comment):
                # Select a random user from voting users (ELO > 800)
                user = random.choice(voting_users)

                # Select comment A from the 30% newest comments
                newest_count = max(1, int(len(comments) * 0.3))
                comment_a = random.choice(comments[-newest_count:])

                # Find a comment B with ELO close to comment A
                # Filter comments that are within ±100 ELO points from comment A
                elo_range = 100  # Fixed range of 100 ELO points
                comments_in_range = [
                    c
                    for c in comments
                    if c != comment_a and abs(c.elo - comment_a.elo) <= elo_range
                ]

                # If no comments in range, take the closest one
                if not comments_in_range:
                    sorted_by_elo_distance = sorted(
                        [c for c in comments if c != comment_a],
                        key=lambda c: abs(c.elo - comment_a.elo),
                    )
                    comment_b = sorted_by_elo_distance[0]  # Take the closest one
                else:
                    # Select random comment from the filtered list
                    comment_b = random.choice(comments_in_range)

                # User chooses between the two comments
                chosen_comment = compare_comments(user, comment_a, comment_b)

                # Update ELO ratings
                if chosen_comment == comment_a:
                    comment_a.elo, comment_b.elo = elo_update(
                        comment_a.elo, comment_b.elo
                    )
                else:
                    comment_b.elo, comment_a.elo = elo_update(
                        comment_b.elo, comment_a.elo
                    )

                # Update counters
                processed_count += 1
                total_voters += 1

            # Calculate voting rate as total voters / processed count
            voting_rate = total_voters / processed_count
            voting_rates.append(voting_rate)

            # Sort comments by their ELO rating
            real_sorted_comments = sorted(comments, key=lambda c: c.elo, reverse=True)

            # Ideal sorted comments by intrinsic quality
            ideal_sorted_comments = sorted(
                comments, key=lambda c: c.quality, reverse=True
            )

            # Randomly shuffled comments for baseline comparison
            random_sorted_comments = comments.copy()
            random.shuffle(random_sorted_comments)

            # Calculate sorting quality
            sorting_quality = calculate_sorting_quality(
                real_sorted_comments, ideal_sorted_comments
            )
            sorting_quality_scores.append(sorting_quality)

            # Calculate random sorting quality
            random_sorting_quality = calculate_sorting_quality(
                random_sorted_comments, ideal_sorted_comments
            )
            random_sorting_quality_scores.append(random_sorting_quality)

            # Record ideal quality (100%) for comparison
            ideal_quality_scores.append(100.0)

            # Record population size as processed count (for x-axis)
            population_sizes.append(processed_count)
            comments_count.append(len(comments))

            pbar.update(1)
            pbar.set_postfix(comments=len(comments))

        plot_results(
            all_users,
            comments,
            population_sizes,
            voting_rates,
            sorting_quality_scores,
            random_sorting_quality_scores,
            ideal_quality_scores,
            comments_count,
            voting_users,
        )

    return all_users


def plot_results(
    all_users,
    comments,
    population_sizes,
    voting_rates,
    sorting_quality_scores,
    random_sorting_quality_scores,
    ideal_quality_scores,
    comments_count,
    voting_users,
):
    # Ensure all arrays have the same length for plotting
    min_length = min(
        len(population_sizes),
        len(voting_rates),
        len(sorting_quality_scores),
        len(random_sorting_quality_scores),
        len(ideal_quality_scores),
        len(comments_count),
    )

    population_sizes = population_sizes[:min_length]
    voting_rates = voting_rates[:min_length]
    sorting_quality_scores = sorting_quality_scores[:min_length]
    random_sorting_quality_scores = random_sorting_quality_scores[:min_length]
    ideal_quality_scores = ideal_quality_scores[:min_length]
    comments_count = comments_count[:min_length]

    plt.figure(figsize=(15, 8))

    # Create a 2x3 grid layout
    # Subplot 1: Distribution of All Users by ELO
    plt.subplot(2, 3, 1)
    plt.hist([user.elo for user in all_users], bins=50, edgecolor="black")
    plt.axvline(x=800, color="r", linestyle="--", label="ELO = 800")
    plt.xlabel("User ELO")
    plt.ylabel("Number of Users")
    plt.title("Distribution of All Users by ELO")
    plt.legend()
    plt.grid(True)

    # Subplot 2: Distribution of Comments by Quality
    plt.subplot(2, 3, 2)
    plt.hist([comment.quality for comment in comments], bins=50, edgecolor="black")
    plt.xlabel("Quality")
    plt.ylabel("Number of Comments")
    plt.title("Distribution of Comments by Quality")
    plt.grid(True)

    # Subplot 3: Distribution of Comments by Elo Rating
    plt.subplot(2, 3, 3)
    plt.hist([comment.elo for comment in comments], bins=50, edgecolor="black")
    plt.xlabel("Elo Rating")
    plt.ylabel("Number of Comments")
    plt.title("Distribution of Comments by Elo Rating")
    plt.grid(True)

    # Subplot 4: Sorting Quality over Time
    plt.subplot(2, 3, 4)
    plt.plot(population_sizes, sorting_quality_scores, label="Actual Sorting Quality")
    plt.plot(
        population_sizes, random_sorting_quality_scores, label="Random Sorting Quality"
    )
    plt.plot(
        population_sizes, ideal_quality_scores, "r--", label="Ideal Sorting Quality"
    )
    plt.xlabel("Total Voting Rounds")
    plt.ylabel("Sorting Quality (%)")
    plt.title("Sorting Quality Over Time")
    plt.legend()
    plt.grid(True)

    # Subplot 5: Quality vs ELO Scatter Plot
    plt.subplot(2, 3, 5)
    plt.scatter([c.quality for c in comments], [c.elo for c in comments], alpha=0.5)
    plt.xlabel("Comment Quality")
    plt.ylabel("Comment ELO")
    plt.title("Comment Quality vs ELO Rating")
    plt.grid(True)

    # Subplot 6: Voting User Statistics
    plt.subplot(2, 3, 6)
    plt.text(
        0.5,
        0.5,
        f"Total Users: {len(all_users)}\nVoting Users (ELO > 800): {len(voting_users)}\nPercentage: {len(voting_users)/len(all_users)*100:.1f}%",
        horizontalalignment="center",
        verticalalignment="center",
        transform=plt.gca().transAxes,
        fontsize=12,
    )
    plt.axis("off")
    plt.title("Voting User Statistics")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_simulation()
