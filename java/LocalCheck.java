/*
 * $Header: /home/stefano/cvs/gump/java/LocalCheck.java,v 1.5 2003/04/05 17:41:49 stefano Exp $
 * $Revision: 1.5 $
 * $Date: 2003/04/05 17:41:49 $
 *
 * ====================================================================
 *
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999-2003 The Apache Software Foundation.  All rights
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
import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXParseException;

/**
 * This will check if the pkgDir references are still up-to-date
 * and present. This way you can take action before you run the 
 * gump build.
 * 
 * @author <a href="mailto:martin@mvdb.net">Martin van den Bent</a>
 * @version $Id: LocalCheck.java,v 1.5 2003/04/05 17:41:49 stefano Exp $
 */
public class LocalCheck {
    
    private static String DEFAULT_WORKSPACE_FILE="/home/gump/dist/swami.xml";
    private String workspaceFile;
    private String pkgDir;
    private Document profile;
    private String currentDir;
    private Map projectCache;

    DocumentBuilderFactory dFactory = DocumentBuilderFactory.newInstance();
    
    /**
     * Constructor for LocalCheck.
     */
    public LocalCheck(String workSpace)
        throws Exception  {
        this.workspaceFile = workSpace;
        Document doc = parse(workSpace);
        Workspace.init(doc.getDocumentElement());
        this.pkgDir = Workspace.getPkgDir();
        this.pkgDir+=((pkgDir.endsWith(File.separator))?"":File.separator);
        currentDir = new File(workspaceFile).getAbsoluteFile().getParent()+File.separator;
        String profileFile = doc.getElementsByTagName("profile").item(0).getAttributes().getNamedItem("href").getNodeValue();
        if ((new File(profileFile)).isAbsolute()) {
            this.profile = parse(profileFile);
        } else {
            this.profile = parse(currentDir+profileFile);
        }
        parseProfile();
    }
    
    private void parseProfile() {
        NodeList nodeList = profile.getElementsByTagName("project");
        System.out.println("Found "+nodeList.getLength()+" installed packages");
        System.out.println("Using "+pkgDir+" directory to check installed packages");
        int okCounter = 0;
        for (int i = 0; i < nodeList.getLength(); i++) {
            if (check((Element)nodeList.item(i))) {
                okCounter++;
            }
        }
        System.out.println(nodeList.getLength() - okCounter + " packages need updating");
    }
    
    private boolean check(Element element) {
        String name = element.getAttribute("name");
        String pkg = element.getAttribute("package");
        String projectFile = currentDir+"project"+File.separator+name+".xml";
        boolean ok = true;
        Document doc = null;
        try {
            if (!new File(projectFile).exists()) {
                setupCache();
                projectFile = currentDir+"project"+File.separator+(String)projectCache.get(name);
            }
            doc = parse(projectFile);
            ArrayList list = getJars(doc, name);
            String moduleURL = getModuleURL(doc);
            boolean error = false;
            for (int i = 0; i < list.size(); i++) {
                String jar = (String) list.get(i);
                String jarFile = pkgDir+pkg+File.separator+jar;
                if (!new File(jarFile).exists()) {
                    if (!error) {
                        System.out.println("Problems encountered in project "+name);
                        System.out.println("You can get updates at "+moduleURL);
                        error = true;
                    }
                    System.out.println("    cannot find "+jarFile);
                    ok = false;
                }
            }
        } catch (Exception e) {
            System.out.println("problems reading "+projectFile+" for project "+name);
            ok =  false;
        }
        return ok;
    }
    
    private String getModuleURL(Document doc) {
        return ((Element)doc.getElementsByTagName("url").item(0)).getAttribute("href");
    }
    
    private ArrayList getJars(Document doc, String name) {
        ArrayList jars = new ArrayList();
        NodeList list = doc.getElementsByTagName("project");
        for (int i = 0; i < list.getLength(); i++) {
            Element element = (Element)list.item(i);
            if (element.getAttribute("name").equals(name)) {
                NodeList jarNodes = element.getElementsByTagName("jar");
                for (int j=0; j < jarNodes.getLength(); j++) {
                    jars.add(((Element)jarNodes.item(j)).getAttribute("name"));
                }
            }
        }
        return jars;
    }
    
    private void setupCache() {
        if (projectCache == null) {
            projectCache = new HashMap();
        }else{
            return;
        }
        String xmlDirStr = currentDir+"project"+File.separator;
        File xmlDir = new File(xmlDirStr);
        if (xmlDir.isDirectory()) {
            File files[] = xmlDir.listFiles();
            for (int i = 0; i < files.length; i++) {
                File file = files[i];
                // ignore cvs .# files.. 
                if (file.getName().startsWith(".") || file.isDirectory()) {
                    continue;
                }
                setProjectsInCache(file);
            }
        }
    }
    
    /**
     * Adds the projects that it found in the file to the cache
     */
    private void setProjectsInCache(File file) {
        try {
            Document doc = parse(file.toString());
            NodeList list = doc.getElementsByTagName("project");
            for (int i = 0; i < list.getLength();i++) {
                String project = ((Element)list.item(i)).getAttribute("name");
                projectCache.put(project, file.getName());
            }
        }catch(Exception e) { }
    }
        

    public static void main(String[] args)  {
        try {
            String workSpace = DEFAULT_WORKSPACE_FILE;
            if (args.length >= 1) {
                workSpace = args[0];
            }
            new LocalCheck(workSpace);
        }catch(Exception e) {
            System.out.println("Unexpected failure in LocalCheck");
            e.printStackTrace(System.out);
        }
    }
    
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


}
