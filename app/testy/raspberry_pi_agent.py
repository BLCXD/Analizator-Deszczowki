                      
"""Compatibility entry point for the maintained Raspberry agent package."""

import argparse
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi Agent (compatibility entry point)")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    os.environ["DEVICE_ID"] = args.device_id
    os.environ["BACKEND_URL"] = args.api_url
    os.environ["SYNC_INTERVAL"] = str(args.interval)
    if not os.environ.get("DEVICE_SECRET"):
        parser.error("Set DEVICE_SECRET in the environment before starting the agent")

    from raspberry.ad_agent.main import RaspberryPiAgent

    agent = RaspberryPiAgent()
    if args.once:
        return 0 if agent.run_once() else 1
    if not agent.start():
        return 1
    try:
        while agent.running:
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        agent.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
