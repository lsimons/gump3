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
 * $Header: /home/stefano/cvs/gump/java/Repository.java,v 1.7 2004/02/27 08:31:31 bodewig Exp $
 * $Revision: 1.7 $
 * $Date: 2004/02/27 08:31:31 $
 */
 
// DOM classes
import org.w3c.dom.Element;
import org.w3c.dom.Node;

// Java classes
import java.util.Enumeration;
import java.util.Hashtable;

public class Repository {

    static private Hashtable repositories = new Hashtable();
    private Element element;
    private String name;
    private boolean redistributable = false;

    /**
     * Create a set of Repository definitions based on XML nodes.
     * @param moudules list of &lt;module&gt; elements
     */
    public static void load(Enumeration repositories) throws Exception {
        while (repositories.hasMoreElements()) {
            new Repository((Element)repositories.nextElement());
        }
    }

    /**
     * Find a Repository given its name.
     * @param name module name
     * @return Repository
     */
    public static Repository find(String name) {
        return (Repository) repositories.get(name);
    }

    /**
     * Constructor.
     * @param element &lt;module&gt; element
     */
    public Repository(Element element) throws Exception {
        this.element = element;
        name = element.getAttribute("name");

        if (element.getAttributeNode("compress") == null) {
            element.setAttribute("compress", "-z3");
        }

        resolve(element);

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("redistributable")) {
                redistributable = true;
            } else if (child.getNodeName().equals("url")
                       && element.getAttribute("type").equals("svn")) {
                Node grandChild = child.getFirstChild();
                if (grandChild != null 
                    && grandChild.getNodeType() == Node.TEXT_NODE) {
                    element.setAttribute("url", grandChild.getNodeValue());
                }
            }
        }

        repositories.put(name, this);
    }

    /**
     * Property accessor for redistributable attribute.
     * @return Value of the specified attribute.
     */
    public boolean getRedistributable() {
        return redistributable;
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
     * Use text nodes under root elements to fill in defaults for repository
     * attributes.
     */
    private void resolve(Node node) throws Exception {
        // recurse through all children
        Node child=node.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            resolve(child);
        }

        // <parent>text<parent> => <element parent="text">
        if (node.getNodeType() != Node.TEXT_NODE) return;

        Node parent = node.getParentNode();
        Node gparent = parent.getParentNode();
        if (!gparent.getNodeName().equals("root")) return;

        if (element.getAttributeNode(parent.getNodeName()) == null) {
            element.setAttribute(parent.getNodeName(), node.getNodeValue());
        }
    }

}
