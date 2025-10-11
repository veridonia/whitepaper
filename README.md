![Veridonia Logo](assets/logo-veridonia.svg)

**Transparent and Scalable Community-Driven Information Curation**

---

## What is Veridonia?

Veridonia is an experiment in content curation that replaces engagement metrics with community-driven multi-stage voting. Instead of optimizing for clicks and shares, it uses randomized selection and an ELO rating system where influence is earned through demonstrated judgment.

The system rests on five principles: sortition (random selection), consensus (majority voting), ELO-based rating, multi-stage review, and full transparency of all votes and rating changes.

---

## The Whitepaper

For the complete design, read the whitepaper included in this repository:

**→ [Veridonia Whitepaper](Whitepaper.pdf)**

The whitepaper covers the problem analysis, system architecture, voting mechanisms, ELO calculations, IP-based inheritance, throttling, moderation, and the empirical questions we'd need to answer in real deployment.

---

## The Simulation

This repository contains a Python implementation of Veridonia's core mechanics. It's simplified—no IP inheritance, no communities, no real user behavior—but it captures the essential question: does multi-stage voting with ELO-based selection improve content quality over time?

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

Shows the distribution of innate ability to judge content quality. Users above 0.5 tend to vote correctly; users below 0.5 don't. In a well-functioning system, users above 0.5 users should accumulate higher ELO over time.

**Distribution of Users by ELO Rating**

Shows how ELO spreads across the population and where the voting tiers fall. Stage 1 voters are the bottom 70% by user count (blue). Stage 2 voters are the top 30% (orange). The dashed line marks the top 1%, who would have moderation privileges in a real system.

**Correct Votes Ratio Over Time**

Tracks what fraction of voters aligned with actual content quality at each iteration. The regression line shows the trend. An upward slope means the system is getting better at selecting accurate voters.

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
