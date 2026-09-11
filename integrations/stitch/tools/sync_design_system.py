#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: sync_design_system (Facade)"""

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
from stitch_client import sync_design_system, Colors, log, log_error


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", "-f", help="Caminho do design.md")
    args = p.parse_args()
    try:
        res = sync_design_system(design_md_path=args.file)
        log("STITCH", "✅ Design System sincronizado com sucesso!", Colors.GREEN)
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
