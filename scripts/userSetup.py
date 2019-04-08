from maya import cmds, utils


if not cmds.about(batch=True):
    import zUtils.install
    utils.executeDeferred(zUtils.install.shelf)
