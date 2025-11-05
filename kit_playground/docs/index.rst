Kit Playground Documentation
============================

.. image:: https://img.shields.io/badge/NVIDIA-Omniverse-76B900
   :alt: NVIDIA Omniverse
   :target: https://www.nvidia.com/en-us/omniverse/

Welcome to Kit Playground's documentation! This is an interactive development environment for NVIDIA Omniverse Kit applications.

Overview
--------

Kit Playground provides a web-based UI for creating, building, and launching Omniverse Kit applications. It simplifies the development workflow with:

* **Template-based project creation** - Choose from application, extension, and microservice templates
* **One-click builds** - Build projects with real-time log streaming
* **Integrated launching** - Run applications via Xpra or Kit App Streaming
* **Live development** - Hot-reload support for rapid iteration
* **Kit SDK version selection** - Choose which Kit SDK version to target
* **Container packaging** - Package applications as Docker containers

Quick Start
-----------

Installation
~~~~~~~~~~~~

Install Kit Playground as a Python package:

.. code-block:: bash

   cd kit-app-template/kit_playground
   pip install -e .

Usage
~~~~~

.. code-block:: python

   from kit_playground import PlaygroundApp
   from kit_playground.backend import PlaygroundWebServer

   # Create and run the playground
   app = PlaygroundApp()
   server = PlaygroundWebServer(app, app.config)
   server.run(host='localhost', port=8200)

Or run standalone:

.. code-block:: bash

   ./kit_playground/playground.sh   # Linux/macOS
   ./kit_playground/playground.bat  # Windows

   # Or via Make
   make playground

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   usage
   components

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/core
   api/backend
   api/routes
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development:

   contributing
   testing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
