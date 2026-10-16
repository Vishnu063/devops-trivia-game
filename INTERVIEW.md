# DevOps trivia prototype: reviewer guide

A Flask/SQLite quiz API with a static frontend and Docker configuration.

## Start the review

Trace registration, login, question retrieval, and answer scoring. Review the hardcoded signing secret, eval-based option parsing, and repeat-answer scoring before public deployment.

| Source | Review focus |\n| --- | --- |\n| [Dockerfile](Dockerfile) | Build context, runtime configuration, ports, and persistence |\n| [app.py](app.py) | Implementation, assumptions, and operational boundaries |\n| [docker-compose.yml](docker-compose.yml) | Build context, runtime configuration, ports, and persistence |\n| [index.html](index.html) | Implementation, assumptions, and operational boundaries |\n| [requirements.txt](requirements.txt) | Implementation, assumptions, and operational boundaries |\n| [run.sh](run.sh) | Implementation, assumptions, and operational boundaries |

## A useful interview walkthrough

1. State the problem and the specific part you implemented or changed.
2. Open the source above and follow one request, release, or failure from start to finish.
3. Show a reproducible result, including an actual failure and the observation that confirms recovery.
4. Explain one tradeoff and one limitation. Distinguish a local test from a live deployment.

## Evidence and limits

This guide is based on the default-branch source inspected on 16 October 2026. It is a source review, not a fresh deployment or a certification of every feature. Existing CI runs and tests should be checked at the commit being demonstrated. Do not present screenshots, inherited code, planned features, or old README statements as proof of a current deployment.
