#!/usr/bin/env bash
# Lists test files with line count and approximate case count, grouped by directory.
# Usage: inventory.sh [repo-root]
set -euo pipefail

root="${1:-.}"
cd "$root"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required" >&2
  exit 1
fi

case_pattern='^\s*(it|test|it\.each|test\.each|bench)(\.(only|skip|concurrent|todo))?\s*[(`]|^\s*(async\s+)?def\s+test_|^\s*func\s+Test[A-Z_]|#\[(tokio::)?test\]|@Test\b|@pytest\.mark\.parametrize|let%(expect_)?test|^\s*Scenario( Outline)?:'

files=$(rg --files \
  -g '*.test.*' -g '*.spec.*' -g '*_test.*' -g 'test_*.py' -g '*_spec.rb' \
  -g '**/__tests__/**' -g '**/tests/**/*.rs' -g '*Test.java' -g '*Tests.swift' \
  -g '*Test.kt' -g '*.feature' \
  -g '!**/node_modules/**' -g '!**/vendor/**' -g '!**/dist/**' -g '!**/build/**' \
  -g '!**/*.snap' -g '!**/__snapshots__/**' \
  2>/dev/null \
  | grep -E '\.(ts|tsx|mts|cts|js|jsx|mjs|cjs|py|go|rs|rb|java|kt|swift|ml|ex|exs|cs|php|scala|dart|c|cc|cpp|zig|lua|sh|t|feature)$' \
  | awk '{ d = $0; if (!sub("/[^/]*$", "", d)) d = "."; print d "\t" $0 }' \
  | sort -t "$(printf '\t')" -k1,1 -k2,2 | cut -f2 || true)

if [ -z "$files" ]; then
  echo "No test files found under $(pwd)"
  exit 0
fi

total_files=0
total_lines=0
total_cases=0

printf '%-8s %-7s %s\n' "LINES" "CASES" "FILE"
current_area=""
while IFS= read -r f; do
  area=$(dirname "$f")
  if [ "$area" != "$current_area" ]; then
    printf '\n## %s\n' "$area"
    current_area="$area"
  fi
  lines=$(wc -l < "$f" | tr -d ' ')
  cases=$(rg -c -e "$case_pattern" "$f" 2>/dev/null || echo 0)
  printf '%-8s %-7s %s\n' "$lines" "$cases" "$f"
  total_files=$((total_files + 1))
  total_lines=$((total_lines + lines))
  total_cases=$((total_cases + cases))
done <<< "$files"

snapshots=$({ rg --files -g '**/*.snap' -g '!**/node_modules/**' 2>/dev/null || true; } | wc -l | tr -d ' ')
specs=$({ rg --files -g '**/SPEC.md' -g '**/*.spec.md' -g '!**/node_modules/**' 2>/dev/null || true; } | wc -l | tr -d ' ')

printf '\nTOTAL: %s files, %s lines, ~%s cases, %s snapshot files, %s spec files\n' \
  "$total_files" "$total_lines" "$total_cases" "$snapshots" "$specs"
