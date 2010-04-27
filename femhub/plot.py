# Plot solution for mesh editor on the online lab
def plotsln(mesh, sln, colorbar=False, view=(0,0), filename="a.png"):
    x = [n[0] for n in mesh.nodes]
    y = [n[1] for n in mesh.nodes]
    z = [0]*len(y)
    from enthought.mayavi import mlab
    mlab.options.offscreen = True
    #mlab.options.show_scalar_bar = False
    mlab.triangular_mesh(x, y, z, mesh.elems, scalars=sln)
    engine = mlab.get_engine()
    image = engine.current_scene
    image.scene.background = (1.0, 1.0, 1.0)
    image.scene.foreground = (0.0, 0.0, 0.0)
    if colorbar:
        mlab.colorbar(orientation="vertical")
    if view:
        mlab.view(view[0], view[1])
    mlab.savefig(filename)
