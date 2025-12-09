![Veridonia Logo](assets/logo-veridonia.svg)

**A More Trustworthy Online Feed**

---

## What is Veridonia?

Veridonia is an online feed that experiments with redesigning how feeds are shaped. Instead of engagement-based ranking, it lets communities decide what deserves visibility through a transparent review pipeline. Content is evaluated in randomly sampled, multi-stage votes; majority outcomes decide whether a post advances, and an ELO-based rating system adjusts each participant’s influence based on how reliably their past decisions align with community outcomes.

The core aim is to systematically route scarce attention toward high-signal contributions and away from low-value noise. The design rests on five pillars drawn from the whitepaper: sortition (random selection), consensus (majority voting), ELO-based rating, multi-stage review, and full transparency and auditability of votes, rating changes, and moderation actions, complemented by ELO-based throttling of low-rated accounts.

---

## The Whitepaper

For the complete design, read the whitepaper included in this repository:

**→ [Veridonia Whitepaper](Whitepaper.pdf)**

The whitepaper describes the problems with engagement-driven feeds, the system architecture, voting and rating mechanisms (including team-weighted ELO updates, IP-based inheritance, throttling, and moderation), and the empirical questions we need to answer in deployment—most importantly, whether Veridonia can measurably improve the signal-to-noise ratio of what surfaces in community feeds.

---

## The Simulation

This repository contains a Python implementation of Veridonia's core mechanics. It's simplified—no IP inheritance, no communities, no real user behavior—but it captures the essential question from the whitepaper: does multi-stage voting with ELO-based selection and throttling shift attention toward high-signal posts and suppress noise over time?

### Installation

```bash
pip install -r requirements.txt
```

### Usage

Run with defaults:

```bash
python simulation.py
```

Common variations:

```bash
# Faster, smaller simulation
python simulation.py --max-population 1000 --posts-per-user 1

# Change the stage split
python simulation.py --stage1-split 50  # 50/50 instead of 70/30

# More volatile ratings
python simulation.py --k-factor 64

# Stricter throttling
python simulation.py --elo-posting-scale 50
```

See all options:

```bash
python simulation.py --help
```

### Reading the output

The simulation produces four plots.

**Distribution of User Goodness**

Shows the distribution of innate ability to judge content quality. Users above 0.5 tend to vote correctly; users below 0.5 don't. In a well-functioning system, higher-skill users should accumulate higher ELO over time and take on a larger share of high-impact decisions, raising the effective signal-to-noise ratio of collective judgments.

**Distribution of Users by ELO Rating**

Shows how ELO spreads across the population and where the voting tiers fall. Stage 1 voters are the bottom 70% by user count (blue). Stage 2 voters are the top 30% (orange). The dashed line marks the top 1%, who would have moderation privileges in a real system.

**Correct Votes Ratio Over Time**

Tracks what fraction of voters aligned with actual content quality at each iteration. The regression line shows the trend; a sustained upward slope indicates that the system is getting better at routing decisions through reliable reviewers and is reducing noise relative to signal in the decision pipeline.

**Population Growth Over Time**

Shows growth rate over time. Useful for context when comparing different parameter configurations.

### Parameters

**Population and content:**

- `--max-population` (default: 5000)
- `--posts-per-user` (default: 2)
- `--growth-rate` (default: 0.05)

**Voting structure:**

- `--stage1-users` (default: 5)
- `--stage2-users` (default: 5)
- `--stage1-split` (default: 70)

**ELO dynamics:**

- `--elo-start` (default: 800)
- `--k-factor` (default: 32)
- `--elo-posting-scale` (default: 100)

---

## Contributing

Your contributions are WELCOME. If you find edge cases, propose better metrics, identify flaws in the rating mechanism, or want to test different configurations, open an issue or submit a pull request.

---

## License

Open source.
