import sys

class Domain:
    """
    Represents a FE domain.

    Currently the domain is 2D and is defined by a set of nodes and (boundary)
    edges. It can be made more general in the future.

    The edges are always sorted.
    """

    @classmethod
    def from_graph_editor(cls, vertices, edges):
        import triangulation
        vertices, edges = triangulation.convert_graph(vertices, edges)
        edges = triangulation.sort_edges(edges)
        return Domain(vertices, edges)

    def __init__(self, nodes=[], edges=[]):
        self._nodes = nodes
        self._edges = edges

        import sagenb.notebook.interact
        self._cell_id_init = sagenb.notebook.interact.SAGE_CELL_ID

    def __str__(self):
        return """Domain:
    nodes:
        %s
    boundary edges:
        %s""" % (self._nodes, self._edges)

    def get_html(self, self_name="d", editor="js"):
        import sagenb.notebook.interact
        self._cell_id_edit = sagenb.notebook.interact.SAGE_CELL_ID
        if editor != "js":
            raise Exception("Editor is not implemented.")

        if editor == "js":
            path = "/javascript/graph_editor"
            edges = [[a, b] for a, b in self._edges]
            nodes = [[a, b] for a, b in self._nodes]
            return """\
<html><font color='black'><div
id="graph_editor_%(cell_id)s"><table><tbody><tr><td><iframe style="width: 800px;
 height: 400px; border: 0;" id="iframe_graph_editor_%(cell_id)s"
src="%(path)s/graph_editor.html?cell_id=%(cell_id)s"></iframe><input
type="hidden" id="graph_data_%(cell_id)s"
value="num_vertices=%(nodes_len)s;edges=%(edges)s;pos=%(nodes)s;"><input
type="hidden" id="graph_name_%(cell_id)s"
value="%(var_name)s"></td></tr><tr><td><button onclick="
    var f, g, saved_input;
    g = $('#iframe_graph_editor_%(cell_id)s')[0].contentWindow.update_sage();
    if (g[2] === '') {
        alert('You need to give a Sage variable name to the graph, before saving it.');
        return;
    }

    // This is how to comment out the previous contents of the cell:
    //f = '#' + $('#cell_input_%(cell_id_save)s').val() + '\\n';

    f = '# Automatically generated:\\n';
    f += g[2] + ' = Domain.from_graph_editor(' + g[1] + ', ' + g[0] + ')';
    $('#cell_input_%(cell_id_save)s').val(f);
    cell_input_resize(%(cell_id_save)s);
    evaluate_cell(%(cell_id_save)s, false);
">Save</button><button
onclick="cell_delete_output(%(cell_id)s);">Close</button></td></tr></tbody></table></div></font></html>""" % {"path": path,
                "cell_id_save": self._cell_id_init,
                "cell_id": self._cell_id_edit,
                "nodes": nodes,
                "nodes_len": len(self._nodes),
                "edges": edges,
                "var_name": self_name}

    def edit(self, editor="js"):
        self_name = "d"
        locs = sys._getframe(1).f_locals
        for var in locs:
            if id(locs[var]) == id(self):
                self_name = var
        print self.get_html(self_name=self_name, editor=editor)

    def normalize(self):
        pts_list = self._nodes
        _max = -1;
        for v in pts_list:
            if v[0] > _max:
                _max = v[0]
            if v[1] > _max:
                _max = v[1]
        _max = float(_max)
        pts_list = [[v[0]/_max, 1.0-v[1]/_max] for v in pts_list]
        self._nodes = pts_list

    def triangulate(self):
        import triangulation
        print "Triangulating..."
        print "List of points:", self._nodes
        print "List of boundary edges:", self._edges
        elems = triangulation.triangulate_af(self._nodes, self._edges)
        boundaries = [list(b)+[1] for b in self._edges]
        return Mesh(self._nodes, elems, boundaries)

class Mesh:
    """
    Represents a FE mesh.

    Currently the mesh is 2D and is defined by a set of nodes and elements.
    Element is either a set of 3 nodes (triangle) or 4 nodes (quad).
    It can be made more general in the future.

    It contains methods to export this mesh in the hermes2d (and other)
    formats.
    """

    def __init__(self, nodes=[], elements=[], boundaries=[], curves=[]):
        self._nodes = nodes
        self._elements = elements
        self._boundaries = boundaries
        self._curves = curves

        import sagenb.notebook.interact
        self._cell_id = sagenb.notebook.interact.SAGE_CELL_ID

    def __str__(self):
        return """Mesh:
    nodes:
        %s
    elements:
        %s
    boundaries:
        %s
    curves:
        %s""" % (self._nodes, self._elements, self._boundaries, self._curves)

    def plot(self):
        import triangulation
        triangulation.plot_tria_mesh(self._nodes, self._elements)

    def convert_nodes(self, a):
        s = ""
        for n2 in a:
            s += "%s %s," % tuple(n2)
        return s

    def convert_elements(self, a):
        s = ""
        for e in a:
            if len(e) == 4:
                s += "%s %s %s %s," % tuple(e)
            elif len(e) == 5:
                s += "%s %s %s %s %s," % tuple(e)
        return s

    def convert_boundaries(self, a):
        s = ""
        for b in a:
            s += ("%s %s %s,") % tuple(b)
        return s

    def convert_curves(self, a):
        s = ""
        for c in a:
            s += ("%s %s %s,") % tuple(c)
        return s

    def get_html(self, self_name="d", editor="flex"):
        import sagenb.notebook.interact
        self._cell_id_edit = sagenb.notebook.interact.SAGE_CELL_ID

        if editor == "flex":
            path = "/javascript/mesh_editor"
            return """\
<html>
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
            width="830" height="600">
    <param name="movie" value="%(path)s/MeshEditor.swf">
    <param name="flashvars" value="output_cell=%(cn)s&nodes=%(nodes)s&elements=%(elements)s&boundaries=%(boundaries)s&curves=%(curves)s&var_name=%(var_name)s" />
    <!--[if !IE]>-->
        <object type="application/x-shockwave-flash"
            data="%(path)s/MeshEditor.swf" width="830" height="600">
    <!--<![endif]-->
    <param name="flashvars" value="output_cell=%(cn)s&nodes=%(nodes)s&elements=%(elements)s& boundaries=%(boundaries)s&curves=%(curves)s&var_name=%(var_name)s" />
    <p>Alternative Content</p>
    <!--[if !IE]>-->
        </object>
    <!--<![endif]-->
</object>
</html>""" % {"path": path, "cn": self._cell_id,
                "nodes": self.convert_nodes(self._nodes),
                "elements": self.convert_elements(self._elements),
                "boundaries": self.convert_boundaries(self._boundaries),
                "curves": self.convert_curves(self._curves),
                "var_name": self_name}
        else:
            path = "/javascript/graph_editor"
            edges = [[a, b] for a, b in self._edges]
            # in case we needed to flip this upside down:
            #nodes = [[v[0], 1.0-v[1]] for v in self._nodes]
            nodes = self._nodes
            return """\
<html><font color='black'><div
id="graph_editor_%(cell_id)s"><table><tbody><tr><td><iframe style="width: 800px;
 height: 400px; border: 0;" id="iframe_graph_editor_%(cell_id)s"
src="%(path)s/graph_editor.html?cell_id=%(cell_id)s"></iframe><input
type="hidden" id="graph_data_%(cell_id)s"
value="num_vertices=%(nodes_len)s;edges=%(edges)s;pos=%(nodes)s;"><input
type="hidden" id="graph_name_%(cell_id)s"
value="%(var_name)s"></td></tr><tr><td><button onclick="
    var f, g, saved_input;
    g = $('#iframe_graph_editor_%(cell_id)s')[0].contentWindow.update_sage();
    if (g[2] === '') {
        alert('You need to give a Sage variable name to the graph, before saving it.');
        return;
    }

    // This is how to comment out the previous contents of the cell:
    //f = '#' + $('#cell_input_%(cell_id_save)s').val() + '\\n';

    f = '# Automatically generated:\\n';
    f += g[2] + ' = Domain.from_graph_editor(' + g[1] + ', ' + g[0] + ')';
    $('#cell_input_%(cell_id_save)s').val(f);
    cell_input_resize(%(cell_id_save)s);
    evaluate_cell(%(cell_id_save)s, false);
">Save</button><button
onclick="cell_delete_output(%(cell_id)s);">Close</button></td></tr></tbody></table></div></font></html>""" % {"path": path,
                "cell_id_save": self._cell_id,
                "cell_id": self._cell_id_edit,
                "nodes": str(nodes),
                "nodes_len": len(self._nodes),
                "edges": str(edges),
                "elements": self.convert_elements(self._elements),
                "boundaries": self.convert_boundaries(self._boundaries),
                "curves": self.convert_curves(self._curves),
                "var_name": self_name}

    def get_mesh(self, lib="hermes2d"):
        if lib == "hermes2d":
            from hermes2d import Mesh
            m = Mesh()
            nodes = self._nodes
            elements = [list(e)+[0] for e in self._elements]
            boundaries = self._boundaries
            curves = self._curves
            m.create(nodes, elements, boundaries, curves)
            return m
        else:
            raise NotImplementedError("unknown library")

    def edit(self, editor="flex"):
        """
        editor .... either "flex" or "js"
        """

        self_name = "d"
        locs = sys._getframe(1).f_locals
        for var in locs:
            if id(locs[var]) == id(self):
                self_name = var
        print self.get_html(self_name=self_name, editor=editor)
