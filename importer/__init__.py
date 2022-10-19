modules = ["blender","entity","material","model","owmap"]
if "sys" in locals():
    from importlib import reload 
    for module in modules:
        module = __package__+"."+module
        if module in sys.modules:
            reload(sys.modules[module])
        else:
            import_module("."+module, __package__)
else:
    import sys
    from importlib import import_module
    for module in modules:
        import_module("."+module, __package__)