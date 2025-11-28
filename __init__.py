from . import ui

def register():
    ui.BlenderManager.register()

def unregister():
    ui.BlenderManager.unregister()


if __name__ == '__main__':
    register()
