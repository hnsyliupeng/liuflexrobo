# ASSET_MANIFEST

## CHAR_001_LITTLE_ROBOT (collection CHAR_001_robot, 42 objects)
head (sphere, panel seam, hatch) · eye rim L/R · emissive lens L/R · iris core L/R ·
antenna (curve, bent drooped tip) · torso + front panel + rivets + vents + neck ·
shoulder/upperarm/elbow-forearm/wrist-hand L/R · separate right index finger ·
chassis · fender L/R · track curve L/R (closed bezier) · tread plate strip L/R
(array fit-curve + curve deform, driver-scrolled) · 5 wheels/side (driver-rolled) ·
ctrl empty (EYE_BRIGHTNESS / TRACK_PHASE / GAZE_X / GAZE_Y / FLAP-like props) ·
armature CHAR_001_rig (17 bones per §25).
Materials: M_Robot_Paint (pointiness edge chips + rust blotches z-masked + mud + scratch bump),
M_Robot_Metal, M_Track (muddy), M_Robot_Eye (radial-gradient emission, driver gain), M_Robot_EyeRim.

## ENV_001 forest (assets + scene)
Families: TREE_TRUNK_A/B/C (lobed root buttress, dual displace bark), ROOT_A/B/C,
FALLEN_LOG_HERO (7.5 m, moss patches), FERN_A/B/C (arched rachis + paired pinnae),
MOSS_PATCH_A/B (displaced dome grid), GROUND_LEAF_A/B/C (curved wet leaf cards),
TWIG_A/B (curve bevel), ROCK_SMALL (noise-displaced), BACKGROUND_TREE (straight column).
Scene: ENV_ground 96×96 displaced mud plane; hero tree + 6 roots + root moss; fallen log west;
6 mid trees; 26-tree background ring; 70 ferns; 520 leaf litter; 26 twigs; 16 rocks;
14 ground moss; ENV_mist scatter volume. ≈700 objects, all linked-duplicate instances.
Materials: M_Bark_Wet, M_Bark_BG, M_DarkWood, M_Moss, M_WetLeaves (wet sheen), M_Mud (wet reflective),
M_Fern (translucent backlit), M_Stone, M_Mist.

## FX fireflies
FX_001 hero: abdomen (M_Firefly_Glow, driver GLOW) + thorax/head (M_Firefly_Body) +
2 wings (M_Firefly_Wing, flap driver) on FX_001_ctrl.
FX_010 swarm: GN_FireflySwarm — 900 points, layered random volumes (60 % clustered near
root/tree zone), ff_phase attribute, instance dot (M_Swarm_Dot: reveal gate by frame driver
613–708 + per-point sine flicker), scene-time sine drift offset.
