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
 * $Header: /home/stefano/cvs/gump/java/LocalCheck.java,v 1.6 2004/02/27 08:31:31 bodewig Exp $
 * $Revision: 1.6 $
 * $Date: 2004/02/27 08:31:31 $
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
 * @version $Id: LocalCheck.java,v 1.6 2004/02/27 08:31:31 bodewig Exp $
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
