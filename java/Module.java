// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Enumeration;
import java.util.Vector;
import java.util.Hashtable;

public class Module {

    static private Hashtable modules = new Hashtable();
    private Element element;
    private String name;
    private String srcdir;

    /**
     * Create a set of Module definitions based on XML nodes.
     * @param moudules list of &lt;module&gt; elements
     */
    public static void load(Enumeration modules) throws Exception {
        while (modules.hasMoreElements()) {
            new Module((Element)modules.nextElement());
        }
    }

    /**
     * Find a Module given its name.
     * @param String module name
     * @return Module
     */
    public static Module find(String name) {
        return (Module) modules.get(name);
    }

    /**
     * Constructor.
     * @param element &lt;module&gt; element
     */
    public Module(Element element) throws Exception {
        this.element = element;
        name = element.getAttribute("name");

        computeSrcDir();
        promoteProjects();
        resolveRepository();

        modules.put(name, this);
    }

    /**
     * Property accessor for srcdir attribute.
     * @return Source directory associated with this module
     */
    public String getSrcDir() {
        return srcdir;
    }

    /**
     * Resolve the source directory for this module.
     */
    private void computeSrcDir() throws Exception {
        srcdir=element.getAttribute("srcdir");
        if (srcdir.equals("")) srcdir=name;
        srcdir = Workspace.getBaseDir() + "/" + srcdir;

        element.setAttribute("srcdir", srcdir);
    }

    /**
     * Set module name on any projects contained herein, and move the
     * element up to the workspace.
     */
    private void promoteProjects() throws Exception {
        Vector projects = new Vector();

        // Collect a list of projects, marking them as we go
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (! child.getNodeName().equals("project")) continue;

            Element project = (Element) child;
            if (project.getAttributeNode("module") == null) {
                project.setAttribute("module", name);
            }

            projects.add(project);
        }

        // Move each project from the module to the workspace
        Node parent = element.getParentNode();
        String definedIn = element.getAttribute("defined-in");
        for (Enumeration e=projects.elements(); e.hasMoreElements(); ) {
            Element project = (Element) e.nextElement();
            if (project.getAttributeNode("defined-in") == null)
               project.setAttribute("defined-in", definedIn);
            element.removeChild(project);
            parent.appendChild(project);
        }
    }

    /**
     * Resolves a repository name into a cvsroot.  In the process it also
     * decorates the cvs tag with the module name and tag info.
     */
    private void resolveRepository() throws Exception {
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (! child.getNodeName().equals("cvs")) continue;
            Element cvs = (Element) child;

            cvs.setAttribute("srcdir", name);
            if (cvs.getAttributeNode("module") == null) {
                cvs.setAttribute("module", name);
            }

            String tag = element.getAttribute("tag");
            if (!tag.equals("")) cvs.setAttribute("tag", tag);

            Repository r = Repository.find(cvs.getAttribute("repository"));
            String repository = ":" + r.get("method");
            repository += ":" + r.get("user");

            repository += "@";
            if (cvs.getAttributeNode("host-prefix") != null)
                repository += cvs.getAttribute("host-prefix") + ".";
            repository += r.get("hostname");

            repository += ":" + r.get("path");
            if (cvs.getAttributeNode("dir") != null)
                repository += "/" + cvs.getAttribute("dir");

            cvs.setAttribute("repository", repository);
            cvs.setAttribute("password", r.get("password"));
        }
    }
}
