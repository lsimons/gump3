import org.w3c.dom.Element;
import org.w3c.dom.Node;

public class Workspace {

    static final String GUMP_VERSION = "0.3";

    private static Element element;
    private static String basedir;
    private static Element javadoc;

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
            }
        }
    }
}
