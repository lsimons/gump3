/*
 * $Header: /home/stefano/cvs/gump/java/Server.java,v 1.2 2002/08/27 14:54:09 nicolaken Exp $
 * $Revision: 1.2 $
 * $Date: 2002/08/27 14:54:09 $
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
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;

public class Server {

    private static HashMap sites = new HashMap();

    /**
     * Create a set of site definitions based on XML nodes.
     * @param elements list of &lt;server&gt; elements
     */
    public static void load(Enumeration elements) throws Exception {
        Element element = null;
        while (elements.hasMoreElements()) {
            try {
                element = (Element)elements.nextElement();
                new Server(element);
            } catch (Throwable t) {
                System.err.println("Dropping server "
                                   + element.getAttribute("name")
                                   + " because of Exception " + t);
            }
        }
    }

    /**
     * Static accessor for the named site
     * @return the element corresponding to the site, if it is defined
     * in a server document as well as in the workspace.
     */
    public static Element getSite(String name) {
        return (Element) sites.get(name);
    }

    /**
     * Constructor
     *
     * <p>Promotes all &lt;site&gt; children to workspace, if the site
     * is defined in the workspace's deliver element.  Otherwise,
     * simply remove the site child element.</p>
     */
    private Server(Element element) {
        String name = element.getAttribute("name");
        ArrayList children = new ArrayList();
        Node child = element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("site")) {
                Element site = (Element) child;
                site.setAttribute("server", name);
                String siteName = site.getAttribute("name");
                if (Workspace.getServer(name) != null 
                    && Workspace.isSiteDefined(siteName)) {
                    sites.put(siteName, site);
                }
                children.add(site);
            }
        }
            
        Iterator iter = children.iterator();
        Node parent = element.getParentNode();
        while (iter.hasNext()) {
            Element site = (Element) iter.next();
            element.removeChild(site);

            Element server = Workspace.getServer(name);
            if (server != null 
                && Workspace.isSiteDefined(site.getAttribute("name"))) {
                addServerAttributes(server, site);
                parent.appendChild(site);
            }
        }
    }

    /**
     * Adds attributes defined in Workspace to the site element.
     *
     * @param server server element from workspace
     * @param site site element from server
     */
    private void addServerAttributes(Element server, Element site) {
        site.setAttribute("scratchdir", Workspace.getScratchDir());
        site.setAttribute("username", 
                          server.getAttribute("username"));

        String drop = server.getAttribute("dropdir");
        if (drop.equals("")) {
            drop = "/tmp";
        }
        site.setAttribute("dropdir", drop);
    }

}
