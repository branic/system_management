# Creating a Release

## Step 1: Bump the version in `galaxy.yml`

The version field is in `galaxy.yml`. Update it to your target version
(e.g., `1.1.0` or `2.0.0`) following semantic versioning.

## Step 2: (Optional) Add a release summary fragment

Create a fragment in `changelogs/fragments/` with a `release_summary` key:

```yaml
---
release_summary: |
  Brief description of this release.
```

This appears as the top-level summary for the version in `CHANGELOG.rst`.

## Step 3: Run antsibull-changelog to compile the release notes

```bash
pip install antsibull-changelog   # if not already installed
antsibull-changelog release
```

This will:

- Read all fragments from `changelogs/fragments/`
- Generate/update `CHANGELOG.rst` and `changelogs/changelog.yaml`
- Delete the processed fragment files (since `keep_fragments: false`)

## Step 4: Commit and push to `main`

Commit all the changes (bumped `galaxy.yml`, updated `CHANGELOG.rst`,
updated `changelogs/changelog.yaml`, deleted fragments) and merge to
`main` via a PR.

## Step 5: Create a GitHub Release

On the repository's GitHub Releases page, create a new release:

- **Tag:** Use the version number (e.g., `v1.1.0` or `1.1.0`)
- **Target:** `main`
- **Title:** e.g., `branic.system_management 1.1.0`
- **Description:** Paste or reference the changelog entry
- **Publish** the release (do not leave it as a draft)

## Step 6: Verify

Publishing the release triggers the `release.yml` workflow, which
publishes the collection to Ansible Galaxy. Check the Actions tab on
GitHub to confirm the workflow succeeded.

## Prerequisites

- A GitHub Environment named `release` must be configured on the
  repository with the appropriate secrets (e.g., `ANSIBLE_GALAXY_API_KEY`).
- `antsibull-changelog` must be installed locally to compile fragments
  before release. CI only validates fragments; it does not auto-generate
  the changelog.
