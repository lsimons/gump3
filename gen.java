// TRaX classes
import javax.xml.transform.dom.DOMResult;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;

// Java API for XML Parsing classes
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

// DOM classes
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.traversal.NodeIterator;
import org.xml.sax.SAXParseException;


// Java classes
import java.io.FileOutputStream;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;

// Apache xpath
import org.apache.xpath.XPathAPI;

public class gen {

    static final String GUMP_VERSION = "0.3";

    DocumentBuilderFactory dFactory = DocumentBuilderFactory.newInstance();
    TransformerFactory tFactory = TransformerFactory.newInstance();

    Hashtable modules;

    /**
      * parse an XML source file into an DOM
      * @param name of source file
      * @return Node
      */
    private Document parse(String source) throws Exception {
        try {
            DocumentBuilder dBuilder = dFactory.newDocumentBuilder();
            return dBuilder.parse(new java.io.File(source));
        } catch (SAXParseException e) {
            System.err.print("Error parsing file " + source);
            System.err.println(" line " + e.getLineNumber() + ": ");
            throw e;
        }
    }

    /**
      * transform a DOM given a stylesheet
      * @param DOM to be transformed
      * @param sheet to be used
      * @return Node
      */
    private Node transform(Node dom, String sheet) throws Exception {
        StreamSource source = new StreamSource("stylesheet/"+sheet);
        Transformer transformer = tFactory.newTransformer(source);
        DOMResult output = new DOMResult();
        transformer.transform(new DOMSource(dom), output);
        return output.getNode();
    }

    /**
      * copy child nodes (attributes, elements, text, etc).
      * @param source element
      * @param target element
      */
    private void copyChildren(Element source, Element target) {
       Node child=source.getFirstChild();
       while (child != null) {
           Node next=child.getNextSibling();
           target.appendChild(child);
           child=next;
       }

       NamedNodeMap attrs = source.getAttributes();
       for (int i=0; i<attrs.getLength(); i++) {
           Node a = attrs.item(i);
           if (target.getAttributeNode(a.getNodeName())==null) {
               target.setAttribute(a.getNodeName(),a.getNodeValue());
           }
       }
    }

    /**
      * expand hrefs in place, recursively
      * @param source element
      */
    private void expand(Element node) throws Exception {
       // expand hrefs
       Attr href = node.getAttributeNode("href");
       if (href != null && !node.getNodeName().equals("url")) {
           String source=href.getValue();
           Node sub = parse(source);

           if (source.lastIndexOf(".")>0)
               source=source.substring(0,source.lastIndexOf("."));

           if (source.lastIndexOf("/")>0)
               source=source.substring(source.lastIndexOf("/")+1);

           node.removeAttribute("href");
           node.setAttribute("defined-in", source);

           Document doc = node.getOwnerDocument();
           Element copy=(Element)doc.importNode(sub.getFirstChild(), true);
           copyChildren(node, copy);

           Element parent = (Element)node.getParentNode();
           if (node.getNodeName().equals("profile")) {
               copy.removeAttribute("defined-in");
               copyChildren(copy, parent);
           } else {

               parent.replaceChild(copy,node);
           }
       }

       // recurse through the children
       Node child=node.getFirstChild();
       while (child != null) {
           Node next=child.getNextSibling();
           if (child.getNodeType()==Node.ELEMENT_NODE) expand((Element)child);
           child=next;
       }
    }

    /**
      * Merge the contents of nodes with the same value for the name attribute.
      * Attributes from later definitions get added (or overlay) prior
      * definitions.  Elements get appended.
      * @param type Element localname.  Typically project or repository.
      * @param list Hashtable used for recursion.  Must initially be empty.
      * @param Node Starting point for search.
      */
    private void merge(String type, Hashtable list, Node document)
        throws Exception
    {
        NodeIterator nl = XPathAPI.selectNodeIterator(document, "//"+type);
        for (Node child=nl.nextNode(); child!=null; child=nl.nextNode()) {
            Element element = (Element) child;
            String name = element.getAttribute("name");

            Element priorDefinition = (Element)list.get(name);
            if (priorDefinition != null && priorDefinition != element) {
                Element parent  = (Element)priorDefinition.getParentNode();
                String definedIn = parent.getAttribute("defined-in");
                if (!definedIn.equals(""))
                    element.setAttribute("defined-in",definedIn);

                copyChildren(priorDefinition, element);
                parent.removeChild(priorDefinition);
            }
            list.put(name, element);
        }
    }

    /**
      * Unnest all elements of a given type by moving them all to become
      * direct children of the specified root node.  In the process, merge
      * all matching nodes which contain the same value for the name attribute.
      * For elements that get "hoisted", an additional "defined-in" attribute
      * is added indicating where the element was originally defined.
      * @param type Element localname.  Typically project or repository.
      * @param Node Root (workspace) node
      */
    private Hashtable flatten(String type, Node root)
        throws Exception
    {
        Hashtable list = new Hashtable();
        merge(type, list, root);
        for (Enumeration e=list.keys(); e.hasMoreElements();) {
           Element element = (Element)list.get(e.nextElement());
           Element parent  = (Element)element.getParentNode();

           if (parent != root) {
               String definedIn = parent.getAttribute("defined-in");
               if (definedIn.equals(""))
                   definedIn = parent.getAttribute("name");
               element.setAttribute("defined-in",definedIn);

               parent.removeChild(element);
               root.appendChild(element);
           }
        }
        return list;
    }

    /**
      * serialize a DOM tree to file
      * @param DOM to be transformed
      * @param destination file
      */
    private void output(Node dom, String dest) throws Exception {
        DOMSource in = new DOMSource(dom);
        StreamResult out = new StreamResult(dest);
        tFactory.newTransformer().transform(in, out);
    }

    /**
      * Replace ant "depend" elements with "property" elements.  This is
      * a convenience "syntatic sugar" that makes for simpler project
      * definitions.  Attribute "property" becomes name.  Attributes
      * reference="jarpath" and classpath="true" are added.
      * @param document to be transformed
      */
    private void antDependsToProperties(Document document) throws Exception {
        NodeIterator nl = XPathAPI.selectNodeIterator(document, "//ant/depend");
        for (Node depend=nl.nextNode(); depend!=null; depend=nl.nextNode()) {

            // create a new element based on existing element
            Element property = document.createElement("property");
            property.setAttribute("reference", "jarpath");
            property.setAttribute("classpath", "add");
            copyChildren((Element)depend, property);

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
        }
    }

    /**
      * Flatten all modules, and in the process resolve all srcdirs.
      * If the srcdir attribute is not present, it defaults to the value
      * of name.  Either way, basedir gets prepended.
      */
    private void computeSrcdir(Element workspace) throws Exception {
        String basedir = workspace.getAttribute("basedir");
        modules = flatten("module", workspace);
        for (Enumeration e=modules.keys(); e.hasMoreElements();) {
             Element module = (Element)modules.get(e.nextElement());
             String name = module.getAttribute("name");

             // compute source directory
             String srcdir=module.getAttribute("srcdir");
             if (srcdir.equals("")) srcdir=name;
             module.setAttribute("srcdir", basedir + "/" + srcdir);

             // set module name on any projects contained herein
             Node child=module.getFirstChild();
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

    /**
      * Flatten all projects, and in the process resolve all home directories.
      */
    private void computeHome(Element workspace) throws Exception {
        String basedir = workspace.getAttribute("basedir");
        String pkgdir = workspace.getAttribute("pkgdir");
        if (pkgdir.equals("")) pkgdir = basedir;

        Hashtable projects = flatten("project", workspace);
        for (Enumeration keys=projects.keys(); keys.hasMoreElements();) {
             String name = (String)keys.nextElement();
             Element project = (Element)projects.get(name);

             String moduleName = project.getAttribute("module");
             Element module= (Element)modules.get(moduleName);
             String srcdir = module.getAttribute("srcdir");
             
             // compute home directory
             String home=project.getAttribute("home");
             if (home.equals("")) {
                 Element e = (Element)XPathAPI.selectSingleNode(project,"home");
                 if (e != null) {
                     String attr;
                     if (! (attr=e.getAttribute("parent")).equals("")) {
                         home = basedir + "/" + attr;
                     } else if (! (attr=e.getAttribute("nested")).equals("")) {
                         home = srcdir + "/" + attr;
                     } else if (! (attr=e.getAttribute("dir")).equals("")) {
                         home = attr;
                     }
                 }

                 if (home.equals("")) {
                     String pkg = project.getAttribute("package");
                     if (!pkg.equals("")) home = pkgdir + "/" + pkg;
                 }

                 if (home.equals("")) home=srcdir;
                 project.setAttribute("home", home);
             }
        }
    }

    /**
      * Default and verify various workspace attributes.
      * If not specified:
      *   banner-image="http://jakarta.apache.org/images/jakarta-logo.gif"
      *   banner-link="http://jakarta.apache.org"
      *   logdir=basedir+"/log"
      *   cvsdir=basedir+"/cvs"
      * @param Workspace element to be updated
      */
    private void workspaceDefaults(Element workspace) throws Exception {
        if (!workspace.getAttribute("version").equals(GUMP_VERSION)) {
            throw new Exception("workspace version " + GUMP_VERSION +
                                " required.");
        }

        String basedir = workspace.getAttribute("basedir");

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
    }

    /**
      * merge, sort, and insert defaults into a workspace
      * @param DOM to be transformed
      * @param sheet to be used
      * @return Node
      */
    private gen(String source) throws Exception {
        Document doc = parse(source);
        Element workspace = (Element)doc.getFirstChild();
        workspaceDefaults(workspace);

        expand((Element)workspace);
        computeSrcdir(workspace);
        computeHome(workspace);
        flatten("repository", workspace);
        antDependsToProperties(doc);

        Node resolved = transform(doc, "defaults.xsl");
        output (resolved, "work/merge.xml");

        Node sorted   = transform(resolved, "sortdep.xsl");
        output (sorted, "work/sorted.xml");
    }

    public static void main(String[] args) {
        try {
            if (args.length == 1)
                new gen(args[0]);
            else
                System.out.println("Usage: gen workspace.xml");
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(99);
        }
    }
}
