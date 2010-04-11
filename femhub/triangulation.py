from numpy import exp, sqrt, array
from pylab import plot, savefig, grid, legend, clf, pcolor, spy, axis

class TriangulationError(Exception):
    pass

# Check whether a given point c lies on the left of
# the edge (a,b)
def is_on_the_left(c, a, b, pts_list):
   ax, ay = pts_list[a]
   bx, by = pts_list[b]
   cx, cy = pts_list[c]
   ux = float(bx - ax)
   uy = float(by - ay)
   vx = float(cx - ax)
   vy = float(cy - ay)
   return (ux*vy - uy*vx > 0)

# Angle criterion (to be minimized)
def criterion(a, b, c, pts_list):
   ax, ay = pts_list[a]
   bx, by = pts_list[b]
   cx, cy = pts_list[c]
   ux = float(ax - cx)
   uy = float(ay - cy)
   vx = float(bx - cx)
   vy = float(by - cy)
   len_u = sqrt(ux*ux + uy*uy)
   len_v = sqrt(vx*vx + vy*vy)
   return (ux*vx + uy*vy)/(len_u*len_v)

# Take a boundary edge (a,b), and in the list of points
# find a point 'c' that lies on the left of ab and maximizes
# the angle acb
def find_third_point(a, b, pts_list):
   found = 0
   minimum = exp(100)   #this is dirty
   c_index = -1
   pt_index = -1
   for c_point in pts_list:
       c_index += 1
       if c_index != a and c_index != b and is_on_the_left(c_index, a, b, pts_list):
           crit = criterion(a, b, c_index, pts_list)
           if crit < minimum:
               minimum = crit
               pt_index = c_index
               found = 1
   if found == 0:
       raise TriangulationError("ERROR: Optimal point not found in find_third_point().")
   return pt_index

# If the point 'c' belong to a boundary edge, return False,
# otherwise return True
def lies_inside(c, bdy_edges):
   for edge in bdy_edges:
       a,b = edge
       if c == a or c == b: return False
   return True

# Checks whether edge (a, b) is in the list of boundary edges
def is_boundary_edge(a, b, bdy_edges):
   for edge in bdy_edges:
       a0, b0 = edge
       if a == a0 and b == b0: return True
   return False

# Create a triangulation using the advancing front method
def triangulate_af(pts_list, bdy_edges):
   # create empty list of elements
   elems = []
   bdy_edges = bdy_edges[:]
   # main loop
   while bdy_edges != []:
       # take the last item from the list of bdy edges (and remove it)
       a,b = bdy_edges.pop()
       c = find_third_point(a, b, pts_list)
       elems.append((a,b,c))
       if is_boundary_edge(c, a, bdy_edges): bdy_edges.remove((c,a))
       else: bdy_edges.append((a,c))
       if is_boundary_edge(b, c, bdy_edges): bdy_edges.remove((b,c))
       else: bdy_edges.append((c,b))
   return elems

# Plot triangular mesh
def plot_tria_mesh(pts_list, tria_mesh):
   clf()
   label=""
   for elem in tria_mesh:
       a,b,c = elem
       ax,ay = pts_list[a]
       bx,by = pts_list[b]
       cx,cy = pts_list[c]
       x_array = array([ax,bx,cx,ax])
       y_array = array([ay,by,cy,ay])
       plot(x_array, y_array, "g-")
   savefig("a.png")

def sort_edges(edges):
    n = []
    edges = edges[:]
    while edges != []:
        if n == []:
            e = edges[0]
            n.append(e)
            del edges[0]
        else:
            last_i = n[-1][1]
            ok = False
            for i, e in enumerate(edges):
                if e[0] == last_i:
                    n.append(e)
                    del edges[i]
                    ok = True
                    break
                elif e[1] == last_i:
                    n.append((e[1], e[0]))
                    del edges[i]
                    ok = True
                    break
            if not ok:
                raise Exception("Missing some boundary edge")
    return n

def convert_graph(vertices, edges):
    pts_list = []
    _edges = []
    for i in range(len(vertices)):
        pts_list.append(vertices[i])
        for n in edges[i]:
            if n > i:
                _edges.append((i, n))
    _max = -1;
    for v in pts_list:
        if v[0] > _max:
            _max = v[0]
        if v[1] > _max:
            _max = v[1]
    _max = float(_max)
    pts_list = [[v[0]/_max, 1.0-v[1]/_max] for v in pts_list]
    return pts_list, _edges

def doit(edges, vertices):
    pts_list, bdy_edges = convert_graph(edges, vertices)
    print pts_list
    print bdy_edges
    boundary = [b+(1,) for b in bdy_edges]
    #print pts_list
    #print bdy_edges
    #print boundary
    # Example (unit square diagonally split into 4 triangles)
    #pts_list = [(0,0), (1,0), (0,1), (1,1), (0.5,0.5)]
    #print "List of points:", pts_list
    #bdy_edges = [(0,1), (1,3), (3,2), (2,0)]
    #print "List of boundary edges:", bdy_edges
    elems = triangulate_af(pts_list, bdy_edges)
    #print "List of elements:", elems
    #plot_tria_mesh(pts_list, elems)

    # Hermes2D: Example 03 (poisson)
    # This example shows how to solve a first simple PDE.
    #    - create the mesh
    #    - perform initial refinements
    #    - create a H1 space over the mesh
    #    - define weak formulation
    #    - initialize matrix solver
    #    - assemble and solve the matrix system
    #    - visualize the solution
    #
    # PDE: Poisson equation -Laplace u = CONST_F with homogeneous (zero)
    #      Dirichlet boundary conditions.

    from hermes2d import Mesh, MeshView, H1Shapeset, PrecalcShapeset, H1Space, \
           WeakForm, Solution, ScalarView, LinSystem, DummySolver
    from hermes2d.forms import set_forms
    from hermes2d.examples.c03 import set_bc

    mesh = Mesh()

    # Creates a mesh from a list of nodes, elements, boundary and nurbs.
    mesh.create(pts_list, elems, boundary, [])

    #mesh.refine_element(0)
    shapeset = H1Shapeset()
    pss = PrecalcShapeset(shapeset)

    # Create an H1 space
    space = H1Space(mesh, shapeset)
    space.set_uniform_order(5)
    set_bc(space)
    space.assign_dofs()

    # Initialize the discrete problem
    wf = WeakForm(1)
    set_forms(wf)

    solver = DummySolver()
    sys = LinSystem(wf, solver)
    sys.set_spaces(space)
    sys.set_pss(pss)

    # Assemble the stiffness matrix and solve the system
    sys.assemble()
    A = sys.get_matrix()
    b = sys.get_rhs()
    from scipy.sparse.linalg import cg
    x, res = cg(A, b)
    sln = Solution()
    sln.set_fe_solution(space, pss, x)

    # Display the Solution
    view = ScalarView("Solution")
    view.show(sln, lib="mayavi", filename="a.png", notebook=True)

    # Display the Mesh
    mview = MeshView()
    mview.show(mesh, lib="mpl", method="orders", filename="b.png", notebook=True)
    from enthought.mayavi import mlab
    mlab.clf()

    # Positioning the images
    print """<html><table border=1><tr><td><span style="position: relative; top: 33px;"><img src="cell://a.png" width="320" height="280"></span></td><td><img src="cell://b.png" width="540" height="405"></td></tr></table></html>"""

def show_graph_editor(vertices, edges):
    a = """
    <html><font color='black'><div id="graph_editor_2"><table><tbody><tr><td><iframe
    style="width: 800px; height: 400px; border: 0;" id="iframe_graph_editor_2"
    src="/javascript/graph_editor/graph_editor.html?cell_id=2"></iframe><input
    type="hidden" id="graph_data_2" value="num_vertices=%(num_vertices)s;edges=%(edges)s;pos=%(vertices)s;"><input
    type="hidden" id="graph_name_2" value=""></td></tr><tr><td><button onclick="
        var f, g, saved_input;
        g = $('#iframe_graph_editor_2')[0].contentWindow.update_sage();

        f = 'vertices, edges = convert_graph(' + g[1] + ', ' + g[0] + ')\\n';
        f += 'show_graph_editor(vertices, edges)';
        $('#cell_input_%(cell_id)s').val(f);
        cell_input_resize(%(cell_id)s);
        evaluate_cell(%(cell_id)s, false);
    ">Save</button><button onclick="cell_delete_output(%(cell_id)s);">Close</button></td></tr></tbody></table></
    div></font></html>
    """ % {"vertices": vertices, "edges": edges, "num_vertices": len(vertices),
            "cell_id": 2}
    print a
