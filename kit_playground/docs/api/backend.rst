Backend Module
==============

.. automodule:: kit_playground.backend
   :members:
   :undoc-members:
   :show-inheritance:

Web Server
----------

.. autoclass:: kit_playground.backend.web_server.PlaygroundWebServer
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: run

Xpra Manager
------------

.. autoclass:: kit_playground.backend.xpra_manager.XpraManager
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: start_xpra
   .. automethod:: stop_xpra

Job Manager
-----------

.. autoclass:: kit_playground.backend.source.job_manager.JobManager
   :members:
   :undoc-members:
   :show-inheritance:

Port Registry
-------------

.. autoclass:: kit_playground.backend.source.port_registry.PortRegistry
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: get_instance
   .. automethod:: register_backend
   .. automethod:: register_frontend

Process Monitor
---------------

.. automodule:: kit_playground.backend.source.process_monitor
   :members:
   :undoc-members:
   :show-inheritance:
