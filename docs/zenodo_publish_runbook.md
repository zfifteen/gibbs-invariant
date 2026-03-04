# Zenodo Publish Runbook (PDF-First)

This runbook assumes:

- `docs/technical_note.pdf` is final.
- Zenodo production is used (`https://zenodo.org`).
- DOI is reserved before publish.

## 1) Publish primary PDF record in Zenodo UI

1. Open Zenodo -> `New upload`.
2. Upload `docs/technical_note.pdf`.
3. Set upload type to `Publication`.
4. Set subtype to `Technical note` (or closest available).
5. Fill metadata from [`docs/zenodo_pdf_publication_metadata.md`](./zenodo_pdf_publication_metadata.md).
6. Add related identifier:
   - identifier: `https://github.com/zfifteen/gibbs-invariant`
   - relation: `isSupplementTo`
   - resource type: `Software`
7. Click `Reserve DOI`.
8. Publish and record:
   - `PDF_VERSION_DOI`
   - `PDF_CONCEPT_DOI` (if shown)

## 2) Wire PDF DOI into software metadata

Run:

```bash
cd /Users/velocityworks/IdeaProjects/gibbs-invariant
./scripts/wire_pdf_doi_into_zenodo_json.sh <PDF_VERSION_DOI>
```

Verify:

```bash
jq '.related_identifiers' .zenodo.json
```

## 3) Create software GitHub release (`v0.1.0`)

```bash
cd /Users/velocityworks/IdeaProjects/gibbs-invariant
git add .zenodo.json README.md docs/release_verification_v0.1.0.md docs/zenodo_pdf_publication_metadata.md docs/zenodo_publish_runbook.md scripts/wire_pdf_doi_into_zenodo_json.sh
git commit -m "chore: wire Zenodo PDF-first publication workflow"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes "First archival software release for Gibbs invariant results."
```

## 4) Publish software record in Zenodo

1. Wait for Zenodo GitHub integration to ingest `v0.1.0`.
2. Open software draft in Zenodo.
3. Confirm `related_identifiers` includes `isDocumentedBy` to `https://doi.org/<PDF_VERSION_DOI>`.
4. Publish software record and capture:
   - `SW_VERSION_DOI`
   - `SW_CONCEPT_DOI`

## 5) Back-link software DOI in PDF record

1. Edit PDF record metadata (or create metadata-only update if Zenodo requires a new version).
2. Add related identifier:
   - identifier: `https://doi.org/<SW_VERSION_DOI>`
   - relation: `isSupplementedBy` (or closest available relation)
   - resource type: `software`
3. Save/publish update.

## 6) Final docs update in repo

Update:

- [`README.md`](../README.md) DOI placeholders
- [`docs/release_verification_v0.1.0.md`](./release_verification_v0.1.0.md) DOI fields/checklist

