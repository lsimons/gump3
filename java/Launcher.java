/* ====================================================================
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
 * 4. The names "The Jakarta Project", "Gump", and "Apache Software
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
