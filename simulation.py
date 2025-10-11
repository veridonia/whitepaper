import random
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored
from tqdm import tqdm
import math
import scipy.stats as st
import argparse


class User:
    def __init__(self, id, elo=800):
        self.id = id
        self.elo = elo
        self.goodness = self.generate_goodness()
        self.mood_factor = random.uniform(0.05, 0.15)
        self.adjusted_goodness = self.goodness

    def generate_goodness(self):
        goodness = np.random.exponential(scale=0.3)
        if goodness >= 1:
            goodness = np.random.uniform()
        return goodness

    def apply_mood(self):
        self.adjusted_goodness = self.goodness
        if random.random() < self.mood_factor:
            adjustment = random.uniform(0, 0.25)
            if random.choice([True, False]):
                self.adjusted_goodness = min(1, self.goodness * (1 + adjustment))
            else:
                self.adjusted_goodness = max(0, self.goodness * (1 - adjustment))


class Post:
    def __init__(self, id, creator_user):
        self.id = id
        self.creator = creator_user
        self.creator_elo_at_creation = creator_user.elo
        base_quality = creator_user.goodness
        random_variation = random.uniform(-0.2, 0.2)
        self.quality = max(0, min(1, base_quality + random_variation))


def vote(user, post):
    user.apply_mood()
    if post.quality >= 0.5:
        vote_decision = (
            "support"
            if random.uniform(0, 1) < user.adjusted_goodness
            else random.choice(["oppose", "support"])
        )
    else:
        vote_decision = (
            "oppose"
            if random.uniform(0, 1) < user.adjusted_goodness
            else random.choice(["oppose", "support"])
        )
    return vote_decision


def stage_voting(stage_users, post, k_factor=32):
    votes = []
    stage_decision = "draw"
    for user in stage_users:
        vote_decision = vote(user, post)
        votes.append((user, vote_decision))
    supporters = [user for user, vote in votes if vote == "support"]
    opposers = [user for user, vote in votes if vote == "oppose"]
    if not supporters and opposers:
        winning_team = opposers
        losing_team = supporters
        stage_decision = "oppose"
    elif not opposers and supporters:
        winning_team = supporters
        losing_team = opposers
        stage_decision = "support"
    elif len(supporters) > len(opposers):
        winning_team = supporters
        losing_team = opposers
        stage_decision = "support"
    elif len(opposers) > len(supporters):
        winning_team = opposers
        losing_team = supporters
        stage_decision = "oppose"
    else:
        return votes, stage_decision
    if not losing_team:
        pass
    else:
        average_winner_elo = sum(user.elo for user in winning_team) / len(winning_team)
        average_loser_elo = sum(user.elo for user in losing_team) / len(losing_team)
        change_per_winner, change_per_loser = elo_update_team(
            average_winner_elo,
            average_loser_elo,
            k=k_factor,
            winner_size=len(winning_team),
            loser_size=len(losing_team),
        )
        for user in winning_team:
            user.elo += change_per_winner
        for user in losing_team:
            user.elo += change_per_loser
    return votes, stage_decision


def elo_update_team(winner_avg_elo, loser_avg_elo, k=32, winner_size=1, loser_size=1):
    expected_score_winner = 1 / (1 + 10 ** ((loser_avg_elo - winner_avg_elo) / 400))
    expected_score_loser = 1 - expected_score_winner
    total_winner_delta = k * (1 - expected_score_winner)
    total_loser_delta = k * (0 - expected_score_loser)
    change_per_winner = total_winner_delta / winner_size
    change_per_loser = total_loser_delta / loser_size
    return change_per_winner, change_per_loser


def count_votes(votes):
    support_votes = sum(1 for _, vote in votes if vote == "support")
    oppose_votes = sum(1 for _, vote in votes if vote == "oppose")
    total_votes = len(votes)
    majority_supported = support_votes > oppose_votes if total_votes > 0 else False
    return support_votes, oppose_votes, total_votes, majority_supported


def select_posting_users(users, num_posts, elo_scale=400):
    """
    Select users to create posts based on ELO-weighted probability.
    Uses a sigmoid-like function with steeper rise in the middle range.

    Args:
        users: List of all users
        num_posts: Number of posts to be created
        elo_scale: Scale parameter (lower = more extreme difference)

    Returns:
        List of selected users (can include duplicates if a user posts multiple times)
    """
    if not users:
        return []

    # Get ELO range
    min_elo = min(user.elo for user in users)
    max_elo = max(user.elo for user in users)
    mid_elo = (min_elo + max_elo) / 2  # Middle of the ELO range

    # Calculate posting probabilities using a sigmoid-like function
    # centered at the middle of the ELO range with steepness controlled by elo_scale
    weights = []
    for user in users:
        # Normalize ELO to be centered around 0 relative to the midpoint
        normalized_elo = (user.elo - mid_elo) / elo_scale

        # Apply sigmoid function: 1 / (1 + e^(-x))
        # Steepness is controlled by elo_scale - smaller values make the curve steeper
        sigmoid_weight = 1 / (
            1 + math.exp(-normalized_elo * 10)
        )  # Fixed steepness multiplier

        # Apply additional exponential scaling to make higher ELOs even more favored
        weight = sigmoid_weight  # No additional exponential scaling
        weights.append(weight)

    # Normalize weights to probabilities
    total_weight = sum(weights)
    probabilities = [w / total_weight for w in weights]

    # Select users based on weighted probabilities
    selected_users = []
    for _ in range(num_posts):
        selected_user = random.choices(users, weights=probabilities, k=1)[0]
        selected_users.append(selected_user)

    return selected_users


def multi_stage_voting(
    post,
    all_users,
    stage1_users=5,
    stage2_users=5,
    k_factor=32,
    stage1_split=70,
):
    """
    Implements a two-stage voting mechanism for a given post using ELO tiers.
    If the number of users is less than 20, a single stage voting is performed by selecting stage1_users from all users.
    Otherwise:
      - Stage 1: Bottom stage1_split% of all users (select stage1_users)
      - Stage 2: Top (100-stage1_split)% of all users (select stage2_users) - only if Stage 1 has more support than oppose votes
    Publishing rules:
      - Single stage: More support than oppose votes required to publish
      - Two stage: Stage 1 needs more support than oppose votes to advance to Stage 2, then Stage 2 needs more support than oppose votes to publish
    """

    # Use all users for voting
    if not all_users:
        return (
            [],
            "oppose",
            0,
            [],
            [],
            [],
        )  # Added empty lists for stage1, stage2 participants

    sorted_users = sorted(all_users, key=lambda u: u.elo)
    N = len(sorted_users)
    sample_size = 0

    stage1_participants = []
    stage2_participants = []
    if N < 20:
        stage_users = (
            sorted_users
            if N <= stage1_users
            else random.sample(sorted_users, stage1_users)
        )
        votes, stage_decision = stage_voting(stage_users, post, k_factor=k_factor)
        sample_size += len(votes)
        stage1_participants = [user for user, _ in votes]
        support_votes, oppose_votes, total_votes, majority_supported = count_votes(
            votes
        )

        if total_votes > 0:
            decision = "support" if majority_supported else "oppose"
        else:
            decision = "oppose"
    else:
        stage1_group = sorted_users[: int(stage1_split / 100.0 * N)]
        stage1_selected_users = (
            stage1_group
            if len(stage1_group) <= stage1_users
            else random.sample(stage1_group, stage1_users)
        )
        votes1, _ = stage_voting(stage1_selected_users, post, k_factor=k_factor)
        sample_size += len(votes1)
        stage1_participants = [user for user, _ in votes1]
        support_votes, oppose_votes, total_votes, majority_supported = count_votes(
            votes1
        )

        if total_votes > 0:
            if majority_supported:
                stage2_group = sorted_users[int(stage1_split / 100.0 * N) :]
                stage2_selected_users = (
                    stage2_group
                    if len(stage2_group) <= stage2_users
                    else random.sample(stage2_group, stage2_users)
                )
                votes2, _ = stage_voting(stage2_selected_users, post, k_factor=k_factor)
                sample_size += len(votes2)
                stage2_participants = [user for user, _ in votes2]
                stage2_support_votes, stage2_oppose_votes, stage2_total_votes, _ = (
                    count_votes(votes2)
                )

                if stage2_total_votes > 0:
                    decision = (
                        "support"
                        if stage2_support_votes > stage2_oppose_votes
                        else "oppose"
                    )
                    votes = votes2
                else:
                    votes, decision = votes2, "oppose"
            else:
                votes, decision = votes1, "oppose"
        else:
            votes, decision = votes1, "oppose"

    return (
        votes,
        decision,
        sample_size,
        stage1_participants,
        stage2_participants,
    )


def run_simulation(
    max_population=5000,
    posts_per_user=2,
    growth_rate=0.01,
    stage1_users=5,
    stage2_users=5,
    elo_start=800,
    k_factor=32,
    stage1_split=70,
    elo_posting_scale=100,
):

    with tqdm(total=max_population, desc="Growing user population") as pbar:
        posts = []
        supported_posts_count = 0
        total_votes = 0
        correct_votes = 0
        correct_votes_stats = []
        population_sizes = []
        users = []

        # Track participants count from each group
        stage1_participants_count = []
        stage2_participants_count = []
        stage1_population_sizes = []
        stage2_population_sizes = []

        population_increment = 1.0
        while len(users) < max_population:
            new_count = min(int(population_increment), max_population - len(users))

            if new_count > 0:
                new_users = [
                    User(i, elo=elo_start)
                    for i in range(len(users), len(users) + new_count)
                ]
                users.extend(new_users)

                posts_to_create = posts_per_user * new_count
                posting_users = select_posting_users(
                    users, posts_to_create, elo_posting_scale
                )

                new_posts = []
                for i, creator in enumerate(posting_users):
                    post_id = len(posts) + i
                    new_post = Post(post_id, creator)
                    new_posts.append(new_post)

                posts.extend(new_posts)

            for post in new_posts if new_count > 0 else []:
                sorted_users = sorted(users, key=lambda u: u.elo)
                stage1_group_size = int(stage1_split / 100.0 * len(sorted_users))
                stage2_group_size = len(sorted_users) - stage1_group_size

                stage1_population_sizes.append(stage1_group_size)
                stage2_population_sizes.append(stage2_group_size)
                (
                    votes,
                    decision,
                    post_sample_size,
                    stage1_participants,
                    stage2_participants,
                ) = multi_stage_voting(
                    post,
                    users,
                    stage1_users,
                    stage2_users,
                    k_factor,
                    stage1_split,
                )
                total_votes += 1
                stage1_participants_count.append(len(stage1_participants))
                stage2_participants_count.append(len(stage2_participants))

                is_correct = (decision == "support" and post.quality >= 0.5) or (
                    decision == "oppose" and post.quality < 0.5
                )

                if is_correct:
                    correct_votes += 1
                    correct_votes_stats.append(1)
                else:
                    correct_votes_stats.append(0)

                if decision == "support":
                    supported_posts_count += 1
            if new_count > 0:
                population_sizes.append(len(users))
                pbar.update(new_count)
                pbar.set_postfix(current=len(users))

            population_increment *= 1 + growth_rate
    print(f"Number of posts supported through all voting: {supported_posts_count}")
    print(f"Number of correct votes: {correct_votes}")
    print(f"Total number of votes: {total_votes}")
    print(f"Correct votes: {(correct_votes / total_votes) * 100:.2f}%")

    if posts:
        creator_elos = [post.creator_elo_at_creation for post in posts]
        print(f"\nPost Creation Statistics:")
        print(f"Total posts created: {len(posts)}")
        print(f"Average creator ELO at creation: {np.mean(creator_elos):.2f}")
        print(
            f"Creator ELO range at creation: {min(creator_elos):.1f} - {max(creator_elos):.1f}"
        )

        user_elos = [user.elo for user in users]
        print(f"Final user ELO range: {min(user_elos):.1f} - {max(user_elos):.1f}")
        print(f"Final average user ELO: {np.mean(user_elos):.2f}")

        creator_elo_quartiles = np.percentile(creator_elos, [25, 50, 75])
        q1, q2, q3 = creator_elo_quartiles

        print(f"Throttling Analysis (Creator ELO at post creation):")
        print(f"  Creator ELO range: {min(creator_elos):.1f} - {max(creator_elos):.1f}")
        print(f"  Creator ELO average: {np.mean(creator_elos):.1f}")
        print(f"  Population ELO average: {np.mean(user_elos):.1f}")

        elo_bias = np.mean(creator_elos) - np.mean(user_elos)
        print(f"  ELO bias (creators vs population): {elo_bias:+.1f} ELO points")

        print(f"  Creator ELO quartiles: Q1={q1:.1f}, Q2={q2:.1f}, Q3={q3:.1f}")
        print(f"    Q1-Q3 range: {q3-q1:.1f} ELO points")

        population_quartiles = np.percentile(user_elos, [25, 50, 75])
        print(
            f"  Population ELO quartiles: Q1={population_quartiles[0]:.1f}, Q2={population_quartiles[1]:.1f}, Q3={population_quartiles[2]:.1f}"
        )
        print(
            f"    Q1-Q3 range: {population_quartiles[2]-population_quartiles[0]:.1f} ELO points"
        )

        if elo_bias > 0:
            print(f"  → Throttling is working: Higher-ELO users create more posts")
        else:
            print(
                f"  → Throttling may not be effective or population hasn't spread enough"
            )

    plot_distributions(
        users,
        correct_votes_stats,
        population_sizes,
    )
    return users


def plot_distributions(
    users,
    correct_votes_stats,
    population_sizes,
):
    plt.figure(figsize=(16, 8))  # 2x2 grid layout

    # Subplot 1: Distribution of Users by Goodness Factor
    plt.subplot(2, 2, 1)

    user_goodness = [user.goodness for user in users]
    if user_goodness:
        # Define threshold for "good" vs "bad" users
        # Good users (goodness > 0.65): More likely to vote correctly than randomly
        # Bad users (goodness ≤ 0.65): Vote randomly or worse
        threshold = 0.65

        bad_users = [g for g in user_goodness if g <= threshold]
        good_users = [g for g in user_goodness if g > threshold]

        # Create stacked histogram with different colors
        plt.hist(
            [bad_users, good_users],
            bins=50,
            edgecolor="black",
            color=["#ff6b6b", "#51cf66"],  # Red for bad, green for good
            label=[
                f"Bad Users (≤ {threshold}): {len(bad_users)} users",
                f"Good Users (> {threshold}): {len(good_users)} users",
            ],
            alpha=0.8,
            stacked=True,
        )

        # Add vertical line at threshold
        plt.axvline(
            x=threshold,
            color="black",
            linestyle="--",
            alpha=0.7,
            linewidth=2,
            label=f"Threshold: {threshold}",
        )

        plt.legend(fontsize=9, loc="upper right")
    else:
        plt.hist(user_goodness, bins=50, edgecolor="black")

    plt.xlabel("Goodness Factor")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Goodness Factor\n(Bad vs Good Users)")

    # Subplot 2: Distribution of Users by Elo Rating with User Groups
    plt.subplot(2, 2, 2)

    user_elos = [user.elo for user in users]
    if user_elos:
        # Sort users by ELO to determine thresholds based on user count percentiles
        sorted_users = sorted(users, key=lambda u: u.elo)
        N = len(sorted_users)

        # Define thresholds based on user count percentiles (matching voting system)
        # Stage 1: bottom 70% of users by count
        # Stage 2: top 30% of users by count (includes editors)
        # Editor: top 1% of users by count (subset of Stage 2)
        stage1_cutoff_index = int(0.70 * N)  # Bottom 70% of users
        editor_cutoff_index = int(0.99 * N)  # Top 1% of users

        # Get the actual ELO values at these cutoff points
        stage1_threshold = (
            sorted_users[stage1_cutoff_index - 1].elo
            if stage1_cutoff_index > 0
            else sorted_users[0].elo
        )
        editor_threshold = (
            sorted_users[editor_cutoff_index - 1].elo
            if editor_cutoff_index > 0
            else sorted_users[0].elo
        )

        # Separate users into groups based on user count percentiles
        stage1_elos = [user.elo for user in sorted_users[:stage1_cutoff_index]]
        stage2_non_editor_elos = [
            user.elo for user in sorted_users[stage1_cutoff_index:editor_cutoff_index]
        ]
        editor_elos = [user.elo for user in sorted_users[editor_cutoff_index:]]

        # Stage 2 includes both non-editors and editors (top 30% total)
        stage2_elos = stage2_non_editor_elos + editor_elos

        # Create histogram with 50 bins
        bins = 50

        # Plot stacked histogram with different colors for each group
        # Stage 2 includes both regular voters and editors visually
        plt.hist(
            [stage1_elos, stage2_non_editor_elos, editor_elos],
            bins=bins,
            edgecolor="black",
            log=True,
            color=["#ff9999", "#99ccff", "#51cf66"],  # Red, Blue, Green
            label=[
                f"Stage 1 Voters (Bottom 70%): {len(stage1_elos)} users",
                f"Stage 2 Voters (Top 30%): {len(stage2_elos)} users",
                f"Editors (Top 1%): {len(editor_elos)} users",
            ],
            alpha=0.8,
            stacked=True,
        )

        # Add vertical line at Stage 1/Stage 2 threshold
        plt.axvline(
            x=stage1_threshold,
            color="blue",
            linestyle="--",
            alpha=0.7,
            linewidth=2,
            label=f"70th percentile (by user count): {stage1_threshold:.1f}",
        )

        # Add vertical line at editor threshold (for reference)
        plt.axvline(
            x=editor_threshold,
            color="green",
            linestyle="--",
            alpha=0.7,
            linewidth=2,
            label=f"99th percentile (by user count): {editor_threshold:.1f}",
        )

        plt.legend(fontsize=8, loc="upper right")
    else:
        plt.hist(user_elos, bins=50, edgecolor="black", log=True)

    plt.xlabel("Elo Rating")
    plt.ylabel("Number of Users (log scale)")
    plt.title("Distribution of Users by Elo Rating")

    # Subplot 3: Correct Votes Ratio with Linear Regression
    plt.subplot(2, 2, 3)
    if len(correct_votes_stats) > 10:
        if len(correct_votes_stats) < 50:
            window_size = min(10, len(correct_votes_stats))
        else:
            window_size = max(10, int(len(correct_votes_stats) / 100))

        staged_smoothed = (
            np.convolve(
                correct_votes_stats, np.ones(window_size) / window_size, mode="valid"
            )
            * 100
        )

        x = np.arange(len(staged_smoothed))

        # Linear regression for staged voting
        (
            staged_slope,
            staged_intercept,
            staged_r_value,
            staged_p_value,
            staged_std_err,
        ) = st.linregress(x, staged_smoothed)
        staged_r_squared = staged_r_value**2

        # Plot original data
        plt.plot(x, staged_smoothed, "b-", label="Staged Voting", alpha=0.7)

        # Plot regression line
        plt.plot(
            x,
            staged_slope * x + staged_intercept,
            "b--",
            label=f"Regression (R²={staged_r_squared:.3f})",
        )

    else:
        x = np.arange(len(correct_votes_stats))

        # Linear regression for raw data
        (
            staged_slope,
            staged_intercept,
            staged_r_value,
            staged_p_value,
            staged_std_err,
        ) = st.linregress(x, np.array(correct_votes_stats) * 100)
        staged_r_squared = staged_r_value**2

        # Plot original data
        plt.plot(
            x,
            np.array(correct_votes_stats) * 100,
            "b-",
            label="Staged Voting",
            alpha=0.7,
        )

        # Plot regression line
        plt.plot(
            x,
            staged_slope * x + staged_intercept,
            "b--",
            label=f"Regression (R²={staged_r_squared:.3f})",
        )

    plt.title("Correct Votes Ratio")
    plt.xlabel("Stage Index")
    plt.ylabel("Proportion of Correct Votes (%)")
    plt.ylim(0, 110)
    plt.grid(True)
    plt.legend()

    # Subplot 4: Population Over Time
    plt.subplot(2, 2, 4)
    plt.plot(range(len(population_sizes)), population_sizes, label="Population Size")
    plt.xlabel("Stage Index")
    plt.ylabel("Population Size")
    plt.title("Population Over Time")

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Veridonia Voting Simulation")

    # Population and content parameters
    parser.add_argument(
        "--max-population",
        type=int,
        default=5000,
        help="Maximum population size (default: 5000)",
    )
    parser.add_argument(
        "--posts-per-user", type=int, default=2, help="Posts per user (default: 2)"
    )
    parser.add_argument(
        "--growth-rate",
        type=float,
        default=0.05,
        help="Population growth rate (default: 0.05)",
    )

    # Voting stage parameters
    parser.add_argument(
        "--stage1-users",
        type=int,
        default=5,
        help="Number of users in stage 1 voting (default: 5)",
    )
    parser.add_argument(
        "--stage2-users",
        type=int,
        default=5,
        help="Number of users in stage 2 voting (default: 5)",
    )

    # ELO parameters
    parser.add_argument(
        "--elo-start",
        type=int,
        default=800,
        help="Starting ELO rating for new users (default: 800)",
    )

    parser.add_argument(
        "--k-factor",
        type=int,
        default=32,
        help="K-factor for ELO calculations (default: 32)",
    )
    parser.add_argument(
        "--elo-posting-scale",
        type=int,
        default=100,
        help="ELO scale for posting probability (lower = more extreme throttling) (default: 100)",
    )
    parser.add_argument(
        "--stage1-split",
        type=int,
        default=70,
        help="Percentage of high-ELO users for stage 1 (remaining go to stage 2) (default: 70)",
    )

    args = parser.parse_args()

    # Run simulation with parsed arguments
    users = run_simulation(
        max_population=args.max_population,
        posts_per_user=args.posts_per_user,
        growth_rate=args.growth_rate,
        stage1_users=args.stage1_users,
        stage2_users=args.stage2_users,
        elo_start=args.elo_start,
        k_factor=args.k_factor,
        stage1_split=args.stage1_split,
        elo_posting_scale=args.elo_posting_scale,
    )

    return users


if __name__ == "__main__":
    users = main()
