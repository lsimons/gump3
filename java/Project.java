// DOM classes
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.traversal.NodeIterator;

// Java classes
import java.util.Enumeration;
import java.util.Hashtable;

// Apache xpath
import org.apache.xpath.XPathAPI;

public class Project {

    private Document document;
    private Element element;
    private String name;
    private Hashtable depends = new Hashtable();

    /**
     * Create a set of Project definitions based on XML nodes.
     * @param project list of &lt;project&gt; elements
     */
    public static void load(Enumeration projects) throws Exception {
        while (projects.hasMoreElements()) {
           new Project((Element)projects.nextElement());
        }
    }

    /**
     * Constructor.
     * @param element &lt;project&gt; element
     */
    public Project(Element element) throws Exception {
        this.element = element;
        document = element.getOwnerDocument();
        name = element.getAttribute("name");

        Element home = null;
        Element ant = null;

        Node child=element.getFirstChild();
        while (child != null) {
            if (child.getNodeName().equals("depend")) {
                depends.put(((Element)child).getAttribute("project"),child);
            } else if (child.getNodeName().equals("option")) {
                depends.put(((Element)child).getAttribute("project"),child);
            } else if (child.getNodeName().equals("ant")) {
                ant = (Element)child;
            } else if (child.getNodeName().equals("home")) {
                home = (Element)child;
            }
            child=child.getNextSibling();
        }

        computeHome(home);

        if (ant != null) {
            genProperties(ant);
            genDepends(ant);
        }
    }

    /**
     * Replace ant "depend" elements with "property" elements.  This is
     * a convenience "syntatic sugar" that makes for simpler project
     * definitions.  Attribute "property" becomes name.  Attributes
     * reference="jarpath" and classpath="true" are added.
     * @param ant &lt;ant&gt; element to be processed
     */
    private void genProperties(Element ant) throws Exception {

        NodeIterator nl = XPathAPI.selectNodeIterator(ant, "depend");
        for (Node depend=nl.nextNode(); depend!=null;) {
            Node next = nl.nextNode();

            // create a new element based on existing element
            Element property = document.createElement("property");
            property.setAttribute("reference", "jarpath");
            property.setAttribute("classpath", "add");
            Jenny.copyChildren((Element)depend, property);

            // change property attribute to name attribute
            if (property.getAttributeNode("name")==null) {
               Attr pname = property.getAttributeNode("property");
               if (pname != null) {
                   property.setAttribute("name",pname.getValue());
                   property.removeAttributeNode(pname);
               }
            }

            // replace existing element with new one
            depend.getParentNode().replaceChild(property, depend);

            depend = next;
        }
    }

    /**
     * Generate Depend elements from property references to projects.
     * @param ant &lt;ant&gt; element to be processed
     */
    private void genDepends(Element ant) throws Exception {
        NodeIterator nl = XPathAPI.selectNodeIterator(ant, "property");
        for (Node child=nl.nextNode(); child!=null; child=nl.nextNode()) {
            Element property = (Element) child;

            String dependency = property.getAttribute("project");
            if (dependency.equals("")) continue;
            if (dependency.equals(name)) continue;
            if (depends.get(dependency) != null) continue;

            if (property.getAttribute("reference").equals("srcdir")) continue;

            Element depend = document.createElement("depend");
            depend.setAttribute("project", dependency);
            if (property.getAttributeNode("classpath") == null)
                depend.appendChild(document.createElement("noclasspath"));

            element.appendChild(depend);
            depends.put(dependency, depend);
        }
    }

    /**
     * Resolve home directory.
     * @param home &lt;ant&gt; element which may contain info
     */
    private void computeHome(Element home) {
        String basedir = Workspace.getBaseDir();
        String pkgdir = Workspace.getPkgDir();

        String module = element.getAttribute("module");
        String srcdir = Module.find(module).getSrcDir();

        // compute home directory
        String result=element.getAttribute("home");
        if (result.equals("")) {
            if (home != null) {
                String attr;
                if (! (attr=home.getAttribute("parent")).equals("")) {
                    result = basedir + "/" + attr;
                } else if (! (attr=home.getAttribute("nested")).equals("")) {
                    result = srcdir + "/" + attr;
                } else if (! (attr=home.getAttribute("dir")).equals("")) {
                    result = attr;
                }
            }

            if (result.equals("")) {
                String pkg = element.getAttribute("package");
                if (!pkg.equals("")) result = pkgdir + "/" + pkg;
            }

            if (result.equals("")) result=srcdir;
            element.setAttribute("home", result);
        }
    }
}
