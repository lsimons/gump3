// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Enumeration;
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
        markProjects();

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
     * Set module name on any projects contained herein.
     */
    private void markProjects() throws Exception {
        Node child=element.getFirstChild();
        while (child != null) {
            if (child.getNodeName().equals("project")) {
                Element project = (Element) child;
                if (project.getAttributeNode("module") == null) {
                    project.setAttribute("module", name);
                }
            }
            child=child.getNextSibling();
        }
    }

}
