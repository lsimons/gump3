package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

public class HistoryVO implements Serializable {

    private int currentState;

    private int durationInState;

    private String startOfState;

    private int previusState;

    private String firstSuccess = null;

    private String lastSuccess = null;

    private String[] states = new String[] { "success", "failure", "stalled" };

    private HashMap<String, Integer> numberAtState = new HashMap<String, Integer>();

    private List<HistoryObject> values = new LinkedList<HistoryObject>();

    public HistoryVO() {
        for (int i = 0; i < states.length; i++) {
            numberAtState.put(states[i], 0);
        }
    }

    /**
     * Sets the values for the history object from a resultset from the
     * database.
     * 
     * @param rs -
     *            ResultSet from db.
     * @throws SQLException
     */
    public void addValues(int result, String start) {
        values.add(new HistoryObject(start, result));
    }

    public void setValues() throws SQLException {

        HistoryObject tmp;
        while (values.size() != 0) {
            // String start = rs.getString("start");
            // int result = rs.getInt("result");
            tmp = values.remove(0);
            String start = tmp.getStart();
            int result = tmp.getResult();

            currentState = result;
            this.updateNumberOfState(result);
            durationInState = 0;
            startOfState = start;
            previusState = currentState;
            if (currentState == 0) {
                this.setSuccessStatus(start);
            }

            this.checkDurationAndState();

        }
    }

    /**
     * Recursive method to check for the states that this package has gone
     * through historicly and check for duration in state.
     * 
     * @param rs
     *            result from the db.
     * @throws SQLException
     */
    private void checkDurationAndState() throws SQLException {
        if (values.size() == 0)
            return;
        HistoryObject tmp;
        tmp = values.remove(0);
        int result = tmp.getResult();
        String start = tmp.getStart();
        this.updateNumberOfState(result);
        if (result == 0)
            this.setSuccessStatus(start);

        if (result != currentState) {
            previusState = result;
            this.checkState();

        } else {
            startOfState = start;
            this.checkDurationAndState();

        }
    }

    /**
     * Recursive method to go throu the states that this package has gone
     * through historicly. With out checking for duration in state.
     * 
     * @param rs
     *            the result from the db
     * @throws SQLException
     */
    private void checkState() throws SQLException {
        if (values.size() == 0)
            return;
        HistoryObject tmp = values.remove(0);

        int result = tmp.getResult();
        String start = tmp.getStart();
        this.updateNumberOfState(result);
        if (result == 0)
            this.setSuccessStatus(start);
        this.checkState();
    }

    /**
     * Updates the first and last success for this package by the given date.
     * 
     * @param start
     */
    private void setSuccessStatus(String start) {
        if (firstSuccess == null) {
            firstSuccess = start;
        }
        lastSuccess = start;
    }

    private void updateNumberOfState(int result) {
        numberAtState.put(states[result], numberAtState.get(states[result]) + 1);
    }

    /* Getters and Setters */
    public String getCurrentStateString() {
        return states[currentState];
    }

    public int getCurrentState() {
        return currentState;
    }

    public int getDurationInState() {
        return durationInState;
    }

    public String getStartOfState() {
        return startOfState;
    }

    public String getFirsSuccess() {
        if (firstSuccess == null) {
            return "-";
        }
        return firstSuccess;
    }

    public String getLastSuccess() {
        if (lastSuccess == null) {
            return "-";
        }
        return lastSuccess;
    }

    public String getPreviusStateString() {
        return states[previusState];
    }

    public int getPreviusState() {
        return previusState;
    }

    public int getNumberOfSuccess() {
        return numberAtState.get(states[0]);
    }

    public int getNumberOfFailures() {
        return numberAtState.get(states[1]);
    }

    public int getNumberOfStalled() {
        return numberAtState.get(states[2]);
    }
}
