# Veridonia

## A Whitepaper on Transparent and Scalable Community-Driven Information Curation

### Abstract

Veridonia introduces a novel approach to online content curation, addressing the limitations of conventional, engagement-driven systems that have fuelled sensationalism, misinformation, and the creation of echo chambers. ([1](https://doi.org/10.1016/j.tics.2021.02.007), [2](https://doi.org/10.1126/science.aao2998), [3](https://doi.org/10.1073/pnas.2023301118)) This whitepaper outlines the challenges posed by today's digital information ecosystem and details the design, architecture, and operational principles of Veridonia. Central to our approach is a framework grounded in five key principles—including transparent governance, merit-based reputation, and randomized peer review—that together foster community-driven, trustworthy content curation.

### 1. Introduction

The digital landscape today is dominated by engagement metrics such as views, likes, and shares, which serve as the primary indicators of content performance. This focus on the attention economy has led to the widespread prioritisation of sensationalist content over substantive information, contributing to the rapid spread of misinformation, the formation of ideological echo chambers, and a general decline in content quality. ([1](https://doi.org/10.1016/j.tics.2021.02.007), [2](https://doi.org/10.1126/science.aao2998), [3](https://doi.org/10.1073/pnas.2023301118)) Furthermore, opaque algorithms that dictate content visibility and maximise engagement at any cost have amplified mistrust and decreased accountability ([4](https://doi.org/10.1177/1461444816676645)).

The current paradigm of social media platforms is increasingly misaligned with the broader interests of society. Rather than facilitating meaningful information exchange, these systems have evolved into attention-capture mechanisms engineered to maximise screen time. Their algorithms prioritise engagement through psychological manipulation, often at the expense of informative or socially valuable content. As a result, content with the highest emotional appeal—not necessarily the highest quality—achieves the greatest visibility, while important discourse is frequently relegated to the margins.

Veridonia is conceived as a response to these challenges. By re-engineering the content curation process, Veridonia aims to restore public trust in online content and empower communities to determine quality based on transparent, verifiable standards rather than commercial or algorithmic bias.

### 2. Problem Statement

The prevailing model for information sharing suffers from several critical flaws:

1. **Sensationalist Content Over Substantive Information:** Content is often designed to attract clicks and emotional responses rather than provide well-researched, balanced perspectives ([2](https://doi.org/10.1126/science.aao2998)).
2. **Misinformation Propagation:** The race for engagement results in the rapid spread of false or misleading information ([1](https://doi.org/10.1016/j.tics.2021.02.007)).
3. **Filter Bubbles and Echo Chambers:** Personalised algorithms confine users to ideologically homogenous groups, diminishing exposure to diverse viewpoints ([2](https://doi.org/10.1126/science.aao2998)).
4. **Opaque Decision-Making:** Hidden algorithmic processes limit transparency and accountability, fostering widespread mistrust ([4](https://doi.org/10.1177/1461444816676645)).
5. **Negative Societal Impacts:** The relentless pursuit of engagement contributes significantly to mental health issues and decreased productivity ([5](https://doi.org/10.1080/02673843.2019.1590851)).

### 3. Veridonia's Proposed Solution

Veridonia introduces a novel, community-driven approach to online content curation based on five foundational pillars:

**1. Sortition (Randomized Participant Selection)**  
Participants evaluating content are randomly selected, ensuring fairness, diversity, and resistance to manipulation.

**2. Consensus (Majority-Based Decision-Making)**  
Content decisions rely on majority voting at multiple stages, fostering community alignment and collective agreement.

**3. ELO-Based Reputation System**  
A dynamic reputation system based on ELO ratings rewards accurate decision-making, ensuring meritocracy and thoughtful engagement.

**4. Multi-Stage Voting Process**  
A structured, tiered voting mechanism balances efficiency with quality, using progressively qualified groups of community members to evaluate content.

**5. Transparency and Auditability**  
All moderation actions, votes, and reputation adjustments are publicly recorded, ensuring full transparency and enabling independent verification. This openness safeguards the integrity of the community governance model.

This combined framework seeks to address flaws in engagement-driven platforms, aiming to restore trust and prioritize content integrity.

### 4. System Architecture

The following components detail the implementation of Veridonia’s five foundational pillars.

#### 4.1 User Onboarding and Baseline Attributes

- **IP-Based ELO Inheritance:** To protect the platform from bot attacks and coordinated manipulation, all new users inherit the ELO rating assigned to their IP address. After each voting stage, an IP address is updated to reflect the lowest ELO among its associated users. For example, if users from an IP (e.g., 156.156.156.3) have ELO ratings of 850, 700, and 1500, the IP is assigned an ELO of 700. Any new users registering from this IP will begin with an ELO of 700, capped at a default maximum (e.g., 800) for first-time IPs.
- **Initial Assignment:** If the IP address has no previous users, a default ELO rating (e.g., 800) is used.
- **Reputation Development:** Users' influence in content curation evolves over time, reflecting the accuracy and consistency of their judgements.

#### 4.2 Post Submission

When a post is submitted, a random subset of relevant community members is selected to review the content. This randomness is essential to ensure that decisions reflect genuine community consensus rather than the influence of targeted manipulation.

#### 4.3 Multi-Stage Voting Process

Veridonia employs a dynamic, two-stage voting mechanism designed for accuracy, transparency, and scalability. The system operates similarly to a series of community referendums, where a small, carefully selected group of voters represents the broader community's likely preferences. This approach allows us to efficiently determine whether content should be published without requiring every community member to vote on every piece of content, whilst maintaining the integrity and accuracy of the decision-making process.

The effectiveness of sortition depends heavily on community size. In larger communities, a broad participant pool makes random selection fairer and more resistant to manipulation. Smaller communities, by contrast, have fewer participants, which can make them more vulnerable to coordinated attacks—though in practice many niche groups remain relatively safe due to their focused interests and close-knit nature. The greater concern lies with very large, influential communities, such as those centred on politics, where attempts at coordinated domination are more likely. Here, Veridonia’s design scales effectively: the larger the pool of participants, the stronger the randomness, making coordinated manipulation significantly harder.

- **Stage 1: Initial Filtering**

  - Participants: A random sample selected from users in the lower 70% ELO tier of all community members.
  - Decision Criterion: Participants assess content quality and community alignment.
  - Outcome:
    - If the majority of participants approve the content, the content advances to Stage 2 for final evaluation.
    - If the majority reject the content, the content is immediately rejected without proceeding to Stage 2.

- **Stage 2: Final Decision (Conditional)**

  - Participants: A random sample from the top 30% ELO tier of all community members.
  - Decision Criterion: A simple majority finalises the content decision.
  - Outcome: The content is either approved ("publish") or rejected ("do not publish") based on the majority decision.

- **Special Conditions:**

  - For populations with fewer than 20 community members, a simplified single-stage voting process is employed, with participants selected randomly from all available users.

Reputation adjustments are applied independently after each stage. This means participants in Stage 1 see their reputations updated based on that round’s outcome, and participants in Stage 2 receive a separate update based on the final decision.

#### 4.4 ELO-Based Reputation System

As one of Veridonia's five foundational pillars, the ELO-based reputation system plays a key role in supporting its meritocratic model:

- **Dynamic Influence:** Users' ELO ratings not only reflect their decision-making accuracy but also serve as a gateway to enhanced moderation privileges. As users consistently align with community standards and see their ratings increase, they become eligible for promotion from the initial tier to higher groups—Stage 2 or Stage 3 group. These promotions grant them greater influence over content curation and the overall quality of the platform.
- **Zero-Sum ELO Adjustments:** Post-evaluation, votes are compared against the post's assessed quality. Points are reallocated—users in the majority gain influence, whilst those in the minority see a corresponding decrease.
- **Team-Based Reputation Adjustments:** When users vote on a piece of content, they form two groups: those whose votes match the final outcome ("winners") and those whose votes oppose it ("losers"). To adjust reputation ratings (ELO):

  1. The average ELO rating for each group (winners and losers) is calculated separately.
  2. Each user's new ELO is updated based on how their group's average compares to the opposing group's average, scaled by a predefined constant (K-factor).
  3. Winners gain ELO, moving their ratings upward towards the opposing group's average rating, whilst losers lose ELO, moving downward towards the winners' average.
  4. This method promotes accuracy and fairness by rewarding collective correct judgements and gradually increasing the decision-making influence of consistently accurate users.

**Community-Specific Reputation**  
Reputation is maintained separately within each community, meaning that a user's performance and standing in one community do not carry over into another. This design prevents the emergence of “universal elites” who dominate multiple communities and ensures that influence is contextual, reflecting expertise and alignment within each distinct group. As a result, reputation—and therefore influence—is always earned locally within each community, never transferred globally across the platform.

#### 4.5 ELO-Based Throttling Mechanism

Veridonia implements a sophisticated throttling system that regulates users' ability to post and comment based on their ELO ratings:

- **Rate Limiting:** Users with lower ELO ratings face greater restrictions on how frequently they can post content or comment. This throttling mechanism scales dynamically with ELO scores, and users with particularly low reputation may be limited to posting only once per hour, per day, or even per week, depending on the severity of their low ELO.
- **Cooldown Periods:** After posting or commenting, users experience a mandatory cooldown period before they can contribute again. The duration of this cooldown is inversely proportional to their ELO rating.
- **Progressive Relaxation:** As users demonstrate consistent quality contributions and their ELO increases, throttling restrictions are gradually relaxed, allowing for more frequent participation.

The throttling mechanism serves several critical functions:

1. **Quality Control:** By limiting the volume of content from users with lower reputation scores, the system naturally elevates the average quality of visible content.
2. **Spam Prevention:** Rate limiting creates an effective barrier against automated spam and coordinated manipulation attempts.
3. **Incentivizing Quality:** The direct relationship between contribution privileges and ELO motivates users to focus on thoughtful, community-aligned contributions rather than quantity.
4. **Self-Regulation:** The system creates a natural self-regulatory environment where users who consistently provide low-quality content have diminished impact on the community.
5. **Resource Management:** Throttling helps manage computational resources by preventing system overload from excessive low-quality submissions.

This mechanism reinforces Veridonia's core principle that influence within the community should be earned through demonstrated alignment with community standards and quality contribution.

### 5. Transparency and Self-Governance

Veridonia is designed to be an open and self-regulating ecosystem:

- **Public Auditability:** All voting records, ELO adjustments, and moderation actions are logged and accessible for independent review, emulating blockchain-like transparency. These community standards are shaped through historical voting patterns and collective moderation, and they evolve over time.
- **Decentralised Moderation:** Governance is vested in the community, with every member (including guests) empowered to contribute, vote, and shape content standards. Moderation rights are held by approximately the top 10% of users in a community by reputation, who are able to soft-delete posts to uphold standards. Every moderation action is publicly logged, ensuring accountability, and any such action can be appealed by the broader community through a randomized jury voting process.

**Privacy by Design and Data Control:**  
Veridonia does not require sign-up to participate and does not track users across the web. The system only uses minimal signals necessary for fairness—for example, new accounts inherit the lowest reputation from their IP to discourage bot farms. Beyond this, reputation is tied entirely to actions within the platform: voting, posting, and how those decisions align with the community.

At the same time, users retain full control of their data. All activity histories can be accessed and verified without compromising security, reinforcing both transparency and individual privacy.

### 6. Additional Core Principles

- **Independence from Advertiser Influence:** Veridonia is free from advertiser funding, ensuring that content curation remains unbiased and dictated solely by community standards. The platform will never employ advertising as a monetisation strategy. Instead, future revenue models may involve subscriptions or donations, but public benefit content—such as community feeds—will always remain free to access. Only private benefit features may be offered as paid options, balancing sustainability with Veridonia’s commitment to open access and public good.

- **Integrity in Information Sharing:** By prioritising transparency and quality, Veridonia mitigates the risks of misinformation and preserves the integrity of the information ecosystem.
- **User Empowerment:** The platform is structured to empower users, granting them direct oversight of the content curation process without the interference of centralised authorities.

### 7. Conclusion

Veridonia offers an alternative approach to online information sharing—one that emphasizes transparency, community participation, and accountability over engagement-driven metrics. Its multi-stage voting process and ELO-based reputation system are intended to elevate quality content and reduce the spread of misinformation and sensationalism.

While no system can entirely eliminate bias or error, Veridonia provides a framework that encourages more thoughtful and community-aligned curation. By enabling users to actively participate in content governance, it aims to contribute to a more informed and balanced digital ecosystem.

### References

1. Pennycook, G., & Rand, D. G. (2021). "The Psychology of Fake News." _Trends in Cognitive Sciences_, 25(5), 388–402. [https://doi.org/10.1016/j.tics.2021.02.007](https://doi.org/10.1016/j.tics.2021.02.007)

2. Lazer, D. M. J., Baum, M. A., Benkler, Y., Berinsky, A. J., Greenhill, K. M., Menczer, F., & Zittrain, J. L. (2018). "The Science of Fake News." _Science_, 359(6380), 1094–1096. [https://doi.org/10.1126/science.aao2998](https://doi.org/10.1126/science.aao2998)

3. Cinelli, M., Morales, G. D. F., Galeazzi, A., Quattrociocchi, W., & Starnini, M. (2021). "The Echo Chamber Effect on Social Media." _Proceedings of the National Academy of Sciences_, 118(9). [https://doi.org/10.1073/pnas.2023301118](https://doi.org/10.1073/pnas.2023301118)

4. Ananny, M., & Crawford, K. (2018). "Seeing without Knowing: Limitations of the Transparency Ideal and Its Application to Algorithmic Accountability." _New Media & Society_, 20(3), 973–989. [https://doi.org/10.1177/1461444816676645](https://doi.org/10.1177/1461444816676645)

5. Keles, B., McCrae, N., & Grealish, A. (2020). "A Systematic Review: The Influence of Social Media on Depression, Anxiety, and Psychological Distress in Adolescents." _International Journal of Adolescence and Youth_, 25(1), 79–93. [https://doi.org/10.1080/02673843.2019.1590851](https://doi.org/10.1080/02673843.2019.1590851)
