/*
 * Copyright  1999-2004 The Apache Software Foundation
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 * $Header: /home/stefano/cvs/gump/java/Jenny.java,v 1.26 2004/02/27 08:31:31 bodewig Exp $
 * $Revision: 1.26 $
 * $Date: 2004/02/27 08:31:31 $
 */
 
// TRaX classes
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
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
import java.io.File;
import java.net.ConnectException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;

public class Jenny {
    
    /** Indicates whether extrenal references should be followed or not */
    private boolean online = true;

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
            return dBuilder.parse(source);
        } catch (SAXParseException e) {
            System.err.print("Error parsing file " + source);
            System.err.println(" line " + e.getLineNumber() + ": ");
            throw e;
        } catch (java.net.UnknownHostException uhe) {
            System.out.println(uhe.toString());
            return null;
        }
    }
    
    /**
     * Replace all occurances of @@DATE@@ with the current datestamp in
     * attribute values.  The datestamp to be used is persisted on disk,
     * so it will remain stable until the .timestamp file is touched or
     * removed.
     * @param parent node to be processed recursively
     * @param dstamp string to substitute for @@DATE@@
     */
    private void replaceDate(Element parent, String dstamp) {
       Node first = parent.getFirstChild();
       for (Node child=first; child != null; child=child.getNextSibling()) {
           if (child.getNodeType()==Node.ELEMENT_NODE) {
               NamedNodeMap attrs = ((Element)child).getAttributes();
               for (int i=0; i<attrs.getLength(); i++) {
                   Node a = attrs.item(i);
                   String v = a.getNodeValue();
                   int start = v.indexOf("@@DATE@@");
                   while (start>=0) {
                       v = v.substring(0,start) + dstamp + v.substring(start+8);
                       ((Element)child).setAttribute(a.getNodeName(),v);
                       start = v.indexOf("@@DATE@@");
                   }
               }
               replaceDate((Element)child, dstamp);
           }
       }
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
           String source = href.getValue();
           if (source.startsWith("http://") && !online) {
               throw new ConnectException("Not online");
           }
           Node sub = parse(source);

           boolean isExtern = source.startsWith("http://")
                       || source.startsWith("file://");

           if (sub != null) {
               if (source.lastIndexOf(".")>0) {
                   source=source.substring(0,source.lastIndexOf("."));
               }

               if (source.lastIndexOf("/")>0) {
                   source=source.substring(source.lastIndexOf("/")+1);
               }

               String cacheName = getCachedNodeName(node);
               node.removeAttribute("href");
               node.setAttribute("defined-in", source);

               Document doc = node.getOwnerDocument();
               Element copy = null;
               Node first = sub.getFirstChild();
               for (Node child=first; child!=null; 
                    child=child.getNextSibling()) {
                   if (child.getNodeType() == Node.ELEMENT_NODE) {
                       copy = (Element)doc.importNode(child, true);
                       break;
                   }
               }

               moveChildren(node, copy);

               node.getParentNode().replaceChild(copy,node);
               node = copy;

               // if expanded xml is not local to gump, make a local copy
               // and "redirect" location using extern-prefix attribute
               if (isExtern) {
                   String prefix = node.getNodeName() + "_";
                   // try to use name attribute as source, otherwise cross
                   // fingers and hope the current source is unique
                   if (node.getAttribute("name") != null) {
                       source = node.getAttribute("name");
                   }
                   output (sub, "work/" + prefix + source + ".xml");
                   node.setAttribute("defined-in", source);
                   node.setAttribute("extern-prefix",prefix);
                   node.setAttribute("cache-as", cacheName);
               }
           }
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
               Element elem = (Element)child;
               try {
                   child=expand(elem);
               } catch (Throwable t) {
                   String tagName = elem.getTagName();
                   String nameAttr = elem.getAttribute("name");
                   String hrefAttr = elem.getAttribute("href");

                   StringBuffer name = new StringBuffer(tagName);
                   if (!"".equals(nameAttr)) {
                       name.append(" with name ").append(nameAttr);
                   }
                   if (!"".equals(hrefAttr)) {
                       name.append(" with href ").append(hrefAttr);
                   }
                   
                   System.err.println("Failed to expand "
                                      + name.toString());
                   System.err.println("   - " + t);
                   
                   String cache = getCachedNodeName(elem);
                   File f = new File(cache);
                   if (f.exists()) {
                       System.err.println("Using cached document " 
                                          + cache + ".");
                       Node sub = parse(cache);
                       Document doc = elem.getOwnerDocument();
                       Element copy = null;
                       Node firstNode = sub.getFirstChild();
                       for (Node childNode = firstNode; childNode != null; 
                            childNode = childNode.getNextSibling()) {
                           if (childNode.getNodeType() == Node.ELEMENT_NODE) {
                               copy = (Element)doc.importNode(childNode, true);
                               break;
                           }
                       }

                       moveChildren(elem, copy);

                       elem.getParentNode().replaceChild(copy, elem);

                       cache = cache.substring(6 /* "cache/".length() */,
                                               cache.length() 
                                               - 4 /* ".xml".length() */);

                       copy.setAttribute("defined-in", cache);
                       copy.setAttribute("extern-prefix", "../cache/");

                       child = copy;
                   } else {
                       System.err.println("No cache " + cache + " available.");
                   }
               }
           }
       }

       return node;
    }

    /**
     * Merge the contents of nodes with the same value for the name attribute.
     * Attributes from later definitions get added (or overlay) prior
     * definitions.  Elements get appended.  Elements marked for removal are
     * removed.
     * @param type Element localname.  Typically project or repository.
     * @param document Starting point for search.
     * @return hashtable of resulting elements
     */
    private Hashtable merge(String type, Node document)
        throws Exception
    {
        boolean needRemove = false;
        Hashtable list = new Hashtable();

        Node child=document.getFirstChild();
        for (; child!=null; child=child.getNextSibling()) {
            if (!child.getNodeName().equals(type)) continue;
            Element element = (Element) child;
            String name = element.getAttribute("name");

            // check for "removed" elements
            if (!needRemove
                    && !element.getAttribute("remove").equals("")) {
                needRemove = true;
            }

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

        if (needRemove) {
            Vector removeThem = new Vector();
            Enumeration enum = list.elements();
            while (enum.hasMoreElements()) {
                Element element = (Element)enum.nextElement();
                if (!element.getAttribute("remove").equals("")) {
                    removeThem.addElement(element);
                }
            }

            enum = removeThem.elements();
            while (enum.hasMoreElements()) {
                Element element = (Element)enum.nextElement();
                element.getParentNode().removeChild(element);
                list.remove(element.getAttribute("name"));
            }
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
    private Jenny(String source, boolean online) throws Exception {
        this.online = online;
        // Obtain the date to be used
        Date lastModified = new Date();
        try {
            File timestamp = new File(".timestamp");
            timestamp.createNewFile();
            lastModified = new Date(timestamp.lastModified());
        } catch (java.io.IOException ioe) {
            ioe.printStackTrace();
        }
        String dstamp = (new SimpleDateFormat("yyyyMMdd")).format(lastModified);

        // process documents
        Document doc = parse(source);
        Element workspace = doc.getDocumentElement();
        Workspace.init(workspace);
        expand(workspace);
        replaceDate(workspace, dstamp);
        Repository.load(merge("repository", workspace).elements());
        Server.load(merge("server", workspace).elements());
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
            boolean onlineOption = true;
            boolean usageOK = true;
            
            if (args.length > 2 || args.length==0) {
                usageOK = false;
            } else if (args.length == 2) {
                if (args[1].equalsIgnoreCase("-offline")) {
                    onlineOption = false;
                } else if (!args[1].equalsIgnoreCase("-online")) {
                    usageOK = false;
                }
            } 
            
            if (usageOK) {
                new Jenny(args[0], onlineOption);
            } else { 
                System.out.println("Usage: Jenny workspace.xml [-offline | -online]");
                System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(99);
        }
    }

    /**
     * Name of the cache file.
     */
    private String getCachedNodeName(Element node) {
        String hrefAttribute = node.getAttribute("href");
        StringBuffer sb = new StringBuffer("cache/");
        int len = hrefAttribute.length();
        for (int i = 0; i < len; i++) {
            char c = hrefAttribute.charAt(i);
            switch (c) {
            case '/':
            case ':':
            case '*':
            case '~':
            case '?':
            case '&':
            case '\\':
            case ';':
            case '(':
            case ')':
            case ' ':
            case '=':
                // these may cause trouble in file names or on the
                // command line
                sb.append('_');
                break;
                
            default:
                sb.append(c);
                break;
            }
        }
        
        return sb.toString() + ".xml";
    }
}
