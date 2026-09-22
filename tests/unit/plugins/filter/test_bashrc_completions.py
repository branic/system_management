"""Unit tests for branic.system_management.plugins.filter.bashrc_completions."""

from __future__ import absolute_import, annotations, division, print_function

import os
import sys

import pytest

from ansible.errors import AnsibleFilterError

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "filter"),
)

from bashrc_completions import (  # noqa: E402 pylint: disable=wrong-import-position,import-error
    SECTION_COMMENT,
    FilterModule,
)


@pytest.fixture()
def filter_func():
    """Return the merge_bashrc_completions filter function."""
    return FilterModule().filters()["merge_bashrc_completions"]


@pytest.fixture()
def sample_head():
    """Return content that should remain above the completion section."""
    return "# shellcheck shell=bash\nexport AWS_PROFILE=redhat\n\n"


@pytest.fixture()
def sample_tail():
    """Return content that should remain below the completion section."""
    return (
        "\n# Source local bashrc overrides if present\n"
        "if [ -f ~/.bashrc-local ]; then\n  . ~/.bashrc-local\nfi\n"
    )


AWS_ENTRY = {
    "cmd": "aws",
    "type": "direct",
    "completer": "/home/user/.local/bin/aws_completer",
}

OC_ENTRY = {
    "cmd": "oc",
    "type": "lazy",
    "generator": ["oc", "completion", "bash"],
}

CRC_ENTRY = {
    "cmd": "crc",
    "type": "lazy",
    "generator": ["crc", "completion", "bash"],
}


class TestFreshBashrc:
    """Insert a new section when no anchor exists."""

    def test_appends_before_bashrc_local(self, filter_func, sample_head, sample_tail):
        """A new section is inserted before the bashrc-local stanza."""
        content = sample_head + sample_tail
        result = filter_func(
            content,
            provider_cmds=["aws", "oc"],
            entries=[AWS_ENTRY, OC_ENTRY],
        )

        assert result["changed"] is True
        assert SECTION_COMMENT in result["content"]
        assert "_lazy_completion()" in result["content"]
        assert "complete -C '/home/user/.local/bin/aws_completer' aws" in result["content"]
        assert (
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash"
            in result["content"]
        )
        assert result["content"].index(SECTION_COMMENT) < result["content"].index("~/.bashrc-local")
        assert sample_head.strip() in result["content"]
        assert "~/.bashrc-local" in result["content"]


class TestExistingSection:
    """Update an anchored section in place."""

    def test_preserves_other_provider_entries(self, filter_func, sample_head, sample_tail):
        """Cloud CLI updates keep an existing crc line from another provider."""
        existing = (
            f"{sample_head}{SECTION_COMMENT}\n"
            "_lazy_completion() {\n    echo stub\n}\n\n"
            "command -v crc &>/dev/null && _lazy_completion crc crc completion bash\n"
            f"{sample_tail}"
        )
        result = filter_func(
            existing,
            provider_cmds=["aws", "oc"],
            entries=[AWS_ENTRY, OC_ENTRY],
        )

        assert result["changed"] is True
        assert (
            "command -v crc &>/dev/null && _lazy_completion crc crc completion bash"
            in result["content"]
        )
        assert (
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash"
            in result["content"]
        )
        assert "printf -v gen_cmd" in result["content"]
        assert "echo stub" not in result["content"]

    def test_prunes_removed_provider_cmds(self, filter_func, sample_head, sample_tail):
        """Entries for provider_cmds not present in entries are removed."""
        existing = (
            f"{sample_head}{SECTION_COMMENT}\n"
            "_lazy_completion() {\n    echo stub\n}\n\n"
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash\n"
            "command -v helm &>/dev/null && _lazy_completion helm helm completion bash\n"
            f"{sample_tail}"
        )
        result = filter_func(
            existing,
            provider_cmds=["aws", "oc", "helm"],
            entries=[OC_ENTRY],
        )

        assert result["changed"] is True
        assert (
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash"
            in result["content"]
        )
        assert (
            "command -v helm &>/dev/null && _lazy_completion helm helm completion bash"
            not in result["content"]
        )


LEGACY_SOURCE_OC = "command -v oc &>/dev/null && source <(oc completion bash)\n"
LEGACY_SOURCE_HELM = "command -v helm &>/dev/null && source <(helm completion bash)\n"
LEGACY_SOURCE_STERN = "command -v stern &>/dev/null && source <(stern --completion=bash)\n"
LEGACY_AWS_COMPLETE_C = (
    "command -v aws &>/dev/null && complete -C /usr/local/bin/aws_completer aws\n"
)
LEGACY_CRC_MULTILINE = (
    "if command -v crc &>/dev/null; then\n"
    "# shellcheck source=/dev/null\n"
    "source <(crc completion bash)\n"
    "fi\n"
)

HELM_ENTRY = {
    "cmd": "helm",
    "type": "lazy",
    "generator": ["helm", "completion", "bash"],
}


class TestMigration:
    """Remove legacy Ansible-managed content."""

    def test_removes_legacy_ansible_block(self, filter_func, sample_head, sample_tail):
        """Old blockinfile markers are removed during migration."""
        legacy_block = (
            "# BEGIN ANSIBLE MANAGED BLOCK branic.system_management.install_cloud_clis\n"
            "if command -v aws &>/dev/null; then\n"
            "    complete -C '/tmp/aws_completer' aws\n"
            "fi\n"
            "# END ANSIBLE MANAGED BLOCK branic.system_management.install_cloud_clis\n"
        )
        content = sample_head + legacy_block + sample_tail
        result = filter_func(
            content,
            provider_cmds=["aws"],
            entries=[AWS_ENTRY],
        )

        assert "ANSIBLE MANAGED BLOCK" not in result["content"]
        assert "complete -C '/home/user/.local/bin/aws_completer' aws" in result["content"]

    def test_removes_legacy_source_one_liners(self, filter_func, sample_head, sample_tail):
        """Old source <(cmd completion bash) one-liners are removed during migration."""
        content = (
            sample_head + LEGACY_SOURCE_OC + LEGACY_SOURCE_HELM + LEGACY_SOURCE_STERN + sample_tail
        )
        result = filter_func(
            content,
            provider_cmds=["oc", "helm"],
            entries=[OC_ENTRY, HELM_ENTRY],
        )

        assert "source <(" not in result["content"]
        assert (
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash"
            in result["content"]
        )
        assert (
            "command -v helm &>/dev/null && _lazy_completion helm helm completion bash"
            in result["content"]
        )

    def test_removes_legacy_aws_complete_c_one_liner(self, filter_func, sample_head, sample_tail):
        """Old command -v aws && complete -C one-liner is removed during migration."""
        content = sample_head + LEGACY_AWS_COMPLETE_C + sample_tail
        result = filter_func(
            content,
            provider_cmds=["aws"],
            entries=[AWS_ENTRY],
        )

        assert "complete -C /usr/local/bin/aws_completer" not in result["content"]
        assert "complete -C '/home/user/.local/bin/aws_completer' aws" in result["content"]

    def test_removes_legacy_crc_multiline_block(self, filter_func, sample_head, sample_tail):
        """Old multi-line crc completion block is removed during migration."""
        content = sample_head + LEGACY_CRC_MULTILINE + sample_tail
        result = filter_func(
            content,
            provider_cmds=["crc"],
            entries=[CRC_ENTRY],
        )

        assert "# shellcheck source=/dev/null" not in result["content"]
        assert "source <(crc completion bash)" not in result["content"]
        assert (
            "command -v crc &>/dev/null && _lazy_completion crc crc completion bash"
            in result["content"]
        )


class TestIdempotency:
    """Second run with the same data should not change content."""

    def test_second_run_unchanged(self, filter_func, sample_head, sample_tail):
        """Applying the same entries twice yields changed=false on the second run."""
        content = sample_head + sample_tail
        first = filter_func(
            content,
            provider_cmds=["aws", "oc"],
            entries=[AWS_ENTRY, OC_ENTRY],
        )
        second = filter_func(
            first["content"],
            provider_cmds=["aws", "oc"],
            entries=[AWS_ENTRY, OC_ENTRY],
        )

        assert first["changed"] is True
        assert second["changed"] is False
        assert second["content"] == first["content"]


class TestStableOrdering:
    """Completion lines use a stable alphabetical order regardless of provider run order."""

    def test_alternating_providers_produces_same_order(self, filter_func, sample_head, sample_tail):
        """Cloud CLIs first then CRC yields the same order as CRC first then cloud CLIs."""
        cloud_provider_cmds = ["aws", "oc"]
        crc_provider_cmds = ["crc"]
        content = sample_head + sample_tail

        cloud_then_crc = filter_func(
            content,
            provider_cmds=cloud_provider_cmds,
            entries=[AWS_ENTRY, OC_ENTRY],
        )
        cloud_then_crc = filter_func(
            cloud_then_crc["content"],
            provider_cmds=crc_provider_cmds,
            entries=[CRC_ENTRY],
        )

        crc_then_cloud = filter_func(
            content,
            provider_cmds=crc_provider_cmds,
            entries=[CRC_ENTRY],
        )
        crc_then_cloud = filter_func(
            crc_then_cloud["content"],
            provider_cmds=cloud_provider_cmds,
            entries=[AWS_ENTRY, OC_ENTRY],
        )

        assert cloud_then_crc["content"] == crc_then_cloud["content"]
        assert (
            cloud_then_crc["content"].index("command -v aws")
            < cloud_then_crc["content"].index("command -v crc")
            < cloud_then_crc["content"].index("command -v oc")
        )

    def test_reorders_existing_non_alphabetical_section(
        self,
        filter_func,
        sample_head,
        sample_tail,
    ):
        """An existing section is normalized to alphabetical cmd order on update."""
        existing = (
            f"{sample_head}{SECTION_COMMENT}\n"
            "_lazy_completion() {\n    echo stub\n}\n\n"
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash\n"
            "if command -v aws &>/dev/null; then\n"
            "    complete -C '/home/user/.local/bin/aws_completer' aws\n"
            "fi\n"
            f"{sample_tail}"
        )
        result = filter_func(
            existing,
            provider_cmds=["aws", "oc"],
            entries=[AWS_ENTRY, OC_ENTRY],
        )

        assert result["content"].index(
            "complete -C '/home/user/.local/bin/aws_completer' aws",
        ) < result["content"].index(
            "command -v oc &>/dev/null && _lazy_completion oc oc completion bash",
        )


class TestValidation:
    """Reject invalid entry payloads."""

    def test_requires_generator_for_lazy_entry(self, filter_func):
        """Lazy entries without a generator list fail fast."""
        with pytest.raises(AnsibleFilterError):
            filter_func("", provider_cmds=["oc"], entries=[{"cmd": "oc", "type": "lazy"}])
