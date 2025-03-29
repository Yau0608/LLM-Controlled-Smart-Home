"""
Mobile Web Interface for Smart Home Voice Control

This script runs a web server that allows you to control your smart home
using voice commands from your phone or any web browser.
"""

from web_interface import run_server

if __name__ == "__main__":
    # Default port is 5000
    run_server(port=5000) 