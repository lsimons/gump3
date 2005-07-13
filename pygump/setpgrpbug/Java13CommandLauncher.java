/*
 * Copyright  2000,2002,2004-2005 The Apache Software Foundation
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
 */
import java.lang.reflect.Method;
import java.io.File;

// MODIFIED FROM ANT CVS HEAD:
//    http://cvs.apache.org/viewcvs.cgi/ant/src/main/org/apache/tools/ant/taskdefs/    
    public class Java13CommandLauncher {
        private Method myExecWithCWD;

        public Java13CommandLauncher() throws Exception {
            System.out.println("  Main.java line #21");
            // Locate method Runtime.exec(String[] cmdarray,
            //                            String[] envp, File dir)
            myExecWithCWD = Runtime.class.getMethod("exec",
                    new Class[] {String[].class, String[].class, File.class});
        }

        public Process exec(String[] cmd, String[] env,
                            File workingDir) throws Exception {
            System.out.println("  Main.java line #41");
            return (Process) myExecWithCWD.invoke(Runtime.getRuntime(),
                   new Object[] {cmd, env, workingDir});
        }
    }
