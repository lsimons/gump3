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

    DocumentBuilderFactory dFactory = DocumentBuilderFactory.newInstance();
    TransformerFactory tFactory = TransformerFactory.newInstance();

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
      * @param type Element localname.	Typically project or repository.
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
		   merge(type, list, element);
	       } else if (priorDefinition != element) {
		   element.getParentNode().removeChild(element);
		   copyChildren(element, priorDefinition);
		   element=priorDefinition;
	       }
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
      * @param type Element localname.	Typically project or repository.
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
      * Replace ant "depend" elements with "property" elements.	 This is
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
      * Rename <module> to <project>.  This is a transitional convenience
      * as I move from the nested project approach to a simple declaration
      * of the projects (or perhaps, instead the targets) contained within
      * a module.
      * @param document to be transformed
      */
    private void renameModuleToProject(Document document) throws Exception {

	// safely get a list of all modules
	NodeIterator nl = XPathAPI.selectNodeIterator(document, "//module");
	Vector list = new Vector();
	for (Node module=nl.nextNode(); module!=null; module=nl.nextNode()) {
	   list.add(module);
	}

	// replace all elements in that list with projects
	for (Enumeration e=list.elements(); e.hasMoreElements();) {
	   Element module = (Element)e.nextElement();
	   Element project = document.createElement("project");
	   copyChildren(module, project);
	   module.getParentNode().replaceChild(project, module);
	}
    }

    /**
      * merge, sort, and insert defaults into a workspace
      * @param DOM to be transformed
      * @param sheet to be used
      * @return Node
      */
    private gen(String source) throws Exception {
	Document workspace = parse(source);
	expand((Element)workspace.getFirstChild());
	renameModuleToProject(workspace);
	flatten("project", workspace.getFirstChild());
	flatten("repository", workspace.getFirstChild());
	antDependsToProperties(workspace);

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
