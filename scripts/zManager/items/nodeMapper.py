from . import nodes


NODE_TYPES_WRAPPER = {
    "zAttachment": nodes.ZivaAttachmentNodeItem,
    "zFiber": nodes.ZivaFiberNodeItem,
    "zMaterial": nodes.ZivaWeightNodeItem,
    "zTet": nodes.ZivaWeightNodeItem,
    "zTissue": nodes.ZivaNodeItem,
    "zBone": nodes.ZivaNodeItem,
    "zLineOfAction": nodes.ZivaLineOfActionNodeItem
}
