"""
Entitle GUI tab plug-ins.

Each module in this package is a self-contained tab: it exposes a ``TAB_TITLE``
string and a ``build(parent, app)`` function. ``gui.app`` loads them from an
explicit registry. Made an explicit package in 0.4.0 for import consistency with
the rest of the project.
"""
