#!/usr/bin/env python3

from webapp import app

if __name__ == '__main__':
    # DEVELOPMENT (Debug on)
    app.run(host="0.0.0.0", port=5000, debug=True)
    # PRODUCTION (External-facing, Debug off)
    # app.run(host="0.0.0.0", port=80, debug=True)
