package org.apache.gump.dynagump.presentation.database;

/**
 * Exception generated when the database couldn't be initiated
 * 
 * @author hodden
 * 
 */
public class CouldNotFindDBException extends Exception {

    private Exception nestedException;

    public CouldNotFindDBException() {
        super();
    }

    public CouldNotFindDBException(String s) {
        super(s);
    }

    public CouldNotFindDBException(Throwable t) {
        super(t);
    }

    public CouldNotFindDBException(String s, Throwable t) {
        super(s, t);
    }

    public CouldNotFindDBException(String message, Exception e) {
        super(message);
        this.nestedException = e;

    }

    public String getMessage() {
        String tempStr = super.getMessage();
        if (nestedException != null) {
            tempStr += "\n\n *** Nested Exception *** \n" + nestedException.getMessage();
        }
        return tempStr;
    }

}
