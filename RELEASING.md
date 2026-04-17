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
- Generate/update `CHANGELOG.rst`, `CHANGELOG.md`, and `changelogs/changelog.yaml`
- Delete the processed fragment files (since `keep_fragments: false`)

## Step 4: Commit and push to `main`

Commit all the changes (bumped `galaxy.yml`, updated changelog outputs,
updated `changelogs/changelog.yaml`, deleted fragments) and merge to
`main` via a PR.

## Step 5: Create a GitHub Release

On the repository's GitHub Releases page, create a new release:

- **Tag:** Use the version number (e.g., `v1.1.0` or `1.1.0`)
- **Target:** `main`
- **Title:** e.g., `branic.system_management 1.1.0`
- **Description:** Use the notes for this version from `CHANGELOG.md` (or `CHANGELOG.rst`). You can **paste** that section into the release body so subscribers see full text in the release UI and emails, or **link** to the file at the tag you are creating, for example `https://github.com/branic/system_management/blob/v1.1.0/CHANGELOG.md` (use your real tag and version). You can also do both: a short summary plus a link to the full changelog.
- **Publish** the release (do not leave it as a draft)

## Step 6: Verify

Publishing the release triggers the `release.yml` workflow, which
publishes the collection to Ansible Galaxy. Check the Actions tab on
GitHub to confirm the workflow succeeded.

## Prerequisites

- Configure a GitHub Environment named **`release`**. The `release.yml` workflow
  assigns that environment to the Galaxy publish job so **deployment protection
  rules apply** and **environment secrets** (including the Galaxy API token) are
  available to the job.
- Add the **Ansible Galaxy API token** under **Settings → Environments →
  `release` → Environment secrets** using the name **`ANSIBLE_GALAXY_API_KEY`**
  (same name the workflow reads). Create or copy the token from Ansible Galaxy
  (profile / token management on [galaxy.ansible.com](https://galaxy.ansible.com)).
  GitHub treats secret names as **case-insensitive**; the UI may show the name in
  uppercase.
- Under **Settings → Environments → `release` → Deployment protection rules**,
  **Deployment branches and tags** must allow the Git tags used for releases.
  For semver tags like `v1.0.0`, add a tag pattern such as `v*.*.*` (or a
  narrower pattern you prefer). If only certain branches are allowed, the
  release workflow fails immediately with an environment protection error when
  a release is published from a tag.
- `antsibull-changelog` must be installed locally to compile fragments
  before release. CI only validates fragments; it does not auto-generate
  the changelog.
