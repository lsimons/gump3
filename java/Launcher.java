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
 * $Header: /home/stefano/cvs/gump/java/Launcher.java,v 1.2 2004/02/27 08:31:31 bodewig Exp $
 * $Revision: 1.2 $
 * $Date: 2004/02/27 08:31:31 $
 */

import java.lang.reflect.Method;
import java.util.Properties;
import java.net.URLClassLoader;
import java.net.URL;
import java.io.FileInputStream;
import java.io.File;
import java.util.Vector;
import java.util.Enumeration;

public class Launcher {
    
    public static void main(String[] args) throws Exception {
        
        if (args.length < 2) {
            printUsage();
        }
        
        String[] realArgs = new String[args.length - 2];
        for (int i = 0, c = realArgs.length; i < c; i++) {
            realArgs[i] = args[ i + 2];
            System.out.println("args="+args[ i + 2]);
        }
        // Build the classloader
        URLClassLoader fc;
        Properties p=new Properties();
        Vector v=new Vector();
        try{
            p.load(new FileInputStream(args[0]));
            
            for(Enumeration e=p.propertyNames();e.hasMoreElements();){
                String name=(String)e.nextElement();
                if (name.indexOf(".boot") > 0)
                    v.add(0, p.getProperty(name));
                else
                    v.add(p.getProperty(name));
                
            }
        } catch (Throwable e) {
            e.printStackTrace();
            System.exit(1);
        }
        URL[] cp=new URL[v.size()];
        for( int i=0 ; i<v.size() ; i++ ){
            File f=new File((String)v.get(i));
            cp[i]=f.toURL();
        }
        // First try to find the class
        fc=new URLClassLoader(cp,p.getClass().getClassLoader()){
            public Class loadClass(String name) throws ClassNotFoundException {
                return super.loadClass(name);
            }
        };
        Class clazz = null;
        try {
            clazz = fc.loadClass(args[1]);
        } catch (ClassNotFoundException e) {
            System.err.println("The class " + args[1] + " was not found in the classpath.");
            System.exit(1);
        } catch (Throwable e) {
            e.printStackTrace();
            System.exit(1);
        }
        // if the class exists, get the main method
        Method mainMethod = null;
        try {
            mainMethod = clazz.getMethod("main", new Class[]{String[].class});
        } catch (NoSuchMethodException e) {
            System.err.println("No method public static void main(String[] args) in " + clazz.getName());
            System.exit(1);
        } catch (Throwable e) {
            e.printStackTrace();
            System.exit(1);
        }
        
        // try to make sure the main method is accessible
        try {
            mainMethod.setAccessible(true);
        } catch (Throwable e) {
        }
        
        
        
        try {
            mainMethod.invoke(null, new Object[]{realArgs});
        } catch (IllegalAccessException e) {
            System.err.println("Please make sure the class " + clazz.getName() +
            " and the method main(String[] args) are public.");
            System.exit(1);
        } catch (Throwable e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    /**
     * Description of the Method
     */
    static void printUsage() {
        String usage = "Launcher - Wrapper to overcome command line length problems in some OSes\n" +
        "Usage: Launcher classpath.properties class [args...]\n" +
        "\n";
        System.out.println(usage);
        System.exit(1);
    }
    
}
