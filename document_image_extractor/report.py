from typing import Dict
def print_file_report(filename: str, stats: Dict) -> None:
    if stats.get("skipped"):
        print(f"⚠️ {filename}: {stats.get('reason')}")
        return

    if "error" in stats:
        print(f"❌ {filename}: {stats['error']}")
        return

    if stats.get("saved", 0) > 0:
        print(
            f"✔️ {filename}: "
            f"found={stats['found']}, saved={stats['saved']}, "
            f"dupes={stats['duplicates']}, "
            f"filtered_small={stats['filtered_small']}, "
            f"filtered_dims={stats['filtered_dims']}, "
            f"errors={stats['errors']}"
        )
    else:
        print(
            f"⚠️ {filename}: No hay imágenes válidas | "
            f"found={stats['found']}, dupes={stats['duplicates']}, "
            f"filtered_small={stats['filtered_small']}, "
            f"filtered_dims={stats['filtered_dims']}, "
            f"errors={stats['errors']}"
        )


def accumulate_totals(total: Dict[str, int], stats: Dict) -> None:
    for k in total:
        total[k] += int(stats.get(k, 0))


def print_summary(files: int, skipped: int, failed: int, total: Dict[str, int]) -> None:
    print("\n=== RESUMEN ===")
    print(
        f"files={files}, skipped={skipped}, failed={failed} | "
        f"found={total['found']}, saved={total['saved']}, dupes={total['duplicates']}, "
        f"filtered_small={total['filtered_small']}, filtered_dims={total['filtered_dims']}, "
        f"errors={total['errors']}"
    )