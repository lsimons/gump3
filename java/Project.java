// DOM classes
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Enumeration;
import java.util.Hashtable;

public class Project {

    static private Hashtable projects = new Hashtable();
    private Document document;
    private Element element;
    private String name;
    private Element ant = null;
    private Hashtable depends = new Hashtable();
    private Hashtable jars = new Hashtable();

    /**
     * Create a set of Project definitions based on XML nodes.
     * @param elements list of &lt;project&gt; elements
     */
    public static void load(Enumeration elements) throws Exception {
        while (elements.hasMoreElements()) {
           new Project((Element)elements.nextElement());
        }

        // Resolve all references so that the XML can be processed in
        // one pass.
        for (Enumeration e=projects.elements(); e.hasMoreElements();) {
            Project p = ((Project)(e.nextElement()));
            p.expandDepends();
            p.resolveProperties();
        }
    }

    /**
     * General attribute accessor.
     * @param name attribute name
     * @return Value of the specified attribute.
     */
    public String get(String name) {
        return element.getAttribute(name);
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

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("depend")) {
                depends.put(((Element)child).getAttribute("project"), child);
            } else if (child.getNodeName().equals("option")) {
                depends.put(((Element)child).getAttribute("project"), child);
            } else if (child.getNodeName().equals("ant")) {
                ant = (Element)child;
            } else if (child.getNodeName().equals("home")) {
                home = (Element)child;
            } else if (child.getNodeName().equals("jar")) {
                jars.put(((Element)child).getAttribute("id"), child);
            }
        }

        computeHome(home);

        if (ant != null) {
            genProperties(ant);
            genDepends(ant);
        }

        // if only one jar is found, make sure that it can be accessed without
        // specifying an id.
        if (jars.size() == 1) {
            jars.put("", jars.elements().nextElement());
        }

        projects.put(name, this);
    }

    /**
     * Replace ant "depend" elements with "property" elements.  This is
     * a convenience "syntatic sugar" that makes for simpler project
     * definitions.  Attribute "property" becomes name.  Attributes
     * reference="jarpath" and classpath="true" are added.
     * @param ant &lt;ant&gt; element to be processed
     */
    private void genProperties(Element ant) throws Exception {

        Node child=ant.getFirstChild();
        while (child != null) {
            Node next = child.getNextSibling();
             
            if (child.getNodeName().equals("depend")) {
                // create a new element based on existing element
                Element property = document.createElement("property");
                property.setAttribute("reference", "jarpath");
                property.setAttribute("classpath", "add");
                Jenny.copyChildren((Element)child, property);
    
                // change property attribute to name attribute
                if (property.getAttributeNode("name")==null) {
                   Attr pname = property.getAttributeNode("property");
                   if (pname != null) {
                       property.setAttribute("name",pname.getValue());
                       property.removeAttributeNode(pname);
                   }
                }

                // replace existing element with new one
                ant.replaceChild(property, child);
            }

            child = next;
        }
    }

    /**
     * Generate Depend elements from property references to projects.
     * @param ant &lt;ant&gt; element to be processed
     */
    private void genDepends(Element ant) throws Exception {
        Node child=ant.getFirstChild();
        for (;child!=null; child=child.getNextSibling()) {
            if (!child.getNodeName().equals("property")) continue;
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

        Module module = Module.find(element.getAttribute("module"));
        if (module == null) return;
        String srcdir = module.getSrcDir();

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

    /**
     * Copy selected attribute and elements from dependent projects.  This
     * simplifies generation by essentially making project definitions
     * self contained.
     */
    private void expandDepends() {
        for (Enumeration e=depends.keys(); e.hasMoreElements(); ) {
            String name = (String)e.nextElement();
            Project target = (Project)projects.get(name);
            if (target == null) continue;

            Element depend = (Element) depends.get(name);
            depend.setAttribute("home",target.get("home"));
            depend.setAttribute("defined-in",target.get("defined-in"));

            Node child=target.element.getFirstChild();
            for (; child != null; child=child.getNextSibling()) {
                if (child.getNodeName().equals("jar")) {
                    depend.appendChild(child.cloneNode(false));
                } else if (child.getNodeName().equals("ant")) {
                    depend.appendChild(document.createElement("ant"));
                } else if (child.getNodeName().equals("script")) {
                    depend.appendChild(document.createElement("script"));
                }
            }
        }
    }

    /**
     * Resolve property references, based on the value of "reference"
     * attribute (if present).  Supported values for reference are:
     *
     * <ul>
     * <li> home: the home directory for the referenced project </li>
     * <li> jar: the simple name (path relative to home) of the jar in a 
     * referenced project. </li>
     * <li> jarpath: the fully qualified path of the jar in a referenced 
     * project. </li>
     * <li> srcdir: the srcdir for the module containing the project. </li>
     * <li> path: a path which is to be interpreted relative to the srcdir 
     * for the module containing this project </li>
     * </ul>
     */
    private void resolveProperties() throws Exception {
        if (ant == null) return;

        Node child=ant.getFirstChild();
        for (;child!=null; child=child.getNextSibling()) {
            if (!child.getNodeName().equals("property")) continue;
            Element property = (Element) child;
            if (property.getAttributeNode("value") != null) continue;

            String reference = property.getAttribute("reference");
            String projectName = property.getAttribute("project");

            String value = null;

            if (reference.equals("home")) {
                Project project = (Project) projects.get(projectName);
                require (project, "project", projectName);
                value = project.get("home");
                property.setAttribute("type", "path");
            } else if (reference.equals("jar")) {
                String id = property.getAttribute("id");
                Element jar = getJar (projectName, property.getAttribute("id"));
                value = jar.getAttribute("name"); 
            } else if (reference.equals("jarpath")) {
                Project project = (Project) projects.get(projectName);
                Element jar = getJar (projectName, property.getAttribute("id"));
                value = project.get("home") + "/" + jar.getAttribute("name"); 
                property.setAttribute("type", "path");
            } else if (reference.equals("srcdir")) {
                Module module = Module.find(projectName);
                require (module, "module", projectName);
                value = module.getSrcDir();
                property.setAttribute("type", "path");
            } else if (property.getAttributeNode("path") != null) {
                Module module = Module.find(this.get("module"));
                require (module, "module", this.get("module"));
                value = module.getSrcDir();
                value += "/" + property.getAttribute("path");
                property.setAttribute("type", "path");
            }

            if (value != null) property.setAttribute("value", value);
        }
    }

    /**
     * Locate a specific jar from a dependency, issuing an exception if 
     * the jar can not be found.
     * @param projectName the name of the project
     * @param id the identifier for which jar is desired
     * @return Value of the specified attribute.
     */
    private Element getJar(String projectName, String id) 
        throws Exception 
    {
        Project project = (Project) projects.get(projectName);
        require (project, "project", projectName);

        Element jar = (Element)project.jars.get(id);
        if (jar != null) return jar;

        if (!id.equals("")) {

            throw new Exception(
               "A jar with id \"" + id + "\" was not found in project \"" + 
               projectName + "\" referenced by project " + name);

        } else if (project.jars.size() > 1) {

            throw new Exception(
               "Multiple jars defined by project \"" + projectName + "\" " + 
               "referenced by project \"" + name + "\"; " +
               "an id attribute is required to select the one you want.");

        } else {

            throw new Exception(
               "Project \"" + projectName + "\" referenced by project " + 
               name + "defines no jars as output.");

        };

    }

    /**
     * Require that a specified object not be null, otherwise produce an error
     * message indicating what attribute the problem occurred on.
     * @param object the object which must not be null
     * @param attr the attribute from which this value was derived
     * @param value the value of this attribute
     * @return Value of the specified attribute.
     */
    private void require(Object object, String attr, String value) 
        throws Exception 
    {
        if (object != null) return;

        throw new Exception(
           attr + " \"" + value + "\" not found processing project " + name
        );
    }
}
