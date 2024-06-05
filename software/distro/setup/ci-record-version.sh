#!/bin/bash -eu
# This script records OS installation versioning information in the same way as the
# install.planktoscope.community/distro.sh script does.

# Utilities for user interaction
# Note: the code in this section was copied and adapted from
# https://github.com/starship/starship's install script,
# which is licensed under ISC and is copyrighted by the Starship Contributors.

BOLD="$(tput bold 2>/dev/null || printf '')"
GREY="$(tput setaf 0 2>/dev/null || printf '')"
UNDERLINE="$(tput smul 2>/dev/null || printf '')"
RED="$(tput setaf 1 2>/dev/null || printf '')"
GREEN="$(tput setaf 2 2>/dev/null || printf '')"
YELLOW="$(tput setaf 3 2>/dev/null || printf '')"
BLUE="$(tput setaf 4 2>/dev/null || printf '')"
MAGENTA="$(tput setaf 5 2>/dev/null || printf '')"
NO_COLOR="$(tput sgr0 2>/dev/null || printf '')"

info() {
  printf '%s\n' "${BOLD}${GREY}>${NO_COLOR} $*"
}

warn() {
  printf '%s\n' "${YELLOW}! $*${NO_COLOR}"
}

error() {
  printf '%s\n' "${RED}x $*${NO_COLOR}" >&2
}

completed() {
  printf '%s\n' "${GREEN}✓${NO_COLOR} $*"
}



# Utilities for interacting with Git repositories

resolve_commit() {
  mirror_dir="$1"
  query_type="$2"
  tag_prefix="$3"
  version_query="$4"
  if [ "${query_type}" = "tag" ]; then
    version_query="${tag_prefix}${version_query}"
  fi
  cmd="git -C ${mirror_dir} rev-list -n 1 ${version_query}"
  $cmd && return 0 || rc=$?

  error "Command failed (exit code $rc): ${BLUE}${cmd}${NO_COLOR}"
  printf "\n" >&2
  return $rc
}

resolve_tag() {
  mirror_dir="$1"
  tag_prefix="$2"
  commit_hash="$3"
  git -C "${mirror_dir}" describe --tags --exact-match --match "${TAG_PREFIX}*" "${commit_hash}" \
    2> /dev/null || printf ""
}

resolve_pseudoversion() {
  mirror_dir="$1"
  tag_prefix="$2"
  commit_hash="$3"
  git -C "${mirror_dir}" describe --tags --match "${TAG_PREFIX}*" --abbrev=7 "${commit_hash}" \
    2> /dev/null || printf ""
}



# Main function

with_empty_placeholder() {
  if [ -z "$1" ]; then
    printf "(none)"
  else
    printf "%s" "$1"
  fi
}

# All code with side-effects is wrapped in a main function
# called at the bottom of the file, so that a truncated partial
# download doesn't cause execution of half a script.
main() {
  # Print configuration information

  pretty_repo=$(printf "%s" "${REPO}" | sed "s~^.*://~~")

  printf "  %s\n" "${UNDERLINE}Configuration${NO_COLOR}"
  info "${BOLD}Repo${NO_COLOR}:          ${GREEN}${pretty_repo}${NO_COLOR}"
  info "${BOLD}Version query${NO_COLOR}: ${GREEN}${VERSION_QUERY}${NO_COLOR}"
  info "${BOLD}Query type${NO_COLOR}:    ${GREEN}${QUERY_TYPE}${NO_COLOR}"
  info "${BOLD}Hardware${NO_COLOR}:      ${GREEN}${HARDWARE}${NO_COLOR}"
  if [ -n "${VERBOSE-}" ]; then
    VERBOSE=v
    info "${BOLD}Tag prefix${NO_COLOR}:    $(with_empty_placeholder "${TAG_PREFIX}")"
    info "${BOLD}Entrypoint${NO_COLOR}:    $(with_empty_placeholder "${SETUP_ENTRYPOINT}")"
    info "${BOLD}Verbose${NO_COLOR}:       yes"
  else
    VERBOSE=
  fi
  printf '\n'

  # Resolve versioning information

  normalized_repo="${REPO}"
  if printf "%s" "${REPO}" | grep -q '@'; then
    # Repo was specified with SCP-like syntax for SSH protocol
    :
  elif printf "%s" "${REPO}" | grep -q '://'; then
    # Repo was specified with a protocol identifier
    :
  else
    normalized_repo="https://${REPO}"
  fi

  commit_hash="$(resolve_commit "${mirror_dir}" "${QUERY_TYPE}" "${TAG_PREFIX}" "${VERSION_QUERY}")"
  short_commit_hash="$(printf "%s" "${commit_hash}" | cut -c 1-7)"
  tag="$(resolve_tag "${mirror_dir}" "${TAG_PREFIX}" "${commit_hash}")"
  version_string="$(resolve_pseudoversion "${mirror_dir}" "${TAG_PREFIX}" "${commit_hash}" \
    | sed "s~^${TAG_PREFIX}~~")"
  if [ -n "${VERBOSE-}" ]; then
    printf "\n"
  fi

  printf "  %s\n" "${UNDERLINE}Versioning${NO_COLOR}"
  info "${BOLD}Git Commit${NO_COLOR}:    ${short_commit_hash}"
  info "${BOLD}Git Tag${NO_COLOR}:       $(with_empty_placeholder "${tag}")"
  info "${BOLD}Version${NO_COLOR}:       ${version_string}"
  printf '\n'

  # Record versioning information

  for versioning_dir in "${HOME}/.local/etc/pkscope-distro" "/usr/share/planktoscope"; do
    versioning_dir="${HOME}/.local/etc/pkscope-distro"
    info "Recording versioning information to ${versioning_dir}..."
    if [ -d "${versioning_dir}" ]; then
      warn "The ${versioning_dir} directory already exists, so it will be erased."
      confirm "Are you sure you want to continue?"
      sudo rm -rf "${versioning_dir}"
    fi
    sudo mkdir -p "${versioning_dir}"
    sudo chown $USER "${versioning_dir}"

    installer_file_header="# This file was auto-generated!"
    installer_config_file="${versioning_dir}/installer-config.yml"
    printf "%s\n" "${installer_file_header}" > "${installer_config_file}"
    printf "%s: \"%s\"\n" \
      "repo" "${pretty_repo}" \
      "version-query" "${VERSION_QUERY}" \
      "query-type" "${QUERY_TYPE}" \
      "hardware" "${HARDWARE}" \
      "tag-prefix" "${TAG_PREFIX}" \
      "setup-entrypoint" "${SETUP_ENTRYPOINT}" \
      >> "${installer_config_file}"

    installer_versioning_file="${versioning_dir}/installer-versioning.yml"
    printf "%s\n" "${installer_file_header}" > "${installer_versioning_file}"
    printf "%s: \"%s\"\n" \
      "repo" "${pretty_repo}" \
      "commit" "${commit_hash}" \
      "tag" "${tag}" \
      "version" "${version_string}" \
      >> "${installer_versioning_file}"
  done
}



# Imperative section

# Set default values for the command-line arguments
if [ -z "${REPO-}" ]; then
  exit 1
fi
DEFAULT_VERSION_QUERY="software/stable"
if [ -z "${VERSION_QUERY-}" ]; then
  error "VERSION_QUERY environment variable was not set!"
  exit 1
fi
DEFAULT_QUERY_TYPE="branch"
if [ -z "${QUERY_TYPE-}" ]; then
  error "QUERY_TYPE environment variable was not set!"
  exit 1
fi
DEFAULT_HARDWARE="planktoscopehat"
if [ -z "${HARDWARE-}" ]; then
  error "HARDWARE environment variable was not set!"
  exit 1
fi
DEFAULT_TAG_PREFIX="software/"
if [ -z "${TAG_PREFIX-}" ]; then
  TAG_PREFIX="${DEFAULT_TAG_PREFIX}"
fi
DEFAULT_SETUP_ENTRYPOINT="software/distro/setup/setup.sh"
if [ -z "${SETUP_ENTRYPOINT-}" ]; then
  SETUP_ENTRYPOINT="${DEFAULT_SETUP_ENTRYPOINT}"
fi
if [ -z "${VERBOSE-}" ]; then
  VERBOSE=""
fi

# Ensure a valid query type
case "${QUERY_TYPE}" in
  branch | tag | hash)
    ;;
  *)
    error "Unknown query type: ${QUERY_TYPE}"
    usage
    exit 1
    ;;
esac

main
