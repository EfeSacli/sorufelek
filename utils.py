import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller bundle.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_path, relative_path)
    if os.path.exists(target):
        return target
    # Fallback to current working directory
    cwd_target = os.path.join(os.getcwd(), relative_path)
    if os.path.exists(cwd_target):
        return cwd_target
    return relative_path
