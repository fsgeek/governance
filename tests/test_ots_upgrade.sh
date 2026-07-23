#!/bin/bash
set -euo pipefail

SOURCE_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SOURCE_ROOT/scripts/ots-upgrade.sh"
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

assert_contains() {
    local haystack=$1
    local needle=$2
    [[ "$haystack" == *"$needle"* ]] || fail "expected output to contain: $needle"
}

cd "$TEST_ROOT"
git init -q
git config user.name "OTS Test"
git config user.email "ots-test@example.invalid"
git config commit.gpgsign false

mkdir -p .venv/bin timestamps
cat > .venv/bin/ots <<'FAKE_OTS'
#!/bin/bash
set -e

if [ "$1" != "upgrade" ]; then
    echo "unsupported fake OTS command: $1" >&2
    exit 2
fi

proof=$2
case "$(cat "$proof")" in
    complete)
        echo "Success! Timestamp complete"
        ;;
    ready)
        cp "$proof" "$proof.bak"
        printf 'complete' > "$proof"
        echo "Success! Timestamp complete"
        ;;
    pending)
        echo "Calendar proof is not ready" >&2
        exit 1
        ;;
    *)
        echo "unexpected proof fixture" >&2
        exit 2
        ;;
esac
FAKE_OTS
chmod +x .venv/bin/ots

printf 'fixture repository\n' > README.md
printf 'complete' > timestamps/complete.ots
printf 'ready' > timestamps/ready.ots
printf 'pending' > timestamps/pending.ots
git add README.md timestamps
git commit -qm "test: initial fixtures"

printf 'must remain outside the OTS commit\n' > unrelated.txt
git add unrelated.txt

output=$(bash "$SCRIPT")

assert_contains "$output" "already complete: timestamps/complete.ots"
assert_contains "$output" "upgraded: timestamps/ready.ots"
assert_contains "$output" "pending:  timestamps/pending.ots"

subject=$(git log -1 --format=%s)
[ "$subject" = "ots: upgrade 1 timestamp(s)" ] || \
    fail "expected one-upgrade subject, got: $subject"

changed=$(git diff-tree --no-commit-id --name-only -r HEAD | sort)
expected=$(printf '%s\n' \
    timestamps/ready.ots \
    timestamps/ready.ots.bak | sort)
[ "$changed" = "$expected" ] || \
    fail "unexpected paths in upgrade commit: $changed"

staged=$(git diff --cached --name-only)
[ "$staged" = "unrelated.txt" ] || \
    fail "unrelated staged content was not preserved: $staged"

head_before=$(git rev-parse HEAD)
second_output=$(bash "$SCRIPT")
head_after=$(git rev-parse HEAD)

[ "$head_before" = "$head_after" ] || \
    fail "a no-change run created a commit"
assert_contains "$second_output" "No timestamps ready to upgrade yet."

echo "PASS: OTS upgrade accounting and commit isolation"
