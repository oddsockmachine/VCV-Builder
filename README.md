# VCV Builder

## What?

_Taking "modular" one step further_
Building big VCV Racks out of smaller VCV Racks

## Why?

Have you ever found yourself:

- Wanting to start a patch from a template?
- Using standardized blocks of modules for particular functions?
- Tired of repeatedly patching the same input/output modules each time?

I have!

## How?

A little bit of hacky Python, which is gradually growing into a larger VCV-focused library.

#### Create one or more "export Blocks" in VCV patch files
- Each Block starts with a text box (SubmarineFree's TD-202)
- The Block is identified by the text which states "EXPORT: {Block name}
- Blocks includes all modules which are to the right and contiguous with the text box

[[screenshot1.png]]

#### Pass in a list of files to the Builder

- By default, all valid Blocks are imported from each file
- eg: `vcv_build.py example1.vcv example2.vcv`
- You can also specify Blocks by name from each file
- eg: `vcv_build.py example1.vcv.myblock.anotherblock example2.vcv`

#### Create a new VCV patch file

- A new `.vcv` file is generated, containing each of the Blocks requested
- Each Block is placed into the new patch on a new row of the rack

[[TODO_example.png]]

#### Don't forget your cables

- Any cables that exist within a Block are automatically imported
- This means your Block can come pre-wired
- Cables that enter/leave the Block from elsewhere are not included

[[TODO_example.png]]


## Tips

#### Blocks can be defined within normally functioning patches
There's no need to make these standalone. Simply label useful Blocks within your existing patches.
Then, you can easily pull in fragments of working patches to start your new patch.
Just leave a small gap where you want the Block to end to avoid importing extraneous modules.

[[TODO_example.png]]

#### External cables are ignored, but you can add a buffer module to your Block for convenient ins/outs when patching

[[TODO_example.png]]


## Coming next...

- Auto-routing between Blocks
- Packing Blocks on the rack to make better use of the screen, not just vertically stacked