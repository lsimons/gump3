package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Value object to represent the each run made by gump.
 * 
 * @author hodden
 * 
 */
public class Run implements Serializable {

    private String id;

    private String start;

    private String end;

    private String workspace;

    private String name;

    public Run() {
    }

    public Run(String id, String start, String end, String workspace, String name) {
        this.id = id;
        this.start = start;
        this.end = end;
        this.workspace = workspace;
        this.name = name;
    }

    public Run(ResultSet rs) throws SQLException {
        this.id = rs.getString("id");
        this.start = rs.getString("start_time");
        this.end = rs.getString("end_time");
        this.workspace = rs.getString("workspace_id");
        this.name = rs.getString("name");
    }

    /** Getter and setters for the Run Value Object */
    public String getEnd() {
        return end;
    }

    public void setEnd(String end) {
        this.end = end;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getStart() {
        return start;
    }

    public void setStart(String start) {
        this.start = start;
    }

    public String getWorkspace() {
        return workspace;
    }

    public void setWorkspace(String workspace) {
        this.workspace = workspace;
    }

}
