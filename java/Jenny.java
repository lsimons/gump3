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
import org.xml.sax.SAXParseException;

// Java classes
import java.util.Enumeration;
import java.util.Hashtable;

public class Jenny {

    DocumentBuilderFactory dFactory = DocumentBuilderFactory.newInstance();
    TransformerFactory tFactory = TransformerFactory.newInstance();

    /**
     * Parse an XML source file into an DOM.
     * @param source name of source file
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
     * Transform a DOM given a stylesheet.
     * @param dom document to be transformed
     * @param sheet stylesheet to be used
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
     * Move child nodes (attributes, elements, text, etc).
     * @param source element to move from
     * @param target element to update
     */
    protected static void moveChildren(Element source, Element target) {
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
     * Expand hrefs in place, recursively.
     * @param node source element
     */
    private Element expand(Element node) throws Exception {
       // expand hrefs
       Attr href = node.getAttributeNode("href");
       if (href != null && !node.getNodeName().equals("url")) {
           String source=href.getValue();
           Node sub = parse(source);

           if (source.lastIndexOf(".")>0) {
               source=source.substring(0,source.lastIndexOf("."));
           }

           if (source.lastIndexOf("/")>0) {
               source=source.substring(source.lastIndexOf("/")+1);
           }

           node.removeAttribute("href");
           node.setAttribute("defined-in", source);

           Document doc = node.getOwnerDocument();
           Element copy=(Element)doc.importNode(sub.getFirstChild(), true);
           moveChildren(node, copy);

           node.getParentNode().replaceChild(copy,node);
           node = copy;
       }

       // move all profile information to the front
       Node first = node.getFirstChild();
       for (Node child=first; child!=null; child=child.getNextSibling()) {
           if (child.getNodeName().equals("profile")) {
              child = expand((Element)child);
              while (child.getFirstChild() != null) {
                 node.insertBefore(child.getFirstChild(), first); 
              }
           }
       }

       // recurse through the children
       first = node.getFirstChild();
       for (Node child=first; child != null; child=child.getNextSibling()) {
           if (child.getNodeType()==Node.ELEMENT_NODE) {
               child=expand((Element)child);
           }
       }

       return node;
    }

    /**
     * Merge the contents of nodes with the same value for the name attribute.
     * Attributes from later definitions get added (or overlay) prior
     * definitions.  Elements get appended.
     * @param type Element localname.  Typically project or repository.
     * @param document Starting point for search.
     * @return hashtable of resulting elements
     */
    private Hashtable merge(String type, Node document)
        throws Exception
    {
        Hashtable list = new Hashtable();

        Node child=document.getFirstChild();
        for (; child!=null; child=child.getNextSibling()) {
            if (!child.getNodeName().equals(type)) continue;
            Element element = (Element) child;
            String name = element.getAttribute("name");

            Element priorDefinition = (Element)list.get(name);
            if (priorDefinition != null && priorDefinition != element) {
                Element parent  = (Element)priorDefinition.getParentNode();
                String definedIn = parent.getAttribute("defined-in");
                if (!definedIn.equals("")) {
                    element.setAttribute("defined-in",definedIn);
                }

                moveChildren(priorDefinition, element);
                parent.removeChild(priorDefinition);
            }
            list.put(name, element);
        }

        return list;
    }

    /**
     * Serialize a DOM tree to file.
     * @param dom document to be transformed
     * @param dest name of file where the results are to be placed
     */
    private void output(Node dom, String dest) throws Exception {
        DOMSource in = new DOMSource(dom);
        StreamResult out = new StreamResult(dest);
        tFactory.newTransformer().transform(in, out);
    }

    /**
     * merge, sort, and insert defaults into a workspace
     * @param source document to be transformed
     */
    private Jenny(String source) throws Exception {
        Document doc = parse(source);
        Element workspace = (Element)doc.getFirstChild();
        Workspace.init(workspace);

        expand(workspace);
        Repository.load(merge("repository", workspace).elements());
        Module.load(merge("module",workspace).elements());
        Project.load(merge("project",workspace).elements());
        output (doc, "work/merge.xml");
    }

    /**
     * Combine, colasce, and sort the files referenced by a workspace
     * definition into a single XML file.
     */
    public static void main(String[] args) {
        try {
            if (args.length == 1) {
                new Jenny(args[0]);
            } else {
                System.out.println("Usage: Jenny workspace.xml");
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(99);
        }
    }
}
