# KOMPOSOS Streamlit Portfolio Deploy

## What This Is

`streamlit_app.py` is a free-hostable personal portfolio site for James Hawkins
and the main KOMPOSOS repos.

The app is designed as a proof-of-work doorway, not a complete technical
archive. It highlights the systems, gives each one an honest caveat, and helps
visitors connect with a concrete question.

## Local Run

From this repo:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app uses:

```text
streamlit_app.py
requirements.txt
.streamlit/config.toml
assets/komposos-system-map.png
```

## Free Deploy Path

Use Streamlit Community Cloud:

1. Push this repo to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Set the main file path to `streamlit_app.py`.
5. Deploy.
6. Share the resulting `streamlit.app` URL from LinkedIn, GitHub, and direct
   outreach emails.

Official Streamlit deployment docs:

<https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app>

## Editing Project Cards

Project data lives in the `PROJECTS` list at the top of
`streamlit_app.py`.

Each card has:

- `name`
- `short`
- `domain`
- `stage`
- `audiences`
- `summary`
- `use`
- `proof`
- `ask`
- `caveat`
- optional `repo`
- optional `demo`
- `local`

For public use, prefer direct demo and GitHub links. Keep local paths as
proof-of-work notes for your own orientation, but do not rely on local paths for
public visitors.

## Positioning Rule

The site should say:

> I build fast research systems that organize complex evidence into explainable
> next actions.

It should not say:

> The system proves everything, replaces domain experts, or guarantees outcomes.

The best audience is someone who has a hard domain problem and wants a builder
who can rapidly turn the problem into a working research tool, prototype, audit,
or evidence map.

## Good First Improvements

1. Add screenshots for PHARM, CHEM, and WESyS.
2. Replace any local-only repo cards with public GitHub links as they become
   available.
3. Add one short demo video or GIF for the strongest chemistry example.
4. Add a small "work with me" paragraph with the exact kind of paid or
   collaborative work wanted.
5. Add a simple custom domain later if the site starts getting useful replies.

