#!/usr/bin/env bash
#
# Build a SeedSigner OS image running instrumented v0.8.7, for capturing the raw bytes
# that v0.8.7 feeds into its entropy hash.
#
# See README.md for what this produces and why each step is here. Every step below that
# looks arbitrary is working around something that silently breaks the build or, worse,
# produces an image that looks fine and isn't.
#
# Usage:
#   ./build-instrumented-image.sh --app /path/to/seedsigner --os /path/to/seedsigner-os [--board pi0]
#
# Requirements: docker (usable without sudo), git, ~6 GB free disk, network for the first build.

set -o errexit -o pipefail -o nounset

BOARD="pi0"
APP_REPO=""
OS_REPO=""
WORK=""
IMAGE_MB=256
# Both refs must be release tags traceable to the upstream project, NOT convenience
# branches. See "Baseline provenance" in README.md -- an earlier round of this measurement
# was invalidated because the OS layer was silently built from a fork branch while only the
# app layer was pinned to a release.
APP_TAG="0.8.7"
OS_REF="v0.8.7"
UPSTREAM_REMOTE="upstream"
ALLOW_UNPINNED=0
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: $0 --app <seedsigner checkout> --os <seedsigner-os checkout> [options]

  --app PATH      seedsigner app repo. Must have tag ${APP_TAG} and the
                  seedsigner-translations submodule checked out.
  --os PATH       seedsigner-os repo. Checked out at --os-ref.
  --app-tag REF   app release tag (default ${APP_TAG}).
  --os-ref REF    OS release tag (default ${OS_REF}). Must be traceable to upstream.
  --upstream-remote NAME   remote to verify provenance against (default ${UPSTREAM_REMOTE}).
  --allow-unpinned-baseline
                  Build from a ref not traceable to upstream. Records the deviation
                  in PROVENANCE.txt. Do not use for measurements that characterise a
                  released version.
  --board NAME    pi0 (default) or pi02w.
  --work PATH     Scratch build dir. Default: <os-repo>-instrumented-build
  --image-mb N    Boot partition size in MB (default ${IMAGE_MB}).
  -h, --help
EOF
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --app) APP_REPO="$2"; shift 2 ;;
    --os) OS_REPO="$2"; shift 2 ;;
    --board) BOARD="$2"; shift 2 ;;
    --work) WORK="$2"; shift 2 ;;
    --image-mb) IMAGE_MB="$2"; shift 2 ;;
    --app-tag) APP_TAG="$2"; shift 2 ;;
    --os-ref) OS_REF="$2"; shift 2 ;;
    --upstream-remote) UPSTREAM_REMOTE="$2"; shift 2 ;;
    --allow-unpinned-baseline) ALLOW_UNPINNED=1; shift ;;
    -h|--help) usage ;;
    *) echo "unknown arg: $1" >&2; usage ;;
  esac
done
[ -n "$APP_REPO" ] && [ -n "$OS_REPO" ] || usage
[ -d "$APP_REPO/.git" ] || { echo "ERROR: --app is not a git repo: $APP_REPO" >&2; exit 1; }
[ -d "$OS_REPO/.git" ] || { echo "ERROR: --os is not a git repo: $OS_REPO" >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "ERROR: docker not usable (needs to work without sudo)" >&2; exit 1; }
WORK="${WORK:-${OS_REPO}-instrumented-build}"

# --- 0. BASELINE PROVENANCE GATE ---------------------------------------------------------
# Every layer of the stack must be pinned to a ref that is traceable to the upstream
# project. Verifying only the layer you happen to be editing is how a measurement ends up
# characterising something no released device runs.
#
# This gate is deliberately hard to bypass: the override exists, but it stamps the fact
# into the provenance record that ships with the data, so a fork-based build can never be
# mistaken for a release-baseline one at analysis time.
provenance_check() {
  local repo="$1" ref="$2" label="$3"
  local sha upstream_ok=0 remote_url
  sha="$(git -C "$repo" rev-parse --verify "${ref}^{commit}" 2>/dev/null)" || {
    echo "ERROR: ${label}: ref '${ref}' does not exist in ${repo}" >&2; exit 1; }
  remote_url="$(git -C "$repo" remote get-url "$UPSTREAM_REMOTE" 2>/dev/null || echo "")"
  if [ -n "$remote_url" ]; then
    # Reachable from an upstream branch, or present as an upstream tag.
    if git -C "$repo" branch -r --contains "$sha" 2>/dev/null | grep -q "^\s*${UPSTREAM_REMOTE}/" \
       || git -C "$repo" ls-remote --tags "$UPSTREAM_REMOTE" 2>/dev/null | grep -q "$sha"; then
      upstream_ok=1
    fi
  fi
  PROV+=("${label}: ${ref} @ ${sha}")
  PROV+=("${label}_upstream_remote: ${remote_url:-<none configured>}")
  if [ "$upstream_ok" = "1" ]; then
    PROV+=("${label}_upstream_verified: YES")
    echo "==> ${label}: ${ref} (${sha:0:12}) -- upstream-verified"
  else
    PROV+=("${label}_upstream_verified: NO  *** NOT A RELEASE BASELINE ***")
    echo "!!! ${label}: ${ref} (${sha:0:12}) is NOT reachable from '${UPSTREAM_REMOTE}'" >&2
    if [ "$ALLOW_UNPINNED" != "1" ]; then
      cat >&2 <<EOF

REFUSING TO BUILD. '${ref}' in ${repo} cannot be traced to the upstream project via
remote '${UPSTREAM_REMOTE}'. A measurement built on it does not characterise any released
device, and that will not be visible in the resulting data.

Fix the ref, or if the deviation is intentional re-run with --allow-unpinned-baseline
(which records the deviation in PROVENANCE.txt alongside the image).
EOF
      exit 1
    fi
    echo "!!! continuing because --allow-unpinned-baseline was given" >&2
  fi
}

PROV=()
PROV+=("board: ${BOARD}")
provenance_check "$APP_REPO" "$APP_TAG" "app"
provenance_check "$OS_REPO" "$OS_REF" "os"
echo "==> board=${BOARD}  app=${APP_TAG}  os=${OS_REF}  work=${WORK}"

# --- 1. Fresh clone of seedsigner-os, so the caller's working tree is untouched -----------
if [ ! -d "$WORK/.git" ]; then
  echo "==> cloning seedsigner-os -> $WORK"
  git clone --quiet --recurse-submodules "$OS_REPO" "$WORK"
fi
git -C "$WORK" checkout --quiet --detach "$OS_REF"
git -C "$WORK" submodule update --quiet --init --recursive
echo "==> os checked out at ${OS_REF} ($(git -C "$WORK" rev-parse --short HEAD))"

# The board config must still carry picamera. If this fails you are on a branch that has
# migrated to libcamera, and v0.8.7's camera code cannot run on it at all.
grep -q "BR2_PACKAGE_PYTHON_PICAMERA=y" "$WORK/opt/${BOARD}/configs/${BOARD}_defconfig" \
  || { echo "ERROR: ${BOARD}_defconfig has no python-picamera. Wrong branch?" >&2; exit 1; }

# --- 2. Boot partition size --------------------------------------------------------------
# Stock is 50 MB, which leaves ~5 MB free after the OS. One capture run writes ~14 MB, so
# the run dies partway through with "no space left on device".
POSTIMG="$WORK/opt/${BOARD}/board/post-image-seedsigner.sh"
if grep -q "count=50 " "$POSTIMG"; then
  sed -i "s|^dd if=/dev/zero of=disk.img bs=1M count=50 .*$|dd if=/dev/zero of=disk.img bs=1M count=${IMAGE_MB}  # enlarged for capture data|" "$POSTIMG"
  echo "==> boot partition enlarged to ${IMAGE_MB} MB"
fi

# --- 3. Download cache mount -------------------------------------------------------------
# The defconfigs set BR2_DL_DIR="\$(TOPDIR)/../../buildroot_dl", which resolves to
# /buildroot_dl inside the container. docker-compose does not mount it, so without this
# every build redownloads ~1 GB of sources.
if ! grep -q "buildroot_dl:/buildroot_dl" "$WORK/docker-compose.yml"; then
  sed -i 's|\(\s*\)- ./.buildroot-ccache:/root/.buildroot-ccache|&\n\1- ./.buildroot_dl:/buildroot_dl|' \
    "$WORK/docker-compose.yml"
  mkdir -p "$WORK/.buildroot_dl"
  echo "==> added .buildroot_dl mount to docker-compose.yml"
fi

# --- 4. App source: clean v0.8.7 export + patch -------------------------------------------
OV="$WORK/opt/rootfs-overlay/opt"
echo "==> staging ${APP_TAG} app source into the overlay"
rm -rf "$OV"; mkdir -p "$OV"
git -C "$APP_REPO" archive "$APP_TAG" | tar -x -C "$OV"

# git archive does not include submodules, and build.sh's translation step needs this
# populated or it fails partway through compiling catalogs.
SUBMOD="src/seedsigner/resources/seedsigner-translations"
[ -d "$APP_REPO/$SUBMOD/l10n" ] \
  || { echo "ERROR: translations submodule not checked out in $APP_REPO/$SUBMOD" >&2; exit 1; }

# The submodule is copied from the WORKING TREE, not from the tag, because git archive omits
# submodules. So the working tree's submodule commit must actually match what the app tag
# pins -- otherwise a checkout on some other branch silently ships different translations
# into a build that claims to be the release. Same failure mode as an unpinned OS layer:
# invisible in the resulting data.
SUBMOD_PIN="$(git -C "$APP_REPO" ls-tree "$APP_TAG" -- "$SUBMOD" | awk '{print $3}')"
SUBMOD_HAVE="$(git -C "$APP_REPO/$SUBMOD" rev-parse HEAD 2>/dev/null || echo "unknown")"
if [ "$SUBMOD_PIN" != "$SUBMOD_HAVE" ]; then
  echo "ERROR: translations submodule is at ${SUBMOD_HAVE}, but ${APP_TAG} pins ${SUBMOD_PIN}." >&2
  echo "       Run: git -C '$APP_REPO' submodule update --init --recursive" >&2
  echo "       (after checking out ${APP_TAG}, or the submodule will follow another branch)" >&2
  exit 1
fi
PROV+=("app_translations_submodule: ${SUBMOD_HAVE} (matches ${APP_TAG})")
echo "==> translations submodule ${SUBMOD_HAVE:0:12} matches ${APP_TAG}"

cp -a "$APP_REPO/$SUBMOD/." "$OV/$SUBMOD/"

echo "==> applying instrumentation patch"
git -C "$OV" apply --verbose "$HERE/0.8.7-burst-instrumentation.patch" 2>/dev/null \
  || patch -p0 -d "$OV" < "$HERE/0.8.7-burst-instrumentation.patch"

# --- 5. version.json, only if this OS revision demands it ---------------------------------
# Some post-0.8.7 OS revisions added write_version_json(), which hard-exits unless either
# tools/write_versionfile.py exists or version.json is already present -- and v0.8.7's app
# predates that tool. Release-baseline v0.8.7 has no such function, so writing the file
# there would be adding a fork-shaped workaround to a build that does not need it. Detect
# rather than assume.
if grep -q "write_version_json" "$WORK/opt/build.sh"; then
  echo "==> this OS revision requires version.json; writing a stub"
  cat > "$OV/src/seedsigner/version.json" <<JSON
{
    "name": "${APP_TAG}-BURST-DEBUG",
    "fork": "instrumented",
    "short_commit_hash": "${APP_TAG}",
    "timestamp": "2026-01-01T00:00:00"
}
JSON
else
  echo "==> OS revision has no write_version_json(); skipping the stub"
fi

# --- 5b. Bake provenance into the image ---------------------------------------------------
# So that it lands on the device and can be copied off with the captured frames. Provenance
# that lives only next to the build is provenance that gets separated from the data.
{
  printf '%s\n' "${PROV[@]}"
  echo "patch: $(sha256sum "$HERE/0.8.7-burst-instrumentation.patch" | cut -d' ' -f1)"
  echo "image_mb: ${IMAGE_MB}"
} > "$OV/src/seedsigner/BUILD-PROVENANCE.txt"
cat "$OV/src/seedsigner/BUILD-PROVENANCE.txt" | sed 's/^/    /'

# --- 6. Strip host bytecode ---------------------------------------------------------------
# Any __pycache__ created by running python on the source tree gets copied verbatim into the
# image. Harmless in practice (the tags will not match the device's interpreter) but it puts
# stale copies of edited code inside the artefact and makes verification ambiguous.
find "$OV" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$OV" -name "*.pyc" -delete 2>/dev/null || true

# --- 7. Build -----------------------------------------------------------------------------
echo "==> building (this takes a while; first run downloads sources)"
( cd "$WORK" && docker compose run --rm -T build-images --"${BOARD}" --skip-repo ) \
  > "$WORK/build-${BOARD}.log" 2>&1 \
  || { echo "BUILD FAILED - tail of $WORK/build-${BOARD}.log:" >&2; tail -30 "$WORK/build-${BOARD}.log" >&2; exit 1; }

# The image filename takes the app-branch variable, which is still its default because
# --skip-repo never clones. ".dev." here is cosmetic and does NOT mean a --dev build.
BUILT="$WORK/images/seedsigner_os.dev.${BOARD}.img"
[ -f "$BUILT" ] || { echo "ERROR: expected image not found: $BUILT" >&2; exit 1; }
OUT="$WORK/images/seedsigner_os.${APP_TAG}-BURST-DEBUG.${BOARD}.img"
mv -f "$BUILT" "$OUT"

{
  printf '%s\n' "${PROV[@]}"
  echo "patch: $(sha256sum "$HERE/0.8.7-burst-instrumentation.patch" | cut -d' ' -f1)"
  echo "image_mb: ${IMAGE_MB}"
  echo "image: $(sha256sum "$OUT" | cut -d' ' -f1)"
  echo "built_from: $(basename "$WORK")"
} > "$WORK/images/PROVENANCE.txt"

echo
echo "==> built: $OUT"
sha256sum "$OUT"
echo "==> provenance: $WORK/images/PROVENANCE.txt  (copy this alongside any captured data)"
echo
echo "==> verifying the instrumentation is inside the image"
python3 "$HERE/verify-image.py" "$OUT"
