# eyelidAutorigger
Python tool for Maya 2025+ that creates joint based eyelid rig 

Instructions: 
Place all 3 files in your maya/prefs/scripts folder and run the loadAutorigger script once you open Maya. 

You will need a mesh with a single eyeball mesh to run this successfully - if your mesh has integrated eyeballs, 
I suggest duplicating and separating the meshes until you have a body mesh and an eyeball mesh. These do not need to be the 
meshes you use to skin the rig later. 

The autorigger will take care of splitting the eyeball mesh between L and R and finding center. Your only hand work will be placing the 
locators to the positions you want and skinning the mesh to the joints after creating the rig. 
