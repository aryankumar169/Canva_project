PIXELCRAFT STUDIO - MINOR PROJECT
=================================

A beginner-friendly Canva-inspired graphic design editor built with:
- Python and Flask (backend)
- HTML, CSS and JavaScript (frontend)
- SQLite (database)

FEATURES
--------
1. User signup and login
2. Design editor with a canvas
3. Add and edit text
4. Add rectangle and circle shapes
5. Change background and text colors
6. Upload an image
7. Move elements by dragging
8. Save designs to SQLite
9. Reopen saved designs
10. Export canvas as PNG

RUN ON WINDOWS
--------------
1. Install Python 3 from https://www.python.org/downloads/
   During setup, tick "Add Python to PATH".
2. Extract this ZIP file.
3. Open the extracted PixelCraft_Studio folder in VS Code.
4. Open Terminal > New Terminal.
5. Run:
      py -m pip install -r requirements.txt
6. Run:
      py app.py
7. Open this address in Chrome:
      http://127.0.0.1:5000

Keep the terminal open while using the website.
Press Ctrl+C in the terminal to stop the server.

NOTE
----
This is an educational minor-project prototype, not a production Canva replacement.
Change the Flask secret key before any public deployment.
