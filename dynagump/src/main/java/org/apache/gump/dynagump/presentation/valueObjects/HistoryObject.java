package org.apache.gump.dynagump.presentation.valueObjects;

public class HistoryObject {

    private String start;

    private int result;

    public HistoryObject() {
    }

    public HistoryObject(String start, int result) {
        this.start = start;
        this.result = result;
    }

    public int getResult() {
        return result;
    }

    public void setResult(int result) {
        this.result = result;
    }

    public String getStart() {
        return start;
    }

    public void setStart(String start) {
        this.start = start;
    }

}
