/*
 * $Header: /home/stefano/cvs/gump/java/Repository.java,v 1.6 2003/11/26 14:14:40 bodewig Exp $
 * $Revision: 1.6 $
 * $Date: 2003/11/26 14:14:40 $
 *
 * ====================================================================
 *
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
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
