import org.w3c.dom.Element;
import org.w3c.dom.Node;

import java.util.HashMap;

public class Workspace {

    static final String GUMP_VERSION = "0.3";

    private static Element element;
    private static String basedir;
    private static Element javadoc;
    private static Element deliver;
    private static HashMap servers = new HashMap();
    private static HashMap sites = new HashMap();

    /**
     * Static property accessor for basedir attribute.
     * @return Base directory associated with this workspace
     */
    public static String getBaseDir() {
        return element.getAttribute("basedir");
    }

    /**
     * Static property accessor for pkgdir attribute.
     * @return Package directory associated with this workspace
     */
    public static String getPkgDir() {
        return element.getAttribute("pkgdir");
    }

    /**
     * Static property accessor for jardir attribute.
     * @return Package directory associated with this workspace
     */
    public static String getJarDir() {
        return element.getAttribute("jardir");
    }

    /**
     * Static property accessor for javadoc element.
     * @return Javadoc element (if any) associated with this workspace
     */
    public static Element getJavaDoc() {
        return javadoc;
    }

    /**
     * Static accessor - do we deliver to the given site?
     * @return true if a server of the given name is defined in the workspace.
     */
    public static boolean isSiteDefined(String name) {
        return sites.containsKey(name);
    }

    /**
     * Static accessor for deliver's scratchdir attribute.
     * @return Deliver scratchdir associated with this workspace.
     */
    public static String getScratchDir() {
        if (deliver != null) {
            return deliver.getAttribute("scratchdir");
        }
        return null;
    }

    /**
     * Static accessor for deliver's named server child.
     * @return null if server is not defined, the server element otherwise.
     */
    public static Element getServer(String name) {
        return (Element) servers.get(name);
    }

    /**
     * Default and verify various workspace attributes.
     * If not specified:
     *   banner-image="http://jakarta.apache.org/images/jakarta-logo.gif"
     *   banner-link="http://jakarta.apache.org"
     *   cvsdir=basedir+"/cvs"
     *   logdir=basedir+"/log"
     *   pkgdir=basedir
     * @param Workspace element to be updated
     */
    public static void init(Element workspace) throws Exception {
        Workspace.element = workspace;

        if (!workspace.getAttribute("version").equals(GUMP_VERSION)) {
            throw new Exception("workspace version " + GUMP_VERSION +
                                " required.");
        }

        basedir = workspace.getAttribute("basedir");

        if (workspace.getAttribute("banner-image").equals("")) {
            workspace.setAttribute("banner-image",
                "http://jakarta.apache.org/images/jakarta-logo.gif");
        }

        if (workspace.getAttribute("banner-link").equals("")) {
            workspace.setAttribute("banner-link", "http://jakarta.apache.org");
        }

        if (workspace.getAttribute("logdir").equals("")) {
            workspace.setAttribute("logdir", basedir + "/log");
        }

        if (workspace.getAttribute("cvsdir").equals("")) {
            workspace.setAttribute("cvsdir", basedir + "/cvs");
        }

        if (workspace.getAttribute("pkgdir").equals("")) {
            workspace.setAttribute("pkgdir", basedir);
        }

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("javadoc")) {
                javadoc = (Element) child;
            } else if (child.getNodeName().equals("deliver")) {
                handleDeliver((Element) child);
            }
        }
        
        if (deliver != null) {
            element.removeChild(deliver);
            String scratchdir = deliver.getAttribute("scratchdir");
            if (scratchdir.equals("")) {
                deliver.setAttribute("scratchdir", basedir+"/scratch");
            }
        }
        
    }

    /**
     * Fill map of servers.
     */
    private static void handleDeliver(Element element) {
        deliver = element;
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("server")) {
                Element server = (Element) child;
                servers.put(server.getAttribute("name"), server);
                handleSites(server);
            }
        }
    }

    /**
     * Fill map of sites.
     */
    private static void handleSites(Element element) {
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("site")) {
                Element site = (Element) child;
                sites.put(site.getAttribute("name"), site);
            }
        }
    }    
}
