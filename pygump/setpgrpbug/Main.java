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
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

// MODIFIED FROM ANT CVS HEAD:
//    http://cvs.apache.org/viewcvs.cgi/ant/src/main/org/apache/tools/ant/taskdefs/
public class Main {
    private static ProcessDestroyer processDestroyer = new ProcessDestroyer();
    private int exitValue;
    
    public static void main(String[] args) throws Exception {
      Main main = new Main();
      int result = main.start(args);
    }
    public int start(String[] args) throws Exception {
        System.out.println("  Main.java line #33");
        System.err.println("  Main.java line #34 (to stderr)");
        
        String javahome = args[0];
        System.out.println("  Java home is " + javahome);
    
        Java13CommandLauncher launcher = new Java13CommandLauncher();
        ExecuteStreamHandler streamHandler = new PumpStreamHandler();
        
        String[] command = new String[] {javahome + "/bin/java", "Main2"};
        String[] env = new String[] {"JAVA_HOME=" + javahome};
        File dir = new File(".");

        Process process = launcher.exec(command, env, dir);
        try {
            streamHandler.setProcessInputStream(process.getOutputStream());
            streamHandler.setProcessOutputStream(process.getInputStream());
            streamHandler.setProcessErrorStream(process.getErrorStream());
        } catch (IOException e) {
            process.destroy();
            throw e;
        }
        streamHandler.start();

        try {
            processDestroyer.add(process);

            waitFor(process);

            streamHandler.stop();
            closeStreams(process);

            return exitValue;
        } catch (ThreadDeath t) {
            // #31928: forcibly kill it before continuing.
            process.destroy();
            throw t;
        } finally {
            // remove the process to the list of those to destroy if
            // the VM exits
            //
            processDestroyer.remove(process);
        }
    }
  
    protected void waitFor(Process process) {
        try {
            process.waitFor();
            exitValue = process.exitValue();
        } catch (InterruptedException e) {
            process.destroy();
        }
    }
    public static void closeStreams(Process process) {
        close(process.getInputStream());
        close(process.getOutputStream());
        close(process.getErrorStream());
    }
    public static void close(InputStream device) {
        if (device != null) {
            try {
                device.close();
            } catch (IOException ioex) {
                //ignore
            }
        }
    }
    public static void close(OutputStream device) {
        if (device != null) {
            try {
                device.close();
            } catch (IOException ioex) {
                //ignore
            }
        }
    }
}
