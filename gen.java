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

    private void collapse(String type, Hashtable list, Node parent) {
       Node child=parent.getFirstChild();
       while (child != null) {
           Node next=child.getNextSibling();
           if (child.getNodeName().equals(type)) {
               Element project = (Element) child;
               String name = project.getAttributeNode("name").getValue();

               Element priorDefinition = (Element)list.get(name);
               if (priorDefinition == null) {
                   list.put(name, project);
               } else {
                   copyChildren(project, priorDefinition);
                   project.getParentNode().removeChild(project);
                   project=priorDefinition;
               }

               collapse(type, list, project);
           }
           child=next;
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
        collapse("project", new Hashtable(), workspace.getFirstChild());
        collapse("repository", new Hashtable(), workspace.getFirstChild());

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
