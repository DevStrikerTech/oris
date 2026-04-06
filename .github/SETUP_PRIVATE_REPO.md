# Private GitHub repository: `oris`

The project is **not** public at this stage. Create the remote as **private**.

## Create the repository

1. GitHub → **New repository**
2. **Repository name:** `oris`
3. Visibility: **Private**
4. Do **not** add README, `.gitignore`, or license (this repo already has them)

## Add remote and push

Replace `YOUR_ORG` with your user or organization:

```bash
git remote add origin git@github.com:YOUR_ORG/oris.git
git push -u origin prod
git push -u origin dev
```

Set the **default branch** on GitHub to **`dev`** (Settings → General → Default branch) so new PRs and clones align with the integration workflow.

## Branch protection (required)

Configure in **Settings → Branches → Add rule**.

### `prod`

- Require a pull request before merging
- Require status checks to pass (select the **CI** workflow / `quality` job)
- Require branches to be up to date before merging
- **Do not** allow force pushes
- Restrict who can push (optional: admins only)

### `dev`

- Require a pull request before merging
- Require status checks to pass (CI)
- **Do not** allow direct pushes from contributors (use rulesets or team settings as appropriate)

### Enforcing `feat/*` only for PRs

Use **Rulesets** (or branch name patterns) so contributors cannot push to `dev`/`prod` without a PR. Feature work must use `feat/<feature-name>` (or `fix/<name>`) branched from `dev`.

## GitHub Pages (documentation site)

The **Deploy documentation** workflow (`.github/workflows/pages.yml`) publishes [MkDocs](https://www.mkdocs.org/) output when **`prod`** is updated.

1. **Settings → Pages**
2. **Build and deployment → Source:** **GitHub Actions**
3. After the first successful run, the site is at **`https://<user>.github.io/oris/`** (e.g. `devstrikertech.github.io/oris`).

**Visibility:** On **GitHub Free**, Pages for a **private** repository may be unavailable or restricted; use a **public** repo or a **Pro/Team/Enterprise** plan for private Pages. See [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## Secrets

Do not store API keys in the repository. Use GitHub **Secrets** only when CI/CD needs authenticated steps later.
