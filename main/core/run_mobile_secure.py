"""
Secure Mobile Web Interface (HTTPS) for Smart Home Voice Control

This script runs a secure web server with HTTPS that allows you to control 
your smart home using voice commands from your phone browser.
"""

from web_interface import run_secure_server

if __name__ == "__main__":
    # Default HTTPS port is 5443 to avoid conflicts
    run_secure_server(port=5443)