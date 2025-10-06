import itertools
import re
from typing import Iterable, List, Optional, Sequence, Set

# Default TLDs used when none are provided
DEFAULT_TLDS: List[str] = [".com", ".in", ".ai", ".co", ".io"]


def slugify(value: str) -> str:
    """Lowercase and remove non-alphanumerics.
    Keeps only a-z0-9 to form domain-safe chunks.
    """
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _unique(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for v in values:
        if v and v not in seen:
            seen.add(v)
            result.append(v)
    return result


def generate_candidates(
    concept: str,
    tlds: Optional[Sequence[str]] = None,
    extras: Optional[Sequence[str]] = None,
    max_per_pattern: int = 50,
) -> List[str]:
    """Generate domain candidates from a concept string.

    - Builds base chunks via join/short/prefix/suffix patterns
    - Combines with provided TLDs
    - Returns de-duplicated candidate list
    """
    if tlds is None:
        tlds = DEFAULT_TLDS

    words = [w for w in re.split(r"[\W_]+", concept.lower()) if w]
    base_chunks: Set[str] = set()

    # Core patterns
    joined = slugify("".join(words))
    dashed = "-".join(words)
    short = "".join(w[:4] for w in words)[:10]

    base_chunks.update(
        {
            joined,
            dashed.replace("-", ""),
            short,
            (words[0] + (words[1] if len(words) > 1 else "")) if words else "",
            ((words[1] + words[0]) if len(words) > 1 else (words[0] if words else "")),
        }
    )

    # Prefixes / suffixes
    prefixes = ["get", "try", "go", "my", "the", "use", "shop", "hey"]
    suffixes = ["hub", "hq", "labs", "tech", "app", "store", "mart", "zone"]
    if words:
        for p in prefixes:
            base_chunks.add(slugify(p + words[0]))
        for s in suffixes:
            base_chunks.add(slugify(words[0] + s))

    # Optional extras
    if extras:
        for e in extras:
            base_chunks.add(slugify(e))

    # Combine with TLDs
    candidates: List[str] = []
    for chunk, tld in itertools.product(sorted(base_chunks), tlds):
        if chunk:
            candidates.append(f"{chunk}{tld}")

    # Deduplicate and trim
    return _unique(candidates)[: max_per_pattern * len(tlds)]
