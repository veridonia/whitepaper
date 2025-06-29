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
        self.mood_factor = random.uniform(0, 0.1)  # Random value from 0 to 0.1
        self.adjusted_goodness = self.goodness
        self.vote_count = 0

    def generate_goodness(self):
        goodness = np.random.exponential(scale=0.3)  # Adjusted scale to 0.3
        if goodness > 1:
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
        self.creator_elo_at_creation = creator_user.elo  # Store ELO at time of creation
        # Post quality is influenced by creator's goodness with some randomness
        # Base quality from user's goodness, plus random variation
        base_quality = creator_user.goodness
        random_variation = random.uniform(-0.2, 0.2)  # ±20% variation
        self.quality = max(0, min(1, base_quality + random_variation))


def elo_update(winner_elo, loser_elo, k=32):
    expected_score = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_score)
    new_loser_elo = loser_elo - k * (1 - expected_score)
    return new_winner_elo, new_loser_elo


def vote(user, post):
    user.apply_mood()  # Update adjusted goodness before voting
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
    user.vote_count += 1
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
        # No ELO change when there's no opposing team
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
            user.elo += change_per_loser  # (it's negative, so they lose Elo)
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
    """Helper function to count support and oppose votes and determine if majority supported."""
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

    # Lists to track which users participated in each stage
    stage1_participants = []
    stage2_participants = []

    # If there are less than 20 filtered users, perform single stage voting
    if N < 20:
        stage_users = (
            sorted_users
            if N <= stage1_users
            else random.sample(sorted_users, stage1_users)
        )
        votes, stage_decision = stage_voting(stage_users, post, k_factor=k_factor)
        sample_size += len(votes)
        stage1_participants = [
            user for user, _ in votes
        ]  # Consider these as stage 1 participants

        # Check if single stage has more support than oppose votes to publish
        support_votes, oppose_votes, total_votes, majority_supported = count_votes(
            votes
        )

        if total_votes > 0:
            decision = "support" if majority_supported else "oppose"
        else:
            decision = "oppose"
    else:
        # Stage 1: Bottom X% of the filtered users
        stage1_group = sorted_users[: int(stage1_split / 100.0 * N)]
        stage1_selected_users = (
            stage1_group
            if len(stage1_group) <= stage1_users
            else random.sample(stage1_group, stage1_users)
        )
        votes1, _ = stage_voting(stage1_selected_users, post, k_factor=k_factor)
        sample_size += len(votes1)
        stage1_participants = [user for user, _ in votes1]

        # Check if stage 1 has more support than oppose votes to advance to stage 2
        support_votes, oppose_votes, total_votes, majority_supported = count_votes(
            votes1
        )

        if total_votes > 0:
            if majority_supported:
                # Stage 1 has more support than oppose votes, advance to Stage 2
                stage2_group = sorted_users[int(stage1_split / 100.0 * N) :]
                stage2_selected_users = (
                    stage2_group
                    if len(stage2_group) <= stage2_users
                    else random.sample(stage2_group, stage2_users)
                )
                votes2, _ = stage_voting(stage2_selected_users, post, k_factor=k_factor)
                sample_size += len(votes2)
                stage2_participants = [user for user, _ in votes2]

                # Check if stage 2 has more support than oppose votes to publish
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
                # Stage 1 doesn't have more support than oppose votes, reject without going to stage 2
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
    growth_rate=0.10,
    stage1_users=5,
    stage2_users=5,
    elo_start=800,
    k_factor=32,
    stage1_split=70,
    elo_posting_scale=100,
):

    with tqdm(total=max_population, desc="Growing user population") as pbar:
        posts = []
        supported_posts_quality = []
        supported_posts_count = 0
        total_votes = 0
        correct_votes = 0
        correct_votes_stats = []
        votes_stats = []
        population_sizes = []
        sample_sizes = []
        cumulative_votes_list = []
        users = []

        # Track participants count from each group
        stage1_participants_count = []
        stage2_participants_count = []

        # Track population of each group over time
        stage1_population_sizes = []
        stage2_population_sizes = []

        population_increment = 1.0  # Start by adding 1 user at a time
        while len(users) < max_population:
            new_count = min(
                math.ceil(population_increment), max_population - len(users)
            )
            new_users = [
                User(i, elo=elo_start)
                for i in range(len(users), len(users) + new_count)
            ]
            users.extend(new_users)

            # Calculate how many posts should be created this iteration
            posts_to_create = posts_per_user * new_count

            # Select users who will create posts (probabilistically based on ELO)
            posting_users = select_posting_users(
                users, posts_to_create, elo_posting_scale
            )

            # Create posts with their creators
            new_posts = []
            for i, creator in enumerate(posting_users):
                post_id = len(posts) + i
                new_post = Post(post_id, creator)
                new_posts.append(new_post)

            posts.extend(new_posts)

            for post in new_posts:
                # Record group populations at this point
                sorted_users = sorted(users, key=lambda u: u.elo)
                # Stage 1: Bottom X%
                stage1_group_size = int(stage1_split / 100.0 * len(sorted_users))
                # Stage 2: Top (100-X)%
                stage2_group_size = len(sorted_users) - stage1_group_size

                stage1_population_sizes.append(stage1_group_size)
                stage2_population_sizes.append(stage2_group_size)

                # Regular staged voting
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
                total_votes += 1  # Count one final decision per post

                # Store participants count from each group
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

                votes_stats.append((post.id, decision))
                if decision == "support":
                    supported_posts_count += 1
                    supported_posts_quality.append(post.quality)

                cumulative_votes_list.append(total_votes)
                sample_sizes.append(post_sample_size)

            # Append the population size once per iteration
            population_sizes.append(len(users))
            pbar.update(new_count)
            pbar.set_postfix(current=len(users))
            population_increment *= 1 + growth_rate
    print(f"Number of posts supported through all voting: {supported_posts_count}")
    print(f"Number of correct votes: {correct_votes}")
    print(f"Total number of votes: {total_votes}")
    print(f"Correct votes: {(correct_votes / total_votes) * 100:.2f}%")

    # Show post creation statistics
    if posts:
        creator_elos = [
            post.creator_elo_at_creation for post in posts
        ]  # Use ELO at creation time
        print(f"\nPost Creation Statistics:")
        print(f"Total posts created: {len(posts)}")
        print(f"Average creator ELO at creation: {np.mean(creator_elos):.2f}")
        print(
            f"Creator ELO range at creation: {min(creator_elos):.1f} - {max(creator_elos):.1f}"
        )

        # Show ELO distribution of post creators
        user_elos = [user.elo for user in users]
        print(f"Final user ELO range: {min(user_elos):.1f} - {max(user_elos):.1f}")
        print(f"Final average user ELO: {np.mean(user_elos):.2f}")

        # Count posts by CREATOR ELO quartiles (to show throttling bias properly)
        # Use creator ELO distribution to avoid temporal mismatch issues
        creator_elo_quartiles = np.percentile(creator_elos, [25, 50, 75])
        q1, q2, q3 = creator_elo_quartiles

        # By definition, each quartile has 25% of posts. Calculate throttling effect differently.
        # Show the ELO range disparity and average ELO bias instead.
        print(f"Throttling Analysis (Creator ELO at post creation):")
        print(f"  Creator ELO range: {min(creator_elos):.1f} - {max(creator_elos):.1f}")
        print(f"  Creator ELO average: {np.mean(creator_elos):.1f}")
        print(f"  Population ELO average: {np.mean(user_elos):.1f}")

        elo_bias = np.mean(creator_elos) - np.mean(user_elos)
        print(f"  ELO bias (creators vs population): {elo_bias:+.1f} ELO points")

        # Show quartile ranges to demonstrate the clustering effect you observed
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
        posts,
        supported_posts_quality,
        correct_votes_stats,
        population_sizes,
        sample_sizes,
        cumulative_votes_list,
        stage1_participants_count,
        stage2_participants_count,
        stage1_population_sizes,
        stage2_population_sizes,
        stage1_split,
        elo_posting_scale,
    )
    return users


def printStageResult(
    stage, post, votes, stage_result, users, users_stage_count, num_stage_users
):
    creator_info = f" (Created by User {post.creator.id}, ELO at creation: {post.creator_elo_at_creation:.1f})"
    print(
        f"Stage {stage} voting for Post {post.id}{creator_info} (Quality: {post.quality:.2f}):"
    )
    print(
        f"Total users: {len(users)}; In stage: {users_stage_count}; Selected: {num_stage_users}"
    )
    for user, vote in votes:
        color_mapping = {"support": "green", "oppose": "red", "draw": "yellow"}
        vote_colored = colored(vote, color_mapping.get(vote, "default_color"))
        print(
            f"User {user.id} (Adj. Goodness: {user.adjusted_goodness:.2f}, ELO: {user.elo:.2f}) voted {vote_colored}"
        )
    stage_result_colored = colored(
        stage_result, color_mapping.get(stage_result, "default_color")
    )
    print(f"Stage {stage} majority decision: {stage_result_colored}\n")


def aggregate_votes(votes, chunk_size):
    aggregated_data = []
    for i in range(0, len(votes), chunk_size):
        chunk = votes[i : i + chunk_size]
        proportion_correct = np.sum(chunk) / len(chunk) * 100
        aggregated_data.append(proportion_correct)
    return aggregated_data


def plot_distributions(
    users,
    posts,
    supported_posts_quality,
    correct_votes_stats,
    population_sizes,
    sample_sizes,
    cumulative_votes_list,
    stage1_participants_count,
    stage2_participants_count,
    stage1_population_sizes,
    stage2_population_sizes,
    stage1_split,
    elo_posting_scale,
):
    plt.figure(figsize=(20, 8))  # Increased width for 2x4 grid

    # Subplot 1: Distribution of Users by Goodness Factor
    plt.subplot(2, 4, 1)
    plt.hist([user.goodness for user in users], bins=50, edgecolor="black")
    plt.xlabel("Goodness Factor")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Goodness Factor")

    # Subplot 2: Distribution of Users by Elo Rating
    plt.subplot(2, 4, 2)
    plt.hist([user.elo for user in users], bins=50, edgecolor="black", log=True)
    plt.xlabel("Elo Rating")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Elo Rating")

    # Subplot 3: Correct Votes Ratio with Linear Regression
    plt.subplot(2, 4, 3)
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
    plt.subplot(2, 4, 4)
    plt.plot(range(len(population_sizes)), population_sizes, label="Population Size")
    plt.xlabel("Stage Index")
    plt.ylabel("Population Size")
    plt.title("Population Over Time")

    # Subplot 5: Sample Size Used Over Time
    plt.subplot(2, 4, 5)

    # Aggregate sample sizes by taking max values over intervals
    target_points = 50  # Target number of data points to show
    if len(sample_sizes) > target_points:
        # For larger datasets, show max values over intervals
        interval_size = max(
            1, len(sample_sizes) // target_points
        )  # Dynamic interval based on data size
        aggregated_sample_sizes = []
        aggregated_indices = []

        for i in range(0, len(sample_sizes), interval_size):
            chunk = sample_sizes[i : i + interval_size]
            if chunk:  # Make sure chunk is not empty
                aggregated_sample_sizes.append(max(chunk))
                aggregated_indices.append(
                    i + interval_size // 2
                )  # Use middle of interval as x-position

        plt.plot(
            aggregated_indices,
            aggregated_sample_sizes,
            "go-",
            label="Max Sample Size (Intervals)",
            markersize=4,
        )
        plt.xlabel("Stage Index")
        plt.ylabel("Number of Voters")
        plt.title(f"Sample Size Used Over Time (Max per {interval_size} rounds)")
    else:
        # For smaller datasets, show all values
        plt.plot(range(len(sample_sizes)), sample_sizes, color="g", label="Sample Size")
        plt.xlabel("Stage Index")
        plt.ylabel("Number of Voters")
        plt.title("Sample Size Used Over Time")

    plt.legend()

    # Subplot 6: Post Creation Bias by ELO Quartiles
    plt.subplot(2, 4, 6)

    if posts:
        # Get ELO data - use creation-time ELO for posts
        user_elos = [user.elo for user in users]  # Current ELO for users
        creator_elos_at_creation = [
            post.creator_elo_at_creation for post in posts
        ]  # ELO at creation time

        # Calculate quartiles based on ELO VALUE RANGE (not population percentiles)
        # Split the ELO range into 4 equal intervals
        min_elo = min(user_elos)
        max_elo = max(user_elos)
        elo_range = max_elo - min_elo

        # Create 4 equal ELO intervals
        q1 = min_elo + elo_range * 0.25
        q2 = min_elo + elo_range * 0.50
        q3 = min_elo + elo_range * 0.75
        # q4 boundary is max_elo

        # Count how many users are in each ELO quartile (can be uneven!)
        user_counts = [
            sum(1 for elo in user_elos if elo <= q1),  # Q1: lowest 25% of ELO range
            sum(1 for elo in user_elos if q1 < elo <= q2),  # Q2: next 25% of ELO range
            sum(1 for elo in user_elos if q2 < elo <= q3),  # Q3: next 25% of ELO range
            sum(1 for elo in user_elos if elo > q3),  # Q4: highest 25% of ELO range
        ]

        # Count posts by population ELO quartiles (using CURRENT creator ELO)
        # This shows: "Users currently in each quartile created how many posts?"
        post_counts = [0, 0, 0, 0]
        for post in posts:
            creator_current_elo = post.creator.elo  # Current ELO of the creator
            if creator_current_elo <= q1:
                post_counts[0] += 1
            elif creator_current_elo <= q2:
                post_counts[1] += 1
            elif creator_current_elo <= q3:
                post_counts[2] += 1
            else:
                post_counts[3] += 1

        # Calculate posts per user in each quartile (approximation)
        # Note: This is approximate since we're using current user distribution vs creation-time post distribution
        posts_per_user = [
            post_counts[i] / user_counts[i] if user_counts[i] > 0 else 0
            for i in range(4)
        ]

        # Calculate bias multiplier (compared to Q1 baseline)
        if posts_per_user[0] > 0:
            bias_multipliers = [rate / posts_per_user[0] for rate in posts_per_user]
        else:
            bias_multipliers = [1, 1, 1, 1]

        # Create bar chart showing posts per user
        x = np.arange(4)
        colors = ["#ff9999", "#ffcc99", "#99ccff", "#99ff99"]  # Red to green gradient

        bars = plt.bar(x, posts_per_user, color=colors, alpha=0.8, edgecolor="black")

        plt.xlabel("ELO Range Quartiles")
        plt.ylabel("Posts per User")
        plt.title("Posts per User by ELO Range Quartile\n(Shows Throttling Bias)")
        plt.xticks(
            x,
            [
                f"Q1\n≤{q1:.0f}\n({user_counts[0]} users)",
                f"Q2\n{q1:.0f}-{q2:.0f}\n({user_counts[1]} users)",
                f"Q3\n{q2:.0f}-{q3:.0f}\n({user_counts[2]} users)",
                f"Q4\n>{q3:.0f}\n({user_counts[3]} users)",
            ],
        )

        # Add value labels on bars showing both rate and multiplier
        for i, (bar, rate, mult) in enumerate(
            zip(bars, posts_per_user, bias_multipliers)
        ):
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.02,
                f"{rate:.2f}\n({mult:.1f}x)",
                ha="center",
                va="bottom",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
            )

        plt.grid(True, alpha=0.3)
        plt.ylim(0, max(posts_per_user) * 1.3)
    else:
        plt.text(
            0.5,
            0.5,
            "No posts available",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
        )

    # Subplot 7: Voting Participation Ratio Over Time (by user group)
    plt.subplot(2, 4, 7)

    # Use a moving window to smooth the data
    window_size = min(50, len(cumulative_votes_list))
    if window_size > 0:
        # Process with a moving average
        stage1_ratio = []
        stage2_ratio = []

        for i in range(len(cumulative_votes_list) - window_size + 1):
            # Average group sizes over the window
            window_stage1_pop = (
                sum(stage1_population_sizes[i : i + window_size]) / window_size
            )
            window_stage2_pop = (
                sum(stage2_population_sizes[i : i + window_size]) / window_size
            )

            # Sum of participants in this window
            window_stage1_votes = sum(stage1_participants_count[i : i + window_size])
            window_stage2_votes = sum(stage2_participants_count[i : i + window_size])

            # Calculate the vote frequency: votes per user in each group
            # This accounts for population growth by normalizing by the population size
            if window_stage1_pop > 0:
                stage1_ratio.append(
                    (window_stage1_votes / window_stage1_pop) * 100 / window_size
                )
            else:
                stage1_ratio.append(0)

            if window_stage2_pop > 0:
                stage2_ratio.append(
                    (window_stage2_votes / window_stage2_pop) * 100 / window_size
                )
            else:
                stage2_ratio.append(0)

        # Plot the ratios
        x_range = range(len(stage1_ratio))
        stage2_split = 100 - stage1_split
        plt.plot(
            x_range, stage1_ratio, "b-", label=f"Stage 1 Users (Bottom {stage1_split}%)"
        )
        plt.plot(
            x_range, stage2_ratio, "r-", label=f"Stage 2 Users (Top {stage2_split}%)"
        )

    plt.xlabel("Stage Index")
    plt.ylabel("Vote Frequency (% of users voting per round)")
    plt.title("Voting Frequency by User Group")
    plt.legend()

    # Subplot 8: ELO Throttling Function
    plt.subplot(2, 4, 8)

    if users:
        # Get ELO range from actual users
        user_elos = [user.elo for user in users]
        min_elo = min(user_elos)
        max_elo = max(user_elos)

        # Create a smooth ELO range for plotting the curve
        elo_range = np.linspace(min_elo - 50, max_elo + 50, 200)

        # Calculate the throttling weights using the same logic as select_posting_users
        mid_elo = (min_elo + max_elo) / 2
        weights = []
        for elo in elo_range:
            # Normalize ELO to be centered around 0 relative to the midpoint
            normalized_elo = (elo - mid_elo) / elo_posting_scale

            # Apply sigmoid function: 1 / (1 + e^(-x))
            sigmoid_weight = 1 / (1 + math.exp(-normalized_elo * 10))

            # Use sigmoid weight directly
            weight = sigmoid_weight
            weights.append(weight)

        # Normalize to show relative probability (0-1 scale)
        max_weight = max(weights)
        normalized_weights = [w / max_weight for w in weights]

        # Plot the sigmoid curve
        plt.plot(
            elo_range,
            normalized_weights,
            "b-",
            linewidth=3,
            label=f"Scale={elo_posting_scale}",
        )

        # Add vertical lines showing ELO range quartiles (not population percentiles)
        elo_range_span = max_elo - min_elo
        q1 = min_elo + elo_range_span * 0.25
        q2 = min_elo + elo_range_span * 0.50
        q3 = min_elo + elo_range_span * 0.75

        elo_quartiles = [q1, q2, q3]
        colors = ["red", "orange", "green"]
        labels = ["Q1 (25%)", "Q2 (50%)", "Q3 (75%)"]

        for i, (q, color, label) in enumerate(zip(elo_quartiles, colors, labels)):
            # Find the corresponding weight for this quartile ELO using the sigmoid function
            normalized_q = (q - mid_elo) / elo_posting_scale
            sigmoid_q_weight = 1 / (1 + math.exp(-normalized_q * 10))
            q_weight = sigmoid_q_weight / max_weight

            plt.axvline(
                x=q, color=color, linestyle="--", alpha=0.7, label=f"{label}: {q:.0f}"
            )
            # Add a point showing the weight at this ELO
            plt.plot(q, q_weight, "o", color=color, markersize=8, alpha=0.8)

        # Add annotations showing the effect
        plt.text(
            0.02,
            0.98,
            f"Throttling Scale: {elo_posting_scale}",
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
        )

        plt.text(
            0.02,
            0.85,
            f"Lower scale = More extreme throttling",
            transform=plt.gca().transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
        )

        plt.xlabel("User ELO Rating")
        plt.ylabel("Relative Posting Probability")
        plt.title("ELO-Based Posting Throttling\n(Sigmoid Function)")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8, loc="center right")
        plt.xlim(min_elo - 30, max_elo + 30)
        plt.ylim(0, 1.1)
    else:
        plt.text(
            0.5,
            0.5,
            "No users available",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
        )

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
        default=0.10,
        help="Population growth rate (default: 0.10)",
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
