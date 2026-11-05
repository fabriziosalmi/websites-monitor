"""
Writes the report for the websites in config.yaml: python main.py.
The scheduler (scheduler.py) and the GitHub Action run it; it is the same
as python -m websites_monitor report --output <output_file>.
"""
import asyncio
import logging
import sys

from websites_monitor.bootstrap import build_service, load_config, read_template

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    config = load_config()
    try:
        service = build_service(config)
        report = asyncio.run(service.report(
            config.websites, "markdown", timeout=config.timeout, template=read_template(config.report_template),
        ))
        with open(config.output_file, "w") as f:
            f.write(report["report_content"])
    except Exception as e:
        # The scheduler reads the exit code: a run that wrote no report
        # must not look like a success.
        logger.error(f"Critical error: {e}")
        return 1
    logger.info(f"Wrote {config.output_file} for {len(config.websites)} websites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
