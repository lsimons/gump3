/*
 * $Header: /home/stefano/cvs/gump/java/Workspace.java,v 1.6 2002/08/27 14:54:09 nicolaken Exp $
 * $Revision: 1.6 $
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
 
import org.w3c.dom.Element;
import org.w3c.dom.Node;

import java.util.HashMap;

public class Workspace {

    static final String GUMP_VERSION = "0.3";

    private static Element element;
    private static String basedir;
    private static Element javadoc;
    private static Element deliver;
    private static Element nag;
    private static HashMap servers = new HashMap();
    private static HashMap sites = new HashMap();

    /**
     * Static property accessor for basedir attribute.
     * @return Base directory associated with this workspace
     */
    public static String getBaseDir() {
        return element.getAttribute("basedir");
    }

    /**
     * Static property accessor for pkgdir attribute.
     * @return Package directory associated with this workspace
     */
    public static String getPkgDir() {
        return element.getAttribute("pkgdir");
    }

    /**
     * Static property accessor for jardir attribute.
     * @return Package directory associated with this workspace
     */
    public static String getJarDir() {
        return element.getAttribute("jardir");
    }

    /**
     * Static property accessor for javadoc element.
     * @return Javadoc element (if any) associated with this workspace
     */
    public static Element getJavaDoc() {
        return javadoc;
    }

    /**
     * Static property accessor for nag element.
     * @return Javadoc element (if any) associated with this workspace
     */
    public static Element getNag() {
        return nag;
    }

    /**
     * Static accessor - do we deliver to the given site?
     * @return true if a server of the given name is defined in the workspace.
     */
    public static boolean isSiteDefined(String name) {
        return sites.containsKey(name);
    }

    /**
     * Static accessor for deliver's scratchdir attribute.
     * @return Deliver scratchdir associated with this workspace.
     */
    public static String getScratchDir() {
        if (deliver != null) {
            return deliver.getAttribute("scratchdir");
        }
        return null;
    }

    /**
     * Static accessor for deliver's named server child.
     * @return null if server is not defined, the server element otherwise.
     */
    public static Element getServer(String name) {
        return (Element) servers.get(name);
    }

    /**
     * Default and verify various workspace attributes.
     * If not specified:
     *   banner-image="http://jakarta.apache.org/images/jakarta-logo.gif"
     *   banner-link="http://jakarta.apache.org"
     *   cvsdir=basedir+"/cvs"
     *   logdir=basedir+"/log"
     *   pkgdir=basedir
     * @param Workspace element to be updated
     */
    public static void init(Element workspace) throws Exception {
        Workspace.element = workspace;

        if (!workspace.getAttribute("version").equals(GUMP_VERSION)) {
            throw new Exception("workspace version " + GUMP_VERSION +
                                " required.");
        }

        basedir = workspace.getAttribute("basedir");

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

        if (workspace.getAttribute("pkgdir").equals("")) {
            workspace.setAttribute("pkgdir", basedir);
        }

        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("javadoc")) {
                javadoc = (Element) child;
            } else if (child.getNodeName().equals("nag")) {
                nag = (Element) child;
            } else if (child.getNodeName().equals("deliver")) {
                handleDeliver((Element) child);
            }
        }
        
        if (deliver != null) {
            element.removeChild(deliver);
            String scratchdir = deliver.getAttribute("scratchdir");
            if (scratchdir.equals("")) {
                deliver.setAttribute("scratchdir", basedir+"/scratch");
            }
        }
        
    }

    /**
     * Fill map of servers.
     */
    private static void handleDeliver(Element element) {
        deliver = element;
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("server")) {
                Element server = (Element) child;
                servers.put(server.getAttribute("name"), server);
                handleSites(server);
            }
        }
    }

    /**
     * Fill map of sites.
     */
    private static void handleSites(Element element) {
        Node child=element.getFirstChild();
        for (; child != null; child=child.getNextSibling()) {
            if (child.getNodeName().equals("site")) {
                Element site = (Element) child;
                sites.put(site.getAttribute("name"), site);
            }
        }
    }    
}
