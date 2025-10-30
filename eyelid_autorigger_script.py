import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel 
import sys


'''		
Written by Tami Tritz 2025
Ok for personal or commercial use. DO NOT USE for AI or LLM training

'''
class eyeAutorigger():
    def __init__(self, Ui_AutoEyeRig):
        #sets a few recurring global variables and libraries - RigDir for Left vs Right generation, RigSec for section
        #generation (anywhere with a lidloc)
        self.m_Ui_AutoEyeRig = Ui_AutoEyeRig
        self.m_strEyeBndJnt = "_eye_bnd_jnt"
        self.m_mpRigDir = {
                            "L": False,
                            "R": False
                        }
        self.m_mpRigSec = {
                            "upr": False,
                            "lwr": False,
                            "upr_crease": False,
                            "misc": False
                        }

    #sets up whether we're looking at R, L, or both
    def update_rig_dir(self):
        if self.m_Ui_AutoEyeRig.FGetLeftLock() == False and self.m_Ui_AutoEyeRig.FGetRightLock() == False:
            cmds.confirmDialog( title='No Selection', message='You must click left, right, or both for the tool to run', button=['Ok'], defaultButton='Yes')
            return False

        self.m_mpRigDir["L"] = self.m_Ui_AutoEyeRig.FGetLeftLock()
        self.m_mpRigDir["R"] = self.m_Ui_AutoEyeRig.FGetRightLock()
        return True
    
    #sets up whether we're looking at upper, lower, crease, or miscellaneous
    def update_rig_sec(self):
        if self.m_Ui_AutoEyeRig.FGetUpperLock() == False and self.m_Ui_AutoEyeRig.FGetLowerLock() == False and self.m_Ui_AutoEyeRig.FGetUpperCreaseLock() == False and self.m_Ui_AutoEyeRig.FGetMiscLock() == False:
            cmds.confirmDialog( title='No Selection', message='You must click at least one of the sections (upper, lower, crease, or misc) for the tool to run', button=['Ok'], defaultButton='Yes')
            return False
        #gets whether the box is checked by the user when the button is pressed
        self.m_mpRigSec["upr"] = self.m_Ui_AutoEyeRig.FGetUpperLock()
        self.m_mpRigSec["lwr"] = self.m_Ui_AutoEyeRig.FGetLowerLock()
        self.m_mpRigSec["upr_crease"] = self.m_Ui_AutoEyeRig.FGetUpperCreaseLock()
        self.m_mpRigSec["misc"] = self.m_Ui_AutoEyeRig.FGetMiscLock()
        return True

    def generate_base_rig(self):
        #function for the first button of the UI, separates the eye mesh into R and L and creates the eye joints
        if not self.update_rig_dir():
            return

        self.autofill_eye_mesh()

        #for each direction, run the create_eye_joints function
        for strKey, fValue in self.m_mpRigDir.items():
            if fValue:
                print (f"{self.m_mpRigDir}")
                self.create_eye_joints(strKey)

    def generate_locators(self):
        #function for the second button of the UI, generates the eyelid locators 
        if not self.update_rig_dir():
            return
        
        if not self.update_rig_sec():
            return

        #For each direction, run however many of the section generators are selected
        for strKey, fValue in self.m_mpRigDir.items():
            if fValue:
                print (f"{self.m_mpRigDir}")
                for strSec, bValue in self.m_mpRigSec.items():  
                    if bValue:
                        print (strSec)
                        if strSec == "misc":
                            self.create_misc_locators(strKey)
                        else:
                            self.create_eye_locators(strKey, strSec)
                        
    def generate_rig(self):
        #function for the third button in the UI, connects those locators to joints and controls and sets a set driven key 
        #so they can be moved as a group like a blink would
        if not self.update_rig_dir():
            return
        
        if not self.update_rig_sec():
            return

        for strKey, fValue in self.m_mpRigDir.items():
            if fValue:
                print (f"{self.m_mpRigDir}")
                self.blink_controls(strKey)
                for strSec, bValue in self.m_mpRigSec.items():  
                    if strSec == "misc":
                        continue
                    if bValue:
                        print (strSec)
                        self.create_joints(strKey, strSec)
                        self.create_controls(strKey, strSec)

                if self.m_Ui_AutoEyeRig.FGetUpperLock():
                    self.set_upr_driven_keys(strKey)
                    
                if self.m_Ui_AutoEyeRig.FGetUpperCreaseLock():
                    self.set_crease_driven_keys(strKey)
                    
                if self.m_Ui_AutoEyeRig.FGetLowerLock():
                    self.set_lwr_driven_keys(strKey)
                    
                if self.m_Ui_AutoEyeRig.FGetUpperLock():
                    self.create_misc_controls(strKey)

        if cmds.objExists("L_lid_loc_grp"):
            cmds.delete("L_lid_loc_grp")
        if cmds.objExists("R_lid_loc_grp"):
            cmds.delete("R_lid_loc_grp")
                  
    def mirror_rig(self):
        #takes existing rigged setup and mirrors it. Could also just generate Left and Right, but this is cleaner for the user 
        #and allows some customization if they want to add joints in or remove some 
        jointsToMirror = ["L_lid_upr_bnd_jnt", "L_lid_lwr_bnd_jnt", "L_lid_upr_crease_bnd_jnt", "L_lid_aim_jnt",
                          "L_inner_eye_corner_bnd_jnt", "L_outer_eye_corner_bnd_jnt", "L_squint_bnd_jnt"]

        for joint in jointsToMirror:
            if cmds.objExists(joint):
                cmds.select(joint, r = True)

                cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=('L_', 'R_'))
                joint = cmds.ls(selection = True)
                cmds.select(joint, hi = True, r = True)
                jointChildren = cmds.ls(selection = True)
                joint = "_bnd_jnt"
                # Remove items containing the substring - for this, existing parent constraints
                oldConstraints = [item for item in jointChildren if joint not in item]
                #cmds.select(oldConstraints, r = True)
                cmds.delete(oldConstraints)
                

        controlsToMirror = ["L_eye_upr_blink_grp", "L_eye_lwr_blink_grp", "L_lid_upr_follow_grp", "L_lid_lwr_follow_grp", 
                            "L_lid_upr_crease_follow_grp", "L_inner_eye_corner_grp", "L_outer_eye_corner_grp", "L_squint_grp"]

        if cmds.objExists("L_eye_controls_grp"):
            children = controlsToMirror
            for each in children:
                cmds.parent(each, world = True)
            cmds.delete("L_eye_controls_grp")

        #controls are less straightforward than joints, and some groups need to be scaled differently so they can be moved together
        cmds.group(name = "L_eye_controls_grp", em = True)
        cmds.parentConstraint("head_bnd_jnt", "L_eye_controls_grp", mo = False)
        cmds.delete("L_eye_controls_grp_parentConstraint1")
        cmds.parent(controlsToMirror, "L_eye_controls_grp")
        cmds.duplicate("L_eye_controls_grp", name = "R_eye_controls_grp")
        cmds.scale(-1, 1, 1, "R_eye_controls_grp")        
        cmds.select("R_eye_controls_grp", hi = True)
        rightControls = cmds.ls(selection = True)

        mel.eval('searchReplaceNames "L_" "R_" "selected";')

        rightControls = cmds.ls(selection = True)

        cmds.select("R_lid_upr_crease_follow_grp", "R_lid_lwr_follow_grp", "R_lid_upr_follow_grp", d = True, hi = True)

        colorControls = cmds.ls(selection = True)

        for each in colorControls:
            controlOverride = str(f"{each}.overrideEnabled")
            controlColor = str(f"{each}.overrideColor")
            cmds.setAttr(controlOverride, 1)
            cmds.setAttr(controlColor, 13)
                
            #reset constraints 
        print (rightControls)
        grp = "_grp"
        shape = "_ctrlShape"

        # Remove items containing the substring
        ctrlSelection = [item for item in rightControls if grp not in item]
        print (ctrlSelection)
        ctrlSelection = [item for item in ctrlSelection if shape not in item]
        print(ctrlSelection)

        cmds.select(ctrlSelection, r=True)
        #removes the blink controls - not used for the next part
        cmds.select("R_eye_upr_blink_ctrl", "R_eye_upr_detail_ctrl", "R_eye_lwr_blink_ctrl", d = True)

        ctrlSelection = cmds.ls(selection = True)
        #list created for testing purposes, leaving in case I want to redo how this works later
        #takes controls, splits at name, adds joint suffix, then constrains joint to control
        #eyeJoints = []

        for ctrl in ctrlSelection:
            jnt = ctrl.rsplit("_", 1)
            jnt = jnt[0] + "_bnd_jnt"
            print (jnt)
            cmds.parentConstraint(ctrl, jnt, mo = True)
            #eyeJoints.append(jnt)

        self.set_lwr_driven_keys("R")
        self.set_upr_driven_keys("R")
        self.set_crease_driven_keys("R")

        if cmds.objExists("head_ctrl"):
            cmds.parent("L_eye_controls_grp", "head_ctrl")
            cmds.parent("R_eye_controls_grp", "head_ctrl")

        #initially written for a few other controls to get flipped but I believe this is unnecessary
        #rOffsetGroups = cmds.ls(filter(lambda x: grps in x, rightControls))
        #print(rOffsetGroups)
        #for grp in rOffsetGroups:
        #    cmds.scale(1, 1, -1, grp)



        #set specific mirror for any controls that need it
        #set up constraints between joints and controls in mimic to L_ side 

    def autofill_eye_mesh(self):

        #if L_ and R_ meshes exist:
        #write this functionality to skip over the next sections later
        
        #if eye mesh combined exist:
        selection = cmds.ls(selection = True)

        if len(selection) == 0:
            cmds.confirmDialog( title='No Selection', message='Select eyeball mesh', button=['Ok'], defaultButton='Yes')
        if len(selection) > 1:
            L_mesh = list(filter(lambda x: "L_" in x, selection))
            cmds.duplicate(L_mesh)
            cmds.rename(L_mesh, "L_eye_dup_mesh")

            R_mesh = list(filter(lambda x: "R_" in x, selection))
            cmds.duplicate(R_mesh)
            cmds.rename(R_mesh, "R_eye_dup_mesh")
        else:
            cmds.duplicate(selection)
            selection = cmds.ls(selection = True)
            cmds.rename(selection, "eye_mesh_dup")
            self.split_eye_mesh()

    def split_eye_mesh(self):
        #select eyeball mesh by faces & find centers, then create joints

        #selects one of the 2 meshes for eyeballs - this setup assumes they are 2 items that were merged, but can still be selected by faces 
        #future expansion of tool: make a function for if they're already separate
        eye_mesh = "eye_mesh_dup"

        for obj in eye_mesh:
            faces = cmds.ls(obj + ".f[*]", flatten=True)  #Get all face indexes from the object.
            
            for face in faces:
                index = int(face.split("[")[1].rstrip("]"))  #Extract the faces index number.
                cmds.polySelect(obj, extendToShell=index)

        #separate the two meshes
        mel.eval("polySeparate -sss 0 -ch 1 eye_mesh_dupShape")
        #selects just the first mesh in what is now a group - silly but it works
        cmds.pickWalk(d = "up")
        cmds.pickWalk(d = "down")
        eye1mesh = cmds.ls(selection = True) 
        cmds.makeIdentity(eye1mesh, a = True, t = True)
        cmds.xform(cp = True) 
        #create a locator to find the location of the geo in world space
        cmds.spaceLocator(a = True, n = "Eye_WS_locator")
        cmds.parentConstraint(eye1mesh, "Eye_WS_locator", mo = False)
        cmds.select("Eye_WS_locator")
        eyeWScoords = cmds.xform(q = True, t = True, ws = True)
        print (eyeWScoords)
        cmds.select(eye_mesh, hi = True, r = True)
        cmds.select("*polySurface*", d = True)
        cmds.select(eye_mesh, d = True) 
        transformNodes = cmds.ls(selection = True)
        cmds.delete(transformNodes)

        if eyeWScoords[0] > 0: #if x value is more than 0, it's the left side
            cmds.rename(eye1mesh, "L_eye_dup_mesh")
            eye1mesh = "L_eye_dup_mesh"

            #isolating the selection to all the miscellaneous stuff in the selection
            cmds.select(eye_mesh, r = True, hi = True)
            cmds.select(eye1mesh, d = True)
            cmds.select(eye_mesh, d = True)
            cmds.select("*Shape*", d = True)

            selection = cmds.ls(sl=True)
            print(selection)
            #this checks whether there's multiple objects - useful for if the eyes have a glass + an interior or any other extra stuff
            if len(selection) > 1:
                #if there is more stuff than just the other side, this just duplicates and mirrors the existing eyeball mesh to the other side
                #a little messy but functional and still reasonably efficient
                #could make all this into an independent function, but this only happens once so decided to just copy and paste
                cmds.duplicate(eye1mesh, n = "R_eye_dup_mesh")
                cmds.spaceLocator(a = True, n = "Reverse_WP_locator")
                cmds.parentConstraint("Reverse_WP_locator", eye2mesh, mo = True)
                cmds.scale(-1, 1, 1)
                selection = "R_eye_dup_mesh"
                eye2mesh = selection
                cmds.delete(eye2mesh+"_parentConstraint1")
                cmds.makeIdentity(eye2mesh, a = True, t = True) 
            #if there's only one other mesh, then it just renames it directly 
            else:
                eye2mesh = selection
                cmds.rename(eye2mesh, "R_eye_dup_mesh")
                    
        else: #if x value is negative, it's the right
            cmds.rename(eye1mesh, "R_eye_dup_mesh")
            eye1mesh = "R_eye_dup_mesh"

            cmds.select(eye_mesh, r = True, hi = True)
            cmds.select(eye1mesh, d = True)
            cmds.select(eye_mesh, d = True)
            cmds.select("*Shape*", d = True)
            
            selection = cmds.ls(sl=True)
            print(selection)

            if len(selection) > 1:
                #cmds.delete(selection)
                cmds.duplicate(eye1mesh, n = "L_eye_dup_mesh")
                eye2mesh = "L_eye_dup_mesh"
                cmds.spaceLocator(a = True, n = "Reverse_WP_locator")
                cmds.parentConstraint("Reverse_WP_locator", eye2mesh, mo = True)
                cmds.scale(-1, 1, 1)  
                selection = "L_eye_dup_mesh"
                eye2mesh = selection
                cmds.delete(eye2mesh+"_parentConstraint1")
                cmds.makeIdentity(eye2mesh, a = True, t = True) 
                        
            else:
                eye2mesh = selection
                cmds.rename(eye2mesh, "L_eye_dup_mesh")
        
        #cleans up the odds and ends from this process
        cmds.xform("L_eye_dup_mesh", cp = True)
        cmds.xform("R_eye_dup_mesh", cp = True)       
        cmds.delete("Eye_WS_locator")
        if cmds.objExists("Reverse_WP_locator"):
            cmds.delete("Reverse_WP_locator")
        
    def create_eye_joints(self, dir):
        
        print ("%s is the direction" % dir)
        eye_center = cmds.objectCenter("%s_eye_dup_mesh" % dir, gl = True)
        cmds.select(clear = True)

        #create joints in center of mesh - 
        #L_eye_bnd_jnt
        #L_eye_aim_jnt
        #L_lid_upr_bnd_jnt
        #L_lid_lwr_bnd_jnt
        #L_lid_upr_crease_bnd_jnt

        cmds.joint(p = eye_center, name = "%s_eye_bnd_jnt" % dir)
        cmds.joint(p = eye_center, name = "%s_lid_upr_bnd_jnt" % dir)
        cmds.joint(p = eye_center, name = "%s_lid_lwr_bnd_jnt" % dir)
        cmds.joint(p = eye_center, name  = "%s_lid_upr_crease_bnd_jnt" % dir)
        cmds.joint(p = eye_center, name = "%s_lid_aim_jnt" % dir)
        
        cmds.select("%s_eye_bnd_jnt" % dir, "%s_lid_upr_bnd_jnt" % dir, "%s_lid_lwr_bnd_jnt" % dir, 
                    "%s_lid_upr_crease_bnd_jnt" % dir, "%s_lid_aim_jnt" % dir)
        
        eye_selection = cmds.ls(selection = True)
        print (eye_selection)
        
        
        if cmds.objExists("head_bnd_jnt"):
             
            for eye in eye_selection:
                  
                cmds.parent(eye, "head_bnd_jnt")

        else:
            cmds.confirmDialog(title= "No head joint", message= "No head_bnd_jnt exists. Eye joints will be orphans.", button=['Ok'], defaultButton='Yes' )
      
        for jnt in eye_selection:
            cmds.setAttr(jnt+".visibility", 0)
        cmds.delete("eye_mesh_dup")

    #create locators for upper, lower, and crease (4 each), groups them, positions them slightly away from the side they're generated on
    #These need to be placed by the user after generation, since every model is different and requires unique joint placement

    def create_eye_locators(self, dir, lidloc):

        eye_center = cmds.objectCenter("%s_eye_bnd_jnt" % dir, gl=True)
        locator_lid_spawn = eye_center
        if cmds.objExists("%s_lid_loc_grp" % dir):
            print ("nothing to see here")
        else:
            cmds.group(name = "%s_lid_loc_grp" % dir, em = True)
        cmds.parentConstraint("%s_eye_bnd_jnt" % dir, "%s_lid_loc_grp" % dir, mo = False)
        cmds.xform(cp=True)
        cmds.delete("%s_lid_loc_grp_parentConstraint1" % dir)

        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_lid_%s_loc_01" % (dir, lidloc))
        cmds.xform(cp = True)
        if lidloc == "upr":
            cmds.move(-1, 0, 10, r = True)
        elif lidloc == "upr_crease":      
            cmds.move(-1, 2, 10, r = True)
        else:
            cmds.move(-1, -2, 10, r = True)

            
        cmds.scale(.5, .5, .5)
        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_lid_%s_loc_02" % (dir, lidloc))
        cmds.xform(cp = True)
        if lidloc == "upr":
            cmds.move(0, 0, 10, r = True)
        elif lidloc == "upr_crease":      
            cmds.move(0, 2, 10, r = True)
        else:
            cmds.move(0, -2, 10, r = True)

        cmds.scale(.5, .5, .5)
        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_lid_%s_loc_03" % (dir, lidloc))
        cmds.xform(cp = True)

        if lidloc == "upr":
            cmds.move(1, 0, 10, r = True)
        elif lidloc == "upr_crease":      
            cmds.move(1, 2, 10, r = True)
        else:
            cmds.move(1, -2, 10, r = True)
        cmds.scale(.5, .5, .5)
        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_lid_%s_loc_04" % (dir, lidloc))
        cmds.xform(cp = True)

        if lidloc == "upr":
            cmds.move(2, 0, 10, r = True)
        elif lidloc == "upr_crease":      
            cmds.move(2, 2, 10, r = True)
        else:
            cmds.move(2, -2, 10, r = True)
        cmds.scale(.5, .5, .5)
        
        loc_grp = cmds.ls("*%s_loc*" % lidloc, et = "locator")
        print (loc_grp) 
        
        for loc in loc_grp:
            
            cmds.parent(loc, "%s_lid_loc_grp" % dir) 
        
    #make the inner, outer and blink locators 

    def create_misc_locators(self, dir):
        eye_center = cmds.objectCenter("%s_eye_bnd_jnt" % dir, gl=True)
        locator_lid_spawn = eye_center

        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_blink_loc" % (dir))
        cmds.xform(cp = True)
        cmds.move(2, 0, 13, r = True)
        cmds.scale(.5, .5, .5)
        
        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_inner_eye_corner_loc" % (dir))
        cmds.xform(cp = True)
        cmds.move(-2.5, 0 , 10, r = True)
        cmds.scale(.5, .5, .5)

        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_outer_eye_corner_loc" % (dir))
        cmds.xform(cp = True)
        cmds.move(3.5, 0 , 10, r = True)
        cmds.scale(.5, .5, .5)

        cmds.spaceLocator(p = locator_lid_spawn, name = "%s_squint_loc" % (dir))
        cmds.xform(cp = True)
        cmds.move(2, -3, 11, r = True)
        cmds.scale(.5, .5, .5)
        
        cmds.parent("%s_inner_eye_corner_loc" % (dir), "%s_lid_loc_grp" % dir) 
        cmds.parent("%s_outer_eye_corner_loc" % (dir), "%s_lid_loc_grp" % dir) 
        cmds.parent( "%s_squint_loc" % (dir), "%s_lid_loc_grp" % dir) 
        cmds.parent( "%s_blink_loc" % (dir), "%s_lid_loc_grp" % dir) 

        locOverride = str("%s_lid_loc_grp.overrideEnabled" % dir)
        locColor = str("%s_lid_loc_grp.overrideColor" % dir)
        cmds.setAttr(locOverride, 1)
        cmds.setAttr(locColor, 31)

    #planning on just mirroring joint setups, but will leave R_ independence in the UI in case there are asymmetrical models 

        if cmds.objExists("R_lid_loc_grp"):
            cmds.scaleX(-1, 1, 1, "R_lid_loc_grp")

    #creates all the exterior joints that actually get weight on them based on the location of the locators made previously 
    #can probably figure out a better way to get the selection at the beginning but hey it works 

    def create_joints(self, dir, lidloc):
        
        cmds.select("%s_lid_loc_grp" % dir, hi = True, r = True)
        cmds.select("%s_lid_loc_grp" % dir, d = True)
        cmds.select("*Shape", d = True)
        innerLoc = str("%s_inner_eye_corner_loc" % dir)
        outerLoc = str("%s_outer_eye_corner_loc" % dir)
        squintLoc = str("%s_squint_loc" % dir)
        blinkLoc = str("%s_blink_loc" % dir)

        miscLocs = (innerLoc, outerLoc, squintLoc, blinkLoc)

        cmds.select(miscLocs, d = True)
        
        if lidloc == "upr":
            cmds.select("*crease*", d = True)
            cmds.select("*lwr*", d = True)
        if lidloc == "upr_crease":
            cmds.select("*lid_upr_loc*", d = True)
            cmds.select("*lwr*", d = True)
        if lidloc == "lwr":
            cmds.select("*upr*", d = True)
            
        jointLocs = cmds.ls(selection = True)
        print (jointLocs)
        cmds.select(cl = True)
                 
        #goes through each locator in the lid_grp and creates & names joint
        for loc in jointLocs:
            joint_pos = cmds.objectCenter(loc, gl=True)
            number = loc.split("_")[-1]
            cmds.joint(position = joint_pos, name = "%s_lid_%s_" % (dir, lidloc) + number + "_bnd_jnt")
            lidJoint = cmds.ls(selection = True)
            
            cmds.parent(lidJoint, "%s_lid_%s_bnd_jnt" % (dir, lidloc), r = True)
            
            cmds.parentConstraint(loc, lidJoint, mo = False)
            cmds.pickWalk(lidJoint, direction = "down")
            deleteConstraint = cmds.ls(selection = True)
            cmds.delete(deleteConstraint)
        
        
        if cmds.objExists("%s_inner_eye_corner_bnd_jnt" % dir):
            print ("misc inner eye joint already created")
        else: 
            jointPos = cmds.objectCenter(innerLoc)
            cmds.joint(position = jointPos, name = "%s_inner_eye_corner_bnd_jnt" % dir)
            lidJoint = cmds.ls(selection = True)
            cmds.parent("%s_inner_eye_corner_bnd_jnt" % (dir), "head_bnd_jnt", r = True)
            cmds.select(cl = True) 

            cmds.parentConstraint(innerLoc, lidJoint, mo = False)
            cmds.pickWalk(lidJoint, direction = "down")
            deleteConstraint = cmds.ls(selection = True)
            cmds.delete(deleteConstraint)
            
        if cmds.objExists("%s_outer_eye_corner_bnd_jnt" % dir):
            print ("misc outer eye joint already created")
        else: 
            jointPos = cmds.objectCenter(outerLoc)
            cmds.joint(position = jointPos, name = "%s_outer_eye_corner_bnd_jnt" % (dir))
            lidJoint = cmds.ls(selection = True)
            cmds.parent("%s_outer_eye_corner_bnd_jnt" % (dir), "head_bnd_jnt", r = True)
            cmds.select(cl = True) 
            cmds.parentConstraint(outerLoc, lidJoint, mo = False)
            cmds.pickWalk(lidJoint, direction = "down")
            deleteConstraint = cmds.ls(selection = True)
            cmds.delete(deleteConstraint)
            
        if cmds.objExists("%s_squint_bnd_jnt" % dir):
            print ("misc squint joint already created")
        else: 
            jointPos = cmds.objectCenter(squintLoc)
            cmds.joint(position = jointPos, name = "%s_squint_bnd_jnt" % (dir))
            lidJoint = cmds.ls(selection = True)
            cmds.parent("%s_squint_bnd_jnt" % (dir), "head_bnd_jnt", r = True)
            cmds.select(cl = True) 

            cmds.parentConstraint(squintLoc, lidJoint, mo = False)
            cmds.pickWalk(lidJoint, direction = "down")
            deleteConstraint = cmds.ls(selection = True)
            cmds.delete(deleteConstraint)

        cmds.setAttr("%s_inner_eye_corner_bnd_jnt" % dir +".visibility", 0)
        cmds.setAttr("%s_outer_eye_corner_bnd_jnt" % dir +".visibility", 0)
        cmds.setAttr("%s_squint_bnd_jnt" % dir +".visibility", 0)
        
        #cmds.select("%s_lid_loc_grp" % dir)
        #removeLocs = cmds.ls(selection = True)
        #cmds.delete(removeLocs)


    #create joint controls with groups (R side + extra group and adjust pivot)
    #constrain joints to controls
    #create upper, crease, + lower lid controls
    #nest in groups with center pivot on eye_bnd_jnt
    def create_misc_controls(self, dir):
        
        miscLocs = pm.ls("%s_inner_eye_corner_loc" % dir, "%s_outer_eye_corner_loc" % dir, "%s_squint_loc" % dir)
        
        for loc in miscLocs:
            loc = str(f"{loc}")
            grp = loc.replace("_loc", "_grp")
            eyeControl = loc.replace("_loc", "_ctrl")
            eyeJoint = loc.replace("_loc", "_bnd_jnt")
            cmds.group(name = grp, empty = True, parent = "head_ctrl")
            
            if loc == "%s_squint_loc" % dir:
                cmds.curve(name = eyeControl, degree = 1,\
                                    knot = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],\
                                    point = [(2.365, -1.299, 1.022),\
                                             (2.567, -.881, 1.00101),\
                                             (2.365, -0.846, 1.00985),\
                                             (1.815, -1.158, 1.105),\
                                             (0.98, -1.595, 1.335),\
                                             (0, -1.783, 1.467),\
                                             (-0.98, -1.595, 1.335),\
                                             (-1.815, -1.158, 1.106),\
                                             (-2.365, -0.846, 1.00983),\
                                             (-2.567, -0.881, 1.00102),\
                                             (-2.365, -1.299, 1.0219),\
                                             (-1.815, -1.887, 1.128),\
                                             (-0.98, -2.373, 1.335),\
                                             (0, -2.567, 1.467),\
                                             (0.98, -2.373, 1.335),\
                                             (1.815, -1.887, 1.128),\
                                             (2.365, -1.299, 1.022),\
                                             (2.567, -0.881, 1.00101),\
                                             (2.365, -0.846, 1.00985)]\
                      )
                cmds.scale(.6, .4, 1)
                cmds.makeIdentity(eyeControl, apply = True, scale = True)
                
            else:
                
                cmds.curve(name = eyeControl, 
                        degree = 1,\
                        knot = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,\
                                21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,\
                                39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],\
                        point = [(0, 1, 0),\
                                 (0, 0.92388000000000003, 0.382683),\
                                 (0, 0.70710700000000004, 0.70710700000000004),\
                                 (0, 0.382683, 0.92388000000000003),\
                                 (0, 0, 1),\
                                 (0, -0.382683, 0.92388000000000003),\
                                 (0, -0.70710700000000004, 0.70710700000000004),\
                                 (0, -0.92388000000000003, 0.382683),\
                                 (0, -1, 0),\
                                 (0, -0.92388000000000003, -0.382683),\
                                 (0, -0.70710700000000004, -0.70710700000000004),\
                                 (0, -0.382683, -0.92388000000000003),\
                                 (0, 0, -1),\
                                 (0, 0.382683, -0.92388000000000003),\
                                 (0, 0.70710700000000004, -0.70710700000000004),\
                                 (0, 0.92388000000000003, -0.382683),\
                                 (0, 1, 0),\
                                 (0.382683, 0.92388000000000003, 0),\
                                 (0.70710700000000004, 0.70710700000000004, 0),\
                                 (0.92388000000000003, 0.382683, 0),\
                                 (1, 0, 0),\
                                 (0.92388000000000003, -0.382683, 0),\
                                 (0.70710700000000004, -0.70710700000000004, 0),\
                                 (0.382683, -0.92388000000000003, 0),\
                                 (0, -1, 0),\
                                 (-0.382683, -0.92388000000000003, 0),\
                                 (-0.70710700000000004, -0.70710700000000004, 0),\
                                 (-0.92388000000000003, -0.382683, 0),\
                                 (-1, 0, 0),\
                                 (-0.92388000000000003, 0.382683, 0),\
                                 (-0.70710700000000004, 0.70710700000000004, 0),\
                                 (-0.382683, 0.92388000000000003, 0),\
                                 (0, 1, 0),\
                                 (0, 0.92388000000000003, -0.382683),\
                                 (0, 0.70710700000000004, -0.70710700000000004),\
                                 (0, 0.382683, -0.92388000000000003),\
                                 (0, 0, -1),\
                                 (-0.382683, 0, -0.92388000000000003),\
                                 (-0.70710700000000004, 0, -0.70710700000000004),\
                                 (-0.92388000000000003, 0, -0.382683),\
                                 (-1, 0, 0),\
                                 (-0.92388000000000003, 0, 0.382683),\
                                 (-0.70710700000000004, 0, 0.70710700000000004),\
                                 (-0.382683, 0, 0.92388000000000003),\
                                 (0, 0, 1),\
                                 (0.382683, 0, 0.92388000000000003),\
                                 (0.70710700000000004, 0, 0.70710700000000004),\
                                 (0.92388000000000003, 0, 0.382683),\
                                 (1, 0, 0),\
                                 (0.92388000000000003, 0, -0.382683),\
                                 (0.70710700000000004, 0, -0.70710700000000004),\
                                 (0.382683, 0, -0.92388000000000003),\
                                 (0, 0, -1)]\
                      )
                cmds.scale(.3, .3, .3, eyeControl)
            cmds.parent(eyeControl, grp) 
            curveShape = cmds.select(cmds.listRelatives(eyeControl))
            cmds.rename(curveShape, eyeControl + "Shape")
            cmds.parentConstraint(eyeJoint, eyeControl, mo = False)
            eyeConstraint = eyeControl + "_parentConstraint1"
            print (eyeConstraint)
            cmds.delete(eyeConstraint) 
            cmds.xform(grp, cp = True)          

            cmds.makeIdentity(eyeControl, apply = True, translate = True, rotate = True, scale = True)
            cmds.delete(eyeControl, constructionHistory = True)
            #constrain the joint to the control
            cmds.parentConstraint(eyeControl, eyeJoint, mo = True)
            controlOverride = str(f"{eyeControl}.overrideEnabled")
            controlColor = str(f"{eyeControl}.overrideColor")
            cmds.setAttr(controlOverride, 1)
            if dir == "L":
                #make it blue!
                cmds.setAttr(controlColor, 6)
            else:   
                #make it red!
                cmds.setAttr(controlColor, 13)

    def create_controls(self, dir, lidloc):
        
        eye_center = cmds.objectCenter("%s_eye_bnd_jnt" % dir, gl=True)
        #select only the upper, upper_crease, or lower locators. Probably a simpler way to do this, but wanted to future proof in case I added more 
        #minor lid controls in the future
        cmds.select("%s_lid_loc_grp" % dir, hi = True, r = True)
        cmds.select("%s_lid_loc_grp" % dir, d = True)
        cmds.select("*Shape", d = True)
        if lidloc == "upr":
            cmds.select("*crease*", d = True)
            cmds.select("*lwr*", d = True)
        if lidloc == "upr_crease":
            cmds.select("*lid_upr_loc*", d = True)
            cmds.select("*lwr*", d = True)
        if lidloc == "lwr":
            cmds.select("*upr*", d = True)
        
        cmds.select("%s_inner_eye_corner_loc" % dir, d = True)
        cmds.select("%s_outer_eye_corner_loc" % dir, d = True)
        cmds.select("%s_squint_loc" % dir, d = True)    
        cmds.select("%s_blink_loc" % dir, d = True)    
        
            
        controlLocs = cmds.ls(selection = True)
        print (controlLocs)

        cmds.select(cl = True)
        cmds.group(name = "%s_lid_%s_follow_grp" % (dir, lidloc), empty = True, parent = "%s_eye_bnd_jnt" % dir)
        cmds.parent("%s_lid_%s_follow_grp" % (dir, lidloc), "head_ctrl")
        cmds.group(name = "%s_lid_%s_fleshy_grp" % (dir, lidloc), empty = True, parent = "%s_eye_bnd_jnt" % dir)
        cmds.parent("%s_lid_%s_fleshy_grp" % (dir, lidloc), "%s_lid_%s_follow_grp" % (dir, lidloc))
        
        
        if lidloc == "lwr":
            if cmds.objExists("%s_lid_%s_" % (dir, lidloc) + "blink_grp"):
                print ("nothing to see here")
            else:
                cmds.group(name = "%s_lid_%s_" % (dir, lidloc) + "blink_grp", empty = True, parent = "%s_lid_%s_fleshy_grp" % (dir, lidloc))
        
        for loc in controlLocs:
            
            joint_pos = cmds.objectCenter(loc, gl=True)
            number = loc.split("_")[-1]
            str(number)
            
            #set individual variables for each control and joint - not necessary, just cleaner
            eyeControl = "%s_lid_%s_" % (dir, lidloc) + number + "_ctrl"
            eyeJoint = "%s_lid_%s_" % (dir, lidloc) + number + "_bnd_jnt"
            str(eyeControl)
            str(eyeJoint)
         
            #create parent groups for the eye controls
            cmds.group(name = "%s_lid_%s_" % (dir, lidloc) + number + "_grp", empty = True, parent = "%s_lid_%s_fleshy_grp" % (dir, lidloc))
            cmds.group(name = "%s_lid_%s_" % (dir, lidloc) + number + "_offset_grp", empty = True, parent ="%s_lid_%s_" % (dir, lidloc) + number + "_grp")
            offsetGrp = "%s_lid_%s_" % (dir, lidloc) + number + "_offset_grp"
            offsetGrp = str(offsetGrp)
            if dir == "R":
                cmds.scale(-1, -1, -1, offsetGrp)
            
            #builds a spherical nurbs curve control that resembles a joint 
            cmds.curve(name = eyeControl, 
                    degree = 1,\
                    knot = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,\
                            21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,\
                            39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],\
                    point = [(0, 1, 0),\
                             (0, 0.92388000000000003, 0.382683),\
                             (0, 0.70710700000000004, 0.70710700000000004),\
                             (0, 0.382683, 0.92388000000000003),\
                             (0, 0, 1),\
                             (0, -0.382683, 0.92388000000000003),\
                             (0, -0.70710700000000004, 0.70710700000000004),\
                             (0, -0.92388000000000003, 0.382683),\
                             (0, -1, 0),\
                             (0, -0.92388000000000003, -0.382683),\
                             (0, -0.70710700000000004, -0.70710700000000004),\
                             (0, -0.382683, -0.92388000000000003),\
                             (0, 0, -1),\
                             (0, 0.382683, -0.92388000000000003),\
                             (0, 0.70710700000000004, -0.70710700000000004),\
                             (0, 0.92388000000000003, -0.382683),\
                             (0, 1, 0),\
                             (0.382683, 0.92388000000000003, 0),\
                             (0.70710700000000004, 0.70710700000000004, 0),\
                             (0.92388000000000003, 0.382683, 0),\
                             (1, 0, 0),\
                             (0.92388000000000003, -0.382683, 0),\
                             (0.70710700000000004, -0.70710700000000004, 0),\
                             (0.382683, -0.92388000000000003, 0),\
                             (0, -1, 0),\
                             (-0.382683, -0.92388000000000003, 0),\
                             (-0.70710700000000004, -0.70710700000000004, 0),\
                             (-0.92388000000000003, -0.382683, 0),\
                             (-1, 0, 0),\
                             (-0.92388000000000003, 0.382683, 0),\
                             (-0.70710700000000004, 0.70710700000000004, 0),\
                             (-0.382683, 0.92388000000000003, 0),\
                             (0, 1, 0),\
                             (0, 0.92388000000000003, -0.382683),\
                             (0, 0.70710700000000004, -0.70710700000000004),\
                             (0, 0.382683, -0.92388000000000003),\
                             (0, 0, -1),\
                             (-0.382683, 0, -0.92388000000000003),\
                             (-0.70710700000000004, 0, -0.70710700000000004),\
                             (-0.92388000000000003, 0, -0.382683),\
                             (-1, 0, 0),\
                             (-0.92388000000000003, 0, 0.382683),\
                             (-0.70710700000000004, 0, 0.70710700000000004),\
                             (-0.382683, 0, 0.92388000000000003),\
                             (0, 0, 1),\
                             (0.382683, 0, 0.92388000000000003),\
                             (0.70710700000000004, 0, 0.70710700000000004),\
                             (0.92388000000000003, 0, 0.382683),\
                             (1, 0, 0),\
                             (0.92388000000000003, 0, -0.382683),\
                             (0.70710700000000004, 0, -0.70710700000000004),\
                             (0.382683, 0, -0.92388000000000003),\
                             (0, 0, -1)]\
                  )
            curveShape = cmds.select(cmds.listRelatives(eyeControl))
            cmds.rename(curveShape, eyeControl + "Shape")
            
            #get control into the right place with 0,0,0 transformations 
            if lidloc == "lwr":
                cmds.delete("%s_lid_%s_" % (dir, lidloc) + number + "_offset_grp")
                cmds.parent(eyeControl, "%s_lid_%s_" % (dir, lidloc) + number + "_grp")
                cmds.parent("%s_lid_%s_" % (dir, lidloc) + number + "_grp", "%s_lid_%s_blink_grp" % (dir, lidloc))
                
            else:
                cmds.parent(eyeControl, "%s_lid_%s_" % (dir, lidloc) + number + "_offset_grp")
                
            cmds.scale(.2, .2, .2, eyeControl)
            cmds.parentConstraint(eyeJoint, eyeControl, mo = False)
            eyeConstraint = eyeControl + "_parentConstraint1"
            print (eyeConstraint)
            cmds.delete(eyeConstraint) 
            cmds.makeIdentity(eyeControl, apply = True, translate = True, rotate = True, scale = True) 
            #set color
            #overrides display and sets color in reference to maya index
            #inner and outer eye corners are blue or red, the other minor lid controls are yellow. 
            
            controlOverride = str(f"{eyeControl}.overrideEnabled")
            controlColor = str(f"{eyeControl}.overrideColor")
            cmds.setAttr(controlOverride, 1)
            cmds.setAttr(controlColor, 17)
            cmds.delete(eyeControl, constructionHistory = True)
            #constrain the joint to the control
            cmds.parentConstraint(eyeControl, eyeJoint, mo = True)
            
        creaseGrp = "%s_lid_upr_crease_fleshy_grp" % dir
        str(creaseGrp)

        if lidloc == "upr_crease":
            cmds.select(creaseGrp)
            cmds.group(name = "%s_lid_%s_follow_detail_grp" % (dir, lidloc))

    #make eye blink controls 
    #could be simplified into more for loops but since we only need these 3 controls twice I put it in by hand
    #didn't feel worth all the extra variables at the moment

    def blink_controls(self, dir):
        if cmds.objExists("%s_eye_upr_blink_grp" % dir):
            print("nothing to see here")
        else:
            cmds.group(name = "%s_eye_upr_blink_grp" % dir, empty = True, parent = "head_ctrl")

        if cmds.objExists("%s_eye_lwr_blink_grp" % dir):
            print("nothing to see here")
        else:
            cmds.group(name = "%s_eye_lwr_blink_grp" % dir, empty = True, parent = "head_ctrl")
        
        points = [
            (0, 0, 0),  # Point 1
            (.8, 0, 0),  # Point 2
            (.4, .6, 0),  # Point 3
            (0, 0, 0)   # Close the curve
        ]
        cmds.curve(degree=1, point=points, name="%s_eye_upr_blink_ctrl" % dir)
        cmds.xform(cp=True)
        cmds.move(0, 3, 0)
        cmds.scale(1.5, 1.5, 1)
        
        #cmds.makeIdentity("%s_eye_upr_blink_ctrl" % dir, apply = True, translate = True, scale = True)
        curveShape = cmds.select(cmds.listRelatives("%s_eye_upr_blink_ctrl" % dir))
        cmds.rename(curveShape, "%s_eye_upr_blink_ctrlShape" % dir)
        cmds.makeIdentity("%s_eye_upr_blink_ctrl" % dir, apply = True, translate = True, scale = True) 
        cmds.delete("%s_eye_upr_blink_ctrl" % dir, constructionHistory = True)
        
        cmds.parentConstraint("%s_blink_loc" % dir, "%s_eye_upr_blink_ctrl" % dir, mo = False)   
        cmds.parent("%s_eye_upr_blink_ctrl" % dir, "%s_eye_upr_blink_grp" % dir)
        
        points = [
            (0, 0, 0),  # Point 1
            (.3, 0, 0),  # Point 2
            (.15, .2, 0),  # Point 3
            (0, 0, 0)   # Close the curve
        ]
        cmds.curve(degree=1, point=points, name="%s_eye_upr_detail_ctrl" % dir)
        cmds.xform(cp=True)
        cmds.scale(1.5, 1.5, 1)
        cmds.move(0, -0.5, 0)
        curveShape = cmds.select(cmds.listRelatives("%s_eye_upr_detail_ctrl" % dir))
        cmds.rename(curveShape, "%s_eye_upr_detail_ctrlShape" % dir)
        cmds.move(.25, .3, 0)
        cmds.makeIdentity("%s_eye_upr_detail_ctrl" % dir, apply = True, translate = True, scale = True) 
        cmds.delete("%s_eye_upr_detail_ctrl" % dir, constructionHistory = True)
        cmds.group(name = "%s_eye_upr_detail_grp" % dir, parent = "%s_eye_upr_blink_ctrl" % dir, relative = True)
        cmds.parentConstraint("%s_blink_loc" % dir, "%s_eye_upr_detail_ctrl" % dir, mo = False)
       
        points = [
            (0, -.1, 0),  # Point 1
            (.8, -.1, 0),  # Point 2
            (.4, -.7, 0),  # Point 3
            (0, -.1, 0)   # Close the curve
        ]
        cmds.curve(degree=1, point=points, name="%s_eye_lwr_blink_ctrl" % dir)
        cmds.xform(cp=True)
        cmds.scale(1.5, 1.5, 1)
        cmds.makeIdentity("%s_eye_lwr_blink_ctrl" % dir, apply = True, scale = True)
        curveShape = cmds.select(cmds.listRelatives("%s_eye_lwr_blink_ctrl" % dir))
        cmds.rename(curveShape, "%s_eye_lwr_blink_ctrlShape" % dir)
        cmds.makeIdentity("%s_eye_lwr_blink_ctrl" % dir, apply = True, translate = True) 
        cmds.delete("%s_eye_lwr_blink_ctrl" % dir, constructionHistory = True)
        cmds.parentConstraint("%s_blink_loc" % dir, "%s_eye_lwr_blink_ctrl" % dir, mo = False)

        cmds.parent("%s_eye_lwr_blink_ctrl" % dir, "%s_eye_lwr_blink_grp" % dir)

        eyeConstraints = ["%s_eye_upr_blink_ctrl" % dir + "_parentConstraint1", "%s_eye_upr_detail_ctrl" % dir + "_parentConstraint1", "%s_eye_lwr_blink_ctrl" % dir + "_parentConstraint1"]
        cmds.delete(eyeConstraints) 
        
        cmds.move(0, .5, 0, "%s_eye_upr_blink_grp" % dir,  r = True)
        cmds.move(0, -.5, 0, "%s_eye_lwr_blink_grp" % dir, r = True)

        blinkControls = pm.ls("%s_eye_lwr_blink_ctrl" % dir, "%s_eye_upr_blink_ctrl" % dir, "%s_eye_upr_detail_ctrl" % dir)
        
        for control in blinkControls:
            controlOverride = str(f"{control}.overrideEnabled")
            controlColor = str(f"{control}.overrideColor")
        
            cmds.setAttr(controlOverride, 1)
            if dir == "L":
                #make it blue!
                cmds.setAttr(controlColor, 6)
            else: 
                #make it red!
                cmds.setAttr(controlColor, 13)
                        
        for control in blinkControls:
            controlTransform = str(f"{control}")
            cmds.makeIdentity(controlTransform, apply=True, t=1, r=1, s=1, n=0) 

            cmds.setAttr(controlTransform + ".translateX", lock = True)
            cmds.setAttr(controlTransform + ".translateZ", lock = True)
            
                
    #blink_controls("L")
    #set lower lid driven keys - this goes on a shared group, so straightforward 3 keys

    def set_lwr_driven_keys(self, dir):
        
        blinkDriven = "%s_lid_lwr_blink_grp.rx" % dir
        blinkDriver = "%s_eye_lwr_blink_ctrl.ty" % dir
        cmds.setDrivenKeyframe(blinkDriven, cd=blinkDriver)
        cmds.setDrivenKeyframe(blinkDriven, cd=blinkDriver)
        cmds.setAttr(blinkDriver, -.5)
        cmds.setAttr(blinkDriven, 15)
        cmds.setDrivenKeyframe(blinkDriven, cd=blinkDriver)
        cmds.setAttr(blinkDriver, .5)
        cmds.setAttr(blinkDriven, -15)
        cmds.setDrivenKeyframe(blinkDriven, cd=blinkDriver)
        cmds.setAttr(blinkDriver, 0)
        cmds.setAttr(blinkDriven, 0)

    #set upper driven keys - this is more complicated bc every control needs a different rotation value
    #for future versions, allow these values to be adjusted manually 
    def set_upr_driven_keys(self, dir):

        #for the super open every value is the same so setting that and the 0 value below
        #this can probably be optimized
        blinkDriver = "%s_eye_upr_blink_ctrl.ty" % dir
        
        blinkDriven01 = "%s_lid_upr_01_offset_grp" % dir
        blinkDriven02 = "%s_lid_upr_02_offset_grp" % dir
        blinkDriven03 = "%s_lid_upr_03_offset_grp" % dir
        blinkDriven04 = "%s_lid_upr_04_offset_grp" % dir
        
        str(blinkDriver)
        str(blinkDriven01+".rx")
        str(blinkDriven02+".rx")
        str(blinkDriven03+".rx")
        str(blinkDriven04+".rx")

        drivens = cmds.ls(blinkDriven01, blinkDriven02, blinkDriven03, blinkDriven04)

        #now the uppers
        cmds.setAttr(blinkDriver, -.5)

        cmds.rotate(40, blinkDriven01, x = True)
        cmds.setDrivenKeyframe(blinkDriven01, cd=blinkDriver)
        cmds.rotate(42, blinkDriven02, x = True)
        cmds.setDrivenKeyframe(blinkDriven02, cd=blinkDriver)
        cmds.rotate(43, blinkDriven03, x = True)
        cmds.setDrivenKeyframe(blinkDriven03, cd=blinkDriver)
        cmds.rotate(36, blinkDriven04, x = True)
        cmds.setDrivenKeyframe(blinkDriven04, cd=blinkDriver)

        cmds.setAttr(blinkDriver, 0)
        cmds.rotate(0, blinkDriven01, x = True)
        cmds.setDrivenKeyframe(blinkDriven01, cd=blinkDriver)
        cmds.rotate(0, blinkDriven02, x = True)
        cmds.setDrivenKeyframe(blinkDriven02, cd=blinkDriver)
        cmds.rotate(0, blinkDriven03, x = True)
        cmds.setDrivenKeyframe(blinkDriven03, cd=blinkDriver)
        cmds.rotate(0, blinkDriven04, x = True)
        cmds.setDrivenKeyframe(blinkDriven04, cd=blinkDriver)

        cmds.setAttr(blinkDriver, .5)
        for driven in drivens:
            cmds.rotate(-15, driven, x = True)
            #cmds.setAttr(blinkDriver, 0)
            cmds.setDrivenKeyframe(driven, cd=blinkDriver)
            cmds.rotate(0, driven, x = True)

        cmds.setAttr(blinkDriver, 0)
            
    def set_crease_driven_keys(self, dir):
        
        #crease controls have no min/max, so setting one direct connection works fine for the direct control
        blinkDriven = "%s_lid_upr_crease_follow_detail_grp.ty" % dir
        blinkDriver = "%s_eye_upr_detail_ctrl.ty" % dir
        
        #CBdeleteConnection doesn't exist in python, so pulling a mel eval for it. 
        if cmds.getAttr(blinkDriven, lock = True):
            mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\""%blinkDriven)

        cmds.setAttr("L_lid_upr_crease_follow_detail_grp.ty", lock = False)
        cmds.setAttr(blinkDriver, lock = False)

        cmds.connectAttr(blinkDriver, blinkDriven, force = True)
        
        #for a more nuanced default blink we also need to set some set driven keys 
        drivens = "%s_lid_upr_crease_01_offset_grp" % dir, "%s_lid_upr_crease_02_offset_grp" % dir, "%s_lid_upr_crease_03_offset_grp" % dir, "%s_lid_upr_crease_04_offset_grp" % dir
        driver = "%s_eye_upr_blink_ctrl" % dir

        for driven in drivens:
            drivenRX = driven + ".rx"
            #drivenRZ = driven + ".rz"
            #driverTX = driver + ".tx"
            driverTY = driver + ".ty"

            #set driver attr at 0 just in case
            #cmds.setAttr(driverTX, 0)
            cmds.setAttr(driverTY, 0)

            cmds.setDrivenKeyframe(drivenRX, cd = driverTY)
            cmds.setAttr(driverTY, -.5)
            cmds.setAttr(drivenRX, 4)
            cmds.setDrivenKeyframe(drivenRX, cd = driverTY)
            cmds.setAttr(driverTY, .5)
            cmds.setAttr(drivenRX, -15)
            cmds.setDrivenKeyframe(drivenRX, cd = driverTY)

            cmds.setAttr(driverTY, 0)
            cmds.setAttr(drivenRX, 0)



