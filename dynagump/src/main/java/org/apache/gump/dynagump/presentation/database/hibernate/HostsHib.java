package org.apache.gump.dynagump.presentation.database.hibernate;

import java.util.Set;

public class HostsHib {

    private String address;

    private String description;

    private String cpuArch;

    private int cpuNumber;

    private int cpuSpeed;

    private int memoryMb;

    private int diskGB;

    private String name;

    private Set workspace;

    public Set getWorkspace() {
        return workspace;
    }

    public void setWorkspace(Set workspace) {
        this.workspace = workspace;
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

    public int getCpuSpeed() {
        return cpuSpeed;
    }

    public void setCpuSpeed(int cpuSpeed) {
        this.cpuSpeed = cpuSpeed;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public int getDiskGB() {
        return diskGB;
    }

    public void setDiskGB(int diskGB) {
        this.diskGB = diskGB;
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

}
