// Imported TraX classes
import javax.xml.transform.dom.DOMResult;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamSource;

// Imported JAVA API for XML Parsing classes
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

// Imported DOM classes
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NamedNodeMap;

// Imported java classes
import java.io.FileOutputStream;
import java.util.Enumeration;
import java.util.Hashtable;

public class gen {

    DocumentBuilderFactory dFactory = DocumentBuilderFactory.newInstance();
    TransformerFactory tFactory = TransformerFactory.newInstance();

    /**
      * parse an XML source file into an DOM
      * @param name of source file
      * @return Node
      */
    private Node parse(String source) throws Exception {
	DocumentBuilder dBuilder = dFactory.newDocumentBuilder();
        return dBuilder.parse(new java.io.File(source));
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
    private void merge(String type, Hashtable list, Node parent) {
       Node child=parent.getFirstChild();
       while (child != null) {
           Node next=child.getNextSibling();
           if (child.getNodeName().equals(type)) {
               Element element = (Element) child;
               String name = element.getAttributeNode("name").getValue();

               Element priorDefinition = (Element)list.get(name);
               if (priorDefinition == null) {
                   list.put(name, element);
               } else {
                   copyChildren(element, priorDefinition);
                   element.getParentNode().removeChild(element);
                   element=priorDefinition;
               }

               merge(type, list, element);
           }
           child=next;
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
    private void flatten(String type, Node root) {
        Hashtable list = new Hashtable();
        merge(type, list, root);
        for (Enumeration e=list.keys(); e.hasMoreElements();) {
           Element element = (Element)list.get(e.nextElement());
           Element parent  = (Element)element.getParentNode();
           if (parent != root) {
               parent.removeChild(element);
               String definedIn = parent.getAttributeNode("name").getValue();
               element.setAttribute("defined-in",definedIn);
               root.appendChild(element);
           }
        }
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
      * merge, sort, and insert defaults into a workspace
      * @param DOM to be transformed
      * @param sheet to be used 
      * @return Node
      */
    private gen(String source) throws Exception {
        Node workspace = parse(source);
        expand((Element)workspace.getFirstChild());
        flatten("project", workspace.getFirstChild());
        flatten("repository", workspace.getFirstChild());

        Node resolved = transform(workspace, "defaults.xsl");
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
