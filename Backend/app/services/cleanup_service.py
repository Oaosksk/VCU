"""Video cleanup service with configurable retention policy"""
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Video

logger = logging.getLogger(__name__)


def cleanup_old_videos(retention_days: int = 7, dry_run: bool = False) -> dict:
    """
    Delete uploaded videos older than retention_days.

    Videos with status 'processing' are skipped to avoid interrupting
    in-flight analysis.

    Args:
        retention_days: Keep videos newer than this many days.
        dry_run: If True, only report what would be deleted.

    Returns:
        dict with counts of deleted / skipped / errors.
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    stats = {"deleted": 0, "skipped": 0, "errors": 0, "freed_bytes": 0}

    db = SessionLocal()
    try:
        old_videos = (
            db.query(Video)
            .filter(Video.uploaded_at < cutoff, Video.status != "processing")
            .all()
        )

        for video in old_videos:
            filepath = Path(video.filepath) if video.filepath else None

            if dry_run:
                logger.info("[DRY RUN] Would delete video %s (%s)", video.id, filepath)
                stats["deleted"] += 1
                continue

            # Delete file on disk
            try:
                if filepath and filepath.exists():
                    size = filepath.stat().st_size
                    filepath.unlink()
                    stats["freed_bytes"] += size
                    logger.info("Deleted file: %s", filepath)

                # Remove DB record
                db.delete(video)
                stats["deleted"] += 1
            except Exception as e:
                logger.error("Failed to delete video %s: %s", video.id, e)
                stats["errors"] += 1

        db.commit()

    except Exception as e:
        logger.error("Cleanup failed: %s", e)
        db.rollback()
        raise
    finally:
        db.close()

    freed_mb = stats["freed_bytes"] / (1024 * 1024)
    logger.info(
        "Cleanup complete — deleted=%d, skipped=%d, errors=%d, freed=%.1f MB",
        stats["deleted"],
        stats["skipped"],
        stats["errors"],
        freed_mb,
    )
    return stats


def get_storage_usage() -> dict:
    """Return current upload directory size and disk space."""
    upload_dir = Path(settings.UPLOAD_DIR)

    total_size = sum(f.stat().st_size for f in upload_dir.rglob("*") if f.is_file())
    disk = shutil.disk_usage(upload_dir if upload_dir.exists() else ".")

    return {
        "upload_dir_mb": round(total_size / (1024 * 1024), 1),
        "disk_free_gb": round(disk.free / (1024 ** 3), 1),
        "disk_total_gb": round(disk.total / (1024 ** 3), 1),
    }


# ---------------------------------------------------------------------------
# CLI entry-point:  python -m app.services.cleanup_service [--days 7] [--dry]
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup old uploaded videos")
    parser.add_argument("--days", type=int, default=7, help="Retention period in days")
    parser.add_argument("--dry", action="store_true", help="Dry run only")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    result = cleanup_old_videos(retention_days=args.days, dry_run=args.dry)
    print(result)
