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
 * $Header: /home/stefano/cvs/gump/resources/test/cvs-modules/module1/src/smoketest/Smoke.java,v 1.1 2004/05/17 20:11:18 ajack Exp $
 * $Revision: 1.1 $
 * $Date: 2004/05/17 20:11:18 $
 */
 


package smoketest;

/**
 * Response to can we smoke.
 * @todo Quit smoking ;-)
 */
public class Smoke {

    private boolean lamp = false;

    public String smoke() {
        //assert true;  // jalopy fails here.
        return lamp
            ? "Smoke em if you got em"
            : "Field strip and police your butts";
    }

    /**
     * Returns the lamp.
     * @return boolean
     */
    public boolean isLampLighted() {
        return lamp;
    }

    /**
     * Sets the lamp.
     * @param lamp The lamp to set
     */
    public void setLamp(boolean lamp) {
        this.lamp = lamp;
    }

    /**
     * A nonsense main method for testing generated execution
     * scripts.
     */
    public static void main(String[] args) {
        Smoke smoker = new Smoke();
        smoker.setLamp(true);
        System.out.println("We turned the lamp on!");
    }
}

