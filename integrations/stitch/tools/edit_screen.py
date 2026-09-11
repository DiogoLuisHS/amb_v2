#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: edit_screen (Facade)"""

import sys, os, argparse

_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
for _s in ["config", "integrations/stitch"]:
    _p = os.path.normpath(os.path.join(_cur, *_s.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from stitch_client import edit_screen, Colors, log, log_error


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--screen-id", "-s", required=True)
    p.add_argument("--prompt", "-p", required=True)
    args = p.parse_args()
    try:
        res = edit_screen(screen_id=args.screen_id, prompt=args.prompt)
        log("STITCH", f"Tela {args.screen_id} refinada com sucesso!", Colors.GREEN)
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
