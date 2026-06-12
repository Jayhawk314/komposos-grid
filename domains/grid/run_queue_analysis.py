# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run OPTIMUS factorization on the LBNL interconnection queue.

    python -m domains.grid.run_queue_analysis ^
        --queue domains\\grid\\data\\lbnl_ix_queue_data_file_thru2025.xlsx

The LBNL file (https://emp.lbl.gov/queues) sits behind a browser
challenge: download it manually and save it under domains/grid/data/.
Use --synthetic for a demo without the file.
"""

from __future__ import annotations

import argparse
import random
import sys

from domains.grid.queue_analysis import analyze_queue
from domains.grid.sources.lbnl_queue import (
    LBNLQueueSource,
    OPERATIONAL,
    QueueProject,
    WITHDRAWN,
)


def synthetic_projects(n: int = 2000, seed: int = 5):
    """Queue fixture with engineered cohort effects for the demo."""
    rng = random.Random(seed)
    fuels = {"gas": 0.45, "solar": 0.11, "wind": 0.16, "storage": 0.08}
    regions = ["pjm", "miso", "caiso", "ercot", "west"]
    projects = []
    for i in range(n):
        fuel = rng.choice(list(fuels))
        completes = rng.random() < fuels[fuel]
        projects.append(
            QueueProject(
                q_id=str(i),
                status=OPERATIONAL if completes else WITHDRAWN,
                q_year=rng.randint(2003, 2019),
                fuel=fuel,
                region=rng.choice(regions),
                state="TX",
                mw=rng.uniform(5, 800),
                ia_status="executed" if completes or rng.random() < 0.2 else "pending",
            )
        )
    return projects


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="OPTIMUS factorization of queue completion/withdrawal"
    )
    parser.add_argument("--queue", help="LBNL queue data workbook (.xlsx)")
    parser.add_argument("--min-cohort", type=int, default=30)
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)

    if args.synthetic:
        projects = synthetic_projects()
    elif args.queue:
        projects = LBNLQueueSource(args.queue).load()
    else:
        parser.error("provide --queue <xlsx> or --synthetic")

    report = analyze_queue(projects, min_cohort=args.min_cohort)
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
