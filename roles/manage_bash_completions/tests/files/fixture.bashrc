# shellcheck shell=bash
export AWS_PROFILE=redhat


# Lazy-load and cache bash completions on first use
_lazy_completion() {
    local cmd=$1; shift
    local cache="${XDG_CACHE_HOME:-$HOME/.cache}/bash_completions/${cmd}.bash"
    local cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/bash_completions"
    local gen_cmd
    printf -v gen_cmd '%q ' "$@"
    gen_cmd=${gen_cmd% }
    eval "_complete_lazy_${cmd}() {
        unset -f _complete_lazy_${cmd}
        complete -r ${cmd} 2>/dev/null
        if [[ ! -s '${cache}' || \$(command -v ${cmd}) -nt '${cache}' ]]; then
            mkdir -p '${cache_dir}'
            ${gen_cmd} > '${cache}'
        fi
        source '${cache}'
        return 124
    }"
    complete -F "_complete_lazy_${cmd}" "$cmd"
}

if command -v aws &>/dev/null; then
    complete -C '/tmp/aws_completer' aws
fi
command -v oc &>/dev/null && _lazy_completion oc oc completion bash
# Source local bashrc overrides if present
if [ -f ~/.bashrc-local ]; then
  . ~/.bashrc-local
fi
