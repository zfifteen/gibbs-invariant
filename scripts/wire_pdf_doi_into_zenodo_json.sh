#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <pdf_doi>" >&2
  echo "Example: $0 10.5281/zenodo.12345678" >&2
  exit 1
fi

PDF_DOI="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZENODO_JSON="$ROOT_DIR/.zenodo.json"

if [[ ! -f "$ZENODO_JSON" ]]; then
  echo "Error: $ZENODO_JSON not found" >&2
  exit 1
fi

TMP_FILE="$(mktemp)"

jq --arg doi "$PDF_DOI" '
  .related_identifiers = (.related_identifiers // []) |
  if any(.related_identifiers[]?; .identifier == ("https://doi.org/" + $doi) or .identifier == $doi) then
    .
  else
    .related_identifiers += [{
      "identifier": ("https://doi.org/" + $doi),
      "relation": "isDocumentedBy",
      "resource_type": "publication-technicalnote"
    }]
  end
' "$ZENODO_JSON" > "$TMP_FILE"

mv "$TMP_FILE" "$ZENODO_JSON"
echo "Updated .zenodo.json with PDF DOI relation: $PDF_DOI"
