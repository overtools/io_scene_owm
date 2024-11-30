from .blender import BLAnimation
from ..readers import OWAnimReader
import bpy

def init(filenames, context):
    armature = context.active_object

    if not getattr(armature, "animation_data", False):
        armature.animation_data_create()

    if len(filenames) == 1:
        animData = OWAnimReader.read(filenames[0])
        if animData is None: return
        
        armature.animation_data.action = BLAnimation.importAction(animData, armature)
        context.scene.frame_end = animData.header.duration
    else:
        track = armature.animation_data.nla_tracks.new()
        track.name = "OWM Anim"
        armature.animation_data.nla_tracks.active = track

        frameOffset = 0
        for filename in filenames:
            animData = OWAnimReader.read(filename)
            if animData is None: continue
        
            action = BLAnimation.importAction(animData, armature)
            track.strips.new(action.name, frameOffset, action)
            frameOffset+=animData.header.duration
        
        context.scene.frame_end = frameOffset
    
    
    context.scene.render.fps = int(animData.header.fps)