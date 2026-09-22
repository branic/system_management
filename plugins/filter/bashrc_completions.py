"""Filter plugin to merge bash completion sections in ~/.bashrc."""

from __future__ import absolute_import, annotations, division, print_function

import re
import shlex

from typing import TYPE_CHECKING, Any

from ansible.errors import AnsibleFilterError

if TYPE_CHECKING:
    from typing import Callable

__metaclass__ = type  # pylint: disable=C0103

DOCUMENTATION = """
    name: merge_bashrc_completions
    author: Brant Evans
    version_added: "1.4.0"
    short_description: Merge provider-scoped bash completion entries into a .bashrc section.
    description:
      - Parses an anchored bash completion section with a canonical C(_lazy_completion) helper.
      - Merges caller-supplied entries for one provider while preserving entries owned by others.
      - Removes legacy Ansible block markers and obsolete one-line completion registrations.
    positional: _input
    options:
      _input:
        description: Current .bashrc file content.
        type: str
        required: true
      provider_cmds:
        description: Command names managed by the calling provider.
        type: list
        elements: str
        required: true
      entries:
        description: Structured completion entries to register for the calling provider.
        type: list
        elements: dict
        required: true
"""

EXAMPLES = """
- name: Merge bash completion section
  ansible.builtin.set_fact:
    __manage_bash_completions_result: >-
      {{ __manage_bash_completions_content
         | branic.system_management.merge_bashrc_completions(
             provider_cmds=manage_bash_completions_provider_cmds,
             entries=manage_bash_completions_entries,
           ) }}
"""

SECTION_COMMENT = "# Lazy-load and cache bash completions on first use"

LAZY_COMPLETION_FUNCTION = """_lazy_completion() {
    local cmd=$1; shift
    local cache="${XDG_CACHE_HOME:-$HOME/.cache}/bash_completions/${cmd}.bash"
    local cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/bash_completions"
    local gen_cmd
    printf -v gen_cmd '%q ' "$@"
    gen_cmd=${gen_cmd% }
    eval "_complete_lazy_${cmd}() {
        unset -f _complete_lazy_${cmd}
        complete -r ${cmd} 2>/dev/null
        if [[ ! -s '${cache}' || \\$(command -v ${cmd}) -nt '${cache}' ]]; then
            mkdir -p '${cache_dir}'
            ${gen_cmd} > '${cache}'
        fi
        source '${cache}'
        return 124
    }"
    complete -F "_complete_lazy_${cmd}" "$cmd"
}"""

LEGACY_ANSIBLE_BLOCKS = [
    re.compile(
        r"# BEGIN ANSIBLE MANAGED BLOCK branic\.system_management\.install_cloud_clis"
        r".*?"
        r"# END ANSIBLE MANAGED BLOCK branic\.system_management\.install_cloud_clis\n?",
        re.DOTALL,
    ),
    re.compile(
        r"# BEGIN ANSIBLE MANAGED BLOCK branic\.system_management\.openshift_local"
        r".*?"
        r"# END ANSIBLE MANAGED BLOCK branic\.system_management\.openshift_local\n?",
        re.DOTALL,
    ),
]

LEGACY_ONE_LINERS = [
    re.compile(r"^command -v aws &>/dev/null && complete -C .* aws\s*$", re.MULTILINE),
    re.compile(
        r"^command -v oc &>/dev/null && source <\(oc completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v ocm &>/dev/null && source <\(ocm completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v rosa &>/dev/null && source <\(rosa completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v tkn &>/dev/null && source <\(tkn completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v kube-linter &>/dev/null && source <\(kube-linter completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v kustomize &>/dev/null && source <\(kustomize completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v stern &>/dev/null && source <\(stern --completion=bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^command -v helm &>/dev/null && source <\(helm completion bash\)\s*$",
        re.MULTILINE,
    ),
    re.compile(
        r"^if command -v crc &>/dev/null; then\s*"
        r"# shellcheck source=/dev/null\s*"
        r"source <\(crc completion bash\)\s*"
        r"fi\s*$",
        re.MULTILINE,
    ),
]

BASHRC_LOCAL_MARKERS = (
    "# Source local bashrc overrides if present",
    "~/.bashrc-local",
)

DIRECT_BLOCK_RE = re.compile(
    r"^if command -v (?P<cmd>\S+) &>/dev/null; then\s+"
    r"complete -C '(?P<completer>[^']+)' (?P=cmd)\s+"
    r"fi\s*$",
    re.MULTILINE,
)

LAZY_LINE_RE = re.compile(
    r"^command -v (?P<cmd>\S+) &>/dev/null && _lazy_completion (?P<generator>.+)\s*$",
)


def _validate_entries(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        raise AnsibleFilterError(
            f"merge_bashrc_completions entries must be a list, got {type(entries).__name__}",
        )

    validated: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise AnsibleFilterError(
                f"merge_bashrc_completions entries[{index}] must be a dict",
            )
        entry_type = entry.get("type")
        cmd = entry.get("cmd")
        if not cmd or not entry_type:
            raise AnsibleFilterError(
                f"merge_bashrc_completions entries[{index}] requires cmd and type",
            )
        if entry_type == "direct":
            if "completer" not in entry:
                raise AnsibleFilterError(
                    f"merge_bashrc_completions entries[{index}] requires completer",
                )
        elif entry_type == "lazy":
            generator = entry.get("generator")
            if not isinstance(generator, list) or not generator:
                raise AnsibleFilterError(
                    f"merge_bashrc_completions entries[{index}]"
                    " requires a non-empty generator list",
                )
        else:
            raise AnsibleFilterError(
                f"merge_bashrc_completions entries[{index}] has unsupported type {entry_type!r}",
            )
        validated.append(entry)
    return validated


def _cleanup_content(content: str) -> str:
    cleaned = content
    for pattern in LEGACY_ANSIBLE_BLOCKS:
        cleaned = pattern.sub("", cleaned)
    for pattern in LEGACY_ONE_LINERS:
        cleaned = pattern.sub("", cleaned)
    return cleaned


def _entry_key(entry: dict[str, Any]) -> str:
    return str(entry["cmd"])


def _parse_direct_block(block: str) -> dict[str, Any]:
    match = DIRECT_BLOCK_RE.search(block)
    if not match:
        raise AnsibleFilterError(
            "merge_bashrc_completions could not parse direct completion block",
        )
    return {
        "cmd": match.group("cmd"),
        "type": "direct",
        "completer": match.group("completer"),
    }


def _parse_lazy_line(line: str) -> dict[str, Any]:
    match = LAZY_LINE_RE.match(line.strip())
    if not match:
        raise AnsibleFilterError(
            f"merge_bashrc_completions could not parse lazy completion line: {line!r}",
        )
    cmd = match.group("cmd")
    parts = shlex.split(match.group("generator"))
    if parts and parts[0] == cmd:
        generator = parts[1:]
    else:
        generator = parts
    if not generator:
        raise AnsibleFilterError(
            f"merge_bashrc_completions lazy completion line has no generator args: {line!r}",
        )
    if generator[0] != cmd:
        generator = [cmd, *generator]
    return {
        "cmd": cmd,
        "type": "lazy",
        "generator": generator,
    }


def _parse_completion_entries(section_body: str) -> list[dict[str, Any]]:
    function_start = section_body.find("_lazy_completion()")
    if function_start == -1:
        return []

    brace_start = section_body.find("{", function_start)
    if brace_start == -1:
        return []

    depth = 0
    index = brace_start
    while index < len(section_body):
        char = section_body[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                remainder = section_body[index + 1 :]
                break
        index += 1
    else:
        return []

    entries: list[dict[str, Any]] = []
    lines = remainder.splitlines()
    line_index = 0
    while line_index < len(lines):
        stripped = lines[line_index].strip()
        if not stripped:
            line_index += 1
            continue
        if stripped.startswith("if command -v"):
            block_lines = []
            while line_index < len(lines):
                block_lines.append(lines[line_index])
                if lines[line_index].strip() == "fi":
                    break
                line_index += 1
            entries.append(_parse_direct_block("\n".join(block_lines)))
            line_index += 1
            continue
        if stripped.startswith("command -v") and "_lazy_completion" in stripped:
            entries.append(_parse_lazy_line(stripped))
            line_index += 1
            continue
        break
    return entries


def _locate_section(content: str) -> tuple[str, str, str, bool]:
    comment_index = content.find(SECTION_COMMENT)
    function_index = content.find("_lazy_completion()")

    if comment_index != -1:
        start = comment_index
    elif function_index != -1:
        start = function_index
    else:
        return content, "", "", False

    head = content[:start]
    section_and_tail = content[start:]

    function_start = section_and_tail.find("_lazy_completion()")
    if function_start == -1:
        return head, section_and_tail, "", True

    brace_start = section_and_tail.find("{", function_start)
    depth = 0
    index = brace_start
    while index < len(section_and_tail):
        char = section_and_tail[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                section_end = index + 1
                break
        index += 1
    else:
        return head, section_and_tail, "", True

    completion_start = section_end
    lines = section_and_tail[completion_start:].splitlines(keepends=True)
    consumed = 0
    line_index = 0
    while line_index < len(lines):
        stripped = lines[line_index].strip()
        if not stripped:
            consumed += len(lines[line_index])
            line_index += 1
            continue
        if stripped.startswith("if command -v"):
            while line_index < len(lines):
                consumed += len(lines[line_index])
                if lines[line_index].strip() == "fi":
                    line_index += 1
                    break
                line_index += 1
            continue
        if stripped.startswith("command -v") and "_lazy_completion" in stripped:
            consumed += len(lines[line_index])
            line_index += 1
            continue
        break

    section_body = section_and_tail[: completion_start + consumed]
    tail = section_and_tail[completion_start + consumed :]
    return head, section_body, tail, True


def _render_entry(entry: dict[str, Any]) -> str:
    cmd = entry["cmd"]
    if entry["type"] == "direct":
        return (
            f"if command -v {cmd} &>/dev/null; then\n"
            f"    complete -C '{entry['completer']}' {cmd}\n"
            f"fi"
        )
    generator = " ".join(entry["generator"])
    return f"command -v {cmd} &>/dev/null && _lazy_completion {cmd} {generator}"


def _render_section(entries: list[dict[str, Any]]) -> str:
    lines = [SECTION_COMMENT, LAZY_COMPLETION_FUNCTION, ""]
    for entry in entries:
        lines.append(_render_entry(entry))
    return "\n".join(lines).rstrip() + "\n"


def _merge_entries(
    parsed_entries: list[dict[str, Any]],
    provider_cmds: list[str],
    new_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    provider_cmd_set = set(provider_cmds)
    new_entry_cmds = {_entry_key(entry) for entry in new_entries}

    by_cmd: dict[str, dict[str, Any]] = {
        _entry_key(entry): entry
        for entry in parsed_entries
        if _entry_key(entry) not in provider_cmd_set
    }

    for entry in new_entries:
        by_cmd[_entry_key(entry)] = entry

    for cmd in provider_cmd_set:
        if cmd not in new_entry_cmds:
            by_cmd.pop(cmd, None)

    return [by_cmd[cmd] for cmd in sorted(by_cmd)]


def _insert_section(content: str, section: str) -> str:
    for marker in BASHRC_LOCAL_MARKERS:
        marker_index = content.find(marker)
        if marker_index != -1:
            line_start = content.rfind("\n", 0, marker_index)
            if line_start == -1:
                return section + content
            prefix = content[: line_start + 1]
            suffix = content[line_start + 1 :]
            if prefix and not prefix.endswith("\n\n"):
                prefix = prefix.rstrip("\n") + "\n\n"
            return prefix + section + suffix

    if content and not content.endswith("\n"):
        content += "\n"
    if content and not content.endswith("\n\n"):
        content += "\n"
    return content + section


def merge_bashrc_completions(
    content: Any,
    provider_cmds: Any,
    entries: Any,
) -> dict[str, Any]:
    """Merge provider-scoped bash completion entries into .bashrc content."""
    if content is None:
        content = ""
    if not isinstance(content, str):
        raise AnsibleFilterError(
            f"merge_bashrc_completions expects a string, got {type(content).__name__}",
        )
    if not isinstance(provider_cmds, list):
        raise AnsibleFilterError(
            "merge_bashrc_completions provider_cmds must be a list",
        )

    validated_entries = _validate_entries(entries)
    cleaned = _cleanup_content(content)
    head, section_body, tail, has_section = _locate_section(cleaned)

    parsed_entries = _parse_completion_entries(section_body) if section_body else []
    merged_entries = _merge_entries(parsed_entries, provider_cmds, validated_entries)
    new_section = _render_section(merged_entries)

    if has_section:
        new_content = head + new_section + tail
    else:
        new_content = _insert_section(head, new_section)

    normalized_current = cleaned if cleaned.endswith("\n") or not cleaned else cleaned + "\n"
    normalized_new = (
        new_content if new_content.endswith("\n") or not new_content else new_content + "\n"
    )
    return {
        "content": normalized_new.rstrip("\n") + ("\n" if normalized_new else ""),
        "changed": normalized_new != normalized_current,
    }


class FilterModule:
    """Ansible filter plugin for bash completion section management."""

    def filters(self) -> dict[str, Callable[..., Any]]:
        """Return filter functions."""
        return {"merge_bashrc_completions": merge_bashrc_completions}
