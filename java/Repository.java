// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Enumeration;
import java.util.Vector;
import java.util.Hashtable;

public class Repository {

    static private Hashtable repositories = new Hashtable();
    private Element element;
    private String name;

    /**
     * Create a set of Repository definitions based on XML nodes.
     * @param moudules list of &lt;module&gt; elements
     */
    public static void load(Enumeration repositories) throws Exception {
        while (repositories.hasMoreElements()) {
            new Repository((Element)repositories.nextElement());
        }
    }

    /**
     * Find a Repository given its name.
     * @param name module name
     * @return Repository
     */
    public static Repository find(String name) {
        return (Repository) repositories.get(name);
    }

    /**
     * Constructor.
     * @param element &lt;module&gt; element
     */
    public Repository(Element element) throws Exception {
        this.element = element;
        name = element.getAttribute("name");

        resolve(element);

        repositories.put(name, this);
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
     * Use text nodes under root elements to fill in defaults for repository
     * attributes.
     */
    private void resolve(Node node) throws Exception {
        // recurse through all children
        Node child=node.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            resolve(child);
        }

        // <parent>text<parent> => <element parent="text">
        if (node.getNodeType() != Node.TEXT_NODE) return;

        Node parent = node.getParentNode();
        Node gparent = parent.getParentNode();
        if (!gparent.getNodeName().equals("root")) return;

        if (element.getAttributeNode(parent.getNodeName()) == null) {
            element.setAttribute(parent.getNodeName(), node.getNodeValue());
        }
    }

}
