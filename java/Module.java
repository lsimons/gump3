// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;

public class Module {

    static private Hashtable modules = new Hashtable();
    private Element element;
    private Element cvs;
    private String name;
    private String srcdir;
    private Element description;
    private Element url;

    private static String cvspass = System.getProperty("user.home")+"/.cvspass";

    /** cvspass char conversion data */
    private static final char shifts[] = {
          0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
         16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
        114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,
        111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,
         41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,
        125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,
         36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,
         58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,
        225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,
        199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,
        174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,
        207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,
        192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,
        227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,
        182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,
        243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152 };

    /**
     * Create a set of Module definitions based on XML nodes.
     * @param moudules list of &lt;module&gt; elements
     */
    public static void load(Enumeration modules) throws Exception {
        while (modules.hasMoreElements()) {
            new Module((Element)modules.nextElement());
        }

        cvslogin();
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
        resolveCvsroot();

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("description")) {
                description = (Element) child;
            } else if (child.getNodeName().equals("url")) {
                url = (Element) child;
            }
        }

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
     * Property accessor for description attribute.
     * @param name attribute name
     * @return Value of the specified attribute.
     */
    public Element getDescription() {
        return description;
    }

    /**
     * Property accessor for url attribute.
     * @param name attribute name
     * @return Value of the specified attribute.
     */
    public Element getUrl() {
        return url;
    }

    /**
     * Append arbitrary XML data to this node.
     * @param child Node to be deep copied to this tree.
     */
    public void appendChild(Node child) {
        element.appendChild(child.cloneNode(true));
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
     * Resolves a repository name into a cvsroot.  If there are multiple
     * cvs entries, first they are combined into a single elemnt.  Then
     * the single resulting element (if any) will get decorated with the
     * the module name, cvsroot, and password info.
     */
    private void resolveCvsroot() throws Exception {
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (! child.getNodeName().equals("cvs")) continue;
            if (cvs == null)  {
                cvs = (Element) child;
            } else {
                Jenny.copyChildren((Element) child, cvs);
            }

        }

        if (cvs != null) {
            cvs.setAttribute("srcdir", name);
            if (cvs.getAttributeNode("module") == null) {
                cvs.setAttribute("module", name);
            }

            String tag = element.getAttribute("tag");
            if (!tag.equals("")) cvs.setAttribute("tag", tag);

            Repository r = Repository.find(cvs.getAttribute("repository"));
            String cvsroot = ":" + r.get("method");
            cvsroot += ":" + r.get("user");

            cvsroot += "@";
            if (cvs.getAttributeNode("host-prefix") != null)
                cvsroot += cvs.getAttribute("host-prefix") + ".";
            cvsroot += r.get("hostname");

            cvsroot += ":" + r.get("path");
            if (cvs.getAttributeNode("dir") != null)
                cvsroot += "/" + cvs.getAttribute("dir");

            cvs.setAttribute("cvsroot", cvsroot);
            cvs.setAttribute("password", r.get("password"));
        }
    }


    /**
     * Add entries to cvspass, as necessary, to simulate logon to 
     * cvs repositories accessed as :pserver:.  Note: the .cvspass file
     * will not be updated unless there are new entries to add.
     */
    private static void cvslogin() throws Exception {

        Hashtable password = new Hashtable();
        File file = new File(cvspass);

        // read existing cvsroot entries

        if (file.exists()) {
            BufferedReader reader = new BufferedReader(new FileReader(file));

            for (String line = null; (line=reader.readLine())!=null; ) {
                int split = line.indexOf(' ');
                password.put(line.substring(0,split), line.substring(split+1));
            }
    
            reader.close();
        }

        // append new entries

        PrintWriter writer = null;

        for (Enumeration e=modules.elements(); e.hasMoreElements(); ) {
            Element cvs = ((Module) e.nextElement()).cvs;
            if (cvs == null) continue;

            String cvsroot = cvs.getAttribute("cvsroot");
            if (!cvsroot.startsWith(":pserver:")) continue;

            if (password.get(cvsroot) == null) {
                if (writer == null) {
                    writer = new PrintWriter(new FileWriter(cvspass, true));
                }
                String data = "A" + mangle(cvs.getAttribute("password"));
                password.put(cvsroot, data);
                writer.println(cvsroot + " " + data);
            }
        }

        if (writer != null) writer.close();
    }

    /**
     * Encode a password using the same encryption scheme that cvs uses.
     */
    private static String mangle(String password){
        char[] buf = password.toCharArray();
        for(int i=0; i<buf.length; i++) {
            buf[i] = shifts[buf[i]];
        }
        return new String(buf);
    }

}
