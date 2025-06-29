# Veridonia Simulation

This repository contains a simulation of the Veridonia content curation system. The simulation implements a community-driven multi-stage voting process paired with an ELO-based reputation system. It is based on the principles outlined in the [Veridonia Whitepaper](Whitepaper.md) included in this repository. Some differences in implementation exist to better suit the simulation environment.

## Overview

Veridonia is designed to improve online content curation by promoting transparency, meritocracy, and community governance. Instead of relying on opaque, engagement-driven algorithms that fuel sensationalism and misinformation, Veridonia leverages a multi-stage voting mechanism and dynamic reputation adjustments to evaluate content quality.

In this simulation:

- **Users** are modeled with a configurable baseline ELO rating (default: 800) and a "goodness" factor, which influences their voting behavior.
- **Posts** have a quality score between 0 and 1, with each user creating a configurable number of posts (default: 2).
- A **multi-stage voting process** determines whether a post is supported or opposed, with users selected based on their ELO ratings.

- The simulation features a growing user population up to a configurable maximum (default: 5,000 users), mimicking a realistic social platform environment.
- **Simple majority voting** is used at all stages - posts need more support than opposition votes to advance or be published.

## Features

- **Configurable Parameters:** All major simulation parameters can be adjusted via command-line arguments.
- **User Modeling:** Each user has attributes including ELO, goodness, mood factor, and a vote count.
- **Voting Mechanism:** Users vote on posts based on a combination of their adjusted goodness (affected by mood) and the quality of the post.
- **Multi-Stage Voting:**
  - For populations with fewer than 20 users, a single stage of voting is performed.
  - For larger populations, a two-stage process is used:
    - **Stage 1:** A configurable number of users from the lower ELO tier (configurable split, default: bottom 70%) votes.
    - **Stage 2:** If Stage 1 has more support than opposition votes, a configurable number of users from the upper ELO tier (remaining percentage) votes to make the final decision.
  - All users participate in the voting process based on their ELO ranking, with no exclusions.
- **ELO Adjustments:** User ratings are updated based on vote outcomes using team-based ELO updates with configurable K-factor.
- **Visualization:** After simulation runs, various plots display:
  - Distribution of user goodness and ELO ratings
  - Correct votes ratio over time with linear regression analysis
  - Population growth over time
  - Sample sizes used in voting
  - Voting participation ratios by user group (with dynamic labels reflecting actual configuration)

## Dependencies

The simulation requires the following Python packages:

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [termcolor](https://pypi.org/project/termcolor/)
- [tqdm](https://tqdm.github.io/)
- [SciPy](https://www.scipy.org/) (for statistical functions)

You can install the required packages using pip:

```bash
pip install numpy matplotlib termcolor tqdm scipy
```

Or using the provided requirements file:

```bash
pip install -r requirements.txt
```

## Command Line Interface

The simulation supports extensive customization through command-line arguments:

### Population & Content Parameters

- `--max-population` (default: 5000) - Maximum population size
- `--posts-per-user` (default: 2) - Posts per user
- `--growth-rate` (default: 0.10) - Population growth rate

### Voting Stage Parameters

- `--stage1-users` (default: 5) - Number of users in stage 1 voting
- `--stage2-users` (default: 5) - Number of users in stage 2 voting
- `--stage1-split` (default: 70) - Percentage of users for stage 1 (remaining go to stage 2)

### ELO System Parameters

- `--elo-start` (default: 800) - Starting ELO rating for new users
- `--k-factor` (default: 32) - K-factor for ELO calculations

## How to Run the Simulation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/veridonia-simulation.git
   cd veridonia-simulation
   ```

2. **Run the Simulation with Default Parameters:**

   ```bash
   python simulation.py
   ```

3. **Run with Custom Parameters:**

   ```bash
   # Smaller, faster simulation
   python simulation.py --max-population 1000 --posts-per-user 1

   # Different stage split (50/50 instead of 70/30)
   python simulation.py --stage1-split 50

   # Custom ELO parameters
   python simulation.py --elo-start 1000 --k-factor 16

   # Different voting group sizes
   python simulation.py --stage1-users 3 --stage2-users 7

   # Combination of parameters
   python simulation.py --max-population 2000 --stage1-split 80 --stage1-users 7
   ```

4. **View All Available Options:**

   ```bash
   python simulation.py --help
   ```

## Voting System Details

The simulation uses a **simple majority voting system**:

- **Stage 1:** If more users support than oppose, the post advances to Stage 2
- **Stage 2:** If more users support than oppose, the post is published; otherwise rejected
- **Single Stage:** (when <20 users total) If more users support than oppose, the post is published

This simplified approach focuses on democratic decision-making while maintaining the two-tier review structure where higher-ELO users have the final say.

## Relationship to the Whitepaper

This simulation serves as a practical implementation of the theoretical framework described in the [Veridonia Whitepaper](Whitepaper.md). While the whitepaper provides the complete conceptual principles and governance model, this simulation focuses specifically on testing the effectiveness of the multi-stage voting and ELO-based reputation mechanisms.

The whitepaper covers additional topics not implemented in this simulation, including:

- Detailed discussion of problems with current content curation systems
- More comprehensive governance frameworks
- Data privacy considerations
- Long-term vision for transparent information ecosystems

For a deeper understanding of the Veridonia concept, please refer to the whitepaper.

## Acknowledgements

This simulation is a proof-of-concept implementation based on the principles outlined in the Veridonia whitepaper. It aims to explore the potential of community-driven content curation and transparent reputation systems.

---

Feel free to contribute, report issues, or suggest improvements by opening an issue or pull request in the repository.

Happy simulating!
