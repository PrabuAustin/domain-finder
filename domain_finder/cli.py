import argparse
from typing import List, Sequence

from .generator import generate_candidates, DEFAULT_TLDS
from .clients import domainr_prefilter, godaddy_find_available


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Domain Finder CLI: generate and check availability")
    p.add_argument("concept", type=str, help="Concept string, e.g. 'AI e-bike store in India'")
    p.add_argument("--tlds", nargs="*", default=None, help="Explicit TLDs to use (overrides defaults)")
    p.add_argument("--add-tlds", nargs="*", default=[], help="TLDs to add to the default set")
    p.add_argument("--remove-tlds", nargs="*", default=[], help="TLDs to remove from the resulting set")
    p.add_argument("--extras", nargs="*", default=[], help="Extra base name chunks to include")
    p.add_argument("--check-type", default="FAST", choices=["FAST", "FULL"], help="GoDaddy check type")
    p.add_argument("--use-domainr-prefilter", action="store_true", help="Use Domainr to prefilter candidates")
    p.add_argument("--max-per-pattern", type=int, default=50, help="Max candidates per pattern x #TLDs")
    return p.parse_args()


def _resolve_tlds(args: argparse.Namespace) -> List[str]:
    # Start with explicit TLDs if provided, else defaults
    tlds = list(args.tlds) if args.tlds else list(DEFAULT_TLDS)
    # Add
    tlds.extend([t for t in args.add_tlds if t not in tlds])
    # Remove
    tlds = [t for t in tlds if t not in set(args.remove_tlds)]
    return tlds


def main() -> None:
    args = _parse_args()

    tlds = _resolve_tlds(args)

    candidates: List[str] = generate_candidates(
        concept=args.concept,
        tlds=tlds,
        extras=args.extras,
        max_per_pattern=args.max_per_pattern,
    )

    to_check: Sequence[str] = candidates
    if args.use_domainr_prefilter:
        to_check = domainr_prefilter(candidates)

    available = godaddy_find_available(to_check, check_type=args.check_type)

    if not available:
        print("No available domains found.")
        return

    print("AVAILABLE DOMAINS:")
    for d in available:
        print(f"- {d}")


if __name__ == "__main__":
    main()
