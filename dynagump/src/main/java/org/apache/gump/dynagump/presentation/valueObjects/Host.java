package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;

/**
 * A value object for one host that contains a list of workspaces that is linked
 * to the host.
 * 
 * @author hodden
 * 
 */
public class Host implements Serializable {

    private String address;

    private String description;

    private String cpuArch;

    private int cpuNumber;

    private int cpuSpeedMhz;

    private int memoryMb;

    private int diskGb;

    private String name;

    private List<WorkSpace> workspaces = new LinkedList<WorkSpace>();

    public Host() {
    }

    public Host(String address, String description, String cpuArch, int cpuNumber, int cpuSpeed, int memoryMb, int diskGb, String name) {
        this.address = address;
        this.description = description;
        this.cpuArch = cpuArch;
        this.cpuNumber = cpuNumber;
        this.cpuSpeedMhz = cpuSpeed;
        this.memoryMb = memoryMb;
        this.diskGb = diskGb;
        this.name = name;

    }

    public Host(ResultSet rs) throws SQLException {
        this.address = rs.getString("address");
        this.description = rs.getString("description");
        this.cpuArch = rs.getString("cpu_arch");
        this.cpuNumber = rs.getInt("cpu_number");
        this.cpuSpeedMhz = rs.getInt("cpu_speed_Mhz");
        this.memoryMb = rs.getInt("memory_Mb");
        this.diskGb = rs.getInt("disk_Gb");
        this.name = rs.getString("name");

    }

    public void addWorkspace(WorkSpace w) {
        workspaces.add(w);
    }

    public void setWorkspaces(ResultSet rs) throws SQLException {
        while (rs.next()) {
            workspaces.add(new WorkSpace(rs));
        }
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCpuArch() {
        return cpuArch;
    }

    public void setCpuArch(String cpuArch) {
        this.cpuArch = cpuArch;
    }

    public int getCpuNumber() {
        return cpuNumber;
    }

    public void setCpuNumber(int cpuNumber) {
        this.cpuNumber = cpuNumber;
    }

    public int getCpuSpeedMhz() {
        return cpuSpeedMhz;
    }

    public void setCpuSpeedMhz(int cpuSpeedMhz) {
        this.cpuSpeedMhz = cpuSpeedMhz;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public int getDiskGb() {
        return diskGb;
    }

    public void setDiskGb(int diskGb) {
        this.diskGb = diskGb;
    }

    public int getMemoryMb() {
        return memoryMb;
    }

    public void setMemoryMb(int memoryMb) {
        this.memoryMb = memoryMb;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<WorkSpace> getWorkspaces() {
        return workspaces;
    }

    public void setWorkspaces(List<WorkSpace> workspaces) {
        this.workspaces = workspaces;
    }

}
