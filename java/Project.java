// DOM classes
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Comparator;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Set;
import java.util.TreeSet;
import java.util.Vector;

public class Project {

    static private Hashtable projects = new Hashtable();
    private Document document;
    private Element element;
    private String name;
    private Element ant = null;
    private Hashtable dependsOn = new Hashtable();
    private Hashtable referencedBy = new Hashtable();
    private Hashtable jars = new Hashtable();
    private Element description;
    private Element url;
    private Vector deliver = new Vector();

    private static String nagTo = null;
    private static String nagPrefix = null;

    /**
     * Create a set of Project definitions based on XML nodes.
     * @param elements list of &lt;project&gt; elements
     */
    public static void load(Enumeration elements) throws Exception {
        Element element = null;
        while (elements.hasMoreElements()) {
            try {
                element = (Element)elements.nextElement();
                new Project(element);
            } catch (Throwable t) {
                System.err.println("Dropping project "
                                   + element.getAttribute("name")
                                   + " because of Exception " + t);
            }
        }
            
        // Resolve all references so that the XML can be processed in
        // one pass.
        for (Enumeration e=((Hashtable) projects.clone()).elements(); e.hasMoreElements();) {
            Project p = ((Project)(e.nextElement()));
            try {
                p.expandDepends();
                p.resolveProperties();
            } catch (Throwable t) {
                System.err.println("Dropping project " + p.get("name")
                                   + " because of Exception " + t);
                p.remove();
            }
        }
        
        sort();
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
        Element javadoc = null;

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("depend")) {
                dependsOn.put(((Element)child).getAttribute("project"), child);
            } else if (child.getNodeName().equals("option")) {
                dependsOn.put(((Element)child).getAttribute("project"), child);
            } else if (child.getNodeName().equals("ant")) {
                if (ant != null) {
                    // multiple ant children?  Merge them!
                    Jenny.moveChildren(ant, (Element)child);
                    element.removeChild(ant);
                }
                ant = (Element)child;
            } else if (child.getNodeName().equals("home")) {
                home = (Element)child;
            } else if (child.getNodeName().equals("description")) {
                description = (Element)child;
            } else if (child.getNodeName().equals("url")) {
                url = (Element)child;
            } else if (child.getNodeName().equals("javadoc")) {
                javadoc = (Element)child;
            } else if (child.getNodeName().equals("jar")) {
                jars.put(((Element)child).getAttribute("id"), child);
            } else if (child.getNodeName().equals("deliver")) {
                deliver.add(child);
            } else if (child.getNodeName().equals("nag")) {
                expandNag((Element) child);
            }
        }

        computeHome(home);

        if (ant != null) {
            genProperties(ant);
            genDepends(ant);
            if (!get("target").equals("")) {
                ant.setAttribute("target", get("target"));
            }
        }

        resolveJavadoc(javadoc);
        handleDeliver();

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
                Jenny.moveChildren((Element)child, property);
    
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
            if (dependsOn.get(dependency) != null) continue;

            if (property.getAttribute("reference").equals("srcdir")) continue;

            Element depend = document.createElement("depend");
            depend.setAttribute("project", dependency);
            if (property.getAttributeNode("classpath") == null) {
                depend.appendChild(document.createElement("noclasspath"));
            }

            Attr runtime = property.getAttributeNode("runtime");
            if (runtime != null) {
                depend.setAttribute("runtime", runtime.getValue());
            }

            element.appendChild(depend);
            dependsOn.put(dependency, depend);
        }
    }

    /**
     * Resolve home directory.  In the process copy any description and
     * url elements necessary to complete this definition.
     * @param home &lt;ant&gt; element which may contain info
     */
    private void computeHome(Element home) {
        String basedir = Workspace.getBaseDir();

        Module module = Module.find(element.getAttribute("module"));
        if (module == null) return;

        String srcdir;
        String pkg = element.getAttribute("package");
        if (pkg.equals("")) {
            srcdir = module.getSrcDir();
        } else { 
            srcdir = Workspace.getPkgDir() + "/" + pkg;
        }
        element.setAttribute("srcdir", srcdir);

        // if a description is not provided, copy the one from the module
        if (description == null) {
            description = module.getDescription();
            if (description != null) {
                element.appendChild(description.cloneNode(true));
            }
        }

        // if a url is not provided, copy the one from the module
        if (url == null) {
            url = module.getUrl();
            if (url != null) {
                element.appendChild(url.cloneNode(true));
            }
        }

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

            if (result.equals("")) result=srcdir;
            element.setAttribute("home", result);
        } else {
            element.setAttribute("srcdir", result);
        }
    }

    /**
     * Copy selected attribute and elements from dependent projects.  This
     * simplifies generation by essentially making project definitions
     * self contained.
     */
    private void expandDepends() throws Exception {
        String jardir = Workspace.getJarDir();

        for (Enumeration e=dependsOn.keys(); e.hasMoreElements(); ) {
            String name = (String)e.nextElement();
            Element depend = (Element) dependsOn.get(name);
            Project target = (Project)projects.get(name);
            boolean buildable = false;

            if (!depend.getNodeName().equals("option")) {
                require(target, "project", name);
            }
            if (target == null) continue;

            target.referencedBy.put(this, depend);
            depend.setAttribute("home",target.get("home"));
            depend.setAttribute("defined-in",target.get("defined-in"));

            Node child=target.element.getFirstChild();
            for (; child != null; child=child.getNextSibling()) {
                if (child.getNodeName().equals("jar")) {
                    depend.appendChild(child.cloneNode(false));
                } else if (child.getNodeName().equals("ant")) {
                    depend.appendChild(document.createElement("ant"));
                    buildable = true;
                } else if (child.getNodeName().equals("script")) {
                    depend.appendChild(document.createElement("script"));
                    buildable = true;
                }
            }

            if (buildable && !jardir.equals("")) {
                String module = target.get("module");
                depend.setAttribute("home", jardir + "/" + module);
                child=depend.getFirstChild();
                for (; child != null; child=child.getNextSibling()) {
                  if (child.getNodeName().equals("jar")) {
                      String jarname = ((Element)child).getAttribute("name");
                      jarname = jarname.substring(jarname.lastIndexOf("/")+1);
                      ((Element)child).setAttribute("name", jarname);
                  }
                }
            }
        }
    }

    /**
     * Determine if this project has any unsatisfied dependencies left
     * on the todo list.
     * @param todo the list of projects yet to be done (includes this one).
     * @return true if this project is ready to go
     */
    private boolean isReady(Set todo) {
        for (Enumeration e=dependsOn.keys(); e.hasMoreElements();) {
            if (todo.contains(e.nextElement())) return false;
        }
        return true;
    }

    /**
     * Determine if this project is referenced by anything on the todo list.
     * @param todo the list of projects yet to be done (includes this one).
     * @return true if this project is holding up progress
     */
    private boolean isPrereq(Set todo) {
        for (Enumeration e=referencedBy.keys(); e.hasMoreElements();) {
            Project p = (Project)e.nextElement();
            if (todo.contains(p.name)) return true;
        }
        return false;
    }

    /**
     * Move this element to the end of the parents set of children.
     */
    private void moveToLast() {
        Element parent = (Element) element.getParentNode();
        parent.removeChild(element);
        parent.appendChild(element);
    }

    /**
     * Process all inherited dependencies.  
     */
    private void inheritDependencies() {
        Vector inheritance = new Vector();

        for (Enumeration e=dependsOn.elements(); e.hasMoreElements(); ) {
            Element depend = (Element) e.nextElement();
            String inherit = depend.getAttribute("inherit");
            Project p = (Project) projects.get(depend.getAttribute("project"));
            if (p == null) continue;

            for (Enumeration d=p.dependsOn.keys(); d.hasMoreElements(); ) {
                String name = (String) d.nextElement();
                if (dependsOn.get(name) != null) continue;
                Element source = (Element) p.dependsOn.get(name);
                String type = source.getNodeName();

                // if inherit="all" is specified on a depends element, then all
                // of the optional and depends elements on the referenced 
                // project are inherited by this project.
                //
                // if inherit="hard", the same thing happens except that all 
                // optional dependencies are converted to "hard" dependencies
                // in the copy.
                if (inherit.equals("all") || inherit.equals("hard")) {
                    Element clone = (Element) source.cloneNode(true);
                    if (inherit.equals("hard") && type.equals("option")) {
                        Element renamed = document.createElement("depend");
                        Jenny.moveChildren(clone, renamed);
                        clone = renamed;
                    }
                    inheritance.add(clone);

                // look for runtime="true" dependencies in the referenced
                // project.  Convert depends to options if the reference to
                // the project is an option.
                } else if (inherit.equals("runtime")) {
                    if (source.getAttribute("runtime").equals("true")) {
                        Element clone = (Element) source.cloneNode(true);
                        if (type.equals("option")) {
                            Element renamed = document.createElement("option");
                            Jenny.moveChildren(clone, renamed);
                            clone = renamed;
                        }
                        inheritance.add(clone);
                    }
                }

                // if this project depends on any project which in turn has
                // a dependency which specifies inherit="jars", then inherit
                // that dependency.
                if (source.getAttribute("inherit").equals("jars")) {
                    Element clone = (Element) source.cloneNode(true);
                    clone.setAttribute("runtime", "true");
                    inheritance.add(clone);
                }
            }
        }

        // Add the inherited nodes
        for (Enumeration e=inheritance.elements(); e.hasMoreElements(); ) {
            Element inherited = (Element) e.nextElement();
            String project = inherited.getAttribute("project");
            if (dependsOn.get(project) == null) {
                inherited.setAttribute("inherited", "true");
                dependsOn.put(project, inherited);
                element.appendChild(inherited);
            }
        }
    }

    /**
     * Implement a deterministing sort order.  Projects which are most
     * referenced get priority.  After that, order is determined alphabetically.
     */
    private static class Ranker implements Comparator {
        public int compare(Object o1, Object o2) {
            Project p1 = (Project) projects.get(o1);
            Project p2 = (Project) projects.get(o2);
            if (p1 == p2) return 0;
            if (p1 == null) return -1;
            if (p2 == null) return 1;

            int diff = p2.referencedBy.size() - p1.referencedBy.size();
            if (diff != 0) return diff;

            return ((String)o1).compareTo((String)o2);
        }
    }

    /**
     * Sort all projects in an order that respects the dependencies.  If such
     * an order can not be determined, print out the ones that form a loop.
     * As we determine the order, process the inherited dependencies.  This
     * way the inheritance will recurse properly.
     */
    private static void sort() throws Exception {
        TreeSet todo = new TreeSet(new Ranker());
        todo.addAll(projects.keySet());

        // As long as there are projects which are ready, put the next
        // available one at the end of the list.
        for (Iterator i=todo.iterator(); i.hasNext();) {
            Project p = (Project) projects.get(i.next());
            if (p.isReady(todo)) {
                p.moveToLast();
                p.inheritDependencies();
                todo.remove(p.name);
                i=todo.iterator();
            }
        }
            
        // Did we succeed?
        if (todo.isEmpty()) return;

        // Remove all elements which are not prereqed by any projects
        // remaining
        if (todo.isEmpty()) return;
        for (Iterator i=todo.iterator(); i.hasNext();) {
            Project p = (Project) projects.get(i.next());
            if (!p.isPrereq(todo)) {
                todo.remove(p.name);
                i=todo.iterator();
            }
        }


        // Construct a list of the rest, and throw an exception
        String message="Circular dependency loop involving:";
        for (Iterator i=todo.iterator(); i.hasNext();) {
            Project p = (Project) projects.get(i.next());
            message += "\n  " + p.name;
        }
        throw new Exception(message);
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
                Project project = (Project) projects.get(projectName);
                if (project == null) project=this;
                value = project.get("srcdir");
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
               name + " defines no jars as output.");

        }

    }

    /**
     * If a javadoc child was found, add any missing project, module,
     * or description information; resolve path; and copy the resulting
     * node to the specified module.
     * @param javadoc child XML element
     */
    private void resolveJavadoc(Element javadoc) throws Exception {
        if (javadoc == null) return;

        // retrieve url and dir of javadoc from the workspace
        Element config = Workspace.getJavaDoc();
        if (config == null) return;
        String url = config.getAttribute("url");
        String javadocDir = config.getAttribute("dir");

        // default project attribute to the name of this project
        if (javadoc.getAttributeNode("project") == null)
            javadoc.setAttribute("project", name);

        // default module attribute to the module which this project belongs
        String moduleName = javadoc.getAttribute("module");
        if (moduleName.equals("")) moduleName = this.get("module");
        Module module = Module.find(moduleName);
        require (module, "module", moduleName);

        if (!moduleName.equals(this.get("module"))) {
            javadoc.setAttribute("defined-in", this.get("module"));
        }

        // if there are no child nodes, add this project's description
        if (!javadoc.hasChildNodes() && description!=null) {
            Element desc = (Element) description.cloneNode(true);
            javadoc.appendChild(desc);
        }

        // resolve relative and full path to this javadoc entry
        String path = javadoc.getAttribute("nested");
        String fullpath;
        if (!path.equals("")) {
            fullpath = get("srcdir") + "/" + path;
        } else {
            path = javadoc.getAttribute("parent");
            fullpath = Workspace.getBaseDir() + "/" + path;
        }
        path = moduleName + "/" + path;

        // for each description entry, resolve source, url, and dest attrs.
        Node child=javadoc.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("description")) {
                Element desc = (Element) child;
                String dir = desc.getAttribute("dir");
                String append = "";
                if (!dir.equals("")) append = "/" + dir;

                desc.setAttribute("source", fullpath + append);

                if (url.equals("")) {
                    desc.setAttribute("url", "file:///" + fullpath + append);
                } else {
                    desc.setAttribute("url", url + path + append);
                }

                if (!javadocDir.equals("")) {
                    desc.setAttribute("dest", javadocDir + "/" + path + append);
                }
            }
        }

        // copy the entire result to the desired module
        module.appendChild(javadoc);
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

    /**
     * Remove this Project instance from the workspace.
     */
    private void remove() {
        projects.remove(name);
        element.getParentNode().removeChild(element);
    }

    /**
     * For all deliver elements, add them to the corresponding site
     * elements, if these are defined.
     */
    private void handleDeliver() {
        Enumeration elements = deliver.elements();
        String srcdir = element.getAttribute("srcdir");
        while (elements.hasMoreElements()) {
            Element deliver = (Element) elements.nextElement();
            String siteName = deliver.getAttribute("tosite");
            Element site = Server.getSite(siteName);
            if (site != null) {
                String fromdir = deliver.getAttribute("fromdir");
                deliver.setAttribute("fromdir", srcdir + "/" + fromdir);
                site.appendChild(deliver);
            }
        }
    }

    /**
     * Add default values for subjects and regexp if none have been
     * specified.
     *
     * Push attributes to nested regexp elements
     */
    private void expandNag(Element nag) {
        if (nagPrefix == null) {
            Element workspaceNag = Workspace.getNag();
            if (workspaceNag == null) {
                nagPrefix = "[GUMP]";
            } else {
                if (!workspaceNag.getAttribute("prefix").equals("")) {
                    nagPrefix = workspaceNag.getAttribute("prefix");
                } else {
                    nagPrefix = "[GUMP]";
                }
                if (!workspaceNag.getAttribute("to").equals("")) {
                    nagTo = workspaceNag.getAttribute("to");
                }
            }
        }
        

        String subject = nagPrefix + " Build Failure - "+name;
        String to = nagTo == null ? nag.getAttribute("to") : nagTo;
        String from = nag.getAttribute("from");

        if (!nag.getAttribute("subject").equals("")) {
            subject = nagPrefix + " " + nag.getAttribute("subject");
        }
        
        if (!nag.hasChildNodes()) {
            Element regexp = nag.getOwnerDocument().createElement("regexp");
            regexp.setAttribute("pattern", "/BUILD FAILED/");
            regexp.setAttribute("subject", subject);
            regexp.setAttribute("to", to);
            regexp.setAttribute("from", from);
            nag.appendChild(regexp);

        } else {

            Node child = nag.getFirstChild();
            for (; child != null; child = child.getNextSibling()) {
                if (child.getNodeName().equals("regexp")) {
                    Element regexp = (Element)child;
                    if (regexp.getAttribute("pattern").equals("")) {
                        regexp.setAttribute("pattern", "/BUILD FAILED/");
                    }

                    if (regexp.getAttribute("subject").equals("")) {
                        regexp.setAttribute("subject", subject);
                    } else {
                        String orig = regexp.getAttribute("subject");
                        regexp.setAttribute("subject", nagPrefix + " " + orig);
                        
                    }

                    if (nagTo != null 
                        || regexp.getAttribute("to").equals("")) {
                        regexp.setAttribute("to", to);
                    }

                    if (regexp.getAttribute("from").equals("")) {
                        regexp.setAttribute("from", from);
                    }
                }
            }

        }
    }
}
