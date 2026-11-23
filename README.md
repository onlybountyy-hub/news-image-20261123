[![competition](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/onlybountyy-hub/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/onlybountyy-hub/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# THE WORLD TODAY — Monday 23 November 2026

One image summing up 23 November 2026's world news, for the
[news-image-20261123](https://make.fun/bounty/news-image-20261123) bounty on
[make.fun](https://make.fun/r/q6ckzx1w).

Hero: COP31 collapses in Antalya — the longest climate summit in history
ends with no deal on fossil fuels. Plus 11 more stories from every region:
the Russian warship sunk at Benghazi, tankers hit by mines in the Strait of
Hormuz, the Dymer drone strike, the Khartoum UN strike, the Banten factory
fire, Seoul's minister resigning, Shuri Castle reopening, the Nepal–India
summit, Liverpool's rout of Manchester United, India's record 720/9d, and
the Lisbon cost-of-living march.

Every story is verified against wire reporting; see SOURCES.md.

## How it is built

`poster.py` draws `entry.png` (1024×1024, deterministic — two runs are
byte-identical) with PIL. `main.py` (Python 3.13, standard library only)
copies `entry.png` to `MAKEFUN_OUTPUT_DIR/entry.png` and refuses if it ever
exceeds the 1 MiB gate cap.
