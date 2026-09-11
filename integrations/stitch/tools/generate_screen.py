#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎨 Stitch Tool: generate_screen (Facade)"""

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
from stitch_client import generate_screen, Colors, log, log_error


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--device", "-d", default="DESKTOP")
    p.add_argument("--model", "-m", default="GEMINI_3_8_FLASH")
    args = p.parse_args()
    try:
        res = generate_screen(
            prompt=args.prompt, device_type=args.device, model_id=args.model
        )
        log(
            "STITCH",
            f"Tela gerada com sucesso! ID: {res.get('screenId')}",
            Colors.GREEN,
        )
    except Exception as e:
        log_error("STITCH", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
