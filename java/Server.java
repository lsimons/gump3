// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;

public class Server {

    private static HashMap sites = new HashMap();

    /**
     * Create a set of site definitions based on XML nodes.
     * @param elements list of &lt;server&gt; elements
     */
    public static void load(Enumeration elements) throws Exception {
        Element element = null;
        while (elements.hasMoreElements()) {
            try {
                element = (Element)elements.nextElement();
                new Server(element);
            } catch (Throwable t) {
                System.err.println("Dropping server "
                                   + element.getAttribute("name")
                                   + " because of Exception " + t);
            }
        }
    }

    /**
     * Static accessor for the named site
     * @return the element corresponding to the site, if it is defined
     * in a server document as well as in the workspace.
     */
    public static Element getSite(String name) {
        return (Element) sites.get(name);
    }

    /**
     * Constructor
     *
     * <p>Promotes all &lt;site&gt; children to workspace, if the site
     * is defined in the workspace's deliver element.  Otherwise,
     * simply remove the site child element.</p>
     */
    private Server(Element element) {
        String name = element.getAttribute("name");
        ArrayList children = new ArrayList();
        Node child = element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("site")) {
                Element site = (Element) child;
                site.setAttribute("server", name);
                String siteName = site.getAttribute("name");
                if (Workspace.getServer(name) != null 
                    && Workspace.isSiteDefined(siteName)) {
                    sites.put(siteName, site);
                }
                children.add(site);
            }
        }
            
        Iterator iter = children.iterator();
        Node parent = element.getParentNode();
        while (iter.hasNext()) {
            Element site = (Element) iter.next();
            element.removeChild(site);

            Element server = Workspace.getServer(name);
            if (server != null 
                && Workspace.isSiteDefined(site.getAttribute("name"))) {
                addServerAttributes(server, site);
                parent.appendChild(site);
            }
        }
    }

    /**
     * Adds attributes defined in Workspace to the site element.
     *
     * @param server server element from workspace
     * @param site site element from server
     */
    private void addServerAttributes(Element server, Element site) {
        site.setAttribute("scratchdir", Workspace.getScratchDir());
        site.setAttribute("username", 
                          server.getAttribute("username"));

        String drop = server.getAttribute("dropdir");
        if (drop.equals("")) {
            drop = "/tmp";
        }
        site.setAttribute("dropdir", drop);
    }

}
