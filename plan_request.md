### Plan for implementing `amb_cli/gui/web/`
1. **Create Web Files (`amb_cli/gui/web/`)**:
   - `index.html`: Base layout, integrating navbar, metrics dashboard, command hub (quick actions), terminal simulation, and session list. We will use plain HTML5.
   - `styles.css`: Dark-mode styling, using variables for colors (slate-950 background, cyan neon accents, violet, emerald green), adding responsive design and subtle glassmorphism effects.
   - `app.js`: Simple vanilla JS script to handle basic interactions like toggling some views or simulating terminal output.
   - `server.py`: A lightweight python module exposing a `start_web_server(port=8080)` function using `http.server`, which launches the browser (`webbrowser.open`) and serves the static files in `amb_cli/gui/web`.
2. **Update CLI Integration**:
   - In `amb_cli/cli_modules/cli_parsers.py`, modify `cmd_gui` arguments. Wait, let's see `cli_parsers.py`: `_c("gui", ..., cmd_gui, ["ui", "wizard"])`. Let's add `--web` argument to it.
   - In `amb_cli/cli_modules/cli_handlers.py`, update `cmd_gui`: if `--web` is set, launch `start_web_server()` from `amb_cli.gui.web.server`. If not set, maybe default to web or launch tkinter. The requirements state: "Atualize amb_cli/gui/wizard_app.py ou crie função start_web_gui() para lançar o servidor local e abrir no navegador quando o usuário executar amb gui --web ou por padrão." So I'll add `--web` and default to web.
3. **Tests (`tests/test_web_gui.py`)**:
   - Write tests for `server.py` and the existence of the HTML/CSS/JS files. Ensure tests run with `pytest -q` without breaking anything. Mock `webbrowser.open` and `http.server.HTTPServer`.
4. **Pre-commit**: Complete pre-commit steps to make sure proper testing, verifications, reviews and reflections are done.
