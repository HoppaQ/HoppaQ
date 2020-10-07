import  BackGroundReduction.motion_detector  as md
import BackGroundReduction.image_processing  as imgp 

vs, reduction, min_area = md.initialize()


md.motion_detector(vs, reduction, min_area )

md.clear_up()

